"""
GIF split module.

This module provides functionality to split GIFs into individual frames
with support for various output formats and naming patterns.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from PIL import Image

from ..utils import (
    DEFAULT_SPLIT,
    SUCCESS_MESSAGES,
    SUPPORTED_IMAGE_FORMATS,
    ValidationError,
    validate_animated_file,
    validate_output_path,
    get_file_handler
)


class GifSplitter:
    """GIF split utility class."""
    
    def __init__(self):
        """Initialize GIF splitter."""
        self.file_handler = get_file_handler()
    
    def split(self,
              input_path: Union[str, Path],
              output_dir: Union[str, Path],
              output_format: str = 'png',
              naming_pattern: str = 'frame_{index:04d}',
              include_metadata: bool = True,
              start_frame: Optional[int] = None,
              end_frame: Optional[int] = None) -> List[Path]:
        """
        Split GIF into individual frames.
        
        Args:
            input_path: Path to input GIF file
            output_dir: Directory to save frames
            output_format: Output format (png, jpg, bmp, etc.)
            naming_pattern: Naming pattern for output files
            include_metadata: Whether to include frame metadata
            start_frame: Start frame index (None for beginning)
            end_frame: End frame index (None for end)
            
        Returns:
            List of output file paths
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if output_format.lower() not in SUPPORTED_IMAGE_FORMATS:
            raise ValidationError(f"Unsupported output format: {output_format}")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Get frame information
                frame_count = getattr(gif, 'n_frames', 1)
                is_animated = getattr(gif, 'is_animated', False)
                
                if not is_animated:
                    # Single frame GIF
                    return self._split_single_frame(gif, output_dir, output_format, naming_pattern)
                
                # Determine frame range
                start_idx = start_frame if start_frame is not None else 0
                end_idx = end_frame if end_frame is not None else frame_count - 1
                
                # Validate frame range
                if start_idx < 0 or end_idx >= frame_count or start_idx > end_idx:
                    raise ValidationError(f"Invalid frame range: {start_idx}-{end_idx}")
                
                # Split frames
                return self._split_frames(
                    gif, output_dir, output_format, naming_pattern,
                    include_metadata, start_idx, end_idx
                )
                
        except Exception as e:
            raise ValidationError(f"GIF split failed: {e}")
    
    def split_to_images(self,
                       input_path: Union[str, Path],
                       output_dir: Union[str, Path],
                       output_format: str = 'png',
                       quality: int = 95) -> List[Path]:
        """
        Split GIF to high-quality images.
        
        Args:
            input_path: Path to input GIF file
            output_dir: Directory to save frames
            output_format: Output format
            quality: Output quality (1-100)
            
        Returns:
            List of output file paths
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if output_format.lower() not in SUPPORTED_IMAGE_FORMATS:
            raise ValidationError(f"Unsupported output format: {output_format}")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                frame_count = getattr(gif, 'n_frames', 1)
                is_animated = getattr(gif, 'is_animated', False)
                
                if not is_animated:
                    # Single frame GIF
                    return self._split_single_frame(gif, output_dir, output_format, 'frame_0000')
                
                # Split all frames
                output_paths = []
                for frame_idx in range(frame_count):
                    gif.seek(frame_idx)
                    
                    # Create output filename
                    output_filename = f"frame_{frame_idx:04d}.{output_format.lower()}"
                    output_path = output_dir / output_filename
                    
                    # Save frame with high quality
                    if output_format.lower() in ['jpg', 'jpeg']:
                        gif.save(output_path, format=output_format.upper(), quality=quality, optimize=True)
                    else:
                        gif.save(output_path, format=output_format.upper(), optimize=True)
                    
                    output_paths.append(output_path)
                
                return output_paths
                
        except Exception as e:
            raise ValidationError(f"GIF split to images failed: {e}")
    
    def split_with_info(self,
                       input_path: Union[str, Path],
                       output_dir: Union[str, Path],
                       output_format: str = 'png') -> Dict[str, Any]:
        """
        Split GIF and return detailed information.
        
        Args:
            input_path: Path to input GIF file
            output_dir: Directory to save frames
            output_format: Output format
            
        Returns:
            Dictionary with split information and file paths
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                frame_count = getattr(gif, 'n_frames', 1)
                is_animated = getattr(gif, 'is_animated', False)
                
                # Split frames
                if is_animated:
                    output_paths = self.split(input_path, output_dir, output_format)
                else:
                    output_paths = self._split_single_frame(gif, output_dir, output_format, 'frame_0000')
                
                # Get frame durations
                durations = []
                if is_animated:
                    for frame_idx in range(frame_count):
                        gif.seek(frame_idx)
                        duration = gif.info.get('duration', 100)  # Default 100ms
                        durations.append(duration)
                else:
                    durations = [100]  # Single frame
                
                return {
                    'input_path': str(input_path),
                    'output_dir': str(output_dir),
                    'output_format': output_format,
                    'frame_count': frame_count,
                    'is_animated': is_animated,
                    'output_files': [str(path) for path in output_paths],
                    'durations': durations,
                    'total_duration': sum(durations) / 1000.0,  # Convert to seconds
                    'gif_info': {
                        'size': gif.size,
                        'mode': gif.mode,
                        'format': gif.format,
                        'loop': gif.info.get('loop', 0)
                    }
                }
                
        except Exception as e:
            raise ValidationError(f"GIF split with info failed: {e}")
    
    def get_split_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get split information for GIF.
        
        Args:
            input_path: Path to input GIF file
            
        Returns:
            Dictionary with split information
        """
        input_path = validate_animated_file(input_path)
        
        try:
            with Image.open(input_path) as gif:
                frame_count = getattr(gif, 'n_frames', 1)
                is_animated = getattr(gif, 'is_animated', False)
                
                # Get frame durations
                durations = []
                if is_animated:
                    for frame_idx in range(frame_count):
                        gif.seek(frame_idx)
                        duration = gif.info.get('duration', 100)
                        durations.append(duration)
                else:
                    durations = [100]
                
                return {
                    'frame_count': frame_count,
                    'is_animated': is_animated,
                    'size': gif.size,
                    'width': gif.width,
                    'height': gif.height,
                    'mode': gif.mode,
                    'format': gif.format,
                    'durations': durations,
                    'total_duration': sum(durations) / 1000.0,
                    'loop': gif.info.get('loop', 0),
                    'supported_formats': SUPPORTED_IMAGE_FORMATS
                }
        except Exception as e:
            raise ValidationError(f"Failed to get split info: {e}")
    
    def _split_single_frame(self, gif: Image.Image, output_dir: Path, 
                           output_format: str, naming_pattern: str) -> List[Path]:
        """
        Split single frame GIF.
        
        Args:
            gif: PIL Image object
            output_dir: Output directory
            output_format: Output format
            naming_pattern: Naming pattern
            
        Returns:
            List of output file paths
        """
        # Create output filename
        output_filename = f"{naming_pattern.format(index=0)}.{output_format.lower()}"
        output_path = output_dir / output_filename
        
        # Save frame
        if output_format.lower() in ['jpg', 'jpeg']:
            gif.save(output_path, format=output_format.upper(), quality=95, optimize=True)
        else:
            gif.save(output_path, format=output_format.upper(), optimize=True)
        
        return [output_path]
    
    def _split_frames(self, gif: Image.Image, output_dir: Path, 
                     output_format: str, naming_pattern: str,
                     include_metadata: bool, start_idx: int, end_idx: int) -> List[Path]:
        """
        Split animated GIF frames.
        
        Args:
            gif: PIL Image object (GIF)
            output_dir: Output directory
            output_format: Output format
            naming_pattern: Naming pattern
            include_metadata: Whether to include metadata
            start_idx: Start frame index
            end_idx: End frame index
            
        Returns:
            List of output file paths
        """
        output_paths = []
        
        for frame_idx in range(start_idx, end_idx + 1):
            gif.seek(frame_idx)
            
            # Create output filename
            output_filename = f"{naming_pattern.format(index=frame_idx)}.{output_format.lower()}"
            output_path = output_dir / output_filename
            
            # Save frame
            if output_format.lower() in ['jpg', 'jpeg']:
                gif.save(output_path, format=output_format.upper(), quality=95, optimize=True)
            else:
                gif.save(output_path, format=output_format.upper(), optimize=True)
            
            output_paths.append(output_path)
        
        return output_paths


def split_gif(input_path: Union[str, Path],
             output_dir: Union[str, Path],
             output_format: str = 'png',
             naming_pattern: str = 'frame_{index:04d}',
             include_metadata: bool = True,
             start_frame: Optional[int] = None,
             end_frame: Optional[int] = None) -> List[Path]:
    """
    Split GIF into individual frames.
    
    Args:
        input_path: Path to input GIF file
        output_dir: Directory to save frames
        output_format: Output format (png, jpg, bmp, etc.)
        naming_pattern: Naming pattern for output files
        include_metadata: Whether to include frame metadata
        start_frame: Start frame index (None for beginning)
        end_frame: End frame index (None for end)
        
    Returns:
        List of output file paths
    """
    splitter = GifSplitter()
    return splitter.split(
        input_path, output_dir, output_format, naming_pattern,
        include_metadata, start_frame, end_frame
    )


def split_gif_to_images(input_path: Union[str, Path],
                       output_dir: Union[str, Path],
                       output_format: str = 'png',
                       quality: int = 95) -> List[Path]:
    """
    Split GIF to high-quality images.
    
    Args:
        input_path: Path to input GIF file
        output_dir: Directory to save frames
        output_format: Output format
        quality: Output quality (1-100)
        
    Returns:
        List of output file paths
    """
    splitter = GifSplitter()
    return splitter.split_to_images(input_path, output_dir, output_format, quality)


def split_gif_with_info(input_path: Union[str, Path],
                       output_dir: Union[str, Path],
                       output_format: str = 'png') -> Dict[str, Any]:
    """
    Split GIF and return detailed information.
    
    Args:
        input_path: Path to input GIF file
        output_dir: Directory to save frames
        output_format: Output format
        
    Returns:
        Dictionary with split information and file paths
    """
    splitter = GifSplitter()
    return splitter.split_with_info(input_path, output_dir, output_format)


def get_split_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get split information for GIF.
    
    Args:
        input_path: Path to input GIF file
        
    Returns:
        Dictionary with split information
    """
    splitter = GifSplitter()
    return splitter.get_split_info(input_path)


# Export all functions and classes
__all__ = [
    'GifSplitter',
    'split_gif',
    'split_gif_to_images',
    'split_gif_with_info',
    'get_split_info'
]
