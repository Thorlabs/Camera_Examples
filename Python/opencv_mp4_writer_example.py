"""
MP4 Video Writing Example - opencv

This example shows how to use Thorlabs TSI Cameras to write videos to a disk using the OpenCV library,
see https://pypi.org/project/opencv-python/ for more information.

In this example 200 images will be saved to a video file called video.mp4 - see NUMBER_OF_IMAGES and FILENAME variables below.
The program will detect if the camera has a color filter and will perform color processing if so. It converts data to 8 bits per pixel.

"""

try:
    # if on Windows, use the provided setup script to add the DLLs folder to the PATH
    from windows_setup import configure_path
    configure_path()
except ImportError:
    configure_path = None

import os
import cv2

from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE
from thorlabs_tsi_sdk.tl_color_enums import FORMAT

NUMBER_OF_IMAGES = 200  # Number of images to be saved
OUTPUT_DIRECTORY = os.path.abspath(r'.')  # Directory the MP4 will be saved to
FILENAME = 'video.mp4'  # The filename of the MP4


# delete duplicate mp4 if it exists
full_file_path = os.path.join(OUTPUT_DIRECTORY, FILENAME)
if os.path.exists(full_file_path):
    os.remove(full_file_path)

with TLCameraSDK() as sdk:
    cameras = sdk.discover_available_cameras()
    if len(cameras) == 0:
        print("Error: no cameras detected!")

    with sdk.open_camera(cameras[0]) as camera:
        #  setup the camera for continuous acquisition
        camera.frames_per_trigger_zero_for_unlimited = 0
        camera.image_poll_timeout_ms = 2000  # 2 second timeout
        camera.arm(2)

        # save for the mp4 framerate
        framerate = camera.frame_rate_control_value

        # need to save the image width and height for color processing
        image_width = camera.image_width_pixels
        image_height = camera.image_height_pixels
        bit_depth = camera.bit_depth

        # initialize a mono to color processor if this is a color camera
        is_color_camera = (camera.camera_sensor_type == SENSOR_TYPE.BAYER)
        mono_to_color_sdk = None
        mono_to_color_processor = None
        if is_color_camera:
            mono_to_color_sdk = MonoToColorProcessorSDK()
            mono_to_color_processor = mono_to_color_sdk.create_mono_to_color_processor(
                camera.camera_sensor_type,
                camera.color_filter_array_phase,
                camera.get_color_correction_matrix(),
                camera.get_default_white_balance_matrix(),
                camera.bit_depth)
            mono_to_color_processor.output_format = FORMAT.BGR_PIXEL # OpenCV default is BGR

        # open an MP4 file
        mp4_video = cv2.VideoWriter(full_file_path, 
                                    cv2.VideoWriter_fourcc(*'mp4v'),
                                    framerate, # NOTE: if using custom triggering, replace this with your desired playback framerate
                                    (image_width, image_height),
                                    isColor=is_color_camera)

        # begin acquisition
        camera.issue_software_trigger()
        frames_counted = 0
        try:
            while frames_counted < NUMBER_OF_IMAGES:
                frame = camera.get_pending_frame_or_null()
                if frame is None:
                    raise TimeoutError("Timeout was reached while polling for a frame, program will now exit")

                frames_counted += 1

                image_data = frame.image_buffer
                if is_color_camera:
                    # transform the raw image data into 8bpp RGB color data (BGR for openCV)
                    image_data = mono_to_color_processor.transform_to_24(image_data, image_width, image_height)
                    image_data = image_data.reshape(image_height, image_width, 3)
                else:
                    # scale to 8bpp for mp4 format
                    image_data = image_data >> (bit_depth - 8)

                mp4_video.write(image_data)
        finally:
            camera.disarm()
            mp4_video.release()

            # we did not use context manager for color processor, so manually dispose of it
            if is_color_camera:
                try:
                    mono_to_color_processor.dispose()
                except Exception as exception:
                    print("Unable to dispose mono to color processor: " + str(exception))
                try:
                    mono_to_color_sdk.dispose()
                except Exception as exception:
                    print("Unable to dispose mono to color sdk: " + str(exception))
