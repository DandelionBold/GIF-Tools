"""
Image processing utilities for GIF-Tools.

This module provides common image processing functions, format conversions,
and image manipulation utilities used throughout the GIF-Tools library.
"""

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

from .constants import (
    COLOR_MODES,
    DEFAULT_FONT,
    DEFAULT_OPTIMIZATION,
    DEFAULT_QUALITY,
    DEFAULT_RESIZE,
    DEFAULT_TEXT,
    FILTER_EFFECTS,
    QUALITY_LEVELS,
    TEXT_ALIGNMENT,
    WATERMARK_POSITIONS
)
from .validation import ValidationError, validate_color, validate_dimensions, validate_position


class ImageProcessor:
    """Image processing utility class."""
    
    def __init__(self):
        """Initialize image processor."""
        self._font_cache: Dict[str, ImageFont.FreeTypeFont] = {}
    
    def load_image(self, file_path: Union[str, Path]) -> Image.Image:
        """
        Load image from file.
        
        Args:
            file_path: Path to image file
            
        Returns:
            PIL Image object
            
        Raises:
            ValidationError: If image cannot be loaded
        """
        try:
            path = Path(file_path)
            image = Image.open(path)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                image = background
            elif image.mode not in COLOR_MODES:
                image = image.convert('RGB')
            
            return image
        except Exception as e:
            raise ValidationError(f"Failed to load image: {e}")
    
    def save_image(self, image: Image.Image, 
                  file_path: Union[str, Path],
                  format: Optional[str] = None,
                  quality: int = DEFAULT_QUALITY,
                  optimize: bool = True,
                  **kwargs) -> Path:
        """
        Save image to file.
        
        Args:
            image: PIL Image object
            file_path: Output file path
            format: Output format (auto-detected from extension if None)
            quality: Image quality (1-100)
            optimize: Whether to optimize the image
            **kwargs: Additional save parameters
            
        Returns:
            Output file path
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if it's an animated GIF
            is_animated = getattr(image, 'is_animated', False)
            file_format = format or path.suffix[1:].upper()
            
            if is_animated and file_format.upper() == 'GIF':
                # For animated GIFs, we need to save with specific parameters
                save_kwargs = {
                    'format': 'GIF',
                    'save_all': True,
                    'optimize': optimize,
                    'disposal': 2,
                    'transparency': 0
                }
                save_kwargs.update(kwargs)
                image.save(path, **save_kwargs)
            else:
                # For static images, use regular save
                save_kwargs = {
                    'format': file_format,
                    'quality': quality,
                    'optimize': optimize
                }
                save_kwargs.update(kwargs)
                image.save(path, **save_kwargs)
            
            return path
        except Exception as e:
            raise ValidationError(f"Failed to save image: {e}")
    
    def get_image_info(self, image: Image.Image) -> Dict[str, Any]:
        """
        Get image information.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with image information
        """
        return {
            'size': image.size,
            'width': image.width,
            'height': image.height,
            'mode': image.mode,
            'format': image.format,
            'has_transparency': image.mode in ('RGBA', 'LA', 'P'),
            'aspect_ratio': image.width / image.height,
            'pixel_count': image.width * image.height,
            'memory_size': image.width * image.height * len(image.getbands()) * 8  # bits
        }
    
    def resize_image(self, image: Image.Image,
                    width: Optional[int] = None,
                    height: Optional[int] = None,
                    size: Optional[Tuple[int, int]] = None,
                    maintain_aspect_ratio: bool = True,
                    resample: int = Image.Resampling.LANCZOS) -> Image.Image:
        """
        Resize image.
        
        Args:
            image: PIL Image object
            width: Target width
            height: Target height
            size: Target size as (width, height) tuple
            maintain_aspect_ratio: Whether to maintain aspect ratio
            resample: Resampling method
            
        Returns:
            Resized image
        """
        if size:
            width, height = size
        
        if width is None and height is None:
            raise ValidationError("Either width, height, or size must be specified")
        
        if maintain_aspect_ratio:
            if width is None:
                width = int(image.width * height / image.height)
            elif height is None:
                height = int(image.height * width / image.width)
        
        # Validate dimensions
        validate_dimensions(width, height)
        
        return image.resize((width, height), resample)
    
    def crop_image(self, image: Image.Image,
                  x: int, y: int, width: int, height: int) -> Image.Image:
        """
        Crop image.
        
        Args:
            image: PIL Image object
            x: Left coordinate
            y: Top coordinate
            width: Crop width
            height: Crop height
            
        Returns:
            Cropped image
        """
        # Validate crop coordinates
        validate_dimensions(width, height)
        
        if x < 0 or y < 0:
            raise ValidationError("Crop coordinates must be non-negative")
        
        if x + width > image.width or y + height > image.height:
            raise ValidationError("Crop area exceeds image bounds")
        
        return image.crop((x, y, x + width, y + height))
    
    def rotate_image(self, image: Image.Image, angle: int) -> Image.Image:
        """
        Rotate image.
        
        Args:
            image: PIL Image object
            angle: Rotation angle (90, 180, or 270)
            
        Returns:
            Rotated image
        """
        if angle not in [90, 180, 270]:
            raise ValidationError(f"Invalid rotation angle: {angle}")
        
        return image.rotate(angle, expand=True)
    
    def flip_image(self, image: Image.Image, 
                  horizontal: bool = False, 
                  vertical: bool = False) -> Image.Image:
        """
        Flip image.
        
        Args:
            image: PIL Image object
            horizontal: Flip horizontally
            vertical: Flip vertically
            
        Returns:
            Flipped image
        """
        if horizontal and vertical:
            return image.transpose(Image.Transpose.ROTATE_180)
        elif horizontal:
            return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif vertical:
            return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        else:
            return image.copy()
    
    def apply_filter(self, image: Image.Image, filter_name: str, intensity: float = 1.0) -> Image.Image:
        """
        Apply filter to image.
        
        Args:
            image: PIL Image object
            filter_name: Name of filter to apply
            intensity: Filter intensity (for enhancement filters)
            
        Returns:
            Filtered image
        """
        if filter_name not in FILTER_EFFECTS:
            raise ValidationError(f"Unknown filter: {filter_name}")
        
        # Handle enhancement filters specially
        if filter_name == 'brightness':
            return self.adjust_brightness(image, intensity)
        elif filter_name == 'contrast':
            return self.adjust_contrast(image, intensity)
        elif filter_name == 'saturation':
            return self.adjust_saturation(image, intensity)
        elif filter_name == 'color':
            return self.adjust_color(image, intensity)
        else:
            # Handle basic PIL filters
            filter_method = getattr(ImageFilter, FILTER_EFFECTS[filter_name])
            return image.filter(filter_method)
    
    def adjust_brightness(self, image: Image.Image, factor: float) -> Image.Image:
        """
        Adjust image brightness.
        
        Args:
            image: PIL Image object
            factor: Brightness factor (1.0 = no change, >1.0 = brighter, <1.0 = darker)
            
        Returns:
            Adjusted image
        """
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
    
    def adjust_contrast(self, image: Image.Image, factor: float) -> Image.Image:
        """
        Adjust image contrast.
        
        Args:
            image: PIL Image object
            factor: Contrast factor (1.0 = no change, >1.0 = more contrast, <1.0 = less contrast)
            
        Returns:
            Adjusted image
        """
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    def adjust_saturation(self, image: Image.Image, factor: float) -> Image.Image:
        """
        Adjust image saturation.
        
        Args:
            image: PIL Image object
            factor: Saturation factor (1.0 = no change, >1.0 = more saturated, <1.0 = less saturated)
            
        Returns:
            Adjusted image
        """
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(factor)
    
    def adjust_sharpness(self, image: Image.Image, factor: float) -> Image.Image:
        """
        Adjust image sharpness.
        
        Args:
            image: PIL Image object
            factor: Sharpness factor (1.0 = no change, >1.0 = sharper, <1.0 = softer)
            
        Returns:
            Adjusted image
        """
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)
    
    def add_text(self, image: Image.Image,
                text: str,
                position: Tuple[int, int] = (10, 10),
                font_family: str = DEFAULT_FONT['family'],
                font_size: int = DEFAULT_FONT['size'],
                color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]] = DEFAULT_FONT['color'],
                text_opacity: float = 1.0,
                alignment: str = 'left',
                background_color: Optional[Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]] = None,
                background_opacity: float = 0.0,
                stroke_width: int = 0,
                stroke_color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]] = (0, 0, 0),
                stroke_opacity: float = 1.0) -> Image.Image:
        """
        Add text to image.
        
        Args:
            image: PIL Image object
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
            
        Returns:
            Image with text added
        """
        if not text:
            return image.copy()
        
        # Validate inputs
        position = validate_position(position)
        color = validate_color(color)
        stroke_color = validate_color(stroke_color)
        
        if background_color is not None:
            background_color = validate_color(background_color)
        
        if alignment not in TEXT_ALIGNMENT:
            raise ValidationError(f"Invalid alignment: {alignment}")
        
        # Create a copy to work with
        result = image.copy()
        draw = ImageDraw.Draw(result)
        
        # Get font
        try:
            font = self._get_font(font_family, font_size)
        except Exception:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Adjust position based on alignment
        x, y = position
        if alignment in ['center', 'middle']:
            x = x - text_width // 2
        elif alignment == 'right':
            x = x - text_width
        
        if alignment in ['middle', 'bottom']:
            y = y - text_height // 2 if alignment == 'middle' else y - text_height
        
        # Draw background if specified
        if background_color and background_opacity > 0:
            bg_alpha = int(255 * background_opacity)
            bg_color = background_color[:3] + (bg_alpha,)
            
            # Create background rectangle
            bg_x1 = x - 5
            bg_y1 = y - 5
            bg_x2 = x + text_width + 5
            bg_y2 = y + text_height + 5
            
            # Draw background
            bg_image = Image.new('RGBA', result.size, (0, 0, 0, 0))
            bg_draw = ImageDraw.Draw(bg_image)
            bg_draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=bg_color)
            
            # Composite background
            result = Image.alpha_composite(result.convert('RGBA'), bg_image).convert(result.mode)
            draw = ImageDraw.Draw(result)
        
        # Apply opacity to colors
        text_alpha = int(255 * text_opacity)
        text_color_with_alpha = color[:3] + (text_alpha,)
        
        stroke_alpha = int(255 * stroke_opacity)
        stroke_color_with_alpha = stroke_color[:3] + (stroke_alpha,)
        
        # Draw text stroke if specified
        if stroke_width > 0:
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text, font=font, fill=stroke_color_with_alpha)
        
        # Draw text
        draw.text((x, y), text, font=font, fill=text_color_with_alpha)
        
        return result
    
    def add_watermark(self, image: Image.Image,
                     watermark: Union[str, Image.Image],
                     position: str = 'bottom_right',
                     opacity: float = 0.7,
                     scale: float = 1.0,
                     margin: int = 10) -> Image.Image:
        """
        Add watermark to image.
        
        Args:
            image: PIL Image object
            watermark: Watermark text or image
            position: Watermark position
            opacity: Watermark opacity (0.0-1.0)
            scale: Watermark scale factor
            margin: Margin from edges
            
        Returns:
            Image with watermark added
        """
        if position not in WATERMARK_POSITIONS:
            raise ValidationError(f"Invalid watermark position: {position}")
        
        result = image.copy()
        
        if isinstance(watermark, str):
            # Text watermark
            font_size = int(24 * scale)
            color = (255, 255, 255, int(255 * opacity))
            
            # Get text size
            font = self._get_font(DEFAULT_FONT['family'], font_size)
            draw = ImageDraw.Draw(result)
            bbox = draw.textbbox((0, 0), watermark, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position
            pos_x, pos_y = WATERMARK_POSITIONS[position]
            x = int(pos_x * (result.width - text_width - margin * 2) + margin)
            y = int(pos_y * (result.height - text_height - margin * 2) + margin)
            
            # Add text watermark
            result = self.add_text(result, watermark, (x, y), 
                                 font_size=font_size, color=color)
        
        elif isinstance(watermark, Image.Image):
            # Image watermark
            # Scale watermark
            if scale != 1.0:
                new_size = (int(watermark.width * scale), int(watermark.height * scale))
                watermark = watermark.resize(new_size, Image.Resampling.LANCZOS)
            
            # Apply opacity
            if opacity < 1.0:
                watermark = watermark.convert('RGBA')
                alpha = watermark.split()[-1]
                alpha = alpha.point(lambda p: int(p * opacity))
                watermark.putalpha(alpha)
            
            # Calculate position
            pos_x, pos_y = WATERMARK_POSITIONS[position]
            x = int(pos_x * (result.width - watermark.width - margin * 2) + margin)
            y = int(pos_y * (result.height - watermark.height - margin * 2) + margin)
            
            # Paste watermark
            if result.mode != 'RGBA':
                result = result.convert('RGBA')
            
            result.paste(watermark, (x, y), watermark if watermark.mode == 'RGBA' else None)
        
        return result
    
    def optimize_image(self, image: Image.Image,
                      quality: int = DEFAULT_QUALITY,
                      optimize: bool = True,
                      colors: int = 256) -> Image.Image:
        """
        Optimize image for size.
        
        Args:
            image: PIL Image object
            quality: Image quality (1-100)
            optimize: Whether to optimize
            colors: Number of colors for palette mode
            
        Returns:
            Optimized image
        """
        result = image.copy()
        
        # Convert to palette mode if beneficial
        if result.mode == 'RGB' and colors < 256:
            result = result.quantize(colors=colors)
        
        return result
    
    def _get_font(self, font_family: str, font_size: int) -> ImageFont.FreeTypeFont:
        """
        Get font with caching.
        
        Args:
            font_family: Font family name
            font_size: Font size
            
        Returns:
            PIL Font object
        """
        cache_key = f"{font_family}_{font_size}"
        
        if cache_key not in self._font_cache:
            try:
                font = ImageFont.truetype(font_family, font_size)
            except (OSError, IOError):
                # Try common font paths
                common_fonts = [
                    'arial.ttf', 'Arial.ttf', 'arial.ttc', 'Arial.ttc',
                    'calibri.ttf', 'Calibri.ttf', 'calibri.ttc', 'Calibri.ttc',
                    'verdana.ttf', 'Verdana.ttf', 'verdana.ttc', 'Verdana.ttc'
                ]
                
                font = None
                for font_name in common_fonts:
                    try:
                        font = ImageFont.truetype(font_name, font_size)
                        break
                    except (OSError, IOError):
                        continue
                
                if font is None:
                    # Fallback to default font
                    font = ImageFont.load_default()
            
            self._font_cache[cache_key] = font
        
        return self._font_cache[cache_key]


def get_image_processor() -> ImageProcessor:
    """
    Get image processor instance.
    
    Returns:
        ImageProcessor instance
    """
    return ImageProcessor()


def load_image(file_path: Union[str, Path]) -> Image.Image:
    """
    Load image from file.
    
    Args:
        file_path: Path to image file
        
    Returns:
        PIL Image object
    """
    processor = get_image_processor()
    return processor.load_image(file_path)


def save_image(image: Image.Image, 
              file_path: Union[str, Path],
              **kwargs) -> Path:
    """
    Save image to file.
    
    Args:
        image: PIL Image object
        file_path: Output file path
        **kwargs: Additional save parameters
        
    Returns:
        Output file path
    """
    processor = get_image_processor()
    return processor.save_image(image, file_path, **kwargs)


def get_image_info(image: Image.Image) -> Dict[str, Any]:
    """
    Get image information.
    
    Args:
        image: PIL Image object
        
    Returns:
        Dictionary with image information
    """
    processor = get_image_processor()
    return processor.get_image_info(image)


def resize_image(image: Image.Image, **kwargs) -> Image.Image:
    """
    Resize image.
    
    Args:
        image: PIL Image object
        **kwargs: Resize parameters
        
    Returns:
        Resized image
    """
    processor = get_image_processor()
    return processor.resize_image(image, **kwargs)


def crop_image(image: Image.Image, **kwargs) -> Image.Image:
    """
    Crop image.
    
    Args:
        image: PIL Image object
        **kwargs: Crop parameters
        
    Returns:
        Cropped image
    """
    processor = get_image_processor()
    return processor.crop_image(image, **kwargs)


def rotate_image(image: Image.Image, angle: int) -> Image.Image:
    """
    Rotate image.
    
    Args:
        image: PIL Image object
        angle: Rotation angle
        
    Returns:
        Rotated image
    """
    processor = get_image_processor()
    return processor.rotate_image(image, angle)


def add_text(image: Image.Image, **kwargs) -> Image.Image:
    """
    Add text to image.
    
    Args:
        image: PIL Image object
        **kwargs: Text parameters
        
    Returns:
        Image with text added
    """
    processor = get_image_processor()
    return processor.add_text(image, **kwargs)


def add_watermark(image: Image.Image, **kwargs) -> Image.Image:
    """
    Add watermark to image.
    
    Args:
        image: PIL Image object
        **kwargs: Watermark parameters
        
    Returns:
        Image with watermark added
    """
    processor = get_image_processor()
    return processor.add_watermark(image, **kwargs)


# Export all functions and classes
__all__ = [
    'ImageProcessor',
    'get_image_processor',
    'load_image',
    'save_image',
    'get_image_info',
    'resize_image',
    'crop_image',
    'rotate_image',
    'add_text',
    'add_watermark'
]
