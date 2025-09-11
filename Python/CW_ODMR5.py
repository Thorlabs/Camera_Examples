import threading
import queue
import time
import numpy as np
import matplotlib.pyplot as plt
import datetime
import glob
import os
try:
    import h5py
    HAS_H5PY = True
except Exception:
    HAS_H5PY = False
from collections import defaultdict
import pyvisa
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, OPERATION_MODE
from thorlabs_tsi_sdk.tl_camera_enums import TRIGGER_POLARITY

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

# 런타임 플래그
PRINT_PER_FRAME = True      # 프레임당 1회 로그 출력 (프레임 번호 + 주파수)
SAVE_TXT = False            # 주파수 폴더별 .txt 저장 (비권장: 파일 수 많음)
SAVE_HDF5 = True            # HDF5에 ROI/메타데이터 스트리밍 저장
LIVE_ODMR = True            # 스윕 1회마다 라이브 평균 ODMR 플롯 업데이트

# 카메라 프레임 데이터와 intensity 데이터 저장용 자료구조
# 프레임 큐: 이미지 전체를 저장하지 않고 (frame_count, roi_total_intensity)만 저장하여 메모리 사용 최소화
frame_queue = queue.Queue(maxsize=512)
plot_queue = queue.Queue(maxsize=16)  # 라이브 플롯 업데이트용 (메인 스레드에서만 그림)
intensity_dict = {}  # key: MW 주파수 (Hz), value: list of ROI 총 intensity 값

# 전역 변수 및 동기화를 위한 변수
frames_captured = 0
capture_lock = threading.Lock()
camera_ready = False  # 카메라가 ARM되면 True로 설정
measurement_complete = False
synth_start_event = threading.Event()  # 연속 프레임 안정 진입 시 SynthHD(CH2) 시작 신호

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
        sdg.write("C1:OUTP LOAD,HZ")
        sdg.write("C1:BSWV AMP,3.3")      # 3.3 Vpp (LVTTL range)
        sdg.write("C1:BSWV OFST,1.65")    # 0–3.3 V level (centered)
        # LVTTL 신호 및 200µs 최소 펄스 폭 권고에 맞춤
        sdg.write("C1:BSWV WIDTH,2e-4")   # 200 µs pulse width (>= 100 µs min)
    except Exception as e:
        print("SDG 초기 설정 오류:", e)
        return

    # -----------------------
    # CH2: SynthHD 트리거 전용 (기본 HIGH, 짧은 LOW 펄스 = 1 step)
    # -----------------------
    try:
        sdg.write("C2:BSWV WVTP,PULSE")
        sdg.write("C2:BSWV FRQ,250")
        sdg.write("C2:OUTP LOAD,HZ")
        sdg.write("C2:BSWV AMP,3.0")      # 0–3.0 V
        sdg.write("C2:BSWV OFST,1.5")     # center @ 1.5 V
        sdg.write("C2:BSWV WIDTH,2e-4")   # 200 µs (LOW 폭으로 사용; step time보다 짧게)
        # 기본 HIGH, 짧은 LOW를 위해 polarity/duty 설정 시도
        try:
            sdg.write("C2:BSWV POL,NEG")  # 지원 시: 펄스 낮아지는 형태(LOW 펄스)
        except Exception:
            try:
                sdg.write("C2:BSWV DUTY,99")  # 대안: 거의 항상 HIGH (펄스 LOW 구간을 매우 짧게)
            except Exception:
                pass
        sdg.write("C2:OUTP OFF")  # 안정 진입 신호 전까지 OFF
    except Exception as e:
        print("SDG CH2 초기 설정 오류:", e)

    # 카메라 준비까지 대기 후 CH1 ON (카메라 트리거)
    print("SDG2082x 제어 시작: 카메라 준비 대기 중...")
    while not camera_ready:
        time.sleep(0.01)
    print("카메라 준비 신호 수신. ARM 안정화 0.5 s 대기...")
    time.sleep(1.5)  # ARM 직후 안정화 대기
    print("SDG2082x 펄스 출력 시작 (CH1→Camera)")
    sdg.write("C1:OUTP ON")  # 카메라용 트리거 시작

    # 컨슈머가 연속 프레임 안정 진입을 알리면 CH2를 켜 SynthHD 스텝 시작
    def enable_ch2_once():
        if not synth_start_event.wait(timeout=60):  # 60s 내 안정 진입 신호 없으면 건너뜀
            return
        try:
            print("STABLE 신호 수신: CH2(SynthHD) 트리거 시작")
            sdg.write("C2:OUTP ON")
        except Exception as e:
            print("CH2 출력 ON 실패:", e)

    ch2_once = threading.Thread(target=enable_ch2_once, daemon=True)
    ch2_once.start()

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
    try:
        sdg.write("C2:OUTP OFF")
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
            # 하드웨어 트리거: Falling edge(HIGH→LOW)로 명시 (SDK Enum 사용)
            try:
                camera.operation_mode = OPERATION_MODE.HARDWARE_TRIGGERED
                camera.frames_per_trigger_zero_for_unlimited = 1
                camera.trigger_polarity = TRIGGER_POLARITY.ACTIVE_LOW  # 시험: Falling edge (HIGH→LOW)
                print("카메라 트리거 극성: ACTIVE_LOW(Falling)로 설정")
            except Exception as e:
                print(f"트리거 모드/극성 설정 실패: {e}")

            camera.exposure_time_us = 1500  # 1.5 ms 노출 (단위: 마이크로초)
            camera.frames_per_trigger_zero_for_unlimited = 1
            camera.image_poll_timeout_ms = 1000
            # 하드웨어 트리거 사용 시 내부 프레임레이트 제어는 비활성화
            camera.is_frame_rate_control_enabled = False

            # 하드웨어 트리거 수신을 위해 충분한 내부 버퍼 확보 (드롭 방지)
            camera.arm(200)
            print("카메라 ARM 완료 (하드웨어 트리거 대기 상태)")
            camera_ready = True  # 카메라 준비 신호 즉시 전달

            last_report = time.time()
            last_frames_local = 0

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
                        # 타임스탬프를 소비자에 전달하기 위해 frame.frame_count와 timestamp를 함께 전달
                        ts_rel_ns = getattr(frame, "time_stamp_relative_ns_or_null", None)
                        frame_queue.put(((frame.frame_count, ts_rel_ns), roi))
                        with capture_lock:
                            frames_captured += 1
                        last_frames_local = frames_captured
                        last_report = time.time()
                        # 디버깅: 매 1000프레임마다 진행상황 출력
                        if frames_captured % 1000 == 0:
                            print(f"DEBUG: 현재까지 {frames_captured} 프레임 수집됨")
                    # 외부 트리거 대기 상태 감시: 일정 시간 프레임이 없으면 안내 로그
                    if time.time() - last_report > 2.0 and frames_captured == last_frames_local:
                        print("WAIT: 아직 수신 프레임 없음 (외부 트리거 대기 중). 트리거 케이블/극성/레벨을 확인하세요.")
                        last_report = time.time()
                    # 프레임 번호 및 현재까지 수집된 프레임 정보 출력
                    # 삭제됨: print(f"프레임 #{frame.frame_count} 저장 (총 {frames_captured}/{n_frames})")
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
    # 안정 진입 판정 파라미터 (250 Hz 기준)
    PREROLL_SEC = 1.0
    STABLE_N = 25
    STABLE_T = 0.004     # 4 ms
    STABLE_TOL = 0.0006  # ±0.6 ms 허용
    stable_mode = False
    stable_count = 0
    last_ts = None
    first_data_ts = None

    # 주파수별 intensity 누적 (평균/라이브 플롯용)
    intensity_dict = defaultdict(list)
    processed_frames = 0

    if PRINT_PER_FRAME:
        print("Consumer 시작: 프레임-주파수 매핑 및 워밍업 스킵 동작 준비")

    # 초기 워밍업 프레임: 정확한 주파수-프레임 정렬을 위해 한 사이클(= mw_steps) 건너뜀
    warmup_skip = mw_steps
    target_frames = n_frames - warmup_skip

    # HDF5 지연 초기화 (첫 유효 ROI 크기 파악 후 생성)
    h5 = None
    d_roi = d_frame = d_freq = None
    h5_index = 0

    # 카메라 프레임카운트에 의존하지 않도록 로컬 카운터 사용
    seen = 0

    while processed_frames < target_frames:
        try:
            meta, roi = frame_queue.get(timeout=0.5)
            # 종료 신호 처리
            if meta is None:
                break
            frame_num, ts_rel_ns = meta

            # 프레임 타임스탬프 확보 (ns 단위가 제공되면 우선 사용)
            if ts_rel_ns is not None:
                ts_now = ts_rel_ns * 1e-9  # ns → s
            else:
                ts_now = time.time()
            if first_data_ts is None:
                first_data_ts = ts_now

            # PREROLL: 카메라 ARM/CH1 시작 후 초기 구간 무시
            if (ts_now - first_data_ts) < PREROLL_SEC and not stable_mode:
                if PRINT_PER_FRAME and (processed_frames % 50 == 0):
                    print(f"PREROLL 진행 중: {(ts_now - first_data_ts):.2f}s")
                continue

            # 안정성 판정: 직전 프레임과의 간격이 목표 주기(4 ms)±tol인지 검사
            if last_ts is None:
                last_ts = ts_now
                continue
            dt = ts_now - last_ts
            last_ts = ts_now
            if abs(dt - STABLE_T) <= STABLE_TOL:
                stable_count += 1
            else:
                stable_count = 0

            if not stable_mode:
                if stable_count >= STABLE_N:
                    stable_mode = True
                    print(f"STABLE 진입: Δt≈{STABLE_T*1000:.1f} ms 범위 내 연속 {STABLE_N} 프레임 확인 → 본측정 시작")
                    # 안정 진입 시점에 SynthHD(CH2) 시작 신호 전송
                    try:
                        synth_start_event.set()
                    except Exception:
                        pass
                    # 카운터/버퍼 초기화: 안정 이전 데이터는 버리고 새로 시작
                    intensity_dict = defaultdict(list)
                    processed_frames = 0
                    seen = 0
                    # HDF5도 안정 이후부터 생성하도록 초기화 리셋
                    h5 = None
                    d_roi = d_frame = d_freq = None
                    h5_index = 0
                else:
                    if PRINT_PER_FRAME and (processed_frames % 50 == 0):
                        print(f"STABILIZING... ({stable_count}/{STABLE_N})")
                    continue

            seen += 1  # stable_mode 진입 후에만 카운트

            # MW 주파수 계산 (로컬 카운터 기반)
            step_index = (seen - warmup_skip - 1) % mw_steps
            freq = mw_start + step_index * mw_step  # Hz

            if PRINT_PER_FRAME:
                print(f"#{int(frame_num)} freq={freq/1e9:.3f} GHz (step {step_index+1}/{mw_steps})")

            # HDF5 초기화
            if SAVE_HDF5 and HAS_H5PY and h5 is None:
                try:
                    h5_path = os.path.join(run_dir, "data.h5")
                    h5 = h5py.File(h5_path, "w")
                    h, w = roi.shape
                    d_roi = h5.create_dataset(
                        "roi",
                        shape=(0, h, w),
                        maxshape=(None, h, w),
                        dtype=np.uint16,
                        chunks=(1, h, w),
                        compression="gzip",
                    )
                    d_frame = h5.create_dataset(
                        "frame_num",
                        shape=(0,),
                        maxshape=(None,),
                        dtype=np.int64,
                        chunks=True,
                        compression="gzip",
                    )
                    d_freq = h5.create_dataset(
                        "freq_hz",
                        shape=(0,),
                        maxshape=(None,),
                        dtype=np.float64,
                        chunks=True,
                        compression="gzip",
                    )
                except Exception as e:
                    print(f"HDF5 초기화 실패: {e}")

            # ROI 저장 (HDF5 우선, 실패 시 옵션에 따라 .txt)
            if SAVE_HDF5 and HAS_H5PY and h5 is not None:
                try:
                    d_roi.resize((h5_index + 1, d_roi.shape[1], d_roi.shape[2]))
                    d_roi[h5_index, :, :] = roi.astype(np.uint16)
                    d_frame.resize((h5_index + 1,))
                    d_frame[h5_index] = int(frame_num)
                    d_freq.resize((h5_index + 1,))
                    d_freq[h5_index] = float(freq)
                    h5_index += 1
                except Exception as e:
                    print(f"HDF5 저장 실패 (frame {frame_num}): {e}")
            elif SAVE_TXT:
                try:
                    freq_mhz = int(round(freq / 1e6))
                    filename = f"roi_frame_{int(frame_num):06d}_f{freq_mhz:04d}MHz.txt"
                    filepath = os.path.join(freq_paths[step_index], filename)
                    np.savetxt(filepath, roi.astype(np.uint16), fmt='%d')
                except Exception as e:
                    print(f"ROI 저장 실패 (frame {frame_num}): {e}")

            # 총 intensity 합 (오버플로 방지)
            s = roi.astype(np.uint32).sum()
            intensity_dict[freq].append(int(s))
            processed_frames += 1

            # 스윕 1회 완료 시 메인스레드 플로터로 데이터 전달
            if LIVE_ODMR and ((seen - warmup_skip) % mw_steps == 0):
                try:
                    freqs_sorted = sorted(intensity_dict.keys())
                    y = np.array([np.mean(intensity_dict[f]) for f in freqs_sorted])
                    x = np.array([f / 1e9 for f in freqs_sorted])
                    pl_norm = y / y.max()
                    I_off = y[y >= np.quantile(y, 0.80)].mean()
                    contrast_pct = (I_off - y) / I_off * 100.0
                    # 최신 데이터만 유지 (큐가 가득 차면 가장 오래된 항목 버림)
                    while not plot_queue.empty():
                        try:
                            plot_queue.get_nowait()
                        except Exception:
                            break
                    plot_queue.put_nowait((x, pl_norm, contrast_pct))
                except Exception:
                    pass

        except queue.Empty:
            continue

    measurement_complete = True

    # HDF5 정리
    try:
        if SAVE_HDF5 and HAS_H5PY and h5 is not None:
            h5.close()
    except Exception:
        pass

def plotter_mainloop():
    if not LIVE_ODMR:
        return
    fig = None
    ax_pl = ax_con = line_pl = line_con = None
    import matplotlib
    try:
        # GUI 백엔드 사용 (Windows에서 TkAgg 기본). 모든 plt 호출은 메인 스레드에서만.
        matplotlib.rcParams["toolbar"] = "toolmanager"
    except Exception:
        pass
    try:
        plt.ion()
    except Exception:
        pass
    last_update = time.time()
    while True:
        try:
            x, pl_norm, contrast_pct = plot_queue.get(timeout=0.2)
            if fig is None:
                fig, (ax_pl, ax_con) = plt.subplots(2, 1, sharex=True)
                line_pl, = ax_pl.plot(x, pl_norm, marker='o')
                line_con, = ax_con.plot(x, contrast_pct, marker='o')
                ax_pl.set_ylabel("PL (norm.)")
                ax_con.set_ylabel("Contrast (%)")
                ax_con.set_xlabel("Frequency (GHz)")
                ax_pl.set_title("Live CW-ODMR")
            else:
                line_pl.set_xdata(x); line_pl.set_ydata(pl_norm)
                line_con.set_xdata(x); line_con.set_ydata(contrast_pct)
                ax_pl.relim(); ax_pl.autoscale_view()
                ax_con.relim(); ax_con.autoscale_view()
            plt.pause(0.001)
            last_update = time.time()
        except queue.Empty:
            # 종료 조건: 측정 완료 이후 일정 시간동안 업데이트 없으면 종료
            if measurement_complete and (time.time() - last_update) > 0.5:
                break
            continue
    try:
        plt.ioff()
        plt.show(block=False)
        plt.pause(0.001)
    except Exception:
        pass
    try:
        plt.close('all')
    except Exception:
        pass

# -----------------------------------------
# 쓰레드 시작 및 데이터 수집 완료
# -----------------------------------------
sdg_thread = threading.Thread(target=sdg_control, daemon=True)
producer_thread = threading.Thread(target=camera_producer, daemon=True)
consumer_thread = threading.Thread(target=camera_consumer, daemon=True)

sdg_thread.start()
producer_thread.start()
consumer_thread.start()

# 라이브 플롯은 메인 스레드에서만 처리 (Tkinter 예외 방지)
plotter_mainloop()

producer_thread.join()
consumer_thread.join()
sdg_thread.join()

# 디버깅: intensity_dict에 저장된 데이터 개수 확인
for freq in sorted(intensity_dict.keys()):
    print(f"DEBUG: 주파수 {freq/1e9:.3f} GHz에 측정된 데이터 개수: {len(intensity_dict[freq])}")

# 각 MW 주파수별 평균 intensity 계산 (각 주파수 당 1000회 측정이 목표)
frequencies = sorted(intensity_dict.keys())
avg_intensities = [np.mean(intensity_dict[freq]) for freq in frequencies]
