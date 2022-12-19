// Read_Parameters.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <string.h>
#include <stdlib.h>
#include <windows.h>
#include "tl_camera_sdk.h"
#include "tl_camera_sdk_load.h"
//This is a comment

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

    //Get Camera Info e.g. Model, Name, Firmware Version
    char model_name[256];
    tl_camera_get_model(camera_handle, model_name, 256);
    std::cout << "Model Name: " << model_name << "\n";

    char camera_name[256];
    tl_camera_get_name(camera_handle, camera_name, 256); // Camera name can be changed by the user 
    std::cout << "Camera Name: " << camera_name << "\n";

    char firmware_version[256];
    tl_camera_get_firmware_version(camera_handle, firmware_version, 256);
    std::cout << "Firmware Version: " << firmware_version << "\n";

    //Get Sensor Type

    TL_CAMERA_SENSOR_TYPE sensor_type;
    tl_camera_get_camera_sensor_type(camera_handle, &sensor_type);
    std::cout << "Sensor Type: " << sensor_type << "\n";

    //Get the camera sensor dimensions in pixels
    int sensor_width; 
    int sensor_height;
    tl_camera_get_sensor_width(camera_handle, &sensor_width);
    tl_camera_get_sensor_height(camera_handle, &sensor_height);
    std::cout << "Sensor Witdh: " << sensor_width << "\n";
    std::cout << "Sensor Height: " << sensor_height << "\n";

    //Get Camera Bit Depth
    int bit_depth;
    tl_camera_get_bit_depth(camera_handle, &bit_depth);
    std::cout << "Sensor Bit Depth: " << bit_depth << "\n";

    //Get Exposure Time Range
    long long exposure_min;
    long long exposure_max;
    if (tl_camera_get_exposure_time_range(camera_handle, &exposure_min, &exposure_max))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    std::cout << "Exposure Minimum: " << exposure_min << "\n";
    std::cout << "Exposure Maximum: " << exposure_max << "\n";

    //Set and Get Exposure Time
    long long exposure_time;
    if (tl_camera_set_exposure_time(camera_handle, 10000))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    if (tl_camera_get_exposure_time(camera_handle, &exposure_time))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    std::cout << "Exposure Time: " << exposure_time << "\n";

    //Get Frames Per Trigger Range
    u_int frames_per_trigger_min;
    u_int frames_per_trigger_max;
    if (tl_camera_get_frames_per_trigger_range(camera_handle, &frames_per_trigger_min, &frames_per_trigger_max))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    std::cout << "Frames per Trigger Minimum: " << frames_per_trigger_min << "\n";
    std::cout << "Frames per Trigger Maximum: " << frames_per_trigger_max << "\n";

    //Set and Get Frames per Trigger
    u_int frames_per_trigger;
    if (tl_camera_set_frames_per_trigger_zero_for_unlimited(camera_handle, 1))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    if (tl_camera_get_frames_per_trigger_zero_for_unlimited(camera_handle, &frames_per_trigger))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    std::cout << "Frames per trigger: " << frames_per_trigger << "\n";

    //Check if camera supports adjusting framerate and check range
    double frame_rate_control_min;
    double frame_rate_control_max;

    if (tl_camera_get_frame_rate_control_value_range(camera_handle, &frame_rate_control_min, &frame_rate_control_max))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    std::cout << "Frame Rate Control Valiue Minimum: " << frame_rate_control_min << "\n";
    std::cout << "Frame Rate Control Valiue Maximum: " << frame_rate_control_max << "\n";

    if (frame_rate_control_max > 0)
    {
        //this camera supports adjusting the frame rate, set and get it
        if (tl_camera_set_frame_rate_control_value(camera_handle, 10.5))
            return report_error_and_cleanup_resources(tl_camera_get_last_error());

        double frame_rate_control_value;
        if (tl_camera_get_frame_rate_control_value(camera_handle, &frame_rate_control_value))
            return report_error_and_cleanup_resources(tl_camera_get_last_error());
        std::cout << "Frame Rate Control Value: " << frame_rate_control_value << "\n";
    }

    //Check if camera supports adjusting gain and check range
    int gain_min;
    int gain_max;
    if (tl_camera_get_gain_range(camera_handle, &gain_min, &gain_max))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    std::cout << "Gain Minimum: " << gain_min << "\n";
    std::cout << "Gain Maximum: " << gain_max << "\n";
    if (gain_max > 0)
    {
        // this camera supports gain, set and get it
        int gain_index;
        //Gain units can vary by camera. Use the helper function to set these for the camera
        if (tl_camera_convert_decibels_to_gain(camera_handle, 6.0, &gain_index))
            return report_error_and_cleanup_resources(tl_camera_get_last_error());
        if (tl_camera_set_gain(camera_handle, gain_index))
            return report_error_and_cleanup_resources(tl_camera_get_last_error());

        double gain_value_dB;
        if (tl_camera_get_gain(camera_handle, &gain_index))
            return report_error_and_cleanup_resources(tl_camera_get_last_error());
        if (tl_camera_convert_gain_to_decibels(camera_handle, gain_index, &gain_value_dB))
            return report_error_and_cleanup_resources(tl_camera_get_last_error());
        std::cout << "Gain Index: " << gain_index << "  Gain Value in dB: " << gain_value_dB << "\n";
    }

    //Check if camera supports adjusting black level and check range
    int black_level_min;
    int black_level_max;
    if (tl_camera_get_black_level_range(camera_handle, &black_level_min, &black_level_max))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    std::cout << "Black Level Minimum: " << black_level_min << "\n";
    std::cout << "Black Level Maximum: " << black_level_max << "\n";
    if (black_level_max > 0)
    {
        // this camera supports setting the black level, set and get it
        if (tl_camera_set_black_level(camera_handle, 100))
            return report_error_and_cleanup_resources(tl_camera_get_last_error());

        int black_level;
        if (tl_camera_get_black_level(camera_handle, &black_level))
            return report_error_and_cleanup_resources(tl_camera_get_last_error());
        std::cout << "Black Level: " << black_level << "\n";
    }

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

    //Set ROI and Bin Values
    if (tl_camera_set_roi(camera_handle, 0, 0, 100, 100)) // int upper_left_x_pixels, int upper_left_y_pixels, int lower_right_x_pixels, int lower_right_y_pixels
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    if (tl_camera_set_binx(camera_handle, 1))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    if (tl_camera_set_biny(camera_handle, 1))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());

    //Get ROI and Bin Values
    int binx, biny;
    int upper_left_x_pixels, upper_left_y_pixels, lower_right_x_pixels, lower_right_y_pixels;
    if (tl_camera_get_binx(camera_handle, &binx))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    if (tl_camera_get_biny(camera_handle, &biny))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());
    if (tl_camera_get_roi(camera_handle, &upper_left_x_pixels, &upper_left_y_pixels, &lower_right_x_pixels, &lower_right_y_pixels))
        return report_error_and_cleanup_resources(tl_camera_get_last_error());

    std::cout << "Bin X Value: " << binx << "\n";
    std::cout << "Bin Y Value: " << biny << "\n";
    std::cout << "ROI Values - Upper Left X: " << upper_left_x_pixels << " Upper Left Y: " << upper_left_y_pixels << " Lower Right X: " << lower_right_x_pixels << " Lower Right Y: " << lower_right_y_pixels << "\n";

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
    strcpy_s(first_camera, 256, camera_ids);
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
