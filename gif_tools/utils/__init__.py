"""
Utility modules for GIF processing.

This module contains helper functions, file handlers, and common utilities
used throughout the GIF-Tools library.
"""

from .constants import *
from .validation import *
from .file_handlers import *
from .image_utils import *

__all__ = [
    # Constants
    'SUPPORTED_VIDEO_FORMATS',
    'SUPPORTED_IMAGE_FORMATS',
    'SUPPORTED_ANIMATED_FORMATS',
    'DEFAULT_FPS',
    'DEFAULT_QUALITY',
    'DEFAULT_LOOP_COUNT',
    'DEFAULT_DURATION',
    'DEFAULT_SIZE',
    'DEFAULT_ROTATION_ANGLES',
    'MAX_FILE_SIZE',
    'MAX_FRAME_COUNT',
    'MAX_DIMENSION',
    'QUALITY_LEVELS',
    'SPEED_MULTIPLIERS',
    'FILTER_EFFECTS',
    'COLOR_MODES',
    'TEXT_ALIGNMENT',
    'WATERMARK_POSITIONS',
    'ERROR_MESSAGES',
    'SUCCESS_MESSAGES',
    'DEFAULT_FONT',
    'DEFAULT_WATERMARK',
    'BATCH_SETTINGS',
    'PERFORMANCE_SETTINGS',
    'LOG_LEVELS',
    'DEFAULT_LOG_LEVEL',
    'API_ENDPOINTS',
    'HTTP_STATUS',
    'MIME_TYPES',
    'VALIDATION_PATTERNS',
    'DEFAULT_CROP',
    'DEFAULT_RESIZE',
    'DEFAULT_MERGE',
    'DEFAULT_SPLIT',
    'DEFAULT_TEXT',
    'DEFAULT_OPTIMIZATION',
    'DEFAULT_SPEED_CONTROL',
    'DEFAULT_LOOP_SETTINGS',
    'DEFAULT_WATERMARK_SETTINGS',
    'DEFAULT_BATCH_SETTINGS',
    
    # Validation
    'ValidationError',
    'validate_file_path',
    'validate_file_format',
    'validate_file_size',
    'validate_dimensions',
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
    'validate_dimensions_string',
    
    # File handlers
    'FileHandler',
    'get_file_handler',
    'create_temp_file',
    'create_temp_dir',
    'cleanup_temp_files',
    'get_file_extension',
    'get_mime_type',
    'is_supported_file',
    'get_supported_extensions',
    
    # Image utils
    'ImageProcessor',
    'get_image_processor',
    'load_image',
    'save_image',
    'get_image_info',
    'resize_image',
    'crop_image',
    'rotate_image',
    'add_text',
    'add_watermark'
]
