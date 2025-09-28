"""
Tool Panels Package

Contains GUI panels for all GIF processing tools.
"""

from .resize_panel import ResizePanel
from .add_text_panel import AddTextPanel
from .video_to_gif_panel import VideoToGifPanel
from .rotate_panel import RotatePanel
from .crop_panel import CropPanel
from .split_panel import SplitPanel
from .merge_panel import MergePanel
from .reverse_panel import ReversePanel
from .optimize_panel import OptimizePanel

__all__ = [
    'ResizePanel',
    'AddTextPanel',
    'VideoToGifPanel',
    'RotatePanel',
    'CropPanel',
    'SplitPanel',
    'MergePanel',
    'ReversePanel',
    'OptimizePanel',
]
