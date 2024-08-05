import numpy as np
import traceback
import ctypes

import clr  
from clr import *
from System import Array, Double, IntPtr, Random, Int64, Convert
from System.Runtime.InteropServices import Marshal

clr.AddReference('Thorlabs.TSI.TLCamera')
clr.AddReference('Thorlabs.TSI.TLCameraInterfaces')
clr.AddReference('Thorlabs.TSI.ImageData')
clr.AddReference('Thorlabs.TSI.ColorInterfaces')

import Thorlabs.TSI.ImageData as thorlabs_tsi_imagedata
import Thorlabs.TSI.TLCamera as thorlabs_tsi_tlcamera
import Thorlabs.TSI.TLCameraInterfaces as thorlabs_tsi_tlcamerainterfaces
import Thorlabs.TSI.ColorInterfaces as thorlabs_tsi_colorinterfaces

TLCameraSDK = thorlabs_tsi_tlcamera.TLCameraSDK
ImageDataUShort1D = thorlabs_tsi_imagedata.ImageDataUShort1D
Taps = thorlabs_tsi_tlcamerainterfaces.Taps
ROIAndBin = thorlabs_tsi_tlcamerainterfaces.ROIAndBin
DataRate = thorlabs_tsi_tlcamerainterfaces.DataRate
CameraConnectEventArgs = thorlabs_tsi_tlcamerainterfaces.CameraConnectEventArgs
CameraDisconnectEventArgs = thorlabs_tsi_tlcamerainterfaces.CameraDisconnectEventArgs
TriggerPolarity = thorlabs_tsi_tlcamerainterfaces.TriggerPolarity
CameraSensorType = thorlabs_tsi_tlcamerainterfaces.CameraSensorType
ColorFilterArrayPhase = thorlabs_tsi_colorinterfaces.ColorFilterArrayPhase

print("DOTNET WRAPPER successfully imported.")


class TL_SDK(object):
    """
    Python object that holds a DotNet TLCameraSDK and wraps its methods in a more pythonic way
    """
    # constructor
    def __init__(self):
        self.connect_delegates = {}
        self.disconnect_delegates = {}
        self.sdk = None
        self.open()

    # assign sdk variable to a new TLCameraSDK
    def open(self):
        try:
            self.connect_delegates = {}
            self.disconnect_delegates = {}
            self.sdk = TLCameraSDK.OpenTLCameraSDK()
        except System.InvalidOperationException as ioe:
            raise SDKExceptionError("Error: Unable to open SDK\n" + str(ioe))
        except Exception as e:
            raise SDKExceptionError("Error: Unable to open SDK\n" + str(e))

    # dispose the TLCameraSDK variable
    def close(self):
        try:    
            self.sdk.Dispose()
            print("SDK DISPOSED")
        except Exception as e:
            raise SDKExceptionError("Error: Unable to dispose SDK\n" + str(e))

    def get_number_of_cameras(self):
        retval = 0
        try:
            cams = self.sdk.DiscoverAvailableCameras()
            retval = cams.Count
        except System.Reflection.TargetInvocationException as tie:
            raise SDKExceptionError("Error: could not get number of cameras\n" + str(tie))
        except Exception as e:
            raise SDKExceptionError("Error: could not get number of cameras\n" + str(e))
        return retval

    # returns a tuple of camera serial numbers
    def get_camera_list(self):
        cams = self.sdk.DiscoverAvailableCameras() # serial numbers
        return tuple(cams)

    # return camera name associated with a serial number
    def get_camera_name(self, camera_number):
        retval = ""
        try:
            cams = self.sdk.DiscoverAvailableCameras()
            if camera_number < cams.Count:
                retval = cams[camera_number]
        except Exception as e:
            raise SDKExceptionError("Error: could not get camera name\n")
        return retval

    # if given an int, use camera_id as index into list of available cameras
    # otherwise open camera where camera_id is a serial number
    # creates a python TL_Camera, which holds a DotNet TLCamera
    def open_camera(self, camera_id):
        retval = None
        if camera_id is None:
            raise SDKExceptionError("Could not open camera with Null camera ID")
        cam = camera_id

        try:
            if type(camera_id) == int:
                cams = self.sdk.DiscoverAvailableCameras()
                cam = cams[camera_id]
            opened_camera = self.sdk.OpenCamera(str(cam), False)
            retval = TL_Camera(self, opened_camera)
        except System.InvalidOperationException as ioe:
             raise SDKExceptionError("Error: could not open camera " + str(camera_id) + "\n" + str(ioe))
        except System.ArgumentOutOfRangeException as aoore:
             raise SDKExceptionError("Error: could not open camera " + str(camera_id) + "\n" + str(aoore))
        except:
            raise SDKExceptionError("Error: could not open camera\n")
        return retval

    # same as open_camera except that it doesn't create a python object; returns a DotNet TLCamera object
    def open_camera_only(self, camera_id):
        retval = None
        cam = camera_id

        try:
            if(type(camera_id) == int):
                cams = self.sdk.DiscoverAvailableCameras()
                cam = cams[camera_id]
            opened_camera = self.sdk.OpenCamera(str(cam), False)
            retval = opened_camera
        except System.InvalidOperationException as ioe:
             raise SDKExceptionError("Error: could not open camera " + str(camera_id) + "\n" + str(ioe))
        except System.ArgumentOutOfRangeException as aoore:
             raise SDKExceptionError("Error: could not open camera " + str(camera_id) + "\n" + str(aoore))
        except Exception as exception:
            raise SDKExceptionError("Error: could not open camera; {exception}\n".format(exception=exception))
        return retval

    def add_on_camera_connect_delegate(self, callback):
        self.sdk.OnCameraConnect += callback

    def remove_camera_connect_delegate(self, callback):
        self.sdk.OnCameraConnect -= callback

    def add_on_camera_disconnect_delegate(self, callback):
        self.sdk.OnCameraDisconnect += callback

    def remove_camera_disconnect_delegate(self, callback):
        self.sdk.OnCameraDisconnect -= callback


class TL_Camera(object):

    def __init__(self, sdk, camera):
        self.sdk = sdk
        self.camera = camera
        self.is_open = True
        self._is_busy = False

    def __del__(self):
        if self.is_open:
            self.close()

    @property
    def is_busy(self):
        return self._is_busy

    @is_busy.setter
    def is_busy(self, is_busy):
        if type(is_busy) == bool:
            self._is_busy = is_busy

    @property
    def is_open(self):
        return self.__is_open

    @is_open.setter
    def is_open(self, is_open):
        if type(is_open) == bool:
            self.__is_open = is_open

    def close(self):
        try:
            self.camera.Dispose()
            self.is_open = False
        except Exception as exception:
            raise CameraExceptionError("Error: could not close camera; {exception}\n".format(exception=exception))

    def reopen(self):
        try:
            id = self.get_serial_number()
            sdk = self.sdk
            self.close()
            self.camera = sdk.open_camera_only(id)
            self.is_open = True
            return True
        except:
            self.is_open = False
            self.camera = None
            return False

    def arm(self):
        try:
            self.camera.Arm()
        except Exception as exception:
            raise CameraExceptionError("Error: could not arm camera; {exception}\n".format(exception=exception))

    def disarm(self):
        try:
            self.camera.Disarm()
        except Exception as exception:
            raise CameraExceptionError("Error: could not disarm camera; {exception}\n".format(exception=exception))

    def set_frames_per_trigger_zero_for_unlimited(self, num_frames):
        try:
            self.camera.FramesPerTrigger_zeroForUnlimited = num_frames
        except Exception as exception:
            raise CameraExceptionError("Error: could not set Frames Per Trigger; {exception}\n".format(
                exception=exception))

    def set_maximum_number_of_frames_to_queue(self, num_frames):
        try:
            self.camera.MaximumNumberOfFramesToQueue = num_frames
        except Exception as exception:
            raise CameraExceptionError("Error: could not set max number of frames to queue; {exception}\n".format(
                exception=exception))

    def issue_software_trigger(self):
        try:
            self.camera.IssueSoftwareTrigger()
        except Exception as exception:
            raise CameraExceptionError("Error: IssueSoftwareTrigger failed; {exception}\n".format(exception=exception))

    # get a frame from camera, result will be clr Frame type
    def get_pending_frame_or_null(self):
        retval = None
        try:
            # t = time.time()
            retval = self.camera.GetPendingFrameOrNull()
            # print("time to get pending frame: {time}".format(time=time.time() - t))
        except Exception as e:
            raise CameraExceptionError("Error: could not get pending frame;{exception}\n".format(exception=e))
        return retval

    # call get_pending_frame_or_null but convert frame to an np array
    def get_pending_array_or_null(self):
        try:
            frame = self.get_pending_frame_or_null()
            frame = self.frame_to_array(frame)
        except Exception as exception:
            frame = None
            print("Error: could not get pending array; {error}".format(error=exception))
        return frame

    # use InteropServices to copy frame image data into an np array
    @staticmethod
    def frame_to_array(frame) -> np.ndarray:
        if frame is None:
            raise ValueError("frame_to_array called with no frame")
        try:
            image = Convert.ChangeType(frame.ImageData, thorlabs_tsi_imagedata.ImageDataUShort1D).ImageData_monoOrBGR

            """
            image_handle = GCHandle.Alloc(image, GCHandleType.Pinned)
            image_ptr = image_handle.AddrOfPinnedObject().ToInt32()
            destination = np.fromstring(ctypes.string_at(image_ptr, len(image)*2), dtype=np.ushort)  # 2 is the size of ushort in bytes
            destination = destination.reshape(frame.ImageData.Height_pixels, frame.ImageData.Width_pixels)
            return destination
            """

            ret_array = np.zeros(len(image), dtype=ctypes.c_uint16)
            Marshal.Copy(image, 0, IntPtr(ret_array.__array_interface__['data'][0]), len(image)) # .NET method that copies image ( a System.UInt16[] type ) memory to ret_array ( an np array dtype = uint16 ) 'data' memory
            ret_array = ret_array.reshape(frame.get_ImageData().get_Height_pixels(), frame.get_ImageData().get_Width_pixels())
            return ret_array
        except IndexError as ie:
            print("frame_to_array: Index out of bounds error")
            raise CameraExceptionError("Error: could not convert frame to array - index out of bounds\n" + ie)
        except Exception as e:
            print("Error converting frame to array")
            raise CameraExceptionError("Error: could not convert frame to array:\n" + str(e))
        #finally:
        #    if image_handle.IsAllocated:
        #        image_handle.Free()

    def set_exposure_time_us(self, time_ms):
        try:
            self.camera.ExposureTime_us = time_ms
        except Exception as exception:
            raise CameraExceptionError("Error: could not set exposure time; {exception}\n".format(exception=exception))

    def set_gain(self, gain):
        try:
            self.camera.Gain = gain
        except Exception as exception:
            raise CameraExceptionError("Error: could not set gain; {exception}\n".format(exception=exception))

    def set_black_level(self, blacklevel):
        try:
            self.camera.BlackLevel = blacklevel
        except Exception as exception:
            raise CameraExceptionError("Error: could not set black level; {exception}\n".format(exception=exception))

    def get_black_level_range(self):
        try:
            return self.camera.BlackLevelRange.Minimum, self.camera.BlackLevelRange.Maximum
        except Exception as exception:
            raise CameraExceptionError("Error: could not get black level range; {exception}\n"
                                       .format(exception=exception))

    def get_gain_range(self):
        try:
            return self.camera.GainRange.Minimum, self.camera.GainRange.Maximum
        except Exception as exception:
            raise CameraExceptionError("Error: could not get gain range; {exception}\n"
                                       .format(exception=exception))

    def get_highest_supported_tap(self):
        if self.get_is_taps_supported(4):
            return 4
        elif self.get_is_taps_supported(2):
            return 2
        else:
            return 1

    def get_data_rate_list(self):
        data_rate_list = []
        if self.get_is_data_rate_supported("20MHz"):
            data_rate_list.append("20MHz")
        if self.get_is_data_rate_supported("40MHz"):
            data_rate_list.append("40MHz")
        if self.get_is_data_rate_supported("FPS30"):
            data_rate_list.append("FPS30")
        if self.get_is_data_rate_supported("FPS50"):
            data_rate_list.append("FPS50")
        return data_rate_list

    def get_sensor_width_pixels(self):
        try:
            return self.camera.SensorWidth_pixels
        except Exception as exception:
            raise CameraExceptionError("Error: could not get sensor width; {error}\n".format(error=exception))

    def get_sensor_height_pixels(self):
        retval = 0
        try:
            retval = self.camera.SensorHeight_pixels
        except Exception as exception:
            raise CameraExceptionError("Error: could not get sensor height; {exception}\n".format(exception=exception))
        return retval

    def get_bit_depth(self):
        retval = 0
        try:
            retval = self.camera.BitDepth
        except Exception as exception:
            raise CameraExceptionError("Error: could not get bit depth; {exception}\n".format(exception=exception))
        return retval

    def set_roi_binning(self, x, y, width, height, binX, binY):
        new_settings = ROIAndBin()
        new_settings.BinX = binX
        new_settings.BinY = binY
        new_settings.ROIWidth_pixels = width
        new_settings.ROIHeight_pixels = height
        new_settings.ROIOriginX_pixels = int(x)
        new_settings.ROIOriginY_pixels = int(y)    
        try:
            self.camera.ROIAndBin = new_settings
        except:
            raise CameraExceptionError("Error: could not set ROIAndBin\n")

    def add_on_image_frame_available_callback(self, callback, *args):
        try:
            if len(args) == 0:
                self.camera.OnImageFrameAvailable += callback
            else:
                self.camera.OnImageFrameAvailable += lambda source, eventargs: callback(source, eventargs, *args) # one could pass any number of arguments to their callback
        except:
            raise CameraExceptionError("Error: could not set image frame available callback\n")

    def remove_on_image_frame_available_callback(self, callback):
        self.camera.OnImageFrameAvailable -= callback # TODO: works with variadic\lambda?

    def get_roi_binning(self):
        retval = []
        try:
            retval = [
                        self.camera.ROIAndBin.ROIOriginX_pixels,
                        self.camera.ROIAndBin.ROIOriginY_pixels,
                        self.camera.ROIAndBin.ROIWidth_pixels,
                        self.camera.ROIAndBin.ROIHeight_pixels,
                        self.camera.ROIAndBin.BinX,
                        self.camera.ROIAndBin.BinY
                      ]
        except Exception as exception:
            raise CameraExceptionError("Error: GetRoiBinning failed\n; {exception}".format(exception=exception))
        return retval

    def get_name(self):
        return self.camera.Name

    def get_model(self) -> str:
        return self.camera.Model

    def get_black_level(self):
        return self.camera.BlackLevel

    def get_gain(self):
        return self.camera.Gain

    def get_taps(self):
        try:
            if self.camera.Taps == Taps.SingleTap:
                return 1
            elif self.camera.Taps == Taps.DualTap:
                return 2
            elif self.camera.Taps == Taps.QuadTap:
                return 4
            return 0
        except BaseException as be:
            raise CameraExceptionError("Error: GetTaps failed\n" + str(be))

    def get_is_taps_supported(self, tap):
        try:
            if tap == 1:
                return self.camera.GetIsTapsSupported(Taps.SingleTap)
            elif tap == 2:
                return self.camera.GetIsTapsSupported(Taps.DualTap)
            elif tap == 4:
                return self.camera.GetIsTapsSupported(Taps.QuadTap)
        except BaseException as be:
            raise CameraExceptionError("Error: GetIsTapsSupported failed\n" + str(be))

    def set_taps(self, tap):
        try:
            if tap == 1:
                self.camera.Taps = Taps.SingleTap
            elif tap == 2:
                self.camera.Taps = Taps.DualTap
            elif tap == 4:
                self.camera.Taps = Taps.QuadTap
        except BaseException as be:
            raise CameraExceptionError("Error: SetTaps failed\n" + str(be))

    def get_roi_height_range(self):
        try:
            return self.camera.ROIHeightRange
        except BaseException as be:
            raise CameraExceptionError("Error: GetROIHeightRange failed\n" + str(be))

    def get_roi_width_range(self):
        try:
            return self.camera.ROIWidthRange
        except BaseException as be:
            raise CameraExceptionError("Error: GetROIWidthRange failed\n" + str(be))

    def set_is_tap_balance_enabled(self, tap_balance_enabled):
        try:
            self.camera.IsTapBalanceEnabled = tap_balance_enabled
        except BaseException as be:
            raise CameraExceptionError("Error: SetIsTapBalanceEnabled failed\n" + str(be))

    def get_is_tap_balance_enabled(self):
        try:
            return self.camera.IsTapBalanceEnabled
        except BaseException as be:
            raise CameraExceptionError("Error: GetIsTapBalanceEnabled failed\n" + str(be))

    def get_exposure_time_us(self):
        try:
            return self.camera.ExposureTime_us
        except BaseException as be:
            raise CameraExceptionError("Error: GetExposureTime failed\n" + str(be))

    def get_serial_number(self):
        try:
            return self.camera.SerialNumber
        except BaseException as be:
            raise CameraExceptionError("Error: GetSerialNumber failed\n" + str(be))

    def set_data_rate(self, data_rate):
        try:
            if data_rate == "20MHz":
                self.camera.DataRate = DataRate.ReadoutSpeed20MHz
            elif data_rate == "40MHz":
                self.camera.DataRate = DataRate.ReadoutSpeed40MHz
            elif data_rate == "FPS30":
                self.camera.DataRate = DataRate.FPS30
            elif data_rate == "FPS50":
                self.camera.DataRate = DataRate.FPS50
        except BaseException as be:
            raise CameraExceptionError("Error: SetDataRate failed\n" + str(be))

    def tap_balance_load_data_from_file(self, file):
        try:
            self.camera.TapBalanceLoadDataFromFile(file)
        except Exception as e:
            raise SDKExceptionError("Error: Tap balance data could not be loaded from file\n" + str(e))

    def tap_balance_write_data_to_camera(self):
        try:
            self.camera.TapBalanceWriteDataToCamera()
        except Exception as e:
            raise SDKExceptionError("Error: Tap balance data could not be written to camera\n" + str(e))

    def get_is_data_rate_supported(self, data_rate):# div by 0 error?
        try:
            if data_rate == "20MHz":
                return self.camera.GetIsDataRateSupported(DataRate.ReadoutSpeed20MHz)
            elif data_rate == "40MHz":
                return self.camera.GetIsDataRateSupported(DataRate.ReadoutSpeed40MHz)
            elif data_rate == "FPS30":
                return self.camera.GetIsDataRateSupported(DataRate.FPS30)
            elif data_rate == "FPS50":
                return self.camera.GetIsDataRateSupported(DataRate.FPS50)
        except ZeroDivisionError as zde:
            raise CameraExceptionError("Error: divide by zero\n" + str(zde))

    def set_hot_pixel_correction_threshold(self, threshold):
        try:
            self.camera.HotPixelCorrectionThreshold = threshold
        except Exception as e:
            raise CameraExceptionError("Error: could not set hot pixel correction threshold " + str(e))

    def get_hot_pixel_correction_threshold(self):
        try:
            return self.camera.HotPixelCorrectionThreshold
        except Exception as e:
            raise CameraExceptionError("Error: could not get hot pixel correction threshold " + str(e))

    def set_is_hot_pixel_correction_enabled(self, is_enabled):
        try:
            self.camera.IsHotPixelCorrectionEnabled = is_enabled
        except Exception as e:
            raise CameraExceptionError("Error: could not set IsHotPixelCorrectionEnabled " + str(e))

    def get_is_hot_pixel_correction_enabled(self):
        try:
            return self.camera.IsHotPixelCorrectionEnabled
        except Exception as e:
            raise CameraExceptionError("Error: could not get IsHotPixelCorrectionEnabled " + str(e))

    def set_is_cooling_enabled(self, is_enabled):
        try:
            self.camera.IsCoolingEnabled = is_enabled
        except Exception as e:
            raise CameraExceptionError("Error: could not set IsCoolingEnabled " + str(e))

    def get_is_cooling_enabled(self):
        try:
            return self.camera.IsCoolingEnabled
        except Exception as e:
            raise CameraExceptionError("Error: could not get IsCoolingEnabled " + str(e))

    def set_is_eep_enabled(self, is_enabled):
        try:
            self.camera.IsEEPEnabled = is_enabled
        except Exception as e:
            raise CameraExceptionError("Error: could not set IsEEPEnabled " + str(e))

    def get_is_eep_enabled(self):
        try:
            return self.camera.IsEEPEnabled
        except Exception as e:
            raise CameraExceptionError("Error: could not get IsEEPEnabled " + str(e))

    def set_is_nir_boost_enabled(self, is_enabled):
        try:
            self.camera.IsNIRBoostEnabled = is_enabled
        except Exception as e:
            raise CameraExceptionError("Error: could not set NIRBoostEnabled " + str(e))

    def get_is_nir_boost_enabled(self):
        try:
            return self.camera.IsNIRBoostEnabled
        except Exception as e:
            raise CameraExceptionError("Error: could not get NIRBoostEnabled " + str(e))

    def set_operation_mode(self, mode):
        try:
            self.camera.OperationMode = mode
        except Exception as e:
            raise CameraExceptionError("Error: could not set operation mode " + str(e))

    def get_operation_mode(self):
        try:
            return self.camera.OperationMode
        except Exception as e:
            raise CameraExceptionError("Error: could not get opration mode " + str(e))

    def get_sensor_height_range(self):
        try:
            return self.camera.SensorHeight_pixels.Minimum, self.camera.SensorHeight_pixels.Maximum
        except Exception as e:
            raise CameraExceptionError("Error: could not get sensor height")

    def get_sensor_width_range(self):
        try:
            return self.camera.SensorWidth_pixels.Minimum, self.camera.SensorWidth_pixels.Maximum
        except Exception as e:
            raise CameraExceptionError("Error: could not get sensor width range")

    def get_sensor_pixel_size_um(self):
        try:
            return self.camera.SensorPixelSize_um
        except Exception as e:
            raise CameraExceptionError("Error: could not get sensor pixel size")

    def get_bin_x_range(self):
        try:
            return self.camera.BinXRange.Minimum, self.camera.BinXRange.Maximum
        except Exception as e:
            raise CameraExceptionError("Error: could not get bin x range")

    def get_number_of_queued_frames(self):
        try:
            return self.camera.NumberOfQueuedFrames
        except Exception as e:
            raise CameraExceptionError("Error: could not get queued frames")

    def get_bin_y_range(self):
        try:
            return self.camera.BinYRange.Minimum, self.camera.BinYRange.Maximum
        except Exception as e:
            raise CameraExceptionError("Error: could not get bin y range")

    def set_trigger_polarity(self, polarity):
        try:
            self.camera.TriggerPolarity = polarity
        except Exception as e:
            raise CameraExceptionError("Error: could not set trigger polarity")

    def get_trigger_polarity(self):
        try:
            if self.camera.TriggerPolarity == TriggerPolarity.ActiveHigh:
                return 0
            elif self.camera.TriggerPolarity == TriggerPolarity.ActiveLow:
                return 1
        except Exception as e:
            raise CameraExceptionError("Error: could not get trigger polarity")

    def tap_balance_config(self, config_select, enable):
        self.camera.TapBalanceConfig(config_select, enable)

    def free_all_but_given_number_of_frames(self, number_of_frames_to_leave_in_queue: int):
        try:
            self.camera.FreeAllButGivenNumberOfFrames(number_of_frames_to_leave_in_queue)
        except Exception as exception:
            raise CameraExceptionError("Unable to free all but given number of frames; {error}".format(error=exception))

    @property
    def is_armed(self):
        try:
            if self.camera.IsArmed:
                return True
            else:
                return False
        except Exception as exception:
            raise CameraExceptionError("Unable to free all but given number of frames; {error}".format(error=exception))

    def take_one_image(self):
        """
        if self.is_armed:
            self.disarm()
        self.set_frames_per_trigger_zero_for_unlimited(1)
        self.set_maximum_number_of_frames_to_queue(10)
        self.free_all_but_given_number_of_frames(0)
        self.arm()
        self.issue_software_trigger()
        image = None
        while self.get_number_of_queued_frames() <= 0:
            pass
        image = self.get_pending_array_or_null()
        self.disarm()
        return image
        """

        self.disarm()
        self.set_frames_per_trigger_zero_for_unlimited(1)
        self.set_maximum_number_of_frames_to_queue(10)
        self.arm()   
        self.issue_software_trigger()
        while self.get_number_of_queued_frames() <= 0:
            pass
        image_array = self.get_pending_array_or_null()
        self.disarm()
        return image_array

    def get_image_width(self):
        try:
            roi_and_bin = self.get_roi_binning()
            return roi_and_bin[2]
        except Exception as e:
            raise CameraExceptionError("Error: could not get image width; {error}".format(error=e))

    def get_image_height(self):
        try:
            roi_and_bin = self.get_roi_binning()
            return roi_and_bin[3]
        except Exception as e:
            raise CameraExceptionError("Error: could not get image height; {error}".format(error=e))

    def get_autoscaled_image(self, image):
        try:
            image = image.astype(np.float64)
            image *= ((2 ** self.get_bit_depth()) - 1) / np.max(image)  # auto-scale
            return image
        except Exception as exception:
            raise SDKExceptionError("unable to autoscale image; {error}".format(error=exception))

    def get_camera_sensor_type(self):
        try:
            if self.camera.CameraSensorType == CameraSensorType.Bayer:
                return 'bayer'
            elif self.camera.CameraSensorType == CameraSensorType.Monochrome:
                return 'monochrome'
            elif self.camera.CameraSensorType == CameraSensorType.MonochromePolarized:
                return 'monochrome polarized'
            else:
                return None
        except Exception as e:
            raise CameraExceptionError("Error: could not get camera sensor type")

    def get_color_filter_array_type(self):
        try:
            if self.camera.ColorFilterArrayPhase == ColorFilterArrayPhase.BayerRed:
                return 'red'
            if self.camera.ColorFilterArrayPhase == ColorFilterArrayPhase.BayerBlue:
                return 'blue'
            if self.camera.ColorFilterArrayPhase == ColorFilterArrayPhase.BayerGreenLeftOfRed:
                return 'green left of red'
            if self.camera.ColorFilterArrayPhase == ColorFilterArrayPhase.BayerGreenLeftOfBlue:
                return 'green left of blue'
            else:
                return None
        except Exception as e:
            raise CameraExceptionError("Error: could not get color filter array type")


class SDKExceptionError(Exception):
    def __init__(self, message):
        print(traceback.format_exc())
        super(SDKExceptionError, self).__init__(message)


class CameraExceptionError(Exception):
    def __init__(self, message):
        print(traceback.format_exc())
        super(CameraExceptionError, self).__init__(message)
