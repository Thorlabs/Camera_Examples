## Included Examples

### Grab Single Frame: 
This examples initializes the first detected camera and sets up for software triggering. A single frame is requested and the recieved image is displayed with OpenCV. 

### Grab Frames Polling Continuous: 
This examples initializes the first detected camera and sets up for continuous capture with software triggering and framerate control. The recieved images are displayed with OpenCV

### OpenCV MP4 Writer:
This example saves images from a Thorlabs camera as an MP4 video file.

## Build Instructions
1. If you have not done so already unzip the following folder to an accesible location on your drive. This contains the Camera SDK. 

   * 32-Bit - C:\Program Files (x86)\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces.zip
   * 64-Bit - C:\Program Files\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces.zip

2. The Python SDK is provided both as an installable package and as source files. To install the Python SDK in your environment, use a package manager such as pip to install from the package file. The zip folder will be found within the location in step 1: \Scientific Camera Interfaces\SDK\Python Toolkit

Example install command: 

```
python.exe -m pip install thorlabs_tsi_camera_python_sdk_package.zip
```

 This will install the thorlabs_tsi_sdk package into your current environment. The examples assume you are using this method. 
 If you want to use the source files directly, they are included in SDK\Python Camera Toolkit\source.

3. To use the examples on a Windows OS, copy the Native DLLs from 
     * 64-Bit - \Scientific Camera Interfaces\SDK\Native Toolkit\dlls\Native_64_lib
     * 32-Bit - \Scientific Camera Interfaces\SDK\Native Toolkit\dlls\Native_32_lib

   To a folder in your script location named __\dlls\64_lib__ for 64-bit machines and __\dlls\32_lib__ for 32-bit. This can be modified in the windows_setup.py script if you wish to change the location. 

4. Additional examples and a requirements.txt file is provided with ThorCam that lists the libraries needed to run the examples (besides the thorlabs_tsi_sdk package). This is dound in \Scientific Camera Interfaces\SDK\Python Toolkit\examples and can be used with pip to install each dependency at once:

```
   pip install -r requirements.txt  
```
