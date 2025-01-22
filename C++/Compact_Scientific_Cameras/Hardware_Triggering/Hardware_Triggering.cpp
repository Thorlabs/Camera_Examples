// Hardware_Triggering.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <string.h>
#include <stdlib.h>
#include "tl_camera_sdk.h"
#include "tl_camera_sdk_load.h"
#ifdef __linux__
  #include <unistd.h>
#endif
int is_camera_sdk_open = 0;
int is_camera_dll_open = 0;
void* camera_handle = 0;

int report_error_and_cleanup_resources(const char* error_string);
int initialize_camera_resources();

int main()
{
    //Initialize the camera by calling the helper function
    if (initialize_camera_resources())
        return 1;

    //Set the exposure time in microseconds
    long long exposure_time = 10000;
    if (tl_camera_set_exposure_time(camera_handle, exposure_time))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());

    // Configure camera for single-shot acquisition by setting the number of frames to 1.
    if (tl_camera_set_frames_per_trigger_zero_for_unlimited(camera_handle, 1))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());

    //Check if hardware triggering is supported. If it is, set the camera operating mode to accept a hardware trigger. 
    int is_hardware_triggering_supported;
    tl_camera_get_is_operation_mode_supported(camera_handle, TL_CAMERA_OPERATION_MODE_HARDWARE_TRIGGERED, &is_hardware_triggering_supported);
    if (is_hardware_triggering_supported)
    {
        //Set the trigger polarity for hardware triggers (ACTIVE_HIGH or ACTIVE_LOW)
        if (tl_camera_set_trigger_polarity(camera_handle, TL_CAMERA_TRIGGER_POLARITY_ACTIVE_HIGH))
            return report_error_and_cleanup_resources(tl_camera_get_last_error());

        if (tl_camera_set_operation_mode(camera_handle, TL_CAMERA_OPERATION_MODE_HARDWARE_TRIGGERED))
            return report_error_and_cleanup_resources(tl_camera_get_last_error());
        std::cout << "Hardware trigger set\n";        
    }
    else {
        report_error_and_cleanup_resources("Camera does not support hardware triggering");
    }

    // Set camera to wait 100 ms for a frame to arrive during a poll.
    // If an image is not received in 100ms, the returned frame will be null
    if (tl_camera_set_image_poll_timeout(camera_handle, 100))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());

    // Arm the camera.
    if (tl_camera_arm(camera_handle, 2))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    std::cout << "Camera Armed\n";

    //initialize frame variables
    unsigned short* image_buffer = 0;
    int frame_count = 0;
    unsigned char* metadata = 0;
    int metadata_size_in_bytes = 0;

    //Loop until 5 images are received. 
    std::cout << "Waiting for images\n";
    int num_images_acquired = 0;
    while (num_images_acquired < 5)
    {
        //Poll for an available image
        if (tl_camera_get_pending_frame_or_null(camera_handle, &image_buffer, &frame_count, &metadata, &metadata_size_in_bytes))
            return report_error_and_cleanup_resources(tl_camera_get_last_error());
        if (!image_buffer)
        {
            //A small sleep is used to prevent too many calls to the camera. 
#ifdef _WIN32
            Sleep(50);
#elif defined __linux__
            usleep(50000);
#endif
            continue; //Timeout case. Skip this loop iteration
        }

        std::cout << "Pointer to Image: 0x"<< image_buffer << "\n";
        std::cout << "Frame Count " << frame_count << "\n\n";

        num_images_acquired++;
    }

    // Stop the camera
    if (tl_camera_disarm(camera_handle))
        std::cout <<"Failed to stop the camera!\n";

    // Clean up and exit
    return report_error_and_cleanup_resources(0);
}


//
// Helper functions for opening and closing camera
//
int initialize_camera_resources()
{
    // Initializes camera dll
    if (tl_camera_sdk_dll_initialize())
        return report_error_and_cleanup_resources("Failed to initialize dll!\n");
    std::cout << "Successfully initialized dll\n";
    is_camera_dll_open = 1;

    // Open the camera SDK
    if (tl_camera_open_sdk())
        return report_error_and_cleanup_resources("Failed to open SDK!\n");
    std::cout << "Successfully Opened SDK\n";
    is_camera_sdk_open = 1;

    char camera_ids[1024];
    camera_ids[0] = 0;

    // Discover cameras.
    if (tl_camera_discover_available_cameras(camera_ids, 1024))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    std::cout << "Available Camera ID's: " << camera_ids << "\n";

    // Check for no cameras.
    if (!strlen(camera_ids))
        return report_error_and_cleanup_resources("Did not find any cameras!\n");

    // Camera IDs are separated by spaces.
    char* p_space = strchr(camera_ids, ' ');
    if (p_space)
        *p_space = '\0'; // isolate the first detected camera
    char first_camera[256];

    // Copy the ID of the first camera to separate buffer (for clarity)
#ifdef _WIN32
    strcpy_s(first_camera, 256, camera_ids);
#elif defined __linux__
    strcpy(first_camera, camera_ids);
#endif
    std::cout << "ID of First Camera: " << first_camera << "\n";

    // Connect to the camera(get a handle to it).
    if (tl_camera_open_camera(first_camera, &camera_handle))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    std::cout << "Camera Handle: " << camera_handle << "\n";

    return 0;
}


int report_error_and_cleanup_resources(const char* error_string)
{
    int num_errors = 0;

    if (error_string)
    {
        std::cout << error_string << "\n";
        num_errors++;
    }

    std::cout << "Closing all resources...\n";

    if (camera_handle)
    {
        if (tl_camera_close_camera(camera_handle))
        {
            std::cout << "Failed to close camera! Error: " << tl_camera_get_last_error() << "\n";
            num_errors++;
        }
        camera_handle = 0;
    }
    if (is_camera_sdk_open)
    {
        if (tl_camera_close_sdk())
        {
            std::cout << "Failed to close SDK!\n";
            num_errors++;
        }
        is_camera_sdk_open = 0;
    }
    if (is_camera_dll_open)
    {
        if (tl_camera_sdk_dll_terminate())
        {
            std::cout << "Failed to close DLL!\n";
            num_errors++;
        }
        is_camera_dll_open = 0;
    }

    std::cout << "Clean up finished\n";
    return num_errors;
}
