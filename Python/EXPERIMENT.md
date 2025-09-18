# ODMR
Python code for ODMR experiment. 

## 1. CW ODMR

### 1.1 Aparatus
- CMOS camera : CS165CU1/M - Zelux 1.6MP Color CMOS camera
- Dual-channel funciton/arbitrary waveform generators : Siglent SDG2082x
- Single-color cold visible mounted LED : Thorlabs M565L3
- Object : Olympus UPlanFL N Objective (x5 ~ x 60)
- Long pass dichroic mirror : Thorlabs DMLP505
- Dual channel microwave RF signal generator - Windfreak SynthHD
- And several convex lens with various focal length.

### 1.2 Method: Continuous-Wave ODMR

We want to obtain ODMR data of spin defect in hBN by using wide field imaging set-up. The experimental scheme follows the steps below:

1. Turn on the LED continously to hBN.
2. Give microwave source to hBN. Since we have to observe the ODMR contrast signal for each frequency of MW, we should sweep the MW frequency from 3GHz to 4GHz with step of 50MHz.

#### Triggering & Timing
To synchronize all sequence of equipment we adopt following triggering sequence.

1. CH.1 of SDG2082x makes pulse signal with width 200μs and frequency 50Hz. CH.2 of SDG2082x makes flipped pulse signal(high 3.0V and make low pulse each period) with same width and frequency of CH.1 (200us and 50Hz) 
2. Because of triggering pulse signal, SynthHD is set to single sweep step mode and moves one frequency step per trigger from 3GHz to 4GHz by 50MHz each time. The exposure time of camera is set to 1.5ms and the trigger arrives every 20ms, leaving approximately 18.5ms for readout.
3. Therefore each frame obtained from camera represents the data of each frequency. The data is saved as hdf5 file. The code makes index matching of frequency and frame number.
4. Then make 2D array whose x axis represents horizontal pixel number of camera in ROI and y axis represents vertical pixel number of camre in ROI.

### 1.3 Code Control
To realize above method, the synchronization of all experimental equipments is controlled by Python code. 

- SDG2082x : Use pyvisa package to controll signal on/off, pulse width, pulse frequency, amplitude, and offset.
- CS165CU1/M Use python SDK from Thorlabs(thorlabs_tsi_sdk). The official document is in '/Users/woojins/Documents/GitHub/ODMR/Thorlabs_Camera_Python_API_Reference.pdf' and the official examples are in [Thorlabs Github](https://github.com/Thorlabs/Camera_Examples.git). Everytime to revise code, please check both official document and examples in Github precisely.
- Other parts also use python and conventional packages such as matplotlib, numpy, scipy and so on.
- **Data handling**: Use `h5py` to stream ROIs and metadata into `data.h5` (chunked, compressed). This is the default (`SAVE_HDF5=True`, `SAVE_TXT=False`).
