"""
GIF-Tools: A comprehensive library for GIF processing and manipulation.

This package provides a complete set of tools for working with GIF files,
including conversion, editing, optimization, and various transformations.
"""

__version__ = "0.1.0"
__author__ = "Kamal Nady"
__email__ = "kamalnadykamal@gmail.com"
__license__ = "MIT"

# Import core modules
from .core import (
    video_to_gif,
    resize,
    rotate,
    crop,
    split,
    merge,
    add_text,
    rearrange,
    reverse,
    optimize,
    speed_control,
    filter_effects,
    extract_frames,
    loop_settings,
    format_conversion,
    batch_processing,
    watermark,
)

# Import utility modules
from .utils import (
    file_handlers,
    image_utils,
    validation,
    constants,
)

__all__ = [
    # Core modules
    "video_to_gif",
    "resize",
    "rotate",
    "crop",
    "split",
    "merge",
    "add_text",
    "rearrange",
    "reverse",
    "optimize",
    "speed_control",
    "filter_effects",
    "extract_frames",
    "loop_settings",
    "format_conversion",
    "batch_processing",
    "watermark",
    # Utility modules
    "file_handlers",
    "image_utils",
    "validation",
    "constants",
]
