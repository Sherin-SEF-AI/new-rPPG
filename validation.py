"""
Validation Module
Validation functions for video files and parameters.
"""

import os
import cv2
from typing import Tuple, Optional


def validate_video_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate if a video file is accessible and readable.
    
    Args:
        file_path: Path to the video file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, f"File does not exist: {file_path}"
    
    if not os.path.isfile(file_path):
        return False, f"Path is not a file: {file_path}"
    
    # Check file extension
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext not in valid_extensions:
        return False, f"Unsupported file format: {file_ext}"
    
    # Try to open with OpenCV
    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return False, f"Cannot open video file: {file_path}"
        
        # Check if we can read at least one frame
        ret, frame = cap.read()
        if not ret:
            return False, f"Cannot read frames from video: {file_path}"
        
        cap.release()
        return True, "Video file is valid"
        
    except Exception as e:
        return False, f"Error reading video file: {str(e)}"


def validate_parameters(params: dict) -> Tuple[bool, str]:
    """
    Validate processing parameters.
    
    Args:
        params: Dictionary of parameters
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate FPS
    fps = params.get('fps', 30)
    if not isinstance(fps, (int, float)) or fps < 1 or fps > 120:
        return False, "FPS must be between 1 and 120"
    
    # Validate heart rate range
    min_hr = params.get('min_hr', 40)
    max_hr = params.get('max_hr', 200)
    
    if not isinstance(min_hr, (int, float)) or min_hr < 20 or min_hr > 100:
        return False, "min_hr must be between 20 and 100"
    
    if not isinstance(max_hr, (int, float)) or max_hr < 100 or max_hr > 300:
        return False, "max_hr must be between 100 and 300"
    
    if min_hr >= max_hr:
        return False, "min_hr must be less than max_hr"
    
    # Validate window size
    window_size = params.get('window_size', 300)
    if not isinstance(window_size, int) or window_size < 30 or window_size > 1000:
        return False, "window_size must be between 30 and 1000"
    
    return True, "Parameters are valid"


def validate_camera(camera_index: int = 0) -> Tuple[bool, str]:
    """
    Validate if camera is accessible.
    
    Args:
        camera_index: Camera device index
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            return False, f"Cannot open camera at index {camera_index}"
        
        # Try to read a frame
        ret, frame = cap.read()
        if not ret:
            return False, f"Cannot read frames from camera {camera_index}"
        
        cap.release()
        return True, f"Camera {camera_index} is accessible"
        
    except Exception as e:
        return False, f"Error accessing camera {camera_index}: {str(e)}"


def get_video_info(file_path: str) -> Optional[dict]:
    """
    Get video file information.
    
    Args:
        file_path: Path to video file
        
    Returns:
        Dictionary with video information or None if error
    """
    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return None
        
        info = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0
        }
        
        cap.release()
        return info
        
    except Exception:
        return None 