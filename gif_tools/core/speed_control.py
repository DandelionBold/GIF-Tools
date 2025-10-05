"""
GIF speed control module.

This module provides functionality to adjust the playback speed of GIF animations
by modifying frame durations and applying speed multipliers.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from PIL import Image

from ..utils import (
    DEFAULT_SPEED_CONTROL,
    SPEED_MULTIPLIERS,
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_output_path,
    validate_speed_multiplier,
    get_image_processor
)


class GifSpeedController:
    """GIF speed control utility class."""
    
    def __init__(self) -> None:
        """Initialize GIF speed controller."""
        self.image_processor = get_image_processor()
    
    def change_speed(self,
                    input_path: Union[str, Path],
                    output_path: Union[str, Path],
                    multiplier: float,
                    min_duration: float = DEFAULT_SPEED_CONTROL['min_duration'],
                    max_duration: float = DEFAULT_SPEED_CONTROL['max_duration'],
                    quality: int = 85) -> Path:
        """
        Change GIF playback speed by applying a multiplier.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            multiplier: Speed multiplier (e.g., 0.5 for half speed, 2.0 for double speed)
            min_duration: Minimum frame duration in seconds
            max_duration: Maximum frame duration in seconds
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        multiplier = validate_speed_multiplier(multiplier)
        
        if min_duration <= 0 or max_duration <= 0:
            raise ValidationError("Duration limits must be positive")
        
        if min_duration >= max_duration:
            raise ValidationError("Minimum duration must be less than maximum duration")
        
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
                
                # Change speed of animated GIF
                speed_gif = self._change_gif_speed(
                    gif, multiplier, min_duration, max_duration
                )
                
                # Save speed-controlled GIF
                self.image_processor.save_image(
                    speed_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF speed change failed: {e}")
    
    def slow_down(self,
                 input_path: Union[str, Path],
                 output_path: Union[str, Path],
                 factor: float = 0.5,
                 **kwargs) -> Path:
        """
        Slow down GIF animation.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            factor: Slow down factor (e.g., 0.5 for half speed)
            **kwargs: Additional speed control parameters
            
        Returns:
            Path to output GIF file
        """
        if factor <= 0:
            raise ValidationError("Slow down factor must be positive")
        
        return self.change_speed(input_path, output_path, factor, **kwargs)
    
    def speed_up(self,
                input_path: Union[str, Path],
                output_path: Union[str, Path],
                factor: float = 2.0,
                **kwargs) -> Path:
        """
        Speed up GIF animation.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            factor: Speed up factor (e.g., 2.0 for double speed)
            **kwargs: Additional speed control parameters
            
        Returns:
            Path to output GIF file
        """
        if factor <= 0:
            raise ValidationError("Speed up factor must be positive")
        
        return self.change_speed(input_path, output_path, factor, **kwargs)
    
    def set_speed_preset(self,
                        input_path: Union[str, Path],
                        output_path: Union[str, Path],
                        preset: str,
                        **kwargs) -> Path:
        """
        Set GIF speed using predefined presets.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            preset: Speed preset ('very_slow', 'slow', 'normal', 'fast', 'very_fast')
            **kwargs: Additional speed control parameters
            
        Returns:
            Path to output GIF file
        """
        if preset not in SPEED_MULTIPLIERS:
            raise ValidationError(f"Invalid speed preset: {preset}")
        
        multiplier = SPEED_MULTIPLIERS[preset]
        return self.change_speed(input_path, output_path, multiplier, **kwargs)
    
    def set_frame_durations(self,
                           input_path: Union[str, Path],
                           output_path: Union[str, Path],
                           durations: List[float],
                           quality: int = 85) -> Path:
        """
        Set custom frame durations for GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            durations: List of frame durations in seconds
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if not durations:
            raise ValidationError("Durations list cannot be empty")
        
        if not all(d > 0 for d in durations):
            raise ValidationError("All durations must be positive")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    raise ValidationError("Cannot set frame durations for non-animated GIF")
                
                # Get frame count
                frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
                
                if len(durations) != frame_count:
                    raise ValidationError(f"Durations count ({len(durations)}) must match frame count ({frame_count})")
                
                # Set custom durations
                custom_gif = self._set_custom_durations(gif, durations)
                
                # Save GIF with custom durations
                self.image_processor.save_image(
                    custom_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF custom durations failed: {e}")
    
    def get_speed_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get speed information for GIF.
        
        Args:
            input_path: Path to input GIF file
            
        Returns:
            Dictionary with speed information
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
                        'can_change_speed': False,
                        'message': 'Single frame GIF - no speed to change',
                        'size': gif.size,
                        'mode': gif.mode,
                        'format': gif.format
                    }
                
                # Get frame durations
                durations = []
                for frame_idx in range(frame_count):
                    gif.seek(frame_idx)
                    duration = gif.info.get('duration', 100)  # Default 100ms
                    durations.append(duration)
                
                # Calculate speed statistics
                total_duration = sum(durations) / 1000.0  # Convert to seconds
                avg_duration = total_duration / frame_count
                fps = frame_count / total_duration if total_duration > 0 else 0
                
                return {
                    'frame_count': frame_count,
                    'is_animated': True,
                    'can_change_speed': True,
                    'durations': durations,
                    'total_duration': total_duration,
                    'average_duration': avg_duration,
                    'fps': round(fps, 2),
                    'size': gif.size,
                    'mode': gif.mode,
                    'format': gif.format,
                    'loop': gif.info.get('loop', 0),
                    'speed_presets': list(SPEED_MULTIPLIERS.keys()),
                    'message': f'Can change speed of {frame_count} frames'
                }
        except Exception as e:
            raise ValidationError(f"Failed to get speed info: {e}")
    
    def _change_gif_speed(self, gif: Image.Image, multiplier: float,
                         min_duration: float, max_duration: float) -> Image.Image:
        """
        Change speed of animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            multiplier: Speed multiplier
            min_duration: Minimum frame duration in seconds
            max_duration: Maximum frame duration in seconds
            
        Returns:
            Speed-controlled GIF
        """
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                frames.append(gif.copy())
                
                # Get original frame duration
                original_duration = gif.info.get('duration', 100)  # Default 100ms
                
                # Calculate new duration
                new_duration_ms = original_duration / multiplier
                
                # Ensure minimum duration of 1ms to prevent zero duration
                new_duration_ms = max(1, new_duration_ms)
                
                durations.append(int(new_duration_ms))
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_speed.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    disposal=2,  # Clear to background
                    transparency=0,
                    optimize=False  # Disable optimization to prevent glitching
                )
                
                # Load the saved GIF
                return Image.open('temp_speed.gif')
            else:
                return gif.copy()
                
        except Exception as e:
            # Fallback to original GIF
            return gif.copy()
    
    def _set_custom_durations(self, gif: Image.Image, durations: List[float]) -> Image.Image:
        """
        Set custom frame durations for GIF.
        
        Args:
            gif: PIL Image object (GIF)
            durations: List of frame durations in seconds
            
        Returns:
            GIF with custom durations
        """
        frames = []
        durations_ms = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                frames.append(gif.copy())
                
                # Convert duration to milliseconds
                duration_ms = int(durations[frame_idx] * 1000)
                durations_ms.append(duration_ms)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_custom_durations.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations_ms,
                    loop=gif.info.get('loop', 0),
                    disposal=2,  # Clear to background
                    transparency=0,
                    optimize=False  # Disable optimization to prevent glitching
                )
                
                # Load the saved GIF
                return Image.open('temp_custom_durations.gif')
            else:
                return gif.copy()
                
        except Exception as e:
            # Fallback to original GIF
            return gif.copy()


def change_gif_speed(input_path: Union[str, Path],
                    output_path: Union[str, Path],
                    multiplier: float,
                    **kwargs) -> Path:
    """
    Change GIF playback speed by applying a multiplier.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        multiplier: Speed multiplier
        **kwargs: Additional speed control parameters
        
    Returns:
        Path to output GIF file
    """
    controller = GifSpeedController()
    return controller.change_speed(input_path, output_path, multiplier, **kwargs)


def slow_down_gif(input_path: Union[str, Path],
                 output_path: Union[str, Path],
                 factor: float = 0.5,
                 **kwargs) -> Path:
    """
    Slow down GIF animation.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        factor: Slow down factor
        **kwargs: Additional speed control parameters
        
    Returns:
        Path to output GIF file
    """
    controller = GifSpeedController()
    return controller.slow_down(input_path, output_path, factor, **kwargs)


def speed_up_gif(input_path: Union[str, Path],
                output_path: Union[str, Path],
                factor: float = 2.0,
                **kwargs) -> Path:
    """
    Speed up GIF animation.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        factor: Speed up factor
        **kwargs: Additional speed control parameters
        
    Returns:
        Path to output GIF file
    """
    controller = GifSpeedController()
    return controller.speed_up(input_path, output_path, factor, **kwargs)


def set_gif_speed_preset(input_path: Union[str, Path],
                        output_path: Union[str, Path],
                        preset: str,
                        **kwargs) -> Path:
    """
    Set GIF speed using predefined presets.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        preset: Speed preset
        **kwargs: Additional speed control parameters
        
    Returns:
        Path to output GIF file
    """
    controller = GifSpeedController()
    return controller.set_speed_preset(input_path, output_path, preset, **kwargs)


def set_gif_frame_durations(input_path: Union[str, Path],
                           output_path: Union[str, Path],
                           durations: List[float],
                           **kwargs) -> Path:
    """
    Set custom frame durations for GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        durations: List of frame durations in seconds
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    controller = GifSpeedController()
    return controller.set_frame_durations(input_path, output_path, durations, **kwargs)


def get_gif_speed_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get speed information for GIF.
    
    Args:
        input_path: Path to input GIF file
        
    Returns:
        Dictionary with speed information
    """
    controller = GifSpeedController()
    return controller.get_speed_info(input_path)


# Export all functions and classes
__all__ = [
    'GifSpeedController',
    'change_gif_speed',
    'slow_down_gif',
    'speed_up_gif',
    'set_gif_speed_preset',
    'set_gif_frame_durations',
    'get_gif_speed_info'
]
