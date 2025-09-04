import threading
import queue
import time
import numpy as np
import matplotlib.pyplot as plt
import datetime
import glob
import os
import pyvisa
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, OPERATION_MODE

try:
    # if on Windows, use the provided setup script to add the DLLs folder to the PATH
    from windows_setup import configure_path
    configure_path()
except ImportError:
    configure_path = None


# 설정
n_frames = 20000  # 측정할 총 프레임 수 (대용량 측정)
mw_start = 3e9    # 시작 MW 주파수: 3 GHz
mw_step = 5e7     # 주파수 스텝: 50 MHz
mw_steps = 20     # 20 스텝 (3 GHz ~ 3.95 GHz)

# ROI 영역 설정 (실험 전 카메라 해상도에 맞게 검증 필요)
roi_y_start, roi_y_end = 400, 801
roi_x_start, roi_x_end = 550, 1001

# 런 폴더(날짜_시간)와 주파수별 저장 폴더를 미리 생성 (효율성 향상)
code_dir = os.path.dirname(os.path.abspath(__file__))
run_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
run_dir = os.path.join(code_dir, run_stamp)
os.makedirs(run_dir, exist_ok=True)

# 인덱스(i) -> 폴더 경로 매핑, 폴더명 예: 3.00GHz, 3.05GHz, ...
freq_paths = []
for i in range(mw_steps):
    f_hz = mw_start + i * mw_step
    folder_name = f"{f_hz/1e9:.2f}GHz"
    folder_path = os.path.join(run_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    freq_paths.append(folder_path)

# 카메라 프레임 데이터와 intensity 데이터 저장용 자료구조
# 프레임 큐: 이미지 전체를 저장하지 않고 (frame_count, roi_total_intensity)만 저장하여 메모리 사용 최소화
frame_queue = queue.Queue(maxsize=n_frames)
intensity_dict = {}  # key: MW 주파수 (Hz), value: list of ROI 총 intensity 값

# 전역 변수 및 동기화를 위한 변수
frames_captured = 0
capture_lock = threading.Lock()
camera_ready = False  # 카메라가 ARM되면 True로 설정
measurement_complete = False

# -----------------------------------------
# SDG2082x 제어 함수 (PyVISA 이용)
# -----------------------------------------
def sdg_control():
    rm = pyvisa.ResourceManager()
    try:
        sdg = rm.open_resource("USB0::0xF4EC::0xEE38::SDG2XCAD1R2393::INSTR")
    except Exception as e:
        print("SDG2082x 연결 실패:", e)
        return

    try:
        sdg.write("*RST")
        time.sleep(0.1)
        sdg.write("C1:BSWV WVTP,PULSE")   # 펄스 모드 선택
        sdg.write("C1:BSWV FRQ,250")         # 250Hz 펄스 → 4ms 주기
        sdg.write("C1:BSWV AMP,2")
        sdg.write("C1:BSWV OFST,1")
        # 노트: 2e-6 = 2 µs (실험 명세에 맞춤)
        sdg.write("C1:BSWV WIDTH,2e-5")      # 펄스 폭 20µs
    except Exception as e:
        print("SDG 초기 설정 오류:", e)
        return

    print("SDG2082x 제어 시작: 카메라 준비 대기 중...")
    while not camera_ready:
        time.sleep(0.01)
    print("카메라 준비 완료. SDG2082x 펄스 출력 시작")
    sdg.write("C1:OUTP ON")  # 출력 활성화

    global frames_captured
    while True:
        with capture_lock:
            if frames_captured >= n_frames:
                break
        time.sleep(0.01)
    # 출력 비활성화 후 종료
    try:
        sdg.write("C1:OUTP OFF")
    except Exception:
        pass
    sdg.close()
    print("SDG 제어 종료: 20000 프레임 수집 후 SDG 꺼짐")

# -----------------------------------------
# 카메라 Producer 함수
# -----------------------------------------
def camera_producer():
    global frames_captured, camera_ready
    with TLCameraSDK() as sdk:
        available_cameras = sdk.discover_available_cameras()
        if len(available_cameras) < 1:
            print("카메라가 감지되지 않았습니다.")
            return
        with sdk.open_camera(available_cameras[0]) as camera:
            camera.exposure_time_us = 1.5  # 1.5 ms 노출
            camera.frames_per_trigger_zero_for_unlimited = 1
            camera.image_poll_timeout_ms = 1000
            # 하드웨어 트리거 사용 시 내부 프레임레이트 제어는 비활성화
            camera.is_frame_rate_control_enabled = False

            camera.operation_mode = OPERATION_MODE.HARDWARE_TRIGGERED
            # 하드웨어 트리거 수신을 위해 충분한 내부 버퍼 확보 (드롭 방지)
            camera.arm(10)
            print("카메라 ARM: 하드웨어 트리거 대기 중")
            camera_ready = True  # 카메라 준비 완료

            try:
                while True:
                    with capture_lock:
                        if frames_captured >= n_frames:
                            break
                    frame = camera.get_pending_frame_or_null()
                    if frame is not None:
                        image_buffer_copy = np.copy(frame.image_buffer)
                        img = image_buffer_copy.reshape(
                            camera.image_height_pixels, camera.image_width_pixels
                        )
                        # ROI 경계 보정 (이미지 범위를 벗어나지 않도록 클램프)
                        y0 = max(0, min(roi_y_start, img.shape[0]))
                        y1 = max(y0, min(roi_y_end,   img.shape[0]))
                        x0 = max(0, min(roi_x_start, img.shape[1]))
                        x1 = max(x0, min(roi_x_end,   img.shape[1]))
                        roi = img[y0:y1, x0:x1]
                        # ROI 2D 배열을 그대로 큐에 전달 (소비자에서 저장 및 집계)
                        frame_queue.put((frame.frame_count, roi))
                        with capture_lock:
                            frames_captured += 1
                        # 디버깅: 매 1000프레임마다 진행상황 출력
                        if frames_captured % 1000 == 0:
                            print(f"DEBUG: 현재까지 {frames_captured} 프레임 수집됨")
                        # 프레임 번호 및 현재까지 수집된 프레임 정보 출력
                        print(f"프레임 #{frame.frame_count} 저장 (총 {frames_captured}/{n_frames})")
            except KeyboardInterrupt:
                print("카메라 Producer 종료 (KeyboardInterrupt)")
            finally:
                camera.disarm()
                # 소비자 종료 신호
                try:
                    frame_queue.put_nowait((None, None))
                except Exception:
                    pass

# -----------------------------------------
# 카메라 Consumer 함수 (ROI 영역 처리: 총 intensity 합 계산 및 디버깅 로그 추가)
# -----------------------------------------
def camera_consumer():
    global measurement_complete, intensity_dict
    intensity_dict = {}
    processed_frames = 0
    # 초기 워밍업 프레임: 정확한 주파수-프레임 정렬을 위해 한 사이클(= mw_steps) 건너뜀
    warmup_skip = mw_steps
    target_frames = n_frames - warmup_skip
    while processed_frames < target_frames:
        try:
            frame_num, roi = frame_queue.get(timeout=0.5)
            # 종료 신호 처리
            if frame_num is None:
                break
            # 워밍업 프레임 건너뜀 (주파수 경계 정렬)
            if frame_num <= warmup_skip:
                continue
            # MW 주파수 계산 및 폴더 선택
            step_index = (frame_num - 1) % mw_steps
            freq = mw_start + step_index * mw_step  # Hz
            # 파일명 생성 후 해당 주파수 폴더에 저장
            freq_mhz = int(round(freq / 1e6))
            filename = f"roi_frame_{frame_num:06d}_f{freq_mhz:04d}MHz.txt"
            filepath = os.path.join(freq_paths[step_index], filename)
            try:
                np.savetxt(filepath, roi.astype(np.uint16), fmt='%d')
            except Exception as e:
                print(f"ROI 저장 실패 (frame {frame_num}): {e}")
            if freq in intensity_dict:
                intensity_dict[freq].append(np.sum(roi))
            else:
                intensity_dict[freq] = [np.sum(roi)]
            processed_frames += 1
            # 디버깅: 각 500프레임마다 데이터 수 확인
            if processed_frames % 500 == 0:
                print(f"DEBUG: 소비된 프레임 수 {processed_frames}, 현재 intensity_dict의 항목 수: {len(intensity_dict)}")
            print(f"프레임 #{frame_num} 처리: MW freq = {freq/1e9:.3f} GHz, ROI 총 intensity = {int(np.sum(roi))}")
        except queue.Empty:
            continue
    measurement_complete = True

# -----------------------------------------
# 쓰레드 시작 및 데이터 수집 완료
# -----------------------------------------
sdg_thread = threading.Thread(target=sdg_control, daemon=True)
producer_thread = threading.Thread(target=camera_producer, daemon=True)
consumer_thread = threading.Thread(target=camera_consumer, daemon=True)

sdg_thread.start()
producer_thread.start()
consumer_thread.start()

producer_thread.join()
consumer_thread.join()
sdg_thread.join()

# 디버깅: intensity_dict에 저장된 데이터 개수 확인
for freq in sorted(intensity_dict.keys()):
    print(f"DEBUG: 주파수 {freq/1e9:.3f} GHz에 측정된 데이터 개수: {len(intensity_dict[freq])}")

# 각 MW 주파수별 평균 intensity 계산 (각 주파수 당 1000회 측정이 목표)
frequencies = sorted(intensity_dict.keys())
avg_intensities = [np.mean(intensity_dict[freq]) for freq in frequencies]

# CSV 저장 로직 제거됨: ROI 2D 배열은 개별 .txt 파일로만 저장됩니다.
