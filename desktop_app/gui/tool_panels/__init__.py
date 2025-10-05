"""
Tool Panels Package

Contains GUI panels for all GIF processing tools.
"""

from .rearrange_panel import RearrangePanel
from .video_to_gif_panel import VideoToGifPanel
from .free_play_panel import FreePlayPanel
from .reverse_panel import ReversePanel
from .optimize_panel import OptimizePanel
from .speed_control_panel import SpeedControlPanel
from .extract_frames_panel import ExtractFramesPanel
from .combine_frames_panel import CombineFramesPanel
from .loop_settings_panel import LoopSettingsPanel
from .format_conversion_panel import FormatConversionPanel
from .watermark_panel import WatermarkPanel

__all__ = [
    'RearrangePanel',
    'VideoToGifPanel',
    'FreePlayPanel',
    'ReversePanel',
    'OptimizePanel',
    'SpeedControlPanel',
    'ExtractFramesPanel',
    'CombineFramesPanel',
    'LoopSettingsPanel',
    'FormatConversionPanel',
    'WatermarkPanel',
]
