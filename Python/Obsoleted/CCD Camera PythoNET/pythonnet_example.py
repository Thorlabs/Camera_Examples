import os
import numpy as np
from tl_dotnet_wrapper import TL_SDK, TL_Camera
# simple example to open camera, set some parameters, wait for an image, and close the camera.

sdk = TL_SDK()
cameras = sdk.get_camera_list()
first_camera_id = cameras[0]
camera = sdk.open_camera(first_camera_id)
camera.set_exposure_time_us(2000)  # 2 second exposure
camera.set_frames_per_trigger_zero_for_unlimited(0)  # continuous mode
camera.arm()
camera.issue_software_trigger()
frame = None
while frame is None:
    frame = camera.get_pending_frame_or_null()
image_array = camera.frame_to_array(frame) # copies image data from frame into a numpy array
camera.disarm()
camera.close()
sdk.close()
