using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Thorlabs.TSI.ImageData;
using Thorlabs.TSI.ImageDataInterfaces;

namespace CameraTypeConversion
{
    public class Converter
    {
        public static ImageDataUShort1D ConvertFrameImageData(IImageData imageData)
        {
            return imageData as ImageDataUShort1D;
        }
    }
}
