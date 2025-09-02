# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Python implementation of Thorlabs Scientific Camera examples. The code demonstrates camera control functionality including software triggering, continuous frame capture, and MP4 video recording using the Thorlabs TSI SDK.

## Development Guidelines

**IMPORTANT**: When making any code changes or additions:
- Base all coding decisions on the Thorlabs official examples in this directory
- Refer to the official Thorlabs Camera Python API Reference at `/Users/woojins/Documents/GitHub/Camera_Examples/Python/Thorlabs_Camera_Python_API_Reference.pdf`
- Follow the patterns and conventions established in the existing official examples
- Use only the APIs and methods documented in the official reference

## CW ODMR Experiment Setup

**CRITICAL**: For the CW ODMR experiment:
- **SynthHD Configuration**: The Windfreak SynthHD is pre-configured to "single step per trigger" mode
- **No SynthHD Control Needed in Code**: When SDG2082x CH.1 sends a trigger pulse, the SynthHD automatically advances to the next frequency step (50MHz increment)
- **Synchronization**: Each SDG trigger simultaneously:
  1. Triggers camera to capture one frame (20ms exposure)
  2. Triggers SynthHD to advance to next frequency step
- **Frame-Frequency Matching**: Frame N corresponds to frequency = 3.000 + ((N-1) % 20) × 0.050 GHz
- **No Manual SynthHD Programming Required**: The hardware is pre-configured externally

## Architecture

The Python examples use the Thorlabs TSI SDK with OpenCV for image processing and display:
- **thorlabs_tsi_sdk.tl_camera**: Core camera control and frame acquisition
- **thorlabs_tsi_sdk.tl_mono_to_color_processor**: Color processing for Bayer sensor cameras
- **opencv-python**: Image display and MP4 video writing
- **numpy**: Array manipulation for image data

All examples depend on the Thorlabs TSI Camera SDK Python package and native DLLs.

## Setup and Installation

### Required Dependencies
```bash
# Install Thorlabs Python SDK (from ThorCam installation)
python -m pip install thorlabs_tsi_camera_python_sdk_package.zip

# Install additional Python packages
pip install opencv-python numpy

# If requirements.txt exists in ThorCam SDK examples
pip install -r requirements.txt
```

### DLL Setup (Windows)
1. Copy Native DLLs from ThorCam installation:
   - Source: `\Scientific Camera Interfaces\SDK\Native Toolkit\dlls\Native_64_lib`
   - Destination: `./dlls/64_lib/` (relative to Python scripts)
2. The `windows_setup.py` script handles DLL path configuration automatically

### Running Examples
```bash
# Single frame capture with display
python grab_single_frame.py

# Continuous frame capture (Ctrl+C to stop)
python grab_frames_polling_continuous.py

# Record MP4 video (200 frames)
python opencv_mp4_writer_example.py
```

## SDK Dependencies

### Thorlabs Scientific Camera SDK
- **Installation**: Download and install ThorCam software package from Thorlabs
- **Location**: `Program Files\Thorlabs\Scientific Imaging\Scientific Camera Support\`
- **Archive**: Extract `Scientific Camera Interfaces.zip`
- **Python Package**: `SDK\Python Toolkit\thorlabs_tsi_camera_python_sdk_package.zip`
- **Native DLLs**: `SDK\Native Toolkit\dlls\Native_64_lib\` → copy to `./dlls/64_lib/`

### Python Dependencies
- **thorlabs_tsi_sdk**: Main camera control SDK
- **opencv-python**: Image processing and video writing
- **numpy**: Array operations for image data

## Available Examples

### grab_single_frame.py
- Initializes first detected camera
- Sets 10ms exposure time and continuous mode
- Captures single frame with software trigger
- Displays image using OpenCV (grayscale converted to RGB)
- Key pattern: SDK context manager, software triggering, OpenCV display

### grab_frames_polling_continuous.py
- Continuous frame capture with 10 FPS frame rate control
- Polls for frames in infinite loop (Ctrl+C to exit)
- Real-time OpenCV display with frame counting
- Key pattern: Continuous acquisition, polling, frame rate control

### opencv_mp4_writer_example.py
- Records 200 frames to `video.mp4` file
- Supports both monochrome and color (Bayer) cameras
- Automatic color processing for Bayer sensors (BGR format)
- Scales bit depth to 8-bit for MP4 compatibility
- Key pattern: Video recording, color processing, proper resource cleanup

## Key Programming Patterns

### SDK Context Management
```python
with TLCameraSDK() as sdk:
    with sdk.open_camera(camera_id) as camera:
        # Camera operations here
        pass
# Automatic cleanup handled by context managers
```

### Frame Acquisition
```python
camera.arm(2)  # Arm camera with 2-frame buffer
camera.issue_software_trigger()
frame = camera.get_pending_frame_or_null()
if frame is not None:
    image_data = np.copy(frame.image_buffer)
```

### Image Data Handling
- Raw data comes as 1D array, reshape using camera dimensions
- Convert to OpenCV format (BGR for color, grayscale to RGB for display)
- Handle bit depth scaling for 8-bit outputs

### Windows DLL Loading
- Import and call `windows_setup.configure_path()` before SDK imports
- Handles both 32-bit and 64-bit DLL detection
- Gracefully handles non-Windows platforms

## Common Camera Parameters

- `camera.exposure_time_us`: Exposure time in microseconds
- `camera.frames_per_trigger_zero_for_unlimited`: 0 for continuous mode
- `camera.image_poll_timeout_ms`: Frame polling timeout
- `camera.frame_rate_control_value`: Target frame rate
- `camera.is_frame_rate_control_enabled`: Enable/disable frame rate limiting
- `camera.image_width_pixels`, `camera.image_height_pixels`: Image dimensions
- `camera.bit_depth`: Sensor bit depth
- `camera.camera_sensor_type`: SENSOR_TYPE.BAYER for color cameras

## Testing

Testing requires physical Thorlabs camera hardware:
1. Connect camera via USB
2. Ensure ThorCam software can detect the camera
3. Run Python examples to verify SDK integration
4. Check OpenCV display windows and generated MP4 files