"""
Validation utilities for GIF-Tools.

This module provides input validation, error handling, and data validation
functions used throughout the GIF-Tools library.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .constants import (
    ERROR_MESSAGES,
    MAX_DIMENSION,
    MAX_FILE_SIZE,
    MAX_FRAME_COUNT,
    SUPPORTED_ANIMATED_FORMATS,
    SUPPORTED_IMAGE_FORMATS,
    SUPPORTED_VIDEO_FORMATS,
    VALIDATION_PATTERNS,
)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """
    Validate that a file path exists and is accessible.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Path object if valid
        
    Raises:
        ValidationError: If file doesn't exist or is not accessible
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise ValidationError(
                ERROR_MESSAGES['file_not_found'].format(file_path=str(path))
            )
        if not path.is_file():
            raise ValidationError(f"Path is not a file: {path}")
        if not os.access(path, os.R_OK):
            raise ValidationError(
                ERROR_MESSAGES['permission_error'].format(file_path=str(path))
            )
        return path
    except (OSError, ValueError) as e:
        raise ValidationError(f"Invalid file path: {e}")


def validate_file_format(file_path: Union[str, Path], 
                        supported_formats: List[str]) -> str:
    """
    Validate that a file has a supported format.
    
    Args:
        file_path: Path to the file to validate
        supported_formats: List of supported file extensions
        
    Returns:
        File extension if valid
        
    Raises:
        ValidationError: If file format is not supported
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    
    if extension not in supported_formats:
        raise ValidationError(
            ERROR_MESSAGES['invalid_format'].format(format=extension)
        )
    
    return extension


def validate_file_size(file_path: Union[str, Path], 
                      max_size: int = MAX_FILE_SIZE) -> int:
    """
    Validate that a file size is within limits.
    
    Args:
        file_path: Path to the file to validate
        max_size: Maximum allowed file size in bytes
        
    Returns:
        File size in bytes if valid
        
    Raises:
        ValidationError: If file is too large
    """
    path = Path(file_path)
    file_size = path.stat().st_size
    
    if file_size > max_size:
        size_mb = file_size / (1024 * 1024)
        max_size_mb = max_size / (1024 * 1024)
        raise ValidationError(
            ERROR_MESSAGES['file_too_large'].format(
                size=round(size_mb, 2),
                max_size=round(max_size_mb, 2)
            )
        )
    
    return file_size


def validate_dimensions(width: int, height: int) -> Tuple[int, int]:
    """
    Validate image dimensions.
    
    Args:
        width: Image width
        height: Image height
        
    Returns:
        Tuple of (width, height) if valid
        
    Raises:
        ValidationError: If dimensions are invalid
    """
    if not isinstance(width, int) or not isinstance(height, int):
        raise ValidationError("Dimensions must be integers")
    
    if width <= 0 or height <= 0:
        raise ValidationError("Dimensions must be positive")
    
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValidationError(
            ERROR_MESSAGES['invalid_dimensions'].format(
                width=width, height=height
            )
        )
    
    return width, height


def validate_size(size: Union[Tuple[int, int], Tuple[float, float]]) -> Tuple[int, int]:
    """
    Validate size tuple (width, height).
    
    Args:
        size: Tuple of (width, height)
        
    Returns:
        Tuple of (width, height) as integers if valid
        
    Raises:
        ValidationError: If size is invalid
    """
    if not isinstance(size, (tuple, list)) or len(size) != 2:
        raise ValidationError("Size must be a tuple or list of 2 elements")
    
    width, height = size
    
    # Convert to integers if they're floats
    try:
        width = int(width)
        height = int(height)
    except (ValueError, TypeError):
        raise ValidationError("Size dimensions must be numeric")
    
    return validate_dimensions(width, height)


def validate_rotation_angle(angle: int) -> int:
    """
    Validate rotation angle.
    
    Args:
        angle: Rotation angle in degrees
        
    Returns:
        Angle if valid
        
    Raises:
        ValidationError: If angle is invalid
    """
    if angle not in [90, 180, 270]:
        raise ValidationError(
            ERROR_MESSAGES['invalid_angle'].format(angle=angle)
        )
    
    return angle


def validate_quality(quality: int) -> int:
    """
    Validate quality setting.
    
    Args:
        quality: Quality value (1-100)
        
    Returns:
        Quality if valid
        
    Raises:
        ValidationError: If quality is invalid
    """
    if not isinstance(quality, int) or quality < 1 or quality > 100:
        raise ValidationError(
            ERROR_MESSAGES['invalid_quality'].format(quality=quality)
        )
    
    return quality


def validate_speed_multiplier(speed: float) -> float:
    """
    Validate speed multiplier.
    
    Args:
        speed: Speed multiplier value
        
    Returns:
        Speed if valid
        
    Raises:
        ValidationError: If speed is invalid
    """
    if not isinstance(speed, (int, float)) or speed <= 0:
        raise ValidationError(
            ERROR_MESSAGES['invalid_speed'].format(speed=speed)
        )
    
    return float(speed)


def validate_color(color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:
    """
    Validate color value.
    
    Args:
        color: Color as hex string, RGB tuple, or RGBA tuple
        
    Returns:
        RGBA tuple if valid
        
    Raises:
        ValidationError: If color is invalid
    """
    if isinstance(color, str):
        # Hex color
        if not re.match(VALIDATION_PATTERNS['hex_color'], color):
            raise ValidationError(f"Invalid hex color: {color}")
        
        # Convert hex to RGB
        hex_color = color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, 255)
    
    elif isinstance(color, tuple):
        if len(color) == 3:
            # RGB tuple
            r, g, b = color
            if not all(0 <= c <= 255 for c in [r, g, b]):
                raise ValidationError(f"Invalid RGB color: {color}")
            return (r, g, b, 255)
        elif len(color) == 4:
            # RGBA tuple
            r, g, b, a = color
            if not all(0 <= c <= 255 for c in [r, g, b, a]):
                raise ValidationError(f"Invalid RGBA color: {color}")
            return (r, g, b, a)
        else:
            raise ValidationError(f"Invalid color tuple length: {color}")
    
    else:
        raise ValidationError(f"Invalid color type: {type(color)}")


def validate_position(position: Union[Tuple[int, int], Tuple[float, float]]) -> Tuple[int, int]:
    """
    Validate position coordinates.
    
    Args:
        position: Position as (x, y) tuple
        
    Returns:
        Position tuple if valid
        
    Raises:
        ValidationError: If position is invalid
    """
    if not isinstance(position, tuple) or len(position) != 2:
        raise ValidationError(f"Position must be a tuple of (x, y): {position}")
    
    x, y = position
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise ValidationError(f"Position coordinates must be numbers: {position}")
    
    if x < 0 or y < 0:
        raise ValidationError(f"Position coordinates must be non-negative: {position}")
    
    return (int(x), int(y))


def validate_crop_coordinates(x: int, y: int, width: int, height: int, 
                            image_width: int, image_height: int) -> Tuple[int, int, int, int]:
    """
    Validate crop coordinates.
    
    Args:
        x: Left coordinate
        y: Top coordinate
        width: Crop width
        height: Crop height
        image_width: Original image width
        image_height: Original image height
        
    Returns:
        Tuple of (x, y, width, height) if valid
        
    Raises:
        ValidationError: If crop coordinates are invalid
    """
    if x < 0 or y < 0:
        raise ValidationError("Crop coordinates must be non-negative")
    
    if width <= 0 or height <= 0:
        raise ValidationError("Crop dimensions must be positive")
    
    if x + width > image_width or y + height > image_height:
        raise ValidationError(
            f"Crop area exceeds image bounds: "
            f"({x}, {y}, {width}, {height}) vs ({image_width}, {image_height})"
        )
    
    return x, y, width, height


def validate_fps(fps: Union[int, float]) -> float:
    """
    Validate frames per second value.
    
    Args:
        fps: Frames per second
        
    Returns:
        FPS if valid
        
    Raises:
        ValidationError: If FPS is invalid
    """
    if not isinstance(fps, (int, float)) or fps <= 0:
        raise ValidationError(f"FPS must be a positive number: {fps}")
    
    if fps > 120:
        raise ValidationError(f"FPS too high (max 120): {fps}")
    
    return float(fps)


def validate_duration(duration: Union[int, float]) -> float:
    """
    Validate duration value.
    
    Args:
        duration: Duration in seconds
        
    Returns:
        Duration if valid
        
    Raises:
        ValidationError: If duration is invalid
    """
    if not isinstance(duration, (int, float)) or duration <= 0:
        raise ValidationError(f"Duration must be a positive number: {duration}")
    
    if duration > 3600:  # 1 hour max
        raise ValidationError(f"Duration too long (max 3600 seconds): {duration}")
    
    return float(duration)


def validate_frame_count(frame_count: int) -> int:
    """
    Validate frame count.
    
    Args:
        frame_count: Number of frames
        
    Returns:
        Frame count if valid
        
    Raises:
        ValidationError: If frame count is invalid
    """
    if not isinstance(frame_count, int) or frame_count <= 0:
        raise ValidationError(f"Frame count must be a positive integer: {frame_count}")
    
    if frame_count > MAX_FRAME_COUNT:
        raise ValidationError(f"Frame count too high (max {MAX_FRAME_COUNT}): {frame_count}")
    
    return frame_count


def validate_output_path(output_path: Union[str, Path], 
                        create_dirs: bool = True) -> Path:
    """
    Validate output path and create directories if needed.
    
    Args:
        output_path: Path for output file
        create_dirs: Whether to create parent directories
        
    Returns:
        Path object if valid
        
    Raises:
        ValidationError: If path is invalid
    """
    try:
        path = Path(output_path)
        
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if parent directory is writable
        if not os.access(path.parent, os.W_OK):
            raise ValidationError(f"Output directory not writable: {path.parent}")
        
        return path
    except (OSError, ValueError) as e:
        raise ValidationError(f"Invalid output path: {e}")


def validate_batch_input(input_paths: List[Union[str, Path]]) -> List[Path]:
    """
    Validate batch input paths.
    
    Args:
        input_paths: List of input file paths
        
    Returns:
        List of valid Path objects
        
    Raises:
        ValidationError: If any path is invalid
    """
    if not input_paths:
        raise ValidationError("No input files provided")
    
    if len(input_paths) > 100:  # Reasonable batch limit
        raise ValidationError(f"Too many files in batch (max 100): {len(input_paths)}")
    
    valid_paths = []
    for path in input_paths:
        valid_path = validate_file_path(path)
        valid_paths.append(valid_path)
    
    return valid_paths


def validate_parameters(params: Dict[str, Any], 
                       required: List[str], 
                       optional: List[str] = None) -> Dict[str, Any]:
    """
    Validate function parameters.
    
    Args:
        params: Dictionary of parameters
        required: List of required parameter names
        optional: List of optional parameter names
        
    Returns:
        Validated parameters dictionary
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(params, dict):
        raise ValidationError("Parameters must be a dictionary")
    
    # Check required parameters
    missing = [param for param in required if param not in params]
    if missing:
        raise ValidationError(f"Missing required parameters: {missing}")
    
    # Check for unknown parameters
    all_params = required + (optional or [])
    unknown = [param for param in params.keys() if param not in all_params]
    if unknown:
        raise ValidationError(f"Unknown parameters: {unknown}")
    
    return params


def validate_image_file(file_path: Union[str, Path]) -> Path:
    """
    Validate that a file is a supported image format.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Path object if valid
        
    Raises:
        ValidationError: If file is not a valid image
    """
    path = validate_file_path(file_path)
    validate_file_format(path, SUPPORTED_IMAGE_FORMATS)
    validate_file_size(path)
    return path


def validate_video_file(file_path: Union[str, Path]) -> Path:
    """
    Validate that a file is a supported video format.
    
    Args:
        file_path: Path to the video file
        
    Returns:
        Path object if valid
        
    Raises:
        ValidationError: If file is not a valid video
    """
    path = validate_file_path(file_path)
    validate_file_format(path, SUPPORTED_VIDEO_FORMATS)
    validate_file_size(path)
    return path


def validate_animated_file(file_path: Union[str, Path]) -> Path:
    """
    Validate that a file is a supported animated format.
    
    Args:
        file_path: Path to the animated file
        
    Returns:
        Path object if valid
        
    Raises:
        ValidationError: If file is not a valid animated format
    """
    path = validate_file_path(file_path)
    validate_file_format(path, SUPPORTED_ANIMATED_FORMATS)
    validate_file_size(path)
    return path


def validate_hex_color(hex_color: str) -> str:
    """
    Validate hex color format.
    
    Args:
        hex_color: Hex color string (e.g., '#FF0000')
        
    Returns:
        Hex color if valid
        
    Raises:
        ValidationError: If hex color is invalid
    """
    if not isinstance(hex_color, str):
        raise ValidationError("Hex color must be a string")
    
    if not re.match(VALIDATION_PATTERNS['hex_color'], hex_color):
        raise ValidationError(f"Invalid hex color format: {hex_color}")
    
    return hex_color.upper()


def validate_dimensions_string(dimensions: str) -> Tuple[int, int]:
    """
    Validate dimensions string format (e.g., '640x480').
    
    Args:
        dimensions: Dimensions string
        
    Returns:
        Tuple of (width, height) if valid
        
    Raises:
        ValidationError: If dimensions string is invalid
    """
    if not isinstance(dimensions, str):
        raise ValidationError("Dimensions must be a string")
    
    if not re.match(VALIDATION_PATTERNS['dimensions'], dimensions):
        raise ValidationError(f"Invalid dimensions format: {dimensions}")
    
    try:
        width, height = map(int, dimensions.split('x'))
        return validate_dimensions(width, height)
    except ValueError:
        raise ValidationError(f"Invalid dimensions format: {dimensions}")


# Export all validation functions
__all__ = [
    'ValidationError',
    'validate_file_path',
    'validate_file_format',
    'validate_file_size',
    'validate_dimensions',
    'validate_size',
    'validate_rotation_angle',
    'validate_quality',
    'validate_speed_multiplier',
    'validate_color',
    'validate_position',
    'validate_crop_coordinates',
    'validate_fps',
    'validate_duration',
    'validate_frame_count',
    'validate_output_path',
    'validate_batch_input',
    'validate_parameters',
    'validate_image_file',
    'validate_video_file',
    'validate_animated_file',
    'validate_hex_color',
    'validate_dimensions_string'
]
