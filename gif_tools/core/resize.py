"""
GIF resize module.

This module provides functionality to resize GIFs while maintaining aspect ratio
or allowing custom sizing with various resampling methods.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from PIL import Image

from ..utils import (
    DEFAULT_RESIZE,
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_dimensions,
    validate_output_path,
    get_image_processor
)


class GifResizer:
    """GIF resize utility class."""
    
    def __init__(self):
        """Initialize GIF resizer."""
        self.image_processor = get_image_processor()
    
    def resize(self,
               input_path: Union[str, Path],
               output_path: Union[str, Path],
               width: Optional[int] = None,
               height: Optional[int] = None,
               size: Optional[Tuple[int, int]] = None,
               maintain_aspect_ratio: bool = True,
               resample: int = Image.Resampling.LANCZOS,
               quality: int = 85) -> Path:
        """
        Resize GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            width: Target width
            height: Target height
            size: Target size as (width, height) tuple
            maintain_aspect_ratio: Whether to maintain aspect ratio
            resample: Resampling method
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if size:
            width, height = size
        
        if width is None and height is None:
            raise ValidationError("Either width, height, or size must be specified")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Get original dimensions
                original_width, original_height = gif.size
                
                # Calculate new dimensions
                new_width, new_height = self._calculate_dimensions(
                    original_width, original_height, width, height, maintain_aspect_ratio
                )
                
                # Validate new dimensions
                validate_dimensions(new_width, new_height)
                
                # Resize GIF
                resized_gif = self._resize_gif(gif, new_width, new_height, resample)
                
                # Save resized GIF
                self.image_processor.save_image(
                    resized_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF resize failed: {e}")
    
    def resize_by_percentage(self,
                           input_path: Union[str, Path],
                           output_path: Union[str, Path],
                           percentage: float,
                           resample: int = Image.Resampling.LANCZOS,
                           quality: int = 85) -> Path:
        """
        Resize GIF by percentage.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            percentage: Resize percentage (e.g., 0.5 for 50%, 2.0 for 200%)
            resample: Resampling method
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        if percentage <= 0:
            raise ValidationError("Percentage must be positive")
        
        try:
            # Load GIF to get original dimensions
            with Image.open(input_path) as gif:
                original_width, original_height = gif.size
                
                # Calculate new dimensions
                new_width = int(original_width * percentage)
                new_height = int(original_height * percentage)
                
                # Validate new dimensions
                validate_dimensions(new_width, new_height)
                
                # Resize GIF
                resized_gif = self._resize_gif(gif, new_width, new_height, resample)
                
                # Save resized GIF
                self.image_processor.save_image(
                    resized_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF resize by percentage failed: {e}")
    
    def resize_to_fit(self,
                     input_path: Union[str, Path],
                     output_path: Union[str, Path],
                     max_width: int,
                     max_height: int,
                     resample: int = Image.Resampling.LANCZOS,
                     quality: int = 85) -> Path:
        """
        Resize GIF to fit within specified dimensions while maintaining aspect ratio.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            max_width: Maximum width
            max_height: Maximum height
            resample: Resampling method
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        validate_dimensions(max_width, max_height)
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                original_width, original_height = gif.size
                
                # Calculate scale factor to fit within bounds
                scale_x = max_width / original_width
                scale_y = max_height / original_height
                scale = min(scale_x, scale_y)
                
                # Calculate new dimensions
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                
                # Only resize if necessary
                if new_width < original_width or new_height < original_height:
                    resized_gif = self._resize_gif(gif, new_width, new_height, resample)
                else:
                    resized_gif = gif.copy()
                
                # Save GIF
                self.image_processor.save_image(
                    resized_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF resize to fit failed: {e}")
    
    def resize_to_fill(self,
                      input_path: Union[str, Path],
                      output_path: Union[str, Path],
                      width: int,
                      height: int,
                      resample: int = Image.Resampling.LANCZOS,
                      quality: int = 85) -> Path:
        """
        Resize GIF to fill specified dimensions (may crop to maintain aspect ratio).
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            width: Target width
            height: Target height
            resample: Resampling method
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        validate_dimensions(width, height)
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                original_width, original_height = gif.size
                
                # Calculate scale factor to fill dimensions
                scale_x = width / original_width
                scale_y = height / original_height
                scale = max(scale_x, scale_y)
                
                # Calculate scaled dimensions
                scaled_width = int(original_width * scale)
                scaled_height = int(original_height * scale)
                
                # Resize first
                resized_gif = self._resize_gif(gif, scaled_width, scaled_height, resample)
                
                # Crop to target dimensions if needed
                if scaled_width > width or scaled_height > height:
                    # Calculate crop coordinates (center crop)
                    crop_x = (scaled_width - width) // 2
                    crop_y = (scaled_height - height) // 2
                    
                    # Crop to target size
                    resized_gif = self._crop_gif(resized_gif, crop_x, crop_y, width, height)
                
                # Save GIF
                self.image_processor.save_image(
                    resized_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF resize to fill failed: {e}")
    
    def get_resize_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get resize information for GIF.
        
        Args:
            input_path: Path to input GIF file
            
        Returns:
            Dictionary with resize information
        """
        input_path = validate_animated_file(input_path)
        
        try:
            with Image.open(input_path) as gif:
                return {
                    'original_size': gif.size,
                    'original_width': gif.width,
                    'original_height': gif.height,
                    'aspect_ratio': gif.width / gif.height,
                    'frame_count': getattr(gif, 'n_frames', 1),
                    'is_animated': getattr(gif, 'is_animated', False),
                    'mode': gif.mode,
                    'format': gif.format
                }
        except Exception as e:
            raise ValidationError(f"Failed to get resize info: {e}")
    
    def _calculate_dimensions(self, original_width: int, original_height: int,
                            width: Optional[int], height: Optional[int],
                            maintain_aspect_ratio: bool) -> Tuple[int, int]:
        """
        Calculate new dimensions for resize.
        
        Args:
            original_width: Original width
            original_height: Original height
            width: Target width
            height: Target height
            maintain_aspect_ratio: Whether to maintain aspect ratio
            
        Returns:
            Tuple of (new_width, new_height)
        """
        if maintain_aspect_ratio:
            if width is None:
                # Calculate width based on height
                new_height = height
                new_width = int(original_width * new_height / original_height)
            elif height is None:
                # Calculate height based on width
                new_width = width
                new_height = int(original_height * new_width / original_width)
            else:
                # Both specified, maintain aspect ratio
                aspect_ratio = original_width / original_height
                target_aspect_ratio = width / height
                
                if aspect_ratio > target_aspect_ratio:
                    # Image is wider, fit to width
                    new_width = width
                    new_height = int(width / aspect_ratio)
                else:
                    # Image is taller, fit to height
                    new_height = height
                    new_width = int(height * aspect_ratio)
        else:
            # Don't maintain aspect ratio
            new_width = width if width is not None else original_width
            new_height = height if height is not None else original_height
        
        return new_width, new_height
    
    def _resize_gif(self, gif: Image.Image, width: int, height: int, 
                   resample: int) -> Image.Image:
        """
        Resize animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            width: Target width
            height: Target height
            resample: Resampling method
            
        Returns:
            Resized GIF
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, simple resize
            return gif.resize((width, height), resample)
        
        # Animated GIF - resize each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = gif.n_frames
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                
                # Resize frame
                resized_frame = gif.resize((width, height), resample)
                frames.append(resized_frame)
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    new_gif.filename or 'temp.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=True
                )
                
                # Load the saved GIF
                return Image.open(new_gif.filename or 'temp.gif')
            else:
                return gif.resize((width, height), resample)
                
        except Exception as e:
            # Fallback to simple resize
            return gif.resize((width, height), resample)
    
    def _crop_gif(self, gif: Image.Image, x: int, y: int, 
                  width: int, height: int) -> Image.Image:
        """
        Crop animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            x: Left coordinate
            y: Top coordinate
            width: Crop width
            height: Crop height
            
        Returns:
            Cropped GIF
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, simple crop
            return gif.crop((x, y, x + width, y + height))
        
        # Animated GIF - crop each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = gif.n_frames
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                
                # Crop frame
                cropped_frame = gif.crop((x, y, x + width, y + height))
                frames.append(cropped_frame)
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    new_gif.filename or 'temp.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=True
                )
                
                # Load the saved GIF
                return Image.open(new_gif.filename or 'temp.gif')
            else:
                return gif.crop((x, y, x + width, y + height))
                
        except Exception as e:
            # Fallback to simple crop
            return gif.crop((x, y, x + width, y + height))


def resize_gif(input_path: Union[str, Path],
              output_path: Union[str, Path],
              width: Optional[int] = None,
              height: Optional[int] = None,
              size: Optional[Tuple[int, int]] = None,
              maintain_aspect_ratio: bool = True,
              resample: int = Image.Resampling.LANCZOS,
              quality: int = 85) -> Path:
    """
    Resize GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        width: Target width
        height: Target height
        size: Target size as (width, height) tuple
        maintain_aspect_ratio: Whether to maintain aspect ratio
        resample: Resampling method
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    resizer = GifResizer()
    return resizer.resize(
        input_path, output_path, width, height, size,
        maintain_aspect_ratio, resample, quality
    )


def resize_gif_by_percentage(input_path: Union[str, Path],
                           output_path: Union[str, Path],
                           percentage: float,
                           resample: int = Image.Resampling.LANCZOS,
                           quality: int = 85) -> Path:
    """
    Resize GIF by percentage.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        percentage: Resize percentage (e.g., 0.5 for 50%, 2.0 for 200%)
        resample: Resampling method
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    resizer = GifResizer()
    return resizer.resize_by_percentage(
        input_path, output_path, percentage, resample, quality
    )


def resize_gif_to_fit(input_path: Union[str, Path],
                     output_path: Union[str, Path],
                     max_width: int,
                     max_height: int,
                     resample: int = Image.Resampling.LANCZOS,
                     quality: int = 85) -> Path:
    """
    Resize GIF to fit within specified dimensions.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        max_width: Maximum width
        max_height: Maximum height
        resample: Resampling method
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    resizer = GifResizer()
    return resizer.resize_to_fit(
        input_path, output_path, max_width, max_height, resample, quality
    )


def resize_gif_to_fill(input_path: Union[str, Path],
                      output_path: Union[str, Path],
                      width: int,
                      height: int,
                      resample: int = Image.Resampling.LANCZOS,
                      quality: int = 85) -> Path:
    """
    Resize GIF to fill specified dimensions.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        width: Target width
        height: Target height
        resample: Resampling method
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    resizer = GifResizer()
    return resizer.resize_to_fill(
        input_path, output_path, width, height, resample, quality
    )


def get_resize_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get resize information for GIF.
    
    Args:
        input_path: Path to input GIF file
        
    Returns:
        Dictionary with resize information
    """
    resizer = GifResizer()
    return resizer.get_resize_info(input_path)


# Export all functions and classes
__all__ = [
    'GifResizer',
    'resize_gif',
    'resize_gif_by_percentage',
    'resize_gif_to_fit',
    'resize_gif_to_fill',
    'get_resize_info'
]
