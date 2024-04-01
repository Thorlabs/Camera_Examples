## Using the Examples
 1. If you have not done so already unzip the following folder to an accesible location on your drive. This contains the Camera SDK.

    * 32-Bit - C:\Program Files (x86)\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces.zip
    * 64-Bit - C:\Program Files\Thorlabs\Scientific Imaging\Scientific Camera Support\Scientific Camera Interfaces.zip 
    
    This example will use the dll's here: \Scientific Camera Interfaces\SDK\DotNet Toolkit\dlls\

2. Copy the dll's to the location of the matlab example you wish to run. The examples in this folder use the current working directory as the location from which to load the dll's. If you need to use a different directory, change the lines of the program that add the .NET assemblies: 

```
NET.addAssembly([PATH_TO_DLLs, NAME_OF_DLL_TO_LOAD]);
```

## Included Examples

### Color Processing: 
This example demonstrates how to retreive the raw data from the camera and convert it to an RGB image. 

### Hardware Triggering: 
This example demonstrates how to set up a camera for hardware triggering.

### Polarization Processing:
This example demonstrates how to retreive the raw data from a polarization camera like the CS505MUP1 and convert it to one of the polarization image types. 

### Software Trigger:
This example demonstrates how to set up a camera for software triggering.

### Thorlabs Camera GUI:
This example uses the MATLAB App Designer to create a simple GUI to control the camera. This implements features like device enumeration, color processing, hardware triggering, etc..