"""
GIF loop settings module.

This module provides functionality to control loop count and behavior
of GIF animations, including infinite loops and custom loop counts.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from PIL import Image

from ..utils import (
    LOOP_BEHAVIORS,
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_output_path,
    get_image_processor
)


class GifLoopController:
    """GIF loop settings utility class."""
    
    def __init__(self) -> None:
        """Initialize GIF loop controller."""
        self.image_processor = get_image_processor()
    
    def set_loop_count(self,
                      input_path: Union[str, Path],
                      output_path: Union[str, Path],
                      loop_count: int,
                      quality: int = 85) -> Path:
        """
        Set loop count for GIF animation.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            loop_count: Number of times to loop (0 = infinite)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if loop_count < 0:
            raise ValidationError("Loop count must be non-negative")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    # Single frame GIF - just copy
                    self.image_processor.save_image(
                        gif, output_path, quality=quality, optimize=True
                    )
                    return output_path
                
                # Set loop count for animated GIF
                loop_gif = self._set_gif_loop_count(gif, loop_count)
                
                # Save GIF with new loop count
                self.image_processor.save_image(
                    loop_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF loop count setting failed: {e}")
    
    def set_infinite_loop(self,
                         input_path: Union[str, Path],
                         output_path: Union[str, Path],
                         quality: int = 85) -> Path:
        """
        Set GIF to loop infinitely.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        return self.set_loop_count(input_path, output_path, 0, quality)
    
    def set_no_loop(self,
                   input_path: Union[str, Path],
                   output_path: Union[str, Path],
                   quality: int = 85) -> Path:
        """
        Set GIF to play only once (no loop).
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        return self.set_loop_count(input_path, output_path, 1, quality)
    
    def set_loop_behavior(self,
                         input_path: Union[str, Path],
                         output_path: Union[str, Path],
                         behavior: str,
                         quality: int = 85) -> Path:
        """
        Set loop behavior for GIF animation.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            behavior: Loop behavior ('infinite', 'once', 'custom')
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if behavior not in LOOP_BEHAVIORS:
            raise ValidationError(f"Invalid loop behavior: {behavior}")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    # Single frame GIF - just copy
                    self.image_processor.save_image(
                        gif, output_path, quality=quality, optimize=True
                    )
                    return output_path
                
                # Set loop behavior
                if behavior == 'infinite':
                    loop_count = 0
                elif behavior == 'once':
                    loop_count = 1
                else:  # custom
                    # Keep original loop count
                    loop_count = gif.info.get('loop', 0)
                
                # Set loop count for animated GIF
                loop_gif = self._set_gif_loop_count(gif, loop_count)
                
                # Save GIF with new loop behavior
                self.image_processor.save_image(
                    loop_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF loop behavior setting failed: {e}")
    
    def get_loop_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get loop information for GIF.
        
        Args:
            input_path: Path to input GIF file
            
        Returns:
            Dictionary with loop information
        """
        input_path = validate_animated_file(input_path)
        
        try:
            with Image.open(input_path) as gif:
                frame_count = getattr(gif, 'n_frames', 1)
                is_animated = getattr(gif, 'is_animated', False)
                
                if not is_animated:
                    return {
                        'frame_count': 1,
                        'is_animated': False,
                        'can_set_loop': False,
                        'message': 'Single frame GIF - no loop to set',
                        'size': gif.size,
                        'mode': gif.mode,
                        'format': gif.format
                    }
                
                # Get loop information
                loop_count = gif.info.get('loop', 0)
                is_infinite = loop_count == 0
                
                # Determine loop behavior
                if is_infinite:
                    behavior = 'infinite'
                elif loop_count == 1:
                    behavior = 'once'
                else:
                    behavior = 'custom'
                
                return {
                    'frame_count': frame_count,
                    'is_animated': True,
                    'can_set_loop': True,
                    'loop_count': loop_count,
                    'is_infinite': is_infinite,
                    'behavior': behavior,
                    'size': gif.size,
                    'mode': gif.mode,
                    'format': gif.format,
                    'available_behaviors': list(LOOP_BEHAVIORS.keys()),
                    'message': f'Current loop: {behavior} ({loop_count if not is_infinite else "infinite"} times)'
                }
        except Exception as e:
            raise ValidationError(f"Failed to get loop info: {e}")
    
    def _set_gif_loop_count(self, gif: Image.Image, loop_count: int) -> Image.Image:
        """
        Set loop count for animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            loop_count: Number of times to loop
            
        Returns:
            GIF with new loop count
        """
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                frames.append(gif.copy())
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Create new GIF with loop count
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_loop.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=loop_count,
                    disposal=2,  # Clear to background
                    transparency=0,
                    optimize=False  # Disable optimization to prevent glitching
                )
                
                # Load the saved GIF
                return Image.open('temp_loop.gif')
            else:
                return gif.copy()
                
        except Exception as e:
            # Fallback to original GIF
            return gif.copy()


def set_gif_loop_count(input_path: Union[str, Path],
                      output_path: Union[str, Path],
                      loop_count: int,
                      **kwargs) -> Path:
    """
    Set loop count for GIF animation.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        loop_count: Number of times to loop
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    controller = GifLoopController()
    return controller.set_loop_count(input_path, output_path, loop_count, **kwargs)


def set_gif_infinite_loop(input_path: Union[str, Path],
                         output_path: Union[str, Path],
                         **kwargs) -> Path:
    """
    Set GIF to loop infinitely.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    controller = GifLoopController()
    return controller.set_infinite_loop(input_path, output_path, **kwargs)


def set_gif_no_loop(input_path: Union[str, Path],
                   output_path: Union[str, Path],
                   **kwargs) -> Path:
    """
    Set GIF to play only once (no loop).
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    controller = GifLoopController()
    return controller.set_no_loop(input_path, output_path, **kwargs)


def set_gif_loop_behavior(input_path: Union[str, Path],
                         output_path: Union[str, Path],
                         behavior: str,
                         **kwargs) -> Path:
    """
    Set loop behavior for GIF animation.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        behavior: Loop behavior
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    controller = GifLoopController()
    return controller.set_loop_behavior(input_path, output_path, behavior, **kwargs)


def get_gif_loop_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get loop information for GIF.
    
    Args:
        input_path: Path to input GIF file
        
    Returns:
        Dictionary with loop information
    """
    controller = GifLoopController()
    return controller.get_loop_info(input_path)


# Export all functions and classes
__all__ = [
    'GifLoopController',
    'set_gif_loop_count',
    'set_gif_infinite_loop',
    'set_gif_no_loop',
    'set_gif_loop_behavior',
    'get_gif_loop_info'
]
