"""
GIF watermark module.

This module provides functionality to add image or text watermarks to GIFs
with customizable positioning, opacity, and styling options.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFont

from ..utils import (
    WATERMARK_POSITIONS,
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_output_path,
    validate_position,
    validate_color,
    get_image_processor
)


class GifWatermarker:
    """GIF watermark utility class."""
    
    def __init__(self) -> None:
        """Initialize GIF watermarker."""
        self.image_processor = get_image_processor()
        self._font_cache: Dict[str, ImageFont.FreeTypeFont] = {}
    
    def add_text_watermark(self,
                          input_path: Union[str, Path],
                          output_path: Union[str, Path],
                          text: str,
                          position: str = 'bottom_right',
                          opacity: float = 0.7,
                          font_family: str = 'Arial',
                          font_size: int = 24,
                          color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]] = (255, 255, 255),
                          background_color: Optional[Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]] = None,
                          padding: int = 10,
                          quality: int = 85) -> Path:
        """
        Add text watermark to GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            text: Watermark text
            position: Watermark position
            opacity: Watermark opacity (0.0-1.0)
            font_family: Font family name
            font_size: Font size
            color: Text color
            background_color: Background color for text
            padding: Padding around text
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
            raise ValidationError("Watermark text cannot be empty")
        
        if position not in WATERMARK_POSITIONS:
            raise ValidationError(f"Invalid watermark position: {position}")
        
        if not 0.0 <= opacity <= 1.0:
            raise ValidationError("Opacity must be between 0.0 and 1.0")
        
        color = validate_color(color)
        if background_color is not None:
            background_color = validate_color(background_color)
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Add text watermark to GIF
                watermarked_gif = self._add_text_watermark_to_gif(
                    gif, text, position, opacity, font_family, font_size,
                    color, background_color, padding
                )
                
                # Save watermarked GIF
                self.image_processor.save_image(
                    watermarked_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF text watermark addition failed: {e}")
    
    def add_image_watermark(self,
                           input_path: Union[str, Path],
                           output_path: Union[str, Path],
                           watermark_path: Union[str, Path],
                           position: str = 'bottom_right',
                           opacity: float = 0.7,
                           scale: float = 0.2,
                           quality: int = 85) -> Path:
        """
        Add image watermark to GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            watermark_path: Path to watermark image
            position: Watermark position
            opacity: Watermark opacity (0.0-1.0)
            scale: Scale factor for watermark (0.0-1.0)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        watermark_path = Path(watermark_path)
        
        if not watermark_path.exists():
            raise ValidationError(f"Watermark image does not exist: {watermark_path}")
        
        if position not in WATERMARK_POSITIONS:
            raise ValidationError(f"Invalid watermark position: {position}")
        
        if not 0.0 <= opacity <= 1.0:
            raise ValidationError("Opacity must be between 0.0 and 1.0")
        
        if not 0.0 <= scale <= 1.0:
            raise ValidationError("Scale must be between 0.0 and 1.0")
        
        try:
            # Load GIF and watermark
            with Image.open(input_path) as gif:
                with Image.open(watermark_path) as watermark:
                    # Add image watermark to GIF
                    watermarked_gif = self._add_image_watermark_to_gif(
                        gif, watermark, position, opacity, scale
                    )
                    
                    # Save watermarked GIF
                    self.image_processor.save_image(
                        watermarked_gif, output_path, quality=quality, optimize=True
                    )
                    
                    return output_path
                    
        except Exception as e:
            raise ValidationError(f"GIF image watermark addition failed: {e}")
    
    def add_multiple_watermarks(self,
                               input_path: Union[str, Path],
                               output_path: Union[str, Path],
                               watermarks: List[Dict[str, Any]],
                               quality: int = 85) -> Path:
        """
        Add multiple watermarks to GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            watermarks: List of watermark dictionaries
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if not watermarks:
            raise ValidationError("No watermarks provided")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Add multiple watermarks to GIF
                watermarked_gif = self._add_multiple_watermarks_to_gif(gif, watermarks)
                
                # Save watermarked GIF
                self.image_processor.save_image(
                    watermarked_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF multiple watermarks addition failed: {e}")
    
    def get_watermark_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get watermark information for GIF.
        
        Args:
            input_path: Path to input GIF file
            
        Returns:
            Dictionary with watermark information
        """
        input_path = validate_animated_file(input_path)
        
        try:
            with Image.open(input_path) as gif:
                return {
                    'size': gif.size,
                    'width': gif.width,
                    'height': gif.height,
                    'frame_count': getattr(gif, 'n_frames', 1),
                    'is_animated': getattr(gif, 'is_animated', False),
                    'mode': gif.mode,
                    'format': gif.format,
                    'watermark_positions': list(WATERMARK_POSITIONS.keys()),
                    'supports_watermarks': True,
                    'recommended_watermark_size': {
                        'small': (gif.width // 8, gif.height // 8),
                        'medium': (gif.width // 4, gif.height // 4),
                        'large': (gif.width // 2, gif.height // 2)
                    }
                }
        except Exception as e:
            raise ValidationError(f"Failed to get watermark info: {e}")
    
    def _add_text_watermark_to_gif(self, gif: Image.Image, text: str, position: str,
                                  opacity: float, font_family: str, font_size: int,
                                  color: Tuple[int, int, int, int],
                                  background_color: Optional[Tuple[int, int, int, int]],
                                  padding: int) -> Image.Image:
        """
        Add text watermark to animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            text: Watermark text
            position: Watermark position
            opacity: Watermark opacity
            font_family: Font family
            font_size: Font size
            color: Text color
            background_color: Background color
            padding: Padding around text
            
        Returns:
            Watermarked GIF
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, simple watermark addition
            return self._add_text_watermark_to_frame(
                gif, text, position, opacity, font_family, font_size,
                color, background_color, padding
            )
        
        # Animated GIF - add watermark to each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                
                # Add watermark to frame
                watermarked_frame = self._add_text_watermark_to_frame(
                    gif, text, position, opacity, font_family, font_size,
                    color, background_color, padding
                )
                frames.append(watermarked_frame)
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_text_watermark.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=True
                )
                
                # Load the saved GIF
                return Image.open('temp_text_watermark.gif')
            else:
                return self._add_text_watermark_to_frame(
                    gif, text, position, opacity, font_family, font_size,
                    color, background_color, padding
                )
                
        except Exception as e:
            # Fallback to single frame watermark
            return self._add_text_watermark_to_frame(
                gif, text, position, opacity, font_family, font_size,
                color, background_color, padding
            )
    
    def _add_image_watermark_to_gif(self, gif: Image.Image, watermark: Image.Image,
                                   position: str, opacity: float, scale: float) -> Image.Image:
        """
        Add image watermark to animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            watermark: Watermark image
            position: Watermark position
            opacity: Watermark opacity
            scale: Scale factor
            
        Returns:
            Watermarked GIF
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, simple watermark addition
            return self._add_image_watermark_to_frame(gif, watermark, position, opacity, scale)
        
        # Animated GIF - add watermark to each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                
                # Add watermark to frame
                watermarked_frame = self._add_image_watermark_to_frame(
                    gif, watermark, position, opacity, scale
                )
                frames.append(watermarked_frame)
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_image_watermark.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=True
                )
                
                # Load the saved GIF
                return Image.open('temp_image_watermark.gif')
            else:
                return self._add_image_watermark_to_frame(gif, watermark, position, opacity, scale)
                
        except Exception as e:
            # Fallback to single frame watermark
            return self._add_image_watermark_to_frame(gif, watermark, position, opacity, scale)
    
    def _add_multiple_watermarks_to_gif(self, gif: Image.Image, watermarks: List[Dict[str, Any]]) -> Image.Image:
        """
        Add multiple watermarks to animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            watermarks: List of watermark dictionaries
            
        Returns:
            Watermarked GIF
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, add watermarks to single frame
            result = gif.copy()
            for watermark_info in watermarks:
                result = self._apply_watermark_to_frame(result, watermark_info)
            return result
        
        # Animated GIF - add watermarks to each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                result_frame = gif.copy()
                
                # Add all watermarks to frame
                for watermark_info in watermarks:
                    result_frame = self._apply_watermark_to_frame(result_frame, watermark_info)
                
                frames.append(result_frame)
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_multiple_watermarks.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=True
                )
                
                # Load the saved GIF
                return Image.open('temp_multiple_watermarks.gif')
            else:
                result = gif.copy()
                for watermark_info in watermarks:
                    result = self._apply_watermark_to_frame(result, watermark_info)
                return result
                
        except Exception as e:
            # Fallback to single frame processing
            result = gif.copy()
            for watermark_info in watermarks:
                result = self._apply_watermark_to_frame(result, watermark_info)
            return result
    
    def _add_text_watermark_to_frame(self, frame: Image.Image, text: str, position: str,
                                    opacity: float, font_family: str, font_size: int,
                                    color: Tuple[int, int, int, int],
                                    background_color: Optional[Tuple[int, int, int, int]],
                                    padding: int) -> Image.Image:
        """
        Add text watermark to single frame.
        
        Args:
            frame: PIL Image object
            text: Watermark text
            position: Watermark position
            opacity: Watermark opacity
            font_family: Font family
            font_size: Font size
            color: Text color
            background_color: Background color
            padding: Padding around text
            
        Returns:
            Watermarked frame
        """
        try:
            # Create a copy of the frame
            result = frame.copy()
            
            # Get frame dimensions
            width, height = result.size
            
            # Create text image
            text_image = self._create_text_image(
                text, font_family, font_size, color, background_color, padding
            )
            
            # Resize watermark if needed
            max_width = width // 4
            max_height = height // 4
            if text_image.width > max_width or text_image.height > max_height:
                text_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Apply opacity
            if opacity < 1.0:
                text_image = text_image.convert('RGBA')
                alpha = text_image.split()[-1]
                alpha = alpha.point(lambda x: int(x * opacity))
                text_image.putalpha(alpha)
            
            # Calculate position
            x, y = self._calculate_watermark_position(
                width, height, text_image.width, text_image.height, position
            )
            
            # Paste watermark
            if text_image.mode == 'RGBA':
                result.paste(text_image, (x, y), text_image)
            else:
                result.paste(text_image, (x, y))
            
            return result
            
        except Exception as e:
            return frame.copy()
    
    def _add_image_watermark_to_frame(self, frame: Image.Image, watermark: Image.Image,
                                     position: str, opacity: float, scale: float) -> Image.Image:
        """
        Add image watermark to single frame.
        
        Args:
            frame: PIL Image object
            watermark: Watermark image
            position: Watermark position
            opacity: Watermark opacity
            scale: Scale factor
            
        Returns:
            Watermarked frame
        """
        try:
            # Create a copy of the frame
            result = frame.copy()
            
            # Get frame dimensions
            width, height = result.size
            
            # Resize watermark
            watermark_width = int(width * scale)
            watermark_height = int(height * scale)
            watermark_resized = watermark.resize(
                (watermark_width, watermark_height), Image.Resampling.LANCZOS
            )
            
            # Apply opacity
            if opacity < 1.0:
                watermark_resized = watermark_resized.convert('RGBA')
                alpha = watermark_resized.split()[-1]
                alpha = alpha.point(lambda x: int(x * opacity))
                watermark_resized.putalpha(alpha)
            
            # Calculate position
            x, y = self._calculate_watermark_position(
                width, height, watermark_width, watermark_height, position
            )
            
            # Paste watermark
            if watermark_resized.mode == 'RGBA':
                result.paste(watermark_resized, (x, y), watermark_resized)
            else:
                result.paste(watermark_resized, (x, y))
            
            return result
            
        except Exception as e:
            return frame.copy()
    
    def _apply_watermark_to_frame(self, frame: Image.Image, watermark_info: Dict[str, Any]) -> Image.Image:
        """
        Apply watermark to frame based on watermark info.
        
        Args:
            frame: PIL Image object
            watermark_info: Watermark information dictionary
            
        Returns:
            Watermarked frame
        """
        watermark_type = watermark_info.get('type', 'text')
        
        if watermark_type == 'text':
            return self._add_text_watermark_to_frame(
                frame,
                watermark_info['text'],
                watermark_info.get('position', 'bottom_right'),
                watermark_info.get('opacity', 0.7),
                watermark_info.get('font_family', 'Arial'),
                watermark_info.get('font_size', 24),
                validate_color(watermark_info.get('color', (255, 255, 255))),
                validate_color(watermark_info.get('background_color')) if watermark_info.get('background_color') else None,
                watermark_info.get('padding', 10)
            )
        elif watermark_type == 'image':
            with Image.open(watermark_info['image_path']) as watermark:
                return self._add_image_watermark_to_frame(
                    frame,
                    watermark,
                    watermark_info.get('position', 'bottom_right'),
                    watermark_info.get('opacity', 0.7),
                    watermark_info.get('scale', 0.2)
                )
        else:
            return frame.copy()
    
    def _create_text_image(self, text: str, font_family: str, font_size: int,
                          color: Tuple[int, int, int, int],
                          background_color: Optional[Tuple[int, int, int, int]],
                          padding: int) -> Image.Image:
        """
        Create text image for watermark.
        
        Args:
            text: Text to render
            font_family: Font family
            font_size: Font size
            color: Text color
            background_color: Background color
            padding: Padding around text
            
        Returns:
            Text image
        """
        try:
            # Try to load font
            try:
                font = ImageFont.truetype(font_family, font_size)
            except (OSError, IOError):
                # Fallback to default font
                font = ImageFont.load_default()
            
            # Get text size
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Create image
            image_width = text_width + 2 * padding
            image_height = text_height + 2 * padding
            
            if background_color:
                image = Image.new('RGBA', (image_width, image_height), background_color)
            else:
                image = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))
            
            # Draw text
            draw = ImageDraw.Draw(image)
            draw.text((padding, padding), text, font=font, fill=color)
            
            return image
            
        except Exception as e:
            # Fallback to simple text
            return Image.new('RGBA', (100, 30), (0, 0, 0, 0))
    
    def _calculate_watermark_position(self, frame_width: int, frame_height: int,
                                     watermark_width: int, watermark_height: int,
                                     position: str) -> Tuple[int, int]:
        """
        Calculate watermark position.
        
        Args:
            frame_width: Frame width
            frame_height: Frame height
            watermark_width: Watermark width
            watermark_height: Watermark height
            position: Position string
            
        Returns:
            (x, y) coordinates
        """
        if position == 'top_left':
            return (10, 10)
        elif position == 'top_right':
            return (frame_width - watermark_width - 10, 10)
        elif position == 'bottom_left':
            return (10, frame_height - watermark_height - 10)
        elif position == 'bottom_right':
            return (frame_width - watermark_width - 10, frame_height - watermark_height - 10)
        elif position == 'center':
            return ((frame_width - watermark_width) // 2, (frame_height - watermark_height) // 2)
        elif position == 'top_center':
            return ((frame_width - watermark_width) // 2, 10)
        elif position == 'bottom_center':
            return ((frame_width - watermark_width) // 2, frame_height - watermark_height - 10)
        elif position == 'left_center':
            return (10, (frame_height - watermark_height) // 2)
        elif position == 'right_center':
            return (frame_width - watermark_width - 10, (frame_height - watermark_height) // 2)
        else:
            return (10, 10)  # Default to top-left


def add_text_watermark_to_gif(input_path: Union[str, Path],
                             output_path: Union[str, Path],
                             text: str,
                             **kwargs) -> Path:
    """
    Add text watermark to GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        text: Watermark text
        **kwargs: Additional watermark parameters
        
    Returns:
        Path to output GIF file
    """
    watermarker = GifWatermarker()
    return watermarker.add_text_watermark(input_path, output_path, text, **kwargs)


def add_image_watermark_to_gif(input_path: Union[str, Path],
                              output_path: Union[str, Path],
                              watermark_path: Union[str, Path],
                              **kwargs) -> Path:
    """
    Add image watermark to GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        watermark_path: Path to watermark image
        **kwargs: Additional watermark parameters
        
    Returns:
        Path to output GIF file
    """
    watermarker = GifWatermarker()
    return watermarker.add_image_watermark(input_path, output_path, watermark_path, **kwargs)


def add_multiple_watermarks_to_gif(input_path: Union[str, Path],
                                  output_path: Union[str, Path],
                                  watermarks: List[Dict[str, Any]],
                                  **kwargs) -> Path:
    """
    Add multiple watermarks to GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        watermarks: List of watermark dictionaries
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    watermarker = GifWatermarker()
    return watermarker.add_multiple_watermarks(input_path, output_path, watermarks, **kwargs)


def get_gif_watermark_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get watermark information for GIF.
    
    Args:
        input_path: Path to input GIF file
        
    Returns:
        Dictionary with watermark information
    """
    watermarker = GifWatermarker()
    return watermarker.get_watermark_info(input_path)


# Export all functions and classes
__all__ = [
    'GifWatermarker',
    'add_text_watermark_to_gif',
    'add_image_watermark_to_gif',
    'add_multiple_watermarks_to_gif',
    'get_gif_watermark_info'
]
