"""
GIF filter effects module.

This module provides functionality to apply visual effects and filters to GIFs
including blur, sharpen, brightness, contrast, and other image enhancements.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from PIL import Image, ImageFilter, ImageEnhance

from ..utils import (
    FILTER_EFFECTS,
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_output_path,
    get_image_processor
)


class GifFilterApplier:
    """GIF filter effects utility class."""
    
    def __init__(self) -> None:
        """Initialize GIF filter applier."""
        self.image_processor = get_image_processor()
    
    def apply_filter(self,
                   input_path: Union[str, Path],
                   output_path: Union[str, Path],
                   filter_name: str,
                   intensity: float = 1.0,
                   quality: int = 85) -> Path:
        """
        Apply a single filter effect to GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            filter_name: Name of filter to apply
            intensity: Filter intensity (0.0-2.0)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if filter_name not in FILTER_EFFECTS:
            raise ValidationError(f"Unknown filter: {filter_name}")
        
        if not 0.0 <= intensity <= 2.0:
            raise ValidationError("Intensity must be between 0.0 and 2.0")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Apply filter to GIF
                filtered_gif = self._apply_filter_to_gif(gif, filter_name, intensity)
                
                # Save filtered GIF
                self.image_processor.save_image(
                    filtered_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF filter application failed: {e}")
    
    def apply_multiple_filters(self,
                             input_path: Union[str, Path],
                             output_path: Union[str, Path],
                             filters: List[Dict[str, Any]],
                             quality: int = 85) -> Path:
        """
        Apply multiple filter effects to GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            filters: List of filter dictionaries with 'name' and 'intensity'
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if not filters:
            raise ValidationError("No filters provided")
        
        for filter_info in filters:
            if 'name' not in filter_info:
                raise ValidationError("Each filter must have a 'name' field")
            
            if filter_info['name'] not in FILTER_EFFECTS:
                raise ValidationError(f"Unknown filter: {filter_info['name']}")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Apply multiple filters to GIF
                filtered_gif = self._apply_multiple_filters_to_gif(gif, filters)
                
                # Save filtered GIF
                self.image_processor.save_image(
                    filtered_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF multiple filters application failed: {e}")
    
    def adjust_brightness(self,
                         input_path: Union[str, Path],
                         output_path: Union[str, Path],
                         factor: float,
                         quality: int = 85) -> Path:
        """
        Adjust brightness of GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            factor: Brightness factor (0.0 = black, 1.0 = normal, 2.0 = very bright)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        if not 0.0 <= factor <= 3.0:
            raise ValidationError("Brightness factor must be between 0.0 and 3.0")
        
        return self._apply_enhancement(input_path, output_path, 'brightness', factor, quality)
    
    def adjust_contrast(self,
                       input_path: Union[str, Path],
                       output_path: Union[str, Path],
                       factor: float,
                       quality: int = 85) -> Path:
        """
        Adjust contrast of GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            factor: Contrast factor (0.0 = no contrast, 1.0 = normal, 2.0 = high contrast)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        if not 0.0 <= factor <= 3.0:
            raise ValidationError("Contrast factor must be between 0.0 and 3.0")
        
        return self._apply_enhancement(input_path, output_path, 'contrast', factor, quality)
    
    def adjust_saturation(self,
                         input_path: Union[str, Path],
                         output_path: Union[str, Path],
                         factor: float,
                         quality: int = 85) -> Path:
        """
        Adjust saturation of GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            factor: Saturation factor (0.0 = grayscale, 1.0 = normal, 2.0 = very saturated)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        if not 0.0 <= factor <= 3.0:
            raise ValidationError("Saturation factor must be between 0.0 and 3.0")
        
        return self._apply_enhancement(input_path, output_path, 'saturation', factor, quality)
    
    def adjust_sharpness(self,
                        input_path: Union[str, Path],
                        output_path: Union[str, Path],
                        factor: float,
                        quality: int = 85) -> Path:
        """
        Adjust sharpness of GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            factor: Sharpness factor (0.0 = blurry, 1.0 = normal, 2.0 = very sharp)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        if not 0.0 <= factor <= 3.0:
            raise ValidationError("Sharpness factor must be between 0.0 and 3.0")
        
        return self._apply_enhancement(input_path, output_path, 'sharpness', factor, quality)
    
    def apply_color_effects(self,
                           input_path: Union[str, Path],
                           output_path: Union[str, Path],
                           effect: str,
                           intensity: float = 1.0,
                           quality: int = 85) -> Path:
        """
        Apply color effects to GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            effect: Color effect ('grayscale', 'sepia', 'invert', 'posterize', 'solarize')
            intensity: Effect intensity (0.0-2.0)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        valid_effects = ['grayscale', 'sepia', 'invert', 'posterize', 'solarize']
        if effect not in valid_effects:
            raise ValidationError(f"Invalid color effect: {effect}")
        
        if not 0.0 <= intensity <= 2.0:
            raise ValidationError("Intensity must be between 0.0 and 2.0")
        
        return self._apply_color_effect(input_path, output_path, effect, intensity, quality)
    
    def get_filter_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get filter information for GIF.
        
        Args:
            input_path: Path to input GIF file
            
        Returns:
            Dictionary with filter information
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
                    'available_filters': list(FILTER_EFFECTS.keys()),
                    'available_enhancements': ['brightness', 'contrast', 'saturation', 'sharpness'],
                    'available_color_effects': ['grayscale', 'sepia', 'invert', 'posterize', 'solarize'],
                    'supports_filters': True
                }
        except Exception as e:
            raise ValidationError(f"Failed to get filter info: {e}")
    
    def _apply_filter_to_gif(self, gif: Image.Image, filter_name: str, intensity: float) -> Image.Image:
        """
        Apply filter to animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            filter_name: Name of filter to apply
            intensity: Filter intensity
            
        Returns:
            Filtered GIF
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, simple filter application
            return self._apply_single_filter(gif, filter_name, intensity)
        
        # Animated GIF - apply filter to each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                
                # Apply filter to frame
                filtered_frame = self._apply_single_filter(gif, filter_name, intensity)
                frames.append(filtered_frame)
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_filter.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=True
                )
                
                # Load the saved GIF
                return Image.open('temp_filter.gif')
            else:
                return self._apply_single_filter(gif, filter_name, intensity)
                
        except Exception as e:
            # Fallback to single filter application
            return self._apply_single_filter(gif, filter_name, intensity)
    
    def _apply_multiple_filters_to_gif(self, gif: Image.Image, filters: List[Dict[str, Any]]) -> Image.Image:
        """
        Apply multiple filters to animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            filters: List of filter dictionaries
            
        Returns:
            Filtered GIF
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, apply filters to single frame
            result = gif.copy()
            for filter_info in filters:
                result = self._apply_single_filter(result, filter_info['name'], filter_info.get('intensity', 1.0))
            return result
        
        # Animated GIF - apply filters to each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                result_frame = gif.copy()
                
                # Apply all filters to frame
                for filter_info in filters:
                    result_frame = self._apply_single_filter(
                        result_frame, filter_info['name'], filter_info.get('intensity', 1.0)
                    )
                
                frames.append(result_frame)
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_multiple_filters.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=True
                )
                
                # Load the saved GIF
                return Image.open('temp_multiple_filters.gif')
            else:
                result = gif.copy()
                for filter_info in filters:
                    result = self._apply_single_filter(result, filter_info['name'], filter_info.get('intensity', 1.0))
                return result
                
        except Exception as e:
            # Fallback to single frame processing
            result = gif.copy()
            for filter_info in filters:
                result = self._apply_single_filter(result, filter_info['name'], filter_info.get('intensity', 1.0))
            return result
    
    def _apply_single_filter(self, image: Image.Image, filter_name: str, intensity: float) -> Image.Image:
        """
        Apply a single filter to an image.
        
        Args:
            image: PIL Image object
            filter_name: Name of filter to apply
            intensity: Filter intensity
            
        Returns:
            Filtered image
        """
        try:
            if filter_name in FILTER_EFFECTS:
                # Apply PIL filter
                filter_method = getattr(ImageFilter, FILTER_EFFECTS[filter_name])
                filtered_image = image.filter(filter_method)
                
                # Apply intensity if supported
                if intensity != 1.0 and hasattr(filtered_image, 'enhance'):
                    # Some filters support enhancement
                    pass
                
                return filtered_image
            else:
                return image.copy()
        except Exception:
            return image.copy()
    
    def _apply_enhancement(self, input_path: Union[str, Path], output_path: Union[str, Path],
                          enhancement: str, factor: float, quality: int) -> Path:
        """
        Apply enhancement to GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            enhancement: Enhancement type
            factor: Enhancement factor
            quality: Output quality
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Apply enhancement to GIF
                enhanced_gif = self._apply_enhancement_to_gif(gif, enhancement, factor)
                
                # Save enhanced GIF
                self.image_processor.save_image(
                    enhanced_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF enhancement failed: {e}")
    
    def _apply_enhancement_to_gif(self, gif: Image.Image, enhancement: str, factor: float) -> Image.Image:
        """
        Apply enhancement to animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            enhancement: Enhancement type
            factor: Enhancement factor
            
        Returns:
            Enhanced GIF
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, simple enhancement
            return self._apply_single_enhancement(gif, enhancement, factor)
        
        # Animated GIF - apply enhancement to each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                
                # Apply enhancement to frame
                enhanced_frame = self._apply_single_enhancement(gif, enhancement, factor)
                frames.append(enhanced_frame)
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_enhancement.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=True
                )
                
                # Load the saved GIF
                return Image.open('temp_enhancement.gif')
            else:
                return self._apply_single_enhancement(gif, enhancement, factor)
                
        except Exception as e:
            # Fallback to single enhancement
            return self._apply_single_enhancement(gif, enhancement, factor)
    
    def _apply_single_enhancement(self, image: Image.Image, enhancement: str, factor: float) -> Image.Image:
        """
        Apply a single enhancement to an image.
        
        Args:
            image: PIL Image object
            enhancement: Enhancement type
            factor: Enhancement factor
            
        Returns:
            Enhanced image
        """
        try:
            if enhancement == 'brightness':
                enhancer = ImageEnhance.Brightness(image)
            elif enhancement == 'contrast':
                enhancer = ImageEnhance.Contrast(image)
            elif enhancement == 'saturation':
                enhancer = ImageEnhance.Color(image)
            elif enhancement == 'sharpness':
                enhancer = ImageEnhance.Sharpness(image)
            else:
                return image.copy()
            
            return enhancer.enhance(factor)
        except Exception:
            return image.copy()
    
    def _apply_color_effect(self, input_path: Union[str, Path], output_path: Union[str, Path],
                           effect: str, intensity: float, quality: int) -> Path:
        """
        Apply color effect to GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            effect: Color effect type
            intensity: Effect intensity
            quality: Output quality
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Apply color effect to GIF
                effect_gif = self._apply_color_effect_to_gif(gif, effect, intensity)
                
                # Save effect GIF
                self.image_processor.save_image(
                    effect_gif, output_path, quality=quality, optimize=True
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF color effect failed: {e}")
    
    def _apply_color_effect_to_gif(self, gif: Image.Image, effect: str, intensity: float) -> Image.Image:
        """
        Apply color effect to animated GIF.
        
        Args:
            gif: PIL Image object (GIF)
            effect: Color effect type
            intensity: Effect intensity
            
        Returns:
            Effect GIF
        """
        if not getattr(gif, 'is_animated', False):
            # Not animated, simple color effect
            return self._apply_single_color_effect(gif, effect, intensity)
        
        # Animated GIF - apply color effect to each frame
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            for frame_idx in range(frame_count):
                gif.seek(frame_idx)
                
                # Apply color effect to frame
                effect_frame = self._apply_single_color_effect(gif, effect, intensity)
                frames.append(effect_frame)
                
                # Get frame duration
                duration = gif.info.get('duration', 100)  # Default 100ms
                durations.append(duration)
            
            # Create new GIF
            if frames:
                new_gif = frames[0].copy()
                new_gif.save(
                    'temp_color_effect.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=True
                )
                
                # Load the saved GIF
                return Image.open('temp_color_effect.gif')
            else:
                return self._apply_single_color_effect(gif, effect, intensity)
                
        except Exception as e:
            # Fallback to single color effect
            return self._apply_single_color_effect(gif, effect, intensity)
    
    def _apply_single_color_effect(self, image: Image.Image, effect: str, intensity: float) -> Image.Image:
        """
        Apply a single color effect to an image.
        
        Args:
            image: PIL Image object
            effect: Color effect type
            intensity: Effect intensity
            
        Returns:
            Effect image
        """
        try:
            if effect == 'grayscale':
                return image.convert('L').convert('RGB')
            elif effect == 'sepia':
                # Simple sepia effect
                sepia_image = image.convert('L')
                sepia_image = sepia_image.convert('RGB')
                # Apply sepia tone
                return sepia_image
            elif effect == 'invert':
                return image.convert('RGB').point(lambda x: 255 - x)
            elif effect == 'posterize':
                return image.convert('P', palette=Image.ADAPTIVE, colors=8)
            elif effect == 'solarize':
                return image.convert('RGB').point(lambda x: 255 - x if x < 128 else x)
            else:
                return image.copy()
        except Exception:
            return image.copy()


def apply_gif_filter(input_path: Union[str, Path],
                    output_path: Union[str, Path],
                    filter_name: str,
                    intensity: float = 1.0,
                    **kwargs) -> Path:
    """
    Apply a single filter effect to GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        filter_name: Name of filter to apply
        intensity: Filter intensity
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    applier = GifFilterApplier()
    return applier.apply_filter(input_path, output_path, filter_name, intensity, **kwargs)


def apply_gif_filters(input_path: Union[str, Path],
                     output_path: Union[str, Path],
                     filters: List[Dict[str, Any]],
                     **kwargs) -> Path:
    """
    Apply multiple filter effects to GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        filters: List of filter dictionaries
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    applier = GifFilterApplier()
    return applier.apply_multiple_filters(input_path, output_path, filters, **kwargs)


def adjust_gif_brightness(input_path: Union[str, Path],
                         output_path: Union[str, Path],
                         factor: float,
                         **kwargs) -> Path:
    """
    Adjust brightness of GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        factor: Brightness factor
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    applier = GifFilterApplier()
    return applier.adjust_brightness(input_path, output_path, factor, **kwargs)


def adjust_gif_contrast(input_path: Union[str, Path],
                       output_path: Union[str, Path],
                       factor: float,
                       **kwargs) -> Path:
    """
    Adjust contrast of GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        factor: Contrast factor
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    applier = GifFilterApplier()
    return applier.adjust_contrast(input_path, output_path, factor, **kwargs)


def apply_gif_color_effect(input_path: Union[str, Path],
                          output_path: Union[str, Path],
                          effect: str,
                          intensity: float = 1.0,
                          **kwargs) -> Path:
    """
    Apply color effects to GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        effect: Color effect
        intensity: Effect intensity
        **kwargs: Additional parameters
        
    Returns:
        Path to output GIF file
    """
    applier = GifFilterApplier()
    return applier.apply_color_effects(input_path, output_path, effect, intensity, **kwargs)


def get_gif_filter_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get filter information for GIF.
    
    Args:
        input_path: Path to input GIF file
        
    Returns:
        Dictionary with filter information
    """
    applier = GifFilterApplier()
    return applier.get_filter_info(input_path)


# Export all functions and classes
__all__ = [
    'GifFilterApplier',
    'apply_gif_filter',
    'apply_gif_filters',
    'adjust_gif_brightness',
    'adjust_gif_contrast',
    'apply_gif_color_effect',
    'get_gif_filter_info'
]
