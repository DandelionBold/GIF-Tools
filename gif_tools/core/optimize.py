"""
GIF optimization module.

This module provides functionality to optimize GIFs by reducing file size
while maintaining quality through various compression techniques.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from PIL import Image

from ..utils import (
    DEFAULT_QUALITY,
    QUALITY_LEVELS,
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_output_path,
    validate_quality,
    get_image_processor
)


class GifOptimizer:
    """GIF optimization utility class."""
    
    def __init__(self) -> None:
        """Initialize GIF optimizer."""
        self.image_processor = get_image_processor()
    
    def optimize(self,
                input_path: Union[str, Path],
                output_path: Union[str, Path],
                quality: int = DEFAULT_QUALITY,
                optimize: bool = True,
                method: int = 6,
                colors: int = 256,
                dither: str = 'FLOYDSTEINBERG',
                transparency: bool = True,
                interlace: bool = False) -> Path:
        """
        Optimize GIF for size while maintaining quality.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            quality: Optimization quality (1-100)
            optimize: Whether to optimize
            method: PIL optimization method
            colors: Number of colors for palette mode
            dither: Dithering method
            transparency: Whether to preserve transparency
            interlace: Whether to use interlacing
            
        Returns:
            Path to output GIF file
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        quality = validate_quality(quality)
        
        if colors < 2 or colors > 256:
            raise ValidationError("Colors must be between 2 and 256")
        
        valid_dithers = ['NONE', 'FLOYDSTEINBERG', 'NONE']
        if dither not in valid_dithers:
            raise ValidationError(f"Invalid dither method: {dither}")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Optimize GIF
                optimized_gif = self._optimize_gif(
                    gif, quality, optimize, method, colors, dither, transparency, interlace
                )
                
                # Save optimized GIF
                self.image_processor.save_image(
                    optimized_gif, output_path, quality=quality, optimize=optimize
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF optimization failed: {e}")
    
    def optimize_by_quality(self,
                           input_path: Union[str, Path],
                           output_path: Union[str, Path],
                           quality_level: str = 'medium',
                           **kwargs) -> Path:
        """
        Optimize GIF by quality level.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            quality_level: Quality level ('low', 'medium', 'high', 'ultra')
            **kwargs: Additional optimization parameters
            
        Returns:
            Path to output GIF file
        """
        if quality_level not in QUALITY_LEVELS:
            raise ValidationError(f"Invalid quality level: {quality_level}")
        
        quality = QUALITY_LEVELS[quality_level]
        return self.optimize(input_path, output_path, quality, **kwargs)
    
    def optimize_with_info(self,
                          input_path: Union[str, Path],
                          output_path: Union[str, Path],
                          **kwargs) -> Dict[str, Any]:
        """
        Optimize GIF and return detailed information.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            **kwargs: Optimization parameters
            
        Returns:
            Dictionary with optimization information
        """
        # Get original file size
        original_size = input_path.stat().st_size
        
        # Optimize GIF
        optimized_path = self.optimize(input_path, output_path, **kwargs)
        
        # Get optimized file size
        optimized_size = optimized_path.stat().st_size
        
        # Calculate compression ratio
        compression_ratio = (original_size - optimized_size) / original_size * 100
        
        return {
            'input_path': str(input_path),
            'output_path': str(output_path),
            'original_size': original_size,
            'optimized_size': optimized_size,
            'size_reduction': original_size - optimized_size,
            'compression_ratio': round(compression_ratio, 2),
            'optimization_successful': True
        }
    
    def get_optimization_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get optimization information for GIF.
        
        Args:
            input_path: Path to input GIF file
            
        Returns:
            Dictionary with optimization information
        """
        input_path = validate_animated_file(input_path)
        
        try:
            with Image.open(input_path) as gif:
                file_size = input_path.stat().st_size
                frame_count = getattr(gif, 'n_frames', 1)
                is_animated = getattr(gif, 'is_animated', False)
                
                # Analyze color usage
                color_info = self._analyze_colors(gif)
                
                return {
                    'file_size': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2),
                    'frame_count': frame_count,
                    'is_animated': is_animated,
                    'size': gif.size,
                    'width': gif.width,
                    'height': gif.height,
                    'mode': gif.mode,
                    'format': gif.format,
                    'color_count': color_info['color_count'],
                    'unique_colors': color_info['unique_colors'],
                    'has_transparency': color_info['has_transparency'],
                    'optimization_potential': self._assess_optimization_potential(gif, color_info),
                    'recommended_settings': self._get_recommended_settings(gif, color_info)
                }
        except Exception as e:
            raise ValidationError(f"Failed to get optimization info: {e}")
    
    def _optimize_gif(self, gif: Image.Image, quality: int, optimize: bool,
                     method: int, colors: int, dither: str, transparency: bool,
                     interlace: bool) -> Image.Image:
        """
        Optimize animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            quality: Optimization quality
            optimize: Whether to optimize
            method: PIL optimization method
            colors: Number of colors
            dither: Dithering method
            transparency: Whether to preserve transparency
            interlace: Whether to use interlacing
            
        Returns:
            Optimized GIF
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, simple optimization
            return self._optimize_single_frame(gif, quality, optimize, method, colors, dither, transparency)
        
        # Animated GIF - optimize each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                
                # Optimize frame
                optimized_frame = self._optimize_single_frame(
                    gif, quality, optimize, method, colors, dither, transparency
                )
                frames.append(optimized_frame)
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_optimize.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    disposal=2,  # Clear to background
                    transparency=0,
                    optimize=optimize,
                    method=method,
                    interlace=interlace
                )
                
                # Load the saved GIF
                return Image.open('temp_optimize.gif')
            else:
                return self._optimize_single_frame(gif, quality, optimize, method, colors, dither, transparency)
                
        except Exception as e:
            # Fallback to single frame optimization
            return self._optimize_single_frame(gif, quality, optimize, method, colors, dither, transparency)
    
    def _optimize_single_frame(self, gif: Image.Image, quality: int, optimize: bool,
                              method: int, colors: int, dither: str, transparency: bool) -> Image.Image:
        """
        Optimize single frame.
        
        Args:
            gif: PIL Image object
            quality: Optimization quality
            optimize: Whether to optimize
            method: PIL optimization method
            colors: Number of colors
            dither: Dithering method
            transparency: Whether to preserve transparency
            
        Returns:
            Optimized frame
        """
        # Convert to palette mode if beneficial
        if gif.mode in ('RGB', 'RGBA') and colors < 256:
            if transparency and gif.mode == 'RGBA':
                # Preserve transparency
                gif = gif.convert('RGBA')
                palette = gif.quantize(colors=colors, method=method)
                gif = palette.convert('RGBA')
            else:
                # Convert to palette mode
                gif = gif.quantize(colors=colors, method=method)
        
        return gif
    
    def _analyze_colors(self, gif: Image.Image) -> Dict[str, Any]:
        """
        Analyze color usage in GIF.
        
        Args:
            gif: PIL Image object
            
        Returns:
            Dictionary with color analysis
        """
        try:
            if gif.mode == 'P':
                # Palette mode - count unique colors
                palette = gif.getpalette()
                if palette:
                    unique_colors = len(set(tuple(palette[i:i+3]) for i in range(0, len(palette), 3)))
                else:
                    unique_colors = 0
            else:
                # Convert to RGB and count unique colors
                if gif.mode == 'RGBA':
                    # Check for transparency
                    has_transparency = any(pixel[3] < 255 for pixel in gif.getdata())
                    rgb_gif = gif.convert('RGB')
                else:
                    has_transparency = False
                    rgb_gif = gif.convert('RGB')
                
                unique_colors = len(set(rgb_gif.getdata()))
            
            return {
                'color_count': unique_colors,
                'unique_colors': unique_colors,
                'has_transparency': gif.mode in ('RGBA', 'LA', 'P') and 'transparency' in gif.info
            }
        except Exception:
            return {
                'color_count': 0,
                'unique_colors': 0,
                'has_transparency': False
            }
    
    def _assess_optimization_potential(self, gif: Image.Image, color_info: Dict[str, Any]) -> str:
        """
        Assess optimization potential.
        
        Args:
            gif: PIL Image object
            color_info: Color analysis information
            
        Returns:
            Optimization potential level
        """
        color_count = color_info['color_count']
        file_size = gif.size[0] * gif.size[1]
        
        if color_count > 200:
            return 'high'
        elif color_count > 100:
            return 'medium'
        else:
            return 'low'
    
    def _get_recommended_settings(self, gif: Image.Image, color_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recommended optimization settings.
        
        Args:
            gif: PIL Image object
            color_info: Color analysis information
            
        Returns:
            Dictionary with recommended settings
        """
        color_count = color_info['color_count']
        has_transparency = color_info['has_transparency']
        
        if color_count > 200:
            recommended_colors = 128
            quality_level = 'medium'
        elif color_count > 100:
            recommended_colors = 64
            quality_level = 'high'
        else:
            recommended_colors = 32
            quality_level = 'ultra'
        
        return {
            'colors': recommended_colors,
            'quality_level': quality_level,
            'optimize': True,
            'transparency': has_transparency,
            'dither': 'FLOYDSTEINBERG' if color_count > 64 else 'NONE'
        }


def optimize_gif(input_path: Union[str, Path],
                output_path: Union[str, Path],
                **kwargs) -> Path:
    """
    Optimize GIF for size while maintaining quality.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        **kwargs: Optimization parameters
        
    Returns:
        Path to output GIF file
    """
    optimizer = GifOptimizer()
    return optimizer.optimize(input_path, output_path, **kwargs)


def optimize_gif_by_quality(input_path: Union[str, Path],
                           output_path: Union[str, Path],
                           quality_level: str = 'medium',
                           **kwargs) -> Path:
    """
    Optimize GIF by quality level.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        quality_level: Quality level ('low', 'medium', 'high', 'ultra')
        **kwargs: Additional optimization parameters
        
    Returns:
        Path to output GIF file
    """
    optimizer = GifOptimizer()
    return optimizer.optimize_by_quality(input_path, output_path, quality_level, **kwargs)


def optimize_gif_with_info(input_path: Union[str, Path],
                          output_path: Union[str, Path],
                          **kwargs) -> Dict[str, Any]:
    """
    Optimize GIF and return detailed information.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        **kwargs: Optimization parameters
        
    Returns:
        Dictionary with optimization information
    """
    optimizer = GifOptimizer()
    return optimizer.optimize_with_info(input_path, output_path, **kwargs)


def get_optimization_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get optimization information for GIF.
    
    Args:
        input_path: Path to input GIF file
        
    Returns:
        Dictionary with optimization information
    """
    optimizer = GifOptimizer()
    return optimizer.get_optimization_info(input_path)


# Export all functions and classes
__all__ = [
    'GifOptimizer',
    'optimize_gif',
    'optimize_gif_by_quality',
    'optimize_gif_with_info',
    'get_optimization_info'
]
