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
    'get_merge_info'
]
