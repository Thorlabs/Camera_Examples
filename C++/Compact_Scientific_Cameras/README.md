## Included Examples

### Hardware Triggering: 
This examples initializes the first detected camera and sets up for hardware triggering. A loop is started that waits for 5 images to be requested and received. 

### Read Parameters: 
This example goes through common settable/gettable parameters for the cameras and prints them to console. This also shows how to interpret returns from cameras that are not compatible with certain settings. 

## Build Instructions

0. If you have not done so already unzip the following folder to an accesible location on your drive. This contains the Camera SDK. 

  * 32-Bit - C:\Program Files (x86)\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces.zip
  * 64-Bit - C:\Program Files\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces.zip
This example will use the dll's here: \Scientific Camera Interfaces\SDK\Native Toolkit\dlls

1. Select the desired project from the Visial Studio Solution by right clicking and selecting "Set as Startup Project"
2. Change the Solution platform to match the bit version of the dll's.
3. From the Project Properties under the C/C++ section, add the following locations as Additional Include Directories:
  * C:\Program Files\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces\SDK\Native Toolkit\include
  * C:\Program Files\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces\SDK\Native Toolkit\load_dll_helpers
4. Right Click on the desired project from the Solution Explorer and select Add -> Existing Item
and add the c source files from C:\Program Files\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces\SDK\Native Toolkit\load_dll_helpers
This is done already in the solution, but it is recommended to check and redo in case you are using a different location for your dll's and helpers
5. Copy the dll's from \Scientific Camera Support\Scientific Camera Interfaces\SDK\Native Toolkit\dlls\Native_64_lib to the bin of the project:\Compact_Scientific_Cameras\x64\Debug\
NOTE: All Projects in the solution will share an output directory


