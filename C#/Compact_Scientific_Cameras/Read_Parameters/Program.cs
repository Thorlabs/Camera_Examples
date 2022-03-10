using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;
using Thorlabs.TSI.TLCamera;
using Thorlabs.TSI.TLCameraInterfaces;
using Thorlabs.TSI.ImageData;
using Thorlabs.TSI.ImageDataInterfaces;

namespace Read_Parameters
{
    class Program
    {
        static void Main(string[] args)
        {
            ITLCameraSDK sdk = TLCameraSDK.OpenTLCameraSDK(); //Create Instance of the TL Camera SDK 

            //Use SDK to Discover and Open cameras
            IList<string> serialNumbers = sdk.DiscoverAvailableCameras();
            if (serialNumbers.Count == 0)
            {
                Console.WriteLine("No Cameras Available");
                return;
            }
            Console.WriteLine("Number of Cameras found: {0}", serialNumbers.Count);
            Console.WriteLine("Serial Number of first camera: ", serialNumbers[0]);

            ITLCamera cam = sdk.OpenCamera(serialNumbers[0], false);
            Console.WriteLine("Camera Opened");

            //Get Camera Info
            Console.WriteLine("Model Number: {0}, Name: {1}, Firmware Version: {2}, Serial Number: {3}", cam.Model, cam.Name, cam.FirmwareVersion, cam.SerialNumber);

            //Get Camera Sensor Type
            Console.WriteLine("Sebsor Type: {0}", cam.CameraSensorType.ToString());

            //Gets the camera sensor dimensions in pixels
            Console.WriteLine("Sensor Size: {0}px x {1}px", cam.SensorWidth_pixels, cam.SensorHeight_pixels);

            //Get Camera Bit Depth
            Console.WriteLine("Bit Depth: {0}", cam.BitDepth);

            //Get Exposure Time Range
            Console.WriteLine("Exposure Time Range: {0} to {1}", cam.ExposureTimeRange_us.Minimum, cam.ExposureTimeRange_us.Maximum); //In microseconds

            //Set and Get Exposure Time
            cam.ExposureTime_us = 45000; //In microseconds
            Console.WriteLine("Exposure Time: {0}", cam.ExposureTime_us);

            //Get Exposure Frames Per Trigger Range
            Console.WriteLine("Frames Per Trigger Range: {0} to {1}", cam.FramesPerTriggerRange.Minimum, cam.FramesPerTriggerRange.Maximum);

            //Set and Get Frames Per Trigger
            cam.FramesPerTrigger_zeroForUnlimited = 1;
            Console.WriteLine("Frames Per Trigger: {0}", cam.FramesPerTrigger_zeroForUnlimited);

            //Check if camera supports adjusting framerate and check range
            if (cam.FrameRateControlValueRange_fps.Maximum != 0)
            {
                Console.WriteLine("Camera supports framerate adjustment with range of: {0} to {1}", cam.FrameRateControlValueRange_fps.Minimum, cam.FrameRateControlValueRange_fps.Maximum);

                //Set and Get Framerate
                cam.FrameRateControlValue_fps = 5; // in fps
                Console.WriteLine("Framerate Value: {0}", cam.FrameRateControlValue_fps);
            }

            //Check if camera supports adjusting gain and check range
            if (cam.GainRange.Maximum != 0)
            {
                Console.WriteLine("Camera supports gain adjustment with range of: {0} to {1}", cam.GainRange.Minimum, cam.GainRange.Maximum);

                //Set and Get Gain
                //Gain units can vary by camera. Use the helper function to set these for the camera
                cam.Gain = cam.ConvertDecibelsToGain(.5); // in dB
                Console.WriteLine("Gain Value: {0}", cam.ConvertGainToDecibels(cam.Gain)); 
            }

            //Check if camera supports adjusting black level and check range
            if (cam.BlackLevelRange.Maximum != 0)
            {
                Console.WriteLine("Camera supports black level adjustment with range of: {0} to {1}", cam.BlackLevelRange.Minimum, cam.BlackLevelRange.Maximum);

                //Set and Get Black Level 
                cam.BlackLevel = 5; // in fps
                Console.WriteLine("Black Level Value: {0}", cam.BlackLevel);
            }

            //Set ROI and Bin Values
            cam.ROIAndBin = new ROIAndBin()
            {
                BinX = 1, 
                BinY = 1, 
                ROIOriginX_pixels = 0, 
                ROIOriginY_pixels = 0, 
                ROIWidth_pixels = cam.SensorWidth_pixels, 
                ROIHeight_pixels = cam.SensorHeight_pixels
            };

            //Get ROI and Bin Values
            Console.WriteLine("Bin X Value: {0} \nBin Y Value: {1} \nROI X Value: {2} \nROI Y Value: {3} \nROI Width {4} \nROI Height {5}", cam.ROIAndBin.BinX,
                cam.ROIAndBin.BinY, cam.ROIAndBin.ROIOriginX_pixels, cam.ROIAndBin.ROIOriginY_pixels, cam.ROIAndBin.ROIWidth_pixels, cam.ROIAndBin.ROIHeight_pixels);

        }
    }
}
