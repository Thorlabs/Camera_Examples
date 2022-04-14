## Included Examples

### Hardware Triggering: 
This examples initializes the first detected camera and sets up for hardware triggering. A loop is started that waits for 5 images to be requested and received. Each image will be saved to the exe location for the project. 

### Read Parameters: 
This example goes through all settable/gettable parameters for the cameras and prints them to console. This also shows how to interpret returns from cameras that are not compatible with certain settings. 

## Build Instructions

1. If you have not done so already unzip the following folder to an accesible location on your drive. This contains the Camera SDK. 

  * 32-Bit - C:\Program Files (x86)\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces.zip
  * 64-Bit - C:\Program Files\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces.zip
This example will use the dll's here: \Scientific Camera Interfaces\SDK\DotNet Toolkit\dlls\

2. Set Project Platform under Project -> Properties -> Build. This should be selected to match the bit-version of the dll's you plan to use (e.g. x64 for 64-bit dll's). 

3. Add References to:
  * Thorlabs.TSI.Core
  * Thorlabs.TSI.Core Interfaces
  * Thorlabs.TSI.ImageData
  * Thorlabs.TSI.ImageDataInterfaces
  * Thorlabs.TSI.TLCamera
  * Thorlabs.TSI.TLCameraInterfaces
  * thorlabs_tsi_camera_sdk1_cli
  * System.Drawing

4. Copy the dll's from the managed folder to the bin of this project: 
\Camera_Examples\C#\Compact_Scientific_Cameras\Hardware_Triggering\bin\Debug\

5. Before running, set the desired startup file. 


