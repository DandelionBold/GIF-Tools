"""
GIF crop module.

This module provides functionality to crop GIFs by cutting out specific
rectangular areas with support for both static and animated GIFs.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from PIL import Image

from ..utils import (
    DEFAULT_CROP,
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_crop_coordinates,
    validate_output_path,
    get_image_processor
)


class GifCropper:
    """GIF crop utility class."""
    
    def __init__(self) -> None:
        """Initialize GIF cropper."""
        self.image_processor = get_image_processor()
    
    def crop(self,
             input_path: Union[str, Path],
             output_path: Union[str, Path],
             x: int,
             y: int,
             width: int,
             height: int,
             quality: int = 85) -> Path:
        """
        Crop GIF by specified coordinates.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            x: Left coordinate
            y: Top coordinate
            width: Crop width
            height: Crop height
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        try:
            # Load GIF to get dimensions
            with Image.open(input_path) as gif:
                # Validate crop coordinates
                validate_crop_coordinates(x, y, width, height, gif.width, gif.height)
                
                # Crop GIF
                cropped_gif = self._crop_gif(gif, x, y, width, height)
                
                # Save cropped GIF
                self.image_processor.save_image(
                    cropped_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF crop failed: {e}")
    
    def crop_center(self,
                   input_path: Union[str, Path],
                   output_path: Union[str, Path],
                   width: int,
                   height: int,
                   quality: int = 85) -> Path:
        """
        Crop GIF from center.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            width: Crop width
            height: Crop height
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        try:
            # Load GIF to get dimensions
            with Image.open(input_path) as gif:
                # Calculate center crop coordinates
                x = (gif.width - width) // 2
                y = (gif.height - height) // 2
                
                # Validate crop coordinates
                validate_crop_coordinates(x, y, width, height, gif.width, gif.height)
                
                # Crop GIF
                cropped_gif = self._crop_gif(gif, x, y, width, height)
                
                # Save cropped GIF
                self.image_processor.save_image(
                    cropped_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF center crop failed: {e}")
    
    def crop_square(self,
                   input_path: Union[str, Path],
                   output_path: Union[str, Path],
                   size: int,
                   position: str = 'center',
                   quality: int = 85) -> Path:
        """
        Crop GIF to square.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            size: Square size
            position: Crop position ('center', 'top_left', 'top_right', 'bottom_left', 'bottom_right')
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if size <= 0:
            raise ValidationError("Square size must be positive")
        
        valid_positions = ['center', 'top_left', 'top_right', 'bottom_left', 'bottom_right']
        if position not in valid_positions:
            raise ValidationError(f"Invalid position: {position}. Must be one of {valid_positions}")
        
        try:
            # Load GIF to get dimensions
            with Image.open(input_path) as gif:
                # Calculate square crop coordinates
                x, y = self._calculate_square_position(gif.width, gif.height, size, position)
                
                # Validate crop coordinates
                validate_crop_coordinates(x, y, size, size, gif.width, gif.height)
                
                # Crop GIF
                cropped_gif = self._crop_gif(gif, x, y, size, size)
                
                # Save cropped GIF
                self.image_processor.save_image(
                    cropped_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF square crop failed: {e}")
    
    def crop_aspect_ratio(self,
                         input_path: Union[str, Path],
                         output_path: Union[str, Path],
                         aspect_ratio: float,
                         position: str = 'center',
                         quality: int = 85) -> Path:
        """
        Crop GIF to specific aspect ratio.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            aspect_ratio: Target aspect ratio (width/height)
            position: Crop position ('center', 'top_left', 'top_right', 'bottom_left', 'bottom_right')
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if aspect_ratio <= 0:
            raise ValidationError("Aspect ratio must be positive")
        
        valid_positions = ['center', 'top_left', 'top_right', 'bottom_left', 'bottom_right']
        if position not in valid_positions:
            raise ValidationError(f"Invalid position: {position}. Must be one of {valid_positions}")
        
        try:
            # Load GIF to get dimensions
            with Image.open(input_path) as gif:
                # Calculate crop dimensions based on aspect ratio
                width, height = self._calculate_aspect_ratio_crop(
                    gif.width, gif.height, aspect_ratio
                )
                
                # Calculate crop position
                x, y = self._calculate_crop_position(
                    gif.width, gif.height, width, height, position
                )
                
                # Validate crop coordinates
                validate_crop_coordinates(x, y, width, height, gif.width, gif.height)
                
                # Crop GIF
                cropped_gif = self._crop_gif(gif, x, y, width, height)
                
                # Save cropped GIF
                self.image_processor.save_image(
                    cropped_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF aspect ratio crop failed: {e}")
    
    def get_crop_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get crop information for GIF.
        
        Args:
            input_path: Path to input GIF file
            
        Returns:
            Dictionary with crop information
        """
        input_path = validate_animated_file(input_path)
        
        try:
            with Image.open(input_path) as gif:
                return {
                    'size': gif.size,
                    'width': gif.width,
                    'height': gif.height,
                    'aspect_ratio': gif.width / gif.height,
                    'frame_count': getattr(gif, 'n_frames', 1),
                    'is_animated': getattr(gif, 'is_animated', False),
                    'mode': gif.mode,
                    'format': gif.format,
                    'max_crop_width': gif.width,
                    'max_crop_height': gif.height,
                    'center_x': gif.width // 2,
                    'center_y': gif.height // 2
                }
        except Exception as e:
            raise ValidationError(f"Failed to get crop info: {e}")
    
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
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
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
                    getattr(new_gif, 'filename', None) or 'temp.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=True
                )
                
                # Load the saved GIF
                return Image.open(getattr(new_gif, 'filename', None) or 'temp.gif')
            else:
                return gif.crop((x, y, x + width, y + height))
                
        except Exception as e:
            # Fallback to simple crop
            return gif.crop((x, y, x + width, y + height))
    
    def _calculate_square_position(self, image_width: int, image_height: int, 
                                 size: int, position: str) -> Tuple[int, int]:
        """
        Calculate square crop position.
        
        Args:
            image_width: Image width
            image_height: Image height
            size: Square size
            position: Crop position
            
        Returns:
            Tuple of (x, y) coordinates
        """
        if position == 'center':
            x = (image_width - size) // 2
            y = (image_height - size) // 2
        elif position == 'top_left':
            x = 0
            y = 0
        elif position == 'top_right':
            x = image_width - size
            y = 0
        elif position == 'bottom_left':
            x = 0
            y = image_height - size
        elif position == 'bottom_right':
            x = image_width - size
            y = image_height - size
        else:
            x = (image_width - size) // 2
            y = (image_height - size) // 2
        
        return x, y
    
    def _calculate_aspect_ratio_crop(self, image_width: int, image_height: int, 
                                   aspect_ratio: float) -> Tuple[int, int]:
        """
        Calculate crop dimensions based on aspect ratio.
        
        Args:
            image_width: Image width
            image_height: Image height
            aspect_ratio: Target aspect ratio
            
        Returns:
            Tuple of (width, height)
        """
        current_aspect_ratio = image_width / image_height
        
        if current_aspect_ratio > aspect_ratio:
            # Image is wider, fit to height
            height = image_height
            width = int(height * aspect_ratio)
        else:
            # Image is taller, fit to width
            width = image_width
            height = int(width / aspect_ratio)
        
        return width, height
    
    def _calculate_crop_position(self, image_width: int, image_height: int,
                               crop_width: int, crop_height: int, 
                               position: str) -> Tuple[int, int]:
        """
        Calculate crop position.
        
        Args:
            image_width: Image width
            image_height: Image height
            crop_width: Crop width
            crop_height: Crop height
            position: Crop position
            
        Returns:
            Tuple of (x, y) coordinates
        """
        if position == 'center':
            x = (image_width - crop_width) // 2
            y = (image_height - crop_height) // 2
        elif position == 'top_left':
            x = 0
            y = 0
        elif position == 'top_right':
            x = image_width - crop_width
            y = 0
        elif position == 'bottom_left':
            x = 0
            y = image_height - crop_height
        elif position == 'bottom_right':
            x = image_width - crop_width
            y = image_height - crop_height
        else:
            x = (image_width - crop_width) // 2
            y = (image_height - crop_height) // 2
        
        return x, y


def crop_gif(input_path: Union[str, Path],
            output_path: Union[str, Path],
            x: int,
            y: int,
            width: int,
            height: int,
            quality: int = 85) -> Path:
    """
    Crop GIF by specified coordinates.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        x: Left coordinate
        y: Top coordinate
        width: Crop width
        height: Crop height
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    cropper = GifCropper()
    return cropper.crop(input_path, output_path, x, y, width, height, quality)


def crop_gif_center(input_path: Union[str, Path],
                   output_path: Union[str, Path],
                   width: int,
                   height: int,
                   quality: int = 85) -> Path:
    """
    Crop GIF from center.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        width: Crop width
        height: Crop height
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    cropper = GifCropper()
    return cropper.crop_center(input_path, output_path, width, height, quality)


def crop_gif_square(input_path: Union[str, Path],
                   output_path: Union[str, Path],
                   size: int,
                   position: str = 'center',
                   quality: int = 85) -> Path:
    """
    Crop GIF to square.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        size: Square size
        position: Crop position
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    cropper = GifCropper()
    return cropper.crop_square(input_path, output_path, size, position, quality)


def crop_gif_aspect_ratio(input_path: Union[str, Path],
                         output_path: Union[str, Path],
                         aspect_ratio: float,
                         position: str = 'center',
                         quality: int = 85) -> Path:
    """
    Crop GIF to specific aspect ratio.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        aspect_ratio: Target aspect ratio
        position: Crop position
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    cropper = GifCropper()
    return cropper.crop_aspect_ratio(
        input_path, output_path, aspect_ratio, position, quality
    )


def get_crop_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get crop information for GIF.
    
    Args:
        input_path: Path to input GIF file
        
    Returns:
        Dictionary with crop information
    """
    cropper = GifCropper()
    return cropper.get_crop_info(input_path)


# Export all functions and classes
__all__ = [
    'GifCropper',
    'crop_gif',
    'crop_gif_center',
    'crop_gif_square',
    'crop_gif_aspect_ratio',
    'get_crop_info'
]
