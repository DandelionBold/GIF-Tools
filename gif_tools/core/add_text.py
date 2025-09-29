"""
GIF add text module.

This module provides functionality to add text overlays to GIFs with
customizable fonts, colors, positioning, and animations.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFont

from ..utils import (
    DEFAULT_TEXT,
    SUCCESS_MESSAGES,
    TEXT_ALIGNMENT,
    ValidationError,
    validate_animated_file,
    validate_color,
    validate_output_path,
    validate_position,
    get_image_processor
)


class GifTextAdder:
    """GIF text addition utility class."""
    
    def __init__(self) -> None:
        """Initialize GIF text adder."""
        self.image_processor = get_image_processor()
        self._font_cache: Dict[str, ImageFont.FreeTypeFont] = {}
    
    def add_text(self,
                 input_path: Union[str, Path],
                 output_path: Union[str, Path],
                 text: str,
                 position: Tuple[int, int] = (10, 10),
                 font_family: str = 'Arial',
                 font_size: int = 24,
                 color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]] = (255, 255, 255),
                 text_opacity: float = 1.0,
                 alignment: str = 'left',
                 background_color: Optional[Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]] = None,
                 background_opacity: float = 0.0,
                 stroke_width: int = 0,
                 stroke_color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]] = (0, 0, 0),
                 stroke_opacity: float = 1.0,
                 quality: int = 85) -> Path:
        """
        Add text to GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            text: Text to add
            position: Text position (x, y)
            font_family: Font family name
            font_size: Font size
            color: Text color
            text_opacity: Text opacity (0.0-1.0)
            alignment: Text alignment
            background_color: Background color for text
            background_opacity: Background opacity (0.0-1.0)
            stroke_width: Text stroke width
            stroke_color: Text stroke color
            stroke_opacity: Stroke opacity (0.0-1.0)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if not text.strip():
            raise ValidationError("Text cannot be empty")
        
        position = validate_position(position)
        color = validate_color(color)
        stroke_color = validate_color(stroke_color)
        
        if background_color is not None:
            background_color = validate_color(background_color)
        
        if alignment not in TEXT_ALIGNMENT:
            raise ValidationError(f"Invalid alignment: {alignment}")
        
        if not 0.0 <= background_opacity <= 1.0:
            raise ValidationError("Background opacity must be between 0.0 and 1.0")
        
        if not 0.0 <= text_opacity <= 1.0:
            raise ValidationError("Text opacity must be between 0.0 and 1.0")
        
        if not 0.0 <= stroke_opacity <= 1.0:
            raise ValidationError("Stroke opacity must be between 0.0 and 1.0")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Add text to GIF
                text_gif = self._add_text_to_gif(
                    gif, text, position, font_family, font_size, color, text_opacity,
                    alignment, background_color, background_opacity,
                    stroke_width, stroke_color, stroke_opacity
                )
                
                # Save text GIF
                self.image_processor.save_image(
                    text_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF text addition failed: {str(e)}")
    
    def add_multiple_text(self,
                         input_path: Union[str, Path],
                         output_path: Union[str, Path],
                         text_elements: List[Dict[str, Any]],
                         quality: int = 85) -> Path:
        """
        Add multiple text elements to GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            text_elements: List of text element dictionaries
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if not text_elements:
            raise ValidationError("No text elements provided")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Add multiple text elements
                text_gif = self._add_multiple_text_to_gif(gif, text_elements)
                
                # Save text GIF
                self.image_processor.save_image(
                    text_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF multiple text addition failed: {e}")
    
    def add_animated_text(self,
                         input_path: Union[str, Path],
                         output_path: Union[str, Path],
                         text: str,
                         animation_type: str = 'fade',
                         duration: int = 1000,
                         **kwargs: Any) -> Path:
        """
        Add animated text to GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            text: Text to add
            animation_type: Animation type ('fade', 'slide', 'bounce', 'typewriter')
            duration: Animation duration in milliseconds
            **kwargs: Additional text parameters
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if animation_type not in ['fade', 'slide', 'bounce', 'typewriter']:
            raise ValidationError(f"Invalid animation type: {animation_type}")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Add animated text
                text_gif = self._add_animated_text_to_gif(
                    gif, text, animation_type, duration, **kwargs
                )
                
                # Save text GIF
                self.image_processor.save_image(
                    text_gif, output_path, quality=kwargs.get('quality', 85), optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF animated text addition failed: {e}")
    
    def get_text_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get text addition information for GIF.
        
        Args:
            input_path: Path to input GIF file
            
        Returns:
            Dictionary with text information
        """
        input_path = validate_animated_file(input_path)
        
        try:
            with Image.open(input_path) as gif:
                return {
                    'size': gif.size,
                    'width': gif.width,
                    'height': gif.height,
                    'frame_count': getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1,
                    'is_animated': getattr(gif, 'is_animated', False) if hasattr(gif, 'is_animated') else False,
                    'mode': gif.mode,
                    'format': gif.format,
                    'available_fonts': self._get_available_fonts(),
                    'text_alignment_options': list(TEXT_ALIGNMENT.keys()),
                    'animation_types': ['fade', 'slide', 'bounce', 'typewriter']
                }
        except Exception as e:
            raise ValidationError(f"Failed to get text info: {e}")
    
    def _add_text_to_gif(self, gif: Image.Image, text: str, position: Tuple[int, int],
                        font_family: str, font_size: int, color: Tuple[int, int, int, int],
                        text_opacity: float, alignment: str, background_color: Optional[Tuple[int, int, int, int]],
                        background_opacity: float, stroke_width: int,
                        stroke_color: Tuple[int, int, int, int], stroke_opacity: float) -> Image.Image:
        """
        Add text to animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            text: Text to add
            position: Text position
            font_family: Font family
            font_size: Font size
            color: Text color
            text_opacity: Text opacity
            alignment: Text alignment
            background_color: Background color
            background_opacity: Background opacity
            stroke_width: Stroke width
            stroke_color: Stroke color
            stroke_opacity: Stroke opacity
            
        Returns:
            GIF with text added
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, simple text addition
            return self.image_processor.add_text(
                gif, text, position, font_family, font_size, color, text_opacity,
                alignment, background_color, background_opacity,
                stroke_width, stroke_color, stroke_opacity
            )
        
        # Animated GIF - add text to each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                
                # Add text to frame
                text_frame = self.image_processor.add_text(
                    gif, text, position, font_family, font_size, color, text_opacity,
                    alignment, background_color, background_opacity,
                    stroke_width, stroke_color, stroke_opacity
                )
                frames.append(text_frame)
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_text.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=True
                )
                
                # Load the saved GIF
                return Image.open('temp_text.gif')
            else:
                return self.image_processor.add_text(
                    gif, text, position, font_family, font_size, color, text_opacity,
                    alignment, background_color, background_opacity,
                    stroke_width, stroke_color, stroke_opacity
                )
                
        except Exception as e:
            # Fallback to simple text addition
            return self.image_processor.add_text(
                gif, text, position, font_family, font_size, color, text_opacity,
                alignment, background_color, background_opacity,
                stroke_width, stroke_color, stroke_opacity
            )
    
    def _add_multiple_text_to_gif(self, gif: Image.Image, 
                                 text_elements: List[Dict[str, Any]]) -> Image.Image:
        """
        Add multiple text elements to animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            text_elements: List of text element dictionaries
            
        Returns:
            GIF with multiple text elements added
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, add text to single frame
            result = gif.copy()
            for element in text_elements:
                result = self.image_processor.add_text(result, **element)
            return result
        
        # Animated GIF - add text to each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                result_frame = gif.copy()
                
                # Add all text elements to frame
                for element in text_elements:
                    result_frame = self.image_processor.add_text(result_frame, **element)
                
                frames.append(result_frame)
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_multiple_text.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=True
                )
                
                # Load the saved GIF
                return Image.open('temp_multiple_text.gif')
            else:
                result = gif.copy()
                for element in text_elements:
                    result = self.image_processor.add_text(result, **element)
                return result
                
        except Exception as e:
            # Fallback to simple text addition
            result = gif.copy()
            for element in text_elements:
                result = self.image_processor.add_text(result, **element)
            return result
    
    def _add_animated_text_to_gif(self, gif: Image.Image, text: str,
                                 animation_type: str, duration: int,
                                 **kwargs: Any) -> Image.Image:
        """
        Add animated text to GIF.
        
        Args:
            gif: PIL Image object (GIF)
            text: Text to add
            animation_type: Animation type
            duration: Animation duration
            **kwargs: Additional text parameters
            
        Returns:
            GIF with animated text added
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, add static text
            return self.image_processor.add_text(gif, text, **kwargs)
        
        # Animated GIF - create animated text
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                result_frame = gif.copy()
                
                # Apply animation effect
                animated_text = self._apply_text_animation(
                    text, animation_type, frame_idx, frame_count, duration, **kwargs
                )
                
                if animated_text:
                    result_frame = self.image_processor.add_text(result_frame, animated_text, **kwargs)
                
                frames.append(result_frame)
                
                # Get frame duration
                duration_ms = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration_ms)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_animated_text.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=True
                )
                
                # Load the saved GIF
                return Image.open('temp_animated_text.gif')
            else:
                return self.image_processor.add_text(gif, text, **kwargs)
                
        except Exception as e:
            # Fallback to simple text addition
            return self.image_processor.add_text(gif, text, **kwargs)
    
    def _apply_text_animation(self, text: str, animation_type: str,
                            frame_idx: int, total_frames: int, duration: int,
                            **kwargs: Any) -> Optional[str]:
        """
        Apply text animation effect.
        
        Args:
            text: Text to animate
            animation_type: Animation type
            frame_idx: Current frame index
            total_frames: Total number of frames
            duration: Animation duration
            **kwargs: Additional parameters
            
        Returns:
            Animated text or None
        """
        if animation_type == 'fade':
            # Fade in/out effect
            progress = frame_idx / total_frames
            if progress < 0.5:
                # Fade in
                alpha = int(255 * (progress * 2))
            else:
                # Fade out
                alpha = int(255 * (2 - progress * 2))
            
            # Apply alpha to color
            if 'color' in kwargs:
                color = kwargs['color']
                if len(color) == 3:
                    color = color + (alpha,)
                else:
                    color = color[:3] + (alpha,)
                kwargs['color'] = color
            
            return text if alpha > 0 else None
        
        elif animation_type == 'slide':
            # Slide effect
            progress = frame_idx / total_frames
            if progress < 0.3:
                # Slide in from left
                offset = int((0.3 - progress) * 100)
                position = kwargs.get('position', (10, 10))
                kwargs['position'] = (position[0] - offset, position[1])
            elif progress > 0.7:
                # Slide out to right
                offset = int((progress - 0.7) * 100)
                position = kwargs.get('position', (10, 10))
                kwargs['position'] = (position[0] + offset, position[1])
            
            return text
        
        elif animation_type == 'bounce':
            # Bounce effect
            progress = frame_idx / total_frames
            bounce_height = int(20 * abs(0.5 - progress) * 2)
            position = kwargs.get('position', (10, 10))
            kwargs['position'] = (position[0], position[1] - bounce_height)
            
            return text
        
        elif animation_type == 'typewriter':
            # Typewriter effect
            progress = frame_idx / total_frames
            char_count = int(len(text) * progress)
            return text[:char_count]
        
        return text
    
    def _get_available_fonts(self) -> List[str]:
        """Get list of available fonts."""
        try:
            import matplotlib.font_manager as fm
            fonts = [f.name for f in fm.fontManager.ttflist]
            return sorted(list(set(fonts)))
        except ImportError:
            # Fallback to common fonts
            return ['Arial', 'Times New Roman', 'Courier New', 'Helvetica', 'Verdana']


def add_text_to_gif(input_path: Union[str, Path],
                   output_path: Union[str, Path],
                   text: str,
                   **kwargs: Any) -> Path:
    """
    Add text to GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        text: Text to add
        **kwargs: Additional text parameters
        
    Returns:
        Path to output GIF file
    """
    adder = GifTextAdder()
    return adder.add_text(input_path, output_path, text, **kwargs)


def add_multiple_text_to_gif(input_path: Union[str, Path],
                            output_path: Union[str, Path],
                            text_elements: List[Dict[str, Any]],
                            **kwargs: Any) -> Path:
    """
    Add multiple text elements to GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        text_elements: List of text element dictionaries
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    adder = GifTextAdder()
    return adder.add_multiple_text(input_path, output_path, text_elements, **kwargs)


def add_animated_text_to_gif(input_path: Union[str, Path],
                            output_path: Union[str, Path],
                            text: str,
                            animation_type: str = 'fade',
                            **kwargs: Any) -> Path:
    """
    Add animated text to GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        text: Text to add
        animation_type: Animation type
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    adder = GifTextAdder()
    return adder.add_animated_text(
        input_path, output_path, text, animation_type, **kwargs
    )


def get_text_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get text addition information for GIF.
    
    Args:
        input_path: Path to input GIF file
        
    Returns:
        Dictionary with text information
    """
    adder = GifTextAdder()
    return adder.get_text_info(input_path)


# Export all functions and classes
__all__ = [
    'GifTextAdder',
    'add_text_to_gif',
    'add_multiple_text_to_gif',
    'add_animated_text_to_gif',
    'get_text_info'
]
