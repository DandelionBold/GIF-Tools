"""
Constants and configuration for GIF-Tools.

This module contains all the constants, default values, and configuration
settings used throughout the GIF-Tools library.
"""

from typing import Dict, List, Tuple

# Version information
__version__ = "0.1.0"

# Supported file formats
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
SUPPORTED_IMAGE_FORMATS = ['.gif', '.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']
SUPPORTED_ANIMATED_FORMATS = ['.gif', '.webp', '.apng']

# Default values
DEFAULT_FPS = 10
DEFAULT_QUALITY = 85
DEFAULT_LOOP_COUNT = 0  # 0 means infinite loop
DEFAULT_DURATION = 5.0  # seconds
DEFAULT_SIZE = (640, 480)
DEFAULT_ROTATION_ANGLES = [90, 180, 270]

# File size limits (in bytes)
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB (increased for modern video files)
MAX_FRAME_COUNT = 1000
MAX_DIMENSION = 4096

# Quality settings
QUALITY_LEVELS = {
    'low': 60,
    'medium': 75,
    'high': 85,
    'ultra': 95
}

# Speed control settings
SPEED_MULTIPLIERS = {
    'very_slow': 0.25,
    'slow': 0.5,
    'normal': 1.0,
    'fast': 2.0,
    'very_fast': 4.0
}

# Loop behavior settings
LOOP_BEHAVIORS = {
    'infinite': 0,      # Loop forever
    'once': 1,          # Play once
    'twice': 2,         # Play twice
    'custom': None      # Custom loop count
}

# Filter effects
FILTER_EFFECTS = {
    'blur': 'BLUR',
    'sharpen': 'SHARPEN',
    'smooth': 'SMOOTH',
    'smooth_more': 'SMOOTH_MORE',
    'edge_enhance': 'EDGE_ENHANCE',
    'edge_enhance_more': 'EDGE_ENHANCE_MORE',
    'emboss': 'EMBOSS',
    'find_edges': 'FIND_EDGES',
    'contour': 'CONTOUR',
    'detail': 'DETAIL'
}

# Color modes
COLOR_MODES = ['RGB', 'RGBA', 'P', 'L', 'LA']

# Text alignment options
TEXT_ALIGNMENT = {
    'left': 'left',
    'center': 'center',
    'right': 'right',
    'top': 'top',
    'middle': 'middle',
    'bottom': 'bottom'
}

# Watermark positions
WATERMARK_POSITIONS = {
    'top_left': (0, 0),
    'top_right': (1, 0),
    'bottom_left': (0, 1),
    'bottom_right': (1, 1),
    'center': (0.5, 0.5)
}

# Error messages
ERROR_MESSAGES = {
    'file_not_found': 'File not found: {file_path}',
    'invalid_format': 'Unsupported file format: {format}',
    'file_too_large': 'File too large: {size}MB (max: {max_size}MB)',
    'invalid_dimensions': 'Invalid dimensions: {width}x{height}',
    'invalid_angle': 'Invalid rotation angle: {angle} (must be 90, 180, or 270)',
    'invalid_quality': 'Invalid quality level: {quality} (must be 1-100)',
    'invalid_speed': 'Invalid speed multiplier: {speed} (must be > 0)',
    'processing_error': 'Error processing file: {error}',
    'memory_error': 'Insufficient memory to process file',
    'permission_error': 'Permission denied: {file_path}'
}

# Success messages
SUCCESS_MESSAGES = {
    'conversion_complete': 'Conversion completed successfully',
    'processing_complete': 'Processing completed successfully',
    'file_saved': 'File saved successfully: {file_path}',
    'batch_complete': 'Batch processing completed: {count} files processed'
}

# Default font settings
DEFAULT_FONT = {
    'family': 'Arial',
    'size': 24,
    'color': (255, 255, 255),  # White
    'bold': False,
    'italic': False
}

# Default watermark settings
DEFAULT_WATERMARK = {
    'opacity': 0.7,
    'position': 'bottom_right',
    'margin': 10,
    'scale': 1.0
}

# Batch processing settings
BATCH_SETTINGS = {
    'max_workers': 4,
    'chunk_size': 10,
    'progress_update_interval': 1.0  # seconds
}

# Performance settings
PERFORMANCE_SETTINGS = {
    'memory_limit': 512 * 1024 * 1024,  # 512MB
    'temp_dir': None,  # Will be set to system temp directory
    'cleanup_temp': True,
    'parallel_processing': True
}

# Logging configuration
LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
DEFAULT_LOG_LEVEL = 'INFO'

# API endpoints (for future web API)
API_ENDPOINTS = {
    'health': '/health',
    'convert': '/convert',
    'resize': '/resize',
    'rotate': '/rotate',
    'crop': '/crop',
    'split': '/split',
    'merge': '/merge',
    'add_text': '/add-text',
    'rearrange': '/rearrange',
    'reverse': '/reverse',
    'optimize': '/optimize',
    'speed_control': '/speed-control',
    'filter_effects': '/filter-effects',
    'extract_frames': '/extract-frames',
    'loop_settings': '/loop-settings',
    'format_conversion': '/format-conversion',
    'batch_processing': '/batch-processing',
    'watermark': '/watermark'
}

# HTTP status codes
HTTP_STATUS = {
    'OK': 200,
    'CREATED': 201,
    'BAD_REQUEST': 400,
    'UNAUTHORIZED': 401,
    'FORBIDDEN': 403,
    'NOT_FOUND': 404,
    'UNPROCESSABLE_ENTITY': 422,
    'INTERNAL_SERVER_ERROR': 500
}

# File type MIME types
MIME_TYPES = {
    '.gif': 'image/gif',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.bmp': 'image/bmp',
    '.tiff': 'image/tiff',
    '.webp': 'image/webp',
    '.mp4': 'video/mp4',
    '.avi': 'video/x-msvideo',
    '.mov': 'video/quicktime',
    '.mkv': 'video/x-matroska',
    '.wmv': 'video/x-ms-wmv',
    '.flv': 'video/x-flv',
    '.webm': 'video/webm',
    '.m4v': 'video/x-m4v'
}

# Validation patterns
VALIDATION_PATTERNS = {
    'filename': r'^[a-zA-Z0-9._-]+$',
    'hex_color': r'^#[0-9A-Fa-f]{6}$',
    'rgb_color': r'^\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$',
    'dimensions': r'^\d+x\d+$'
}

# Default crop settings
DEFAULT_CROP = {
    'x': 0,
    'y': 0,
    'width': None,  # Will be calculated
    'height': None  # Will be calculated
}

# Default resize settings
DEFAULT_RESIZE = {
    'width': None,
    'height': None,
    'maintain_aspect_ratio': True,
    'resample': 'LANCZOS'
}

# Default merge settings
DEFAULT_MERGE = {
    'direction': 'horizontal',  # 'horizontal' or 'vertical'
    'spacing': 0,
    'background_color': (0, 0, 0, 0),  # Transparent
    'align': 'center'
}

# Default split settings
DEFAULT_SPLIT = {
    'output_format': 'png',
    'naming_pattern': 'frame_{index:04d}',
    'include_metadata': True
}

# Default text settings
DEFAULT_TEXT = {
    'font_family': 'Arial',
    'font_size': 24,
    'color': (255, 255, 255),
    'position': (10, 10),
    'alignment': 'left',
    'background_color': None,
    'background_opacity': 0.0,
    'stroke_width': 0,
    'stroke_color': (0, 0, 0)
}

# Default optimization settings
DEFAULT_OPTIMIZATION = {
    'optimize': True,
    'method': 6,  # PIL optimization method
    'colors': 256,
    'dither': 'FLOYDSTEINBERG',
    'transparency': True,
    'interlace': False
}

# Default speed control settings
DEFAULT_SPEED_CONTROL = {
    'multiplier': 1.0,
    'min_duration': 0.01,  # Minimum frame duration in seconds
    'max_duration': 10.0   # Maximum frame duration in seconds
}

# Default loop settings
DEFAULT_LOOP_SETTINGS = {
    'loop_count': 0,  # 0 means infinite
    'loop_delay': 0,  # Delay between loops in seconds
    'disposal': 2     # PIL disposal method
}

# Default watermark settings
DEFAULT_WATERMARK_SETTINGS = {
    'opacity': 0.7,
    'position': 'bottom_right',
    'margin': 10,
    'scale': 1.0,
    'tile': False,
    'tile_spacing': 50
}

# Default batch processing settings
DEFAULT_BATCH_SETTINGS = {
    'input_directory': None,
    'output_directory': None,
    'recursive': True,
    'file_pattern': '*',
    'max_workers': 4,
    'progress_callback': None,
    'error_callback': None
}

# Export all constants
__all__ = [
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
    'LOOP_BEHAVIORS',
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
    'DEFAULT_BATCH_SETTINGS'
]
