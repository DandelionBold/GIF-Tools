"""
GIF rotation module.

This module provides functionality to rotate GIFs by 90°, 180°, or 270° degrees
with support for both clockwise and counterclockwise rotation.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from PIL import Image

from ..utils import (
    DEFAULT_ROTATION_ANGLES,
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_output_path,
    validate_rotation_angle,
    get_image_processor
)


class GifRotator:
    """GIF rotation utility class."""
    
    def __init__(self) -> None:
        """Initialize GIF rotator."""
        self.image_processor = get_image_processor()
    
    def rotate(self,
               input_path: Union[str, Path],
               output_path: Union[str, Path],
               angle: int,
               quality: int = 85,
               progress_callback: Optional[callable] = None) -> Path:
        """
        Rotate GIF by specified angle.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            angle: Rotation angle (90, 180, or 270 degrees)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        angle = validate_rotation_angle(angle)
        
        try:
            # Progress update: Loading GIF
            if progress_callback:
                progress_callback(0, "Loading GIF...")
            
            # Load GIF
            with Image.open(input_path) as gif:
                # Progress update: Rotating GIF
                if progress_callback:
                    progress_callback(20, f"Rotating GIF by {angle}°...")
                
                # Rotate GIF
                rotated_gif = self._rotate_gif(gif, angle, progress_callback)
                
                # Progress update: Saving GIF
                if progress_callback:
                    progress_callback(80, "Saving rotated GIF...")
                
                # Save rotated GIF
                self.image_processor.save_image(
                    rotated_gif, output_path, quality=quality, optimize=True
                )
                
                # Progress update: Complete
                if progress_callback:
                    progress_callback(100, "Rotation complete!")
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF rotation failed: {e}")
    
    def rotate_clockwise(self,
                        input_path: Union[str, Path],
                        output_path: Union[str, Path],
                        quality: int = 85) -> Path:
        """
        Rotate GIF 90 degrees clockwise.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        return self.rotate(input_path, output_path, 90, quality)
    
    def rotate_counterclockwise(self,
                              input_path: Union[str, Path],
                              output_path: Union[str, Path],
                              quality: int = 85) -> Path:
        """
        Rotate GIF 90 degrees counterclockwise (270 degrees clockwise).
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        return self.rotate(input_path, output_path, 270, quality)
    
    def rotate_180(self,
                  input_path: Union[str, Path],
                  output_path: Union[str, Path],
                  quality: int = 85) -> Path:
        """
        Rotate GIF 180 degrees.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        return self.rotate(input_path, output_path, 180, quality)
    
    def flip_horizontal(self,
                       input_path: Union[str, Path],
                       output_path: Union[str, Path],
                       quality: int = 85) -> Path:
        """
        Flip GIF horizontally.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Flip GIF horizontally
                flipped_gif = self._flip_gif(gif, horizontal=True)
                
                # Save flipped GIF
                self.image_processor.save_image(
                    flipped_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF horizontal flip failed: {e}")
    
    def flip_vertical(self,
                     input_path: Union[str, Path],
                     output_path: Union[str, Path],
                     quality: int = 85) -> Path:
        """
        Flip GIF vertically.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Flip GIF vertically
                flipped_gif = self._flip_gif(gif, vertical=True)
                
                # Save flipped GIF
                self.image_processor.save_image(
                    flipped_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF vertical flip failed: {e}")
    
    def get_rotation_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get rotation information for GIF.
        
        Args:
            input_path: Path to input GIF file
            
        Returns:
            Dictionary with rotation information
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
                    'supported_angles': DEFAULT_ROTATION_ANGLES
                }
        except Exception as e:
            raise ValidationError(f"Failed to get rotation info: {e}")
    
    def _rotate_gif(self, gif: Image.Image, angle: int, progress_callback: Optional[callable] = None) -> Image.Image:
        """
        Rotate animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            angle: Rotation angle
            
        Returns:
            Rotated GIF
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, simple rotate
            return gif.rotate(angle, expand=True)
        
        # Animated GIF - rotate each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                # Progress update: Processing frames
                if progress_callback:
                    progress = 20 + int((frame_idx / frame_count) * 50)  # 20-70%
                    progress_callback(progress, f"Rotating frame {frame_idx+1}/{frame_count}...")
                
                gif.seek(frame_idx)
                
                # Rotate frame
                rotated_frame = gif.rotate(angle, expand=True)
                frames.append(rotated_frame)
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Progress update: Creating rotated GIF
            if progress_callback:
                progress_callback(70, "Creating rotated GIF...")
            
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
                return gif.rotate(angle, expand=True)
                
        except Exception as e:
            # Fallback to simple rotate
            return gif.rotate(angle, expand=True)
    
    def _flip_gif(self, gif: Image.Image, 
                 horizontal: bool = False, 
                 vertical: bool = False) -> Image.Image:
        """
        Flip animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            horizontal: Flip horizontally
            vertical: Flip vertically
            
        Returns:
            Flipped GIF
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, simple flip
            return self.image_processor.flip_image(gif, horizontal, vertical)
        
        # Animated GIF - flip each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                
                # Flip frame
                flipped_frame = self.image_processor.flip_image(gif, horizontal, vertical)
                frames.append(flipped_frame)
                
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
                return self.image_processor.flip_image(gif, horizontal, vertical)
                
        except Exception as e:
            # Fallback to simple flip
            return self.image_processor.flip_image(gif, horizontal, vertical)


def rotate_gif(input_path: Union[str, Path],
              output_path: Union[str, Path],
              angle: int,
              quality: int = 85,
              progress_callback: Optional[callable] = None) -> Path:
    """
    Rotate GIF by specified angle.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        angle: Rotation angle (90, 180, or 270 degrees)
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    rotator = GifRotator()
    return rotator.rotate(input_path, output_path, angle, quality, progress_callback)


def rotate_gif_clockwise(input_path: Union[str, Path],
                        output_path: Union[str, Path],
                        quality: int = 85) -> Path:
    """
    Rotate GIF 90 degrees clockwise.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    rotator = GifRotator()
    return rotator.rotate_clockwise(input_path, output_path, quality)


def rotate_gif_counterclockwise(input_path: Union[str, Path],
                               output_path: Union[str, Path],
                               quality: int = 85) -> Path:
    """
    Rotate GIF 90 degrees counterclockwise.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    rotator = GifRotator()
    return rotator.rotate_counterclockwise(input_path, output_path, quality)


def rotate_gif_180(input_path: Union[str, Path],
                  output_path: Union[str, Path],
                  quality: int = 85) -> Path:
    """
    Rotate GIF 180 degrees.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    rotator = GifRotator()
    return rotator.rotate_180(input_path, output_path, quality)


def flip_gif_horizontal(input_path: Union[str, Path],
                       output_path: Union[str, Path],
                       quality: int = 85) -> Path:
    """
    Flip GIF horizontally.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    rotator = GifRotator()
    return rotator.flip_horizontal(input_path, output_path, quality)


def flip_gif_vertical(input_path: Union[str, Path],
                     output_path: Union[str, Path],
                     quality: int = 85) -> Path:
    """
    Flip GIF vertically.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    rotator = GifRotator()
    return rotator.flip_vertical(input_path, output_path, quality)


def get_rotation_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get rotation information for GIF.
    
    Args:
        input_path: Path to input GIF file
        
    Returns:
        Dictionary with rotation information
    """
    rotator = GifRotator()
    return rotator.get_rotation_info(input_path)


# Export all functions and classes
__all__ = [
    'GifRotator',
    'rotate_gif',
    'rotate_gif_clockwise',
    'rotate_gif_counterclockwise',
    'rotate_gif_180',
    'flip_gif_horizontal',
    'flip_gif_vertical',
    'get_rotation_info'
]
