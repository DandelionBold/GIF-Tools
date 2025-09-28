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
from .add_text import *
from .rearrange import *
from .reverse import *
from .optimize import *
from .speed_control import *
from .filter_effects import *

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
    
    # Add Text
    'GifTextAdder',
    'add_text_to_gif',
    'add_multiple_text_to_gif',
    'add_animated_text_to_gif',
    'get_text_info',
    
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
    'get_gif_filter_info'
]
