"""
Polling Example

This example shows how to open a camera, adjust some settings, and poll for images. It also shows how 'with' statements
can be used to automatically clean up camera and SDK resources.

"""

import numpy as np
import os
import cv2
import time
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, OPERATION_MODE

try:
    # if on Windows, use the provided setup script to add the DLLs folder to the PATH
    from windows_setup import configure_path
    configure_path()
except ImportError:
    configure_path = None

with TLCameraSDK() as sdk:
    available_cameras = sdk.discover_available_cameras()
    if len(available_cameras) < 1:
        print("no cameras detected")

    with sdk.open_camera(available_cameras[0]) as camera:
        camera.exposure_time_us = 10000  # set exposure to 11 ms
        camera.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
        camera.image_poll_timeout_ms = 1000  # 1 second polling timeout
        camera.frame_rate_control_value = 10
        camera.is_frame_rate_control_enabled = True

        camera.arm(2)
        camera.issue_software_trigger()

        try:
            while True:
                frame = camera.get_pending_frame_or_null()
                if frame is not None:
                    print("frame #{} received!".format(frame.frame_count))
                    frame.image_buffer
                    image_buffer_copy = np.copy(frame.image_buffer)
                    numpy_shaped_image = image_buffer_copy.reshape(camera.image_height_pixels, camera.image_width_pixels)
                    nd_image_array = np.full((camera.image_height_pixels, camera.image_width_pixels, 3), 0, dtype=np.uint8)
                    nd_image_array[:,:,0] = numpy_shaped_image
                    nd_image_array[:,:,1] = numpy_shaped_image
                    nd_image_array[:,:,2] = numpy_shaped_image
          
                    cv2.imshow("Image From TSI Cam", nd_image_array)
                    cv2.waitKey(1)

                else:
                    print("Unable to acquire image, program exiting...")
                    exit()
        except KeyboardInterrupt:
            print("loop terminated")
            
        cv2.destroyAllWindows()
        camera.disarm()

#  Because we are using the 'with' statement context-manager, disposal has been taken care of.

print("program completed")
