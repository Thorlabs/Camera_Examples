# ODMR
Python code for ODMR experiment. 

## 1. CW ODMR

### 1.1 Aparatus
- CMOS camera : CS165CU1/M - Zelux 1.6MP Color CMOS camera
- Dual-channel funciton/arbitrary waveform generators : Siglent SDG2082x
- Single-color cold visible mounted LED : Thorlabs M565L3
- Object : Mitutoyo M plan apo nir 50x
- Long pass dichroic mirror : Thorlabs DMLP505
- Dual channel microwave RF signal generator - Windfreak SynthHD
- And several convex lens with various focal length.

### 1.2 Method: Continuous-Wave ODMR

We want to obtain ODMR data of spin defect in hBN by using wide field imaging set-up. The experimental scheme follows the steps below:

1. Turn on the LED continously to hBN.
2. Give microwave source to hBN. Since we have to observe the ODMR contrast signal for each frequency of MW, we should sweep the MW frequency from 3GHz to 4GHz with step of 10MHz.

#### Triggering & Timing
To synchronize all sequence of equipment we adopt following triggering sequence.

1. CH.1 of SDG2082x makes pulse signal with width 20μs and frequency 250Hz. By using BNC tee to CH.1, this pulse signal triggers both CMOS camera and SynthHD.
2. Because of triggering pulse signal, SynthHD is set to single sweep step mode and moves one frequency step per trigger from 3GHz to 4GHz by 50MHz each time. The exposure time of camera is set to 1.5ms and the trigger arrives every 4ms, leaving approximately 2.5ms for readout.
3. Therefore each frame obtained from camera represents the data of each frequency. To make the mapping robust in practice, we (i) use a **local frame counter** (not the camera’s internal counter) and (ii) **skip the first one full sweep** (`warmup_skip = mw_steps`) so that the start-step boundary of SynthHD aligns with the frame sequence. After that, the frequency for frame *k* is computed by `step_index = (seen - warmup_skip - 1) % mw_steps` and `freq = mw_start + step_index * mw_step`.
4. Then make 2D array whose x axis represents horizontal pixel number of camera in ROI and y axis represents vertical pixel number of camre in ROI.

#### Data Structure
Data are saved by default to a single **HDF5** file (`data.h5` in the run directory) to avoid I/O bottlenecks and file explosion. Datasets:
- `roi` : shape = (N, H, W), dtype = uint16, each entry is the ROI image for one frame (chunked + gzip)
- `frame_num` : shape = (N,), dtype = int64, the camera-reported frame index for reference
- `freq_hz` : shape = (N,), dtype = float64, the MW frequency matched to each frame  
*(Optional)* If `SAVE_TXT=True`, per-frame ROI can also be written as `.txt` under frequency-specific folders, but this is not recommended for large runs.

#### Quick QC
With `LIVE_ODMR=True`, the code updates a **quick ODMR plot once per sweep**: it aggregates the ROI intensity for each frequency during the sweep and plots the **mean over repeats** vs. frequency.
This is intended for immediate sanity checks (contrast, line position, drift), not final analysis.

### 1.3 Code Control
To realize above method, the synchronization of all experimental equipments is controlled by Python code. 

- SDG2082x : Use pyvisa package to controll signal on/off, pulse width, pulse frequency, amplitude, and offset.
- CS165CU1/M Use python SDK from Thorlabs(thorlabs_tsi_sdk). The official document is in '/Users/woojins/Documents/GitHub/ODMR/Thorlabs_Camera_Python_API_Reference.pdf' and the official examples are in [Thorlabs Github](https://github.com/Thorlabs/Camera_Examples.git). Everytime to revise code, please check both official document and examples in Github precisely.
- Other parts also use python and conventional packages such as matplotlib, numpy, scipy and so on.
- **Data handling**: Use `h5py` to stream ROIs and metadata into `data.h5` (chunked, compressed). This is the default (`SAVE_HDF5=True`, `SAVE_TXT=False`).
- **Runtime flags (top of code)**:
  ```
  PRINT_PER_FRAME = True     # log once per frame: "#<frame> freq=<GHz>"
  SAVE_TXT = False           # legacy text dumps (not recommended for large runs)
  SAVE_HDF5 = True           # default: single data.h5 with roi/frame_num/freq_hz
  LIVE_ODMR = True           # quick preview plot at the end of each sweep
  ```
- **Frame–frequency alignment**: We use a **local frame counter** and skip the first full sweep (`warmup_skip = mw_steps`) to align SynthHD’s step boundary. Frequency per frame is computed by `step_index = (seen - warmup_skip - 1) % mw_steps`.
- **Buffers & throughput**: Camera is armed with `arm(200)` to avoid frame drops under 250 Hz triggering; the inter-thread `frame_queue` has `maxsize=512`.
- **Logging**: Exactly **one line per frame** in the format `#<frame_num> freq=<GHz>`. Extra producer logs removed to prevent clutter.
- **ROI intensity definition**: The default y-value recorded for each frame is the **spatial sum** over the ROI. (This is robust and fast; if needed, it can be changed to a per-pixel mean by replacing the accumulation line with `roi.mean()`.)
- **Overflow safety**: ROI sums are accumulated as `uint32` to prevent overflow (`roi.astype(np.uint32).sum()`).
