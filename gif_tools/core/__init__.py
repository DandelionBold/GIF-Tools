"""
Core GIF processing modules.

This module contains all the main GIF processing tools and functions.
"""

from .video_to_gif import *
from .resize import *
from .rotate import *
from .crop import *
from .split import *
from .merge import *
from .free_play import *
from .rearrange import *
from .reverse import *
from .optimize import *
from .speed_control import *
from .filter_effects import *
from .extract_frames import *
from .loop_settings import *
from .format_conversion import *
from .batch_processing import *
from .watermark import *

__all__ = [
    # Video to GIF
    'VideoToGifConverter',
    'convert_video_to_gif',
    'convert_video_to_gif_with_preview',
    'get_video_info',
    
    # Resize
    'GifResizer',
    'resize_gif',
    'resize_gif_by_percentage',
    'resize_gif_to_fit',
    'resize_gif_to_fill',
    'get_resize_info',
    
    # Rotate
    'GifRotator',
    'rotate_gif',
    'rotate_gif_clockwise',
    'rotate_gif_counterclockwise',
    'rotate_gif_180',
    'flip_gif_horizontal',
    'flip_gif_vertical',
    'get_rotation_info',
    
    # Crop
    'GifCropper',
    'crop_gif',
    'crop_gif_center',
    'crop_gif_square',
    'crop_gif_aspect_ratio',
    'get_crop_info',
    
    # Split
    'GifSplitter',
    'split_gif',
    'split_gif_to_images',
    'split_gif_with_info',
    'get_split_info',
    
    # Merge
    'GifMerger',
    'merge_gifs',
    'merge_gifs_horizontal',
    'merge_gifs_vertical',
    'merge_gifs_with_timing',
    'get_merge_info',
    
    # Free Play
    'layer_gifs_free_play',
    'create_gif_layer',
    
    # Rearrange
    'GifRearranger',
    'rearrange_gif_frames',
    'move_gif_frame',
    'move_gif_frames',
    'duplicate_gif_frame',
    'remove_gif_frames',
    'get_gif_frame_info',
    
    # Reverse
    'GifReverser',
    'reverse_gif',
    'reverse_gif_with_info',
    'get_reverse_info',
    
    # Optimize
    'GifOptimizer',
    'optimize_gif',
    'optimize_gif_by_quality',
    'optimize_gif_with_info',
    'get_optimization_info',
    
    # Speed Control
    'GifSpeedController',
    'change_gif_speed',
    'slow_down_gif',
    'speed_up_gif',
    'set_gif_speed_preset',
    'set_gif_frame_durations',
    'get_gif_speed_info',
    
    # Filter Effects
    'GifFilterApplier',
    'apply_gif_filter',
    'apply_gif_filters',
    'adjust_gif_brightness',
    'adjust_gif_contrast',
    'apply_gif_color_effect',
    'get_gif_filter_info',
    
    # Extract Frames
    'GifFrameExtractor',
    'extract_gif_frames',
    'extract_gif_frame_range',
    'extract_every_nth_gif_frame',
    'extract_gif_key_frames',
    'get_gif_extraction_info',
    
    # Loop Settings
    'GifLoopController',
    'set_gif_loop_count',
    'set_gif_infinite_loop',
    'set_gif_no_loop',
    'set_gif_loop_behavior',
    'get_gif_loop_info',
    
    # Format Conversion
    'GifFormatConverter',
    'convert_gif_format',
    'convert_gif_to_webp',
    'convert_gif_to_apng',
    'convert_to_gif',
    'get_gif_conversion_info',
    
    # Batch Processing
    'GifBatchProcessor',
    'process_gif_batch',
    'resize_gif_batch',
    'optimize_gif_batch',
    'convert_format_gif_batch',
    'add_text_gif_batch',
    'custom_gif_batch',
    'get_gif_batch_info',
    
    # Watermark
    'GifWatermarker',
    'add_text_watermark_to_gif',
    'add_image_watermark_to_gif',
    'add_multiple_watermarks_to_gif',
    'get_gif_watermark_info'
]
