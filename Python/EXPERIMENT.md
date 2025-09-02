# ODMR
Python code for ODMR experiment. 

## 1. CW ODMR
### 1. Aparatus
- CMOS camera : CS165CU1/M - Zelux 1.6MP Color CMOS camera
- Dual-channel funciton/arbitrary waveform generators : Siglent SDG2082x
- Single-color cold visible mounted LED : Thorlabs M565L3
- Object : Mitutoyo M plan apo nir 50x
- Long pass dichroic mirror : Thorlabs DMLP505
- Dual channel microwave RF signal generator - Windfreak SynthHD
- And several convex lens with various focal length.

### 2. Method
We want to obtain ODMR data of spin defect in hBN by using wide field imaging set-up. To do this the experimental scheme should follows the steps below.

1. Turn on the LED continously to hBN.
2. Give microwave source to hBN. Since we have to observe the ODMR contrast signal for each frequency of MW, we should sweep the MW frequency from 3GHz to 4GHz with step of 10MHz. To synchronize all sequence of equipment we adopt following triggering sequence.
    1. CH.1 of SDG2082x makes pulse signal with width 2μs and frequency 25Hz. By using BNC tee to CH.1, this pulse signal triggers both CMOS camera and SynthHD.
    2. Because of triggering pulse signal, SynthHD sweep frequency from 3GHz to 4GHz by 50MHz each time for 40ms. The exposure time of camera is set to 20ms to enable stable readout time(about residue 20ms). 
    3. Therefore each frame obtained from camera represents the data of each frequency. So we should match the index of frame number and the sweep step to know what frequency is matched for this frame.
    4. Then make 2D array whose x axis represents horizontal pixel number of camera in ROI and y axis represents vertical pixel number of camre in ROI.
    5. This 2D array is saved for .txt file in same directory of code. This .txt file will be used for data processing for ODMR.

### 3. Code sequence.
To realize above method, the synchronization of all experimental equipments is controlled by Python code. 
- SDG2082x : Use pyvisa package to controll signal on/off, pulse width, pulse frequency, amplitude, and offset.
- CS165CU1/M Use python SDK from Thorlabs(thorlabs_tsi_sdk). The official document is in '/Users/woojins/Documents/GitHub/ODMR/Thorlabs_Camera_Python_API_Reference.pdf' and the official examples are in [Thorlabs Github](https://github.com/Thorlabs/Camera_Examples.git). Everytime to revise code, please check both official document and examples in Github precisely.
- Other parts also use python and conventional packages such as matplotlib, numpy, scipy and so on.
