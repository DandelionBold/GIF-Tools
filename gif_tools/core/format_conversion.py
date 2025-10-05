"""
GIF format conversion module.

This module provides functionality to convert between different animated
image formats including GIF, WebP, and APNG.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from PIL import Image

from ..utils import (
    SUPPORTED_ANIMATED_FORMATS,
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_output_path,
    get_image_processor
)


class GifFormatConverter:
    """GIF format conversion utility class."""
    
    def __init__(self) -> None:
        """Initialize GIF format converter."""
        self.image_processor = get_image_processor()
    
    def convert_format(self,
                      input_path: Union[str, Path],
                      output_path: Union[str, Path],
                      target_format: str,
                      quality: int = 85,
                      lossless: bool = False,
                      **kwargs) -> Path:
        """
        Convert GIF to different animated format.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output file
            target_format: Target format (GIF, WebP, APNG)
            quality: Output quality for lossy formats (1-100)
            lossless: Whether to use lossless compression
            **kwargs: Additional format-specific parameters
            
        Returns:
            Path to output file
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        target_format = target_format.upper()
        # Check if format is supported (with or without dot)
        format_extensions = [fmt.upper() for fmt in SUPPORTED_ANIMATED_FORMATS]
        if target_format not in format_extensions and f".{target_format}" not in format_extensions:
            raise ValidationError(f"Unsupported target format: {target_format}")
        
        if not 1 <= quality <= 100:
            raise ValidationError("Quality must be between 1 and 100")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    # Single frame GIF - convert to static image
                    return self._convert_single_frame(gif, output_path, target_format, quality, lossless, **kwargs)
                
                # Convert animated GIF
                converted_gif = self._convert_animated_gif(gif, target_format, quality, lossless, **kwargs)
                
                # Save converted file
                self.image_processor.save_image(
                    converted_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF format conversion failed: {e}")
    
    def convert_to_webp(self,
                       input_path: Union[str, Path],
                       output_path: Union[str, Path],
                       quality: int = 85,
                       lossless: bool = False,
                       method: int = 6,
                       **kwargs: Any) -> Path:
        """
        Convert GIF to WebP format.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output WebP file
            quality: Output quality (1-100)
            lossless: Whether to use lossless compression
            method: Compression method (0-6)
            **kwargs: Additional WebP parameters
            
        Returns:
            Path to output WebP file
        """
        if not 0 <= method <= 6:
            raise ValidationError("Method must be between 0 and 6")
        
        return self.convert_format(
            input_path, output_path, 'WEBP', quality, lossless, method=method, **kwargs
        )
    
    def convert_to_apng(self,
                       input_path: Union[str, Path],
                       output_path: Union[str, Path],
                       quality: int = 85,
                       **kwargs: Any) -> Path:
        """
        Convert GIF to APNG format.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output APNG file
            quality: Output quality (1-100)
            **kwargs: Additional APNG parameters
            
        Returns:
            Path to output APNG file
        """
        return self.convert_format(
            input_path, output_path, 'APNG', quality, False, **kwargs
        )
    
    def convert_to_gif(self,
                      input_path: Union[str, Path],
                      output_path: Union[str, Path],
                      quality: int = 85,
                      optimize: bool = True,
                      **kwargs: Any) -> Path:
        """
        Convert other formats to GIF.
        
        Args:
            input_path: Path to input file
            output_path: Path to output GIF file
            quality: Output quality (1-100)
            optimize: Whether to optimize the GIF
            **kwargs: Additional GIF parameters
            
        Returns:
            Path to output GIF file
        """
        return self.convert_format(
            input_path, output_path, 'GIF', quality, False, optimize=optimize, **kwargs
        )
    
    def get_conversion_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get conversion information for file.
        
        Args:
            input_path: Path to input file
            
        Returns:
            Dictionary with conversion information
        """
        input_path = validate_animated_file(input_path)
        
        try:
            with Image.open(input_path) as gif:
                frame_count = getattr(gif, 'n_frames', 1)
                is_animated = getattr(gif, 'is_animated', False)
                current_format = gif.format
                
                return {
                    'frame_count': frame_count,
                    'is_animated': is_animated,
                    'current_format': current_format,
                    'size': gif.size,
                    'width': gif.width,
                    'height': gif.height,
                    'mode': gif.mode,
                    'supported_formats': SUPPORTED_ANIMATED_FORMATS,
                    'can_convert': True,
                    'conversion_options': self._get_conversion_options(current_format),
                    'message': f'Can convert {current_format} to other animated formats'
                }
        except Exception as e:
            raise ValidationError(f"Failed to get conversion info: {e}")
    
    def _convert_single_frame(self, gif: Image.Image, output_path: Path,
                             target_format: str, quality: int, lossless: bool,
                             **kwargs: Any) -> Path:
        """
        Convert single frame to target format.
        
        Args:
            gif: PIL Image object
            output_path: Output file path
            target_format: Target format
            quality: Output quality
            lossless: Whether to use lossless compression
            **kwargs: Additional parameters
            
        Returns:
            Path to output file
        """
        try:
            # Convert to target format
            if target_format == 'WEBP':
                gif.save(
                    output_path,
                    format='WEBP',
                    quality=quality,
                    lossless=lossless,
                    method=kwargs.get('method', 6),
                    optimize=True
                )
            elif target_format == 'APNG':
                # APNG conversion (PIL doesn't support APNG directly)
                # Fallback to PNG for now
                gif.save(output_path, format='PNG', optimize=True)
            else:  # GIF
                gif.save(
                    output_path,
                    format='GIF',
                    quality=quality,
                    optimize=kwargs.get('optimize', True)
                )
            
            return output_path
        except Exception as e:
            raise ValidationError(f"Single frame conversion failed: {e}")
    
    def _convert_animated_gif(self, gif: Image.Image, target_format: str,
                             quality: int, lossless: bool, **kwargs: Any) -> Image.Image:
        """
        Convert animated GIF to target format.
        
        Args:
            gif: PIL Image object (GIF)
            target_format: Target format
            quality: Output quality
            lossless: Whether to use lossless compression
            **kwargs: Additional parameters
            
        Returns:
            Converted image
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
            
            # Create new image in target format
            if frames:
                new_gif = frames[0].copy()
                
                if target_format == 'WEBP':
                    new_gif.save(
                        'temp_convert.webp',
                        save_all=True,
                        append_images=frames[1:],
                        duration=durations,
                        format='WEBP',
                        quality=quality,
                        lossless=lossless,
                        method=kwargs.get('method', 6),
                        optimize=True
                    )
                elif target_format == 'APNG':
                    # APNG conversion (PIL doesn't support APNG directly)
                    # Fallback to PNG for now
                    new_gif.save(
                        'temp_convert.png',
                        save_all=True,
                        append_images=frames[1:],
                        duration=durations,
                        format='PNG',
                        optimize=True
                    )
                else:  # GIF
                    new_gif.save(
                        'temp_convert.gif',
                        save_all=True,
                        append_images=frames[1:],
                        duration=durations,
                        loop=gif.info.get('loop', 0),
                        format='GIF',
                        quality=quality,
                        optimize=kwargs.get('optimize', True)
                    )
                
                # Load the saved image
                return Image.open('temp_convert.webp' if target_format == 'WEBP' 
                                else 'temp_convert.png' if target_format == 'APNG'
                                else 'temp_convert.gif')
            else:
                return gif.copy()
                
        except Exception as e:
            # Fallback to original GIF
            return gif.copy()
    
    def _get_conversion_options(self, current_format: str) -> Dict[str, Any]:
        """
        Get conversion options for current format.
        
        Args:
            current_format: Current file format
            
        Returns:
            Dictionary with conversion options
        """
        options = {
            'GIF': {
                'can_convert_to': ['WEBP', 'APNG'],
                'supports_animation': True,
                'supports_transparency': True,
                'supports_lossless': True
            },
            'WEBP': {
                'can_convert_to': ['GIF', 'APNG'],
                'supports_animation': True,
                'supports_transparency': True,
                'supports_lossless': True
            },
            'APNG': {
                'can_convert_to': ['GIF', 'WEBP'],
                'supports_animation': True,
                'supports_transparency': True,
                'supports_lossless': True
            }
        }
        
        return options.get(current_format, {
            'can_convert_to': ['GIF', 'WEBP', 'APNG'],
            'supports_animation': False,
            'supports_transparency': False,
            'supports_lossless': False
        })


def convert_gif_format(input_path: Union[str, Path],
                      output_path: Union[str, Path],
                      target_format: str,
                      **kwargs: Any) -> Path:
    """
    Convert GIF to different animated format.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output file
        target_format: Target format
        **kwargs: Additional parameters
        
    Returns:
        Path to output file
    """
    converter = GifFormatConverter()
    return converter.convert_format(input_path, output_path, target_format, **kwargs)


def convert_gif_to_webp(input_path: Union[str, Path],
                       output_path: Union[str, Path],
                       **kwargs: Any) -> Path:
    """
    Convert GIF to WebP format.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output WebP file
        **kwargs: Additional parameters
        
    Returns:
        Path to output WebP file
    """
    converter = GifFormatConverter()
    return converter.convert_to_webp(input_path, output_path, **kwargs)


def convert_gif_to_apng(input_path: Union[str, Path],
                       output_path: Union[str, Path],
                       **kwargs: Any) -> Path:
    """
    Convert GIF to APNG format.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output APNG file
        **kwargs: Additional parameters
        
    Returns:
        Path to output APNG file
    """
    converter = GifFormatConverter()
    return converter.convert_to_apng(input_path, output_path, **kwargs)


def convert_to_gif(input_path: Union[str, Path],
                  output_path: Union[str, Path],
                  **kwargs: Any) -> Path:
    """
    Convert other formats to GIF.
    
    Args:
        input_path: Path to input file
        output_path: Path to output GIF file
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    converter = GifFormatConverter()
    return converter.convert_to_gif(input_path, output_path, **kwargs)


def get_gif_conversion_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get conversion information for file.
    
    Args:
        input_path: Path to input file
        
    Returns:
        Dictionary with conversion information
    """
    converter = GifFormatConverter()
    return converter.get_conversion_info(input_path)


# Export all functions and classes
__all__ = [
    'GifFormatConverter',
    'convert_gif_format',
    'convert_gif_to_webp',
    'convert_gif_to_apng',
    'convert_to_gif',
    'get_gif_conversion_info'
]
