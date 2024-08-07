## Included Examples

### PythonNET Software Trigger and Acquire: 
This examples initializes the first detected camera and sets up for software triggering. A loop is started that waits the image to be received. This example should only be used if you have an obsolete CCD camera. For all other Thorlabs cameras (Zelux, Kiralux, Quantalux), the python SDK in the ThorCam installation can be used. 


## Build Instructions
NOTE: This uses the pythonNET and numpy packages and requires that these be installed. The file tl_dotnet_wrapper.py is a wrapper for the .NET dll's located in the ThorCam install. This was last tested with PythonNET version 3.0.1 and Python version 3.10.4

0. If you have not done so already unzip the following folder to an accesible location on your drive. This contains the Camera SDK. 

   * 32-Bit - C:\Program Files (x86)\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces.zip
   * 64-Bit - C:\Program Files\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces.zip
This example will use the dll's here: \Scientific Camera Interfaces\SDK\Native Toolkit\dlls

1. Copy the dll's from \Scientific Camera Interfaces\SDK\DotNet Toolkit\dlls\Managed_64_lib folder into the location where the wrapper and example are located. 
2. Open the folder containing the files in your preferred IDE. PyCharm and Visual Studio Code have been verified. 




