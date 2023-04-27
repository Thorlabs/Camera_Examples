using System;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;

namespace DCx_Camera_Live_capture
{
    public class Program
    {
        private uc480.Camera Camera;
        public bool bLive = false;
        private object bmpLock;
        static void Main(string[] args)
        {
            // Declare variables and create camera device.
            var Pc = new Program();
            var Camera = new uc480.Camera();
            uc480.Defines.Status statusRet = 0;

            // Open Camera
            Console.WriteLine("Initializing Camera....");
            statusRet = Camera.Init();

            if (statusRet != uc480.Defines.Status.SUCCESS)
            {
                Console.WriteLine("Camera initializing failed");
            }

            Console.WriteLine("Allocating Memory....");
          
            // Allocate Memory.
            Int32 s32MemID;
            statusRet = Camera.Memory.Allocate(out s32MemID, true);
            if (statusRet != uc480.Defines.Status.SUCCESS)
            {
                Console.WriteLine("Allocate Memory failed");
            }

            statusRet = Camera.Memory.GetActive(out s32MemID);
            statusRet = Camera.Trigger.Set(uc480.Defines.TriggerMode.Software);

            // Press Enter to take Image.
            Console.WriteLine("Press Enter to Take Image");

            while (Console.ReadKey().Key != ConsoleKey.Enter) 
            {
                System.Threading.Thread.Sleep(1000);
                // Check to see if image is available. 
                // Forms for live capture. 
            }
            
            statusRet = Camera.Acquisition.Freeze(6000);
            if (statusRet != uc480.Defines.Status.SUCCESS)
            {
                Console.WriteLine("Image capture failed");
            }
            else
            {
                Pc.bLive = true;
            }

            statusRet = Camera.Image.Save("Image test.png", s32MemID, System.Drawing.Imaging.ImageFormat.Png);
            if (statusRet != uc480.Defines.Status.SUCCESS)
            {
                Console.WriteLine("Saving Image failed");
            }
            else
            {
                Pc.bLive = true;
            }

            Console.WriteLine("Image saved to Debug folder. Now closing program");
            

            statusRet = Camera.Exit();
            Console.ReadKey();
          
        }

      
    }
}
