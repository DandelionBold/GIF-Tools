"""
GIF reverse module.

This module provides functionality to reverse GIF animations by
reversing the order of all frames to play the animation backwards.
"""

from pathlib import Path
from typing import Any, Dict, Union

from PIL import Image

from ..utils import (
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_output_path,
    get_image_processor
)


class GifReverser:
    """GIF reverse utility class."""
    
    def __init__(self) -> None:
        """Initialize GIF reverser."""
        self.image_processor = get_image_processor()
    
    def reverse(self,
               input_path: Union[str, Path],
               output_path: Union[str, Path],
               quality: int = 85) -> Path:
        """
        Reverse GIF animation by reversing frame order.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
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
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    # Single frame GIF - just copy
                    self.image_processor.save_image(
                        gif, output_path, quality=quality, optimize=True
                    )
                    return output_path
                
                # Reverse animated GIF
                reversed_gif = self._reverse_gif(gif)
                
                # Save reversed GIF
                self.image_processor.save_image(
                    reversed_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF reverse failed: {e}")
    
    def reverse_with_info(self,
                         input_path: Union[str, Path],
                         output_path: Union[str, Path],
                         quality: int = 85) -> Dict[str, Any]:
        """
        Reverse GIF and return detailed information.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            quality: Output quality (1-100)
            
        Returns:
            Dictionary with reverse information
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                frame_count = getattr(gif, 'n_frames', 1)
                is_animated = getattr(gif, 'is_animated', False)
                
                if not is_animated:
                    # Single frame GIF - just copy
                    self.image_processor.save_image(
                        gif, output_path, quality=quality, optimize=True
                    )
                    
                    return {
                        'input_path': str(input_path),
                        'output_path': str(output_path),
                        'frame_count': 1,
                        'is_animated': False,
                        'reversed': False,
                        'message': 'Single frame GIF - no reversal needed'
                    }
                
                # Get original frame durations
                original_durations = []
                for frame_idx in range(frame_count):
                    gif.seek(frame_idx)
                    duration = gif.info.get('duration', 100)  # Default 100ms
                    original_durations.append(duration)
                
                # Reverse animated GIF
                reversed_gif = self._reverse_gif(gif)
                
                # Save reversed GIF
                self.image_processor.save_image(
                    reversed_gif, output_path, quality=quality, optimize=True
                )
                
                return {
                    'input_path': str(input_path),
                    'output_path': str(output_path),
                    'frame_count': frame_count,
                    'is_animated': True,
                    'reversed': True,
                    'original_durations': original_durations,
                    'reversed_durations': list(reversed(original_durations)),
                    'total_duration': sum(original_durations) / 1000.0,  # Convert to seconds
                    'message': f'Successfully reversed {frame_count} frames'
                }
                
        except Exception as e:
            raise ValidationError(f"GIF reverse with info failed: {e}")
    
    def get_reverse_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get reverse information for GIF.
        
        Args:
            input_path: Path to input GIF file
            
        Returns:
            Dictionary with reverse information
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
                        'can_reverse': False,
                        'message': 'Single frame GIF - no reversal needed',
                        'size': gif.size,
                        'mode': gif.mode,
                        'format': gif.format
                    }
                
                # Get frame durations
                durations = []
                for frame_idx in range(frame_count):
                    gif.seek(frame_idx)
                    duration = gif.info.get('duration', 100)
                    durations.append(duration)
                
                return {
                    'frame_count': frame_count,
                    'is_animated': True,
                    'can_reverse': True,
                    'size': gif.size,
                    'mode': gif.mode,
                    'format': gif.format,
                    'durations': durations,
                    'total_duration': sum(durations) / 1000.0,
                    'loop': gif.info.get('loop', 0),
                    'message': f'Can reverse {frame_count} frames'
                }
        except Exception as e:
            raise ValidationError(f"Failed to get reverse info: {e}")
    
    def _reverse_gif(self, gif: Image.Image) -> Image.Image:
        """
        Reverse animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            
        Returns:
            Reversed GIF
        """
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            # Load all frames
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                frames.append(gif.copy())
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Reverse frames and durations
            reversed_frames = list(reversed(frames))
            reversed_durations = list(reversed(durations))
            
            # Create new GIF
            if reversed_frames:
                new_gif = reversed_frames[0].copy()
                new_gif.save(
                    'temp_reverse.gif',
                    save_all=True,
                    append_images=reversed_frames[1:],
                    duration=reversed_durations,
                    loop=gif.info.get('loop', 0),
                    disposal=2,  # Clear to background
                    transparency=0,
                    optimize=False  # Disable optimization to prevent glitching
                )
                
                # Load the saved GIF
                return Image.open('temp_reverse.gif')
            else:
                return gif.copy()
                
        except Exception as e:
            # Fallback to original GIF
            return gif.copy()


def reverse_gif(input_path: Union[str, Path],
               output_path: Union[str, Path],
               quality: int = 85) -> Path:
    """
    Reverse GIF animation by reversing frame order.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    reverser = GifReverser()
    return reverser.reverse(input_path, output_path, quality)


def reverse_gif_with_info(input_path: Union[str, Path],
                         output_path: Union[str, Path],
                         quality: int = 85) -> Dict[str, Any]:
    """
    Reverse GIF and return detailed information.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        quality: Output quality (1-100)
        
    Returns:
        Dictionary with reverse information
    """
    reverser = GifReverser()
    return reverser.reverse_with_info(input_path, output_path, quality)


def get_reverse_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get reverse information for GIF.
    
    Args:
        input_path: Path to input GIF file
        
    Returns:
        Dictionary with reverse information
    """
    reverser = GifReverser()
    return reverser.get_reverse_info(input_path)


# Export all functions and classes
__all__ = [
    'GifReverser',
    'reverse_gif',
    'reverse_gif_with_info',
    'get_reverse_info'
]
