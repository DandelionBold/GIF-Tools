"""
Tool Panels Package

Contains GUI panels for all GIF processing tools.
"""

from .rearrange_panel import RearrangePanel
from .video_to_gif_panel import VideoToGifPanel
from .resize_panel import ResizePanel
from .rotate_panel import RotatePanel
from .crop_panel import CropPanel
from .split_panel import SplitPanel
from .merge_panel import MergePanel
from .free_play_panel import FreePlayPanel
from .reverse_panel import ReversePanel
from .optimize_panel import OptimizePanel
from .speed_control_panel import SpeedControlPanel
from .filter_effects_panel import FilterEffectsPanel
from .extract_frames_panel import ExtractFramesPanel
from .combine_frames_panel import CombineFramesPanel
from .loop_settings_panel import LoopSettingsPanel
from .format_conversion_panel import FormatConversionPanel
from .watermark_panel import WatermarkPanel

__all__ = [
    'RearrangePanel',
    'VideoToGifPanel',
    'ResizePanel',
    'RotatePanel',
    'CropPanel',
    'SplitPanel',
    'MergePanel',
    'FreePlayPanel',
    'ReversePanel',
    'OptimizePanel',
    'SpeedControlPanel',
    'FilterEffectsPanel',
    'ExtractFramesPanel',
    'CombineFramesPanel',
    'LoopSettingsPanel',
    'FormatConversionPanel',
    'WatermarkPanel',
]
