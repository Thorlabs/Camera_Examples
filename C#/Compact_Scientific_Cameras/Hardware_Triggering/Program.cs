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

namespace Hardware_Triggering
{
    class Program
    {
        static void Main(string[] args)
        {    
            ITLCameraSDK sdk = TLCameraSDK.OpenTLCameraSDK(); //Create Instance of the TL Camera SDK 

            //Use SDK to Discover and Open cameras
            IList<string> serialNumbers = sdk.DiscoverAvailableCameras();
            Console.WriteLine("Number of available cameras: {0}", serialNumbers.Count);
            if (serialNumbers.Count == 0)
            {
                Console.WriteLine("No Cameras Available");
                return;
            }
            ITLCamera cam = sdk.OpenCamera(serialNumbers[0], false); //Open first detected serial number

            //Set Camera parameters
            cam.ExposureTime_us = 100; // in microseconds
            cam.FramesPerTrigger_zeroForUnlimited = 1; 

            //Check if hardware triggering is supported by the camera. If not, close the program
            if (cam.GetIsOperationModeSupported(OperationMode.HardwareTriggered))
            {
                cam.OperationMode = OperationMode.HardwareTriggered;
                Console.WriteLine("Camera supports hardware triggering");
            }
            else
            {
                Console.WriteLine("Camera does not support hardware triggering");
                return;
            }
            cam.Arm(); //Arm the camera

            //While loop waits for images to come in from the camera. Once it receives 5 images, the loop exits
            Console.WriteLine("Waiting for image");
            int numImagesAcquired = 0;
            while (numImagesAcquired < 5)
            {
                if (cam.NumberOfQueuedFrames > 0)
                {
                    Frame frame = cam.GetPendingFrameOrNull(); // Get the latest image
                    if (frame != null)
                    {
                        Bitmap image = frame.ImageData.ToBitmap_Format24bppRgb(); //Convert the returned frame to a bitmap
                        image.Save("Received_Image" + (numImagesAcquired + 1) + ".bmp"); // Saves to exe location
                        Console.WriteLine("Image Received from the camera");
                        numImagesAcquired++;
                    }
                }
                System.Threading.Thread.Sleep(50);
            }

            //Close camera and clean up resources
            Console.WriteLine("Camera closing");
            cam.Disarm();
            cam.Dispose();
            sdk.Dispose();
        }
    }
}
