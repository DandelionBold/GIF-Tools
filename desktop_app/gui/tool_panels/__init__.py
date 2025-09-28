"""
Tool Panels Package

Contains GUI panels for all GIF processing tools.
"""

from .resize_panel import ResizePanel
from .add_text_panel import AddTextPanel
from .video_to_gif_panel import VideoToGifPanel
from .rotate_panel import RotatePanel
from .crop_panel import CropPanel

__all__ = [
    'ResizePanel',
    'AddTextPanel',
    'VideoToGifPanel',
    'RotatePanel',
    'CropPanel',
]
