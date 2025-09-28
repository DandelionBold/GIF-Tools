"""
GIF extract frames module.

This module provides functionality to extract specific frames from GIFs
and save them as static images in various formats.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from PIL import Image

from ..utils import (
    SUPPORTED_IMAGE_FORMATS,
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_output_path,
    get_image_processor
)


class GifFrameExtractor:
    """GIF frame extraction utility class."""
    
    def __init__(self):
        """Initialize GIF frame extractor."""
        self.image_processor = get_image_processor()
    
    def extract_frames(self,
                      input_path: Union[str, Path],
                      output_dir: Union[str, Path],
                      frame_indices: Optional[List[int]] = None,
                      output_format: str = 'PNG',
                      quality: int = 95,
                      prefix: str = 'frame') -> List[Path]:
        """
        Extract specific frames from GIF and save as static images.
        
        Args:
            input_path: Path to input GIF file
            output_dir: Directory to save extracted frames
            frame_indices: List of frame indices to extract (None for all frames)
            output_format: Output image format (PNG, JPEG, BMP, etc.)
            quality: Output quality for lossy formats (1-100)
            prefix: Prefix for output filenames
            
        Returns:
            List of paths to extracted frame files
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if output_format.upper() not in SUPPORTED_IMAGE_FORMATS:
            raise ValidationError(f"Unsupported output format: {output_format}")
        
        if not 1 <= quality <= 100:
            raise ValidationError("Quality must be between 1 and 100")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    # Single frame GIF - extract the only frame
                    return self._extract_single_frame(gif, output_dir, output_format, quality, prefix)
                
                # Get frame count
                frame_count = gif.n_frames
                
                # Determine frames to extract
                if frame_indices is None:
                    frame_indices = list(range(frame_count))
                else:
                    # Validate frame indices
                    if not all(0 <= idx < frame_count for idx in frame_indices):
                        raise ValidationError("All frame indices must be within valid range")
                
                # Extract frames
                extracted_paths = []
                for i, frame_idx in enumerate(frame_indices):
                    gif.seek(frame_idx)
                    frame = gif.copy()
                    
                    # Generate output filename
                    filename = f"{prefix}_{frame_idx:04d}.{output_format.lower()}"
                    output_path = output_dir / filename
                    
                    # Save frame
                    self.image_processor.save_image(
                        frame, output_path, quality=quality, optimize=True
                    )
                    
                    extracted_paths.append(output_path)
                
                return extracted_paths
                
        except Exception as e:
            raise ValidationError(f"GIF frame extraction failed: {e}")
    
    def extract_frame_range(self,
                           input_path: Union[str, Path],
                           output_dir: Union[str, Path],
                           start_frame: int,
                           end_frame: int,
                           step: int = 1,
                           output_format: str = 'PNG',
                           quality: int = 95,
                           prefix: str = 'frame') -> List[Path]:
        """
        Extract a range of frames from GIF.
        
        Args:
            input_path: Path to input GIF file
            output_dir: Directory to save extracted frames
            start_frame: Starting frame index (inclusive)
            end_frame: Ending frame index (exclusive)
            step: Step size for frame extraction
            output_format: Output image format
            quality: Output quality for lossy formats
            prefix: Prefix for output filenames
            
        Returns:
            List of paths to extracted frame files
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if start_frame < 0 or end_frame < 0:
            raise ValidationError("Frame indices must be non-negative")
        
        if start_frame >= end_frame:
            raise ValidationError("Start frame must be less than end frame")
        
        if step <= 0:
            raise ValidationError("Step must be positive")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    if start_frame == 0 and end_frame == 1:
                        return self._extract_single_frame(gif, output_dir, output_format, quality, prefix)
                    else:
                        raise ValidationError("Cannot extract frame range from single frame GIF")
                
                # Get frame count
                frame_count = gif.n_frames
                
                # Validate range
                if end_frame > frame_count:
                    raise ValidationError(f"End frame {end_frame} exceeds frame count {frame_count}")
                
                # Generate frame indices
                frame_indices = list(range(start_frame, end_frame, step))
                
                # Extract frames
                extracted_paths = []
                for i, frame_idx in enumerate(frame_indices):
                    gif.seek(frame_idx)
                    frame = gif.copy()
                    
                    # Generate output filename
                    filename = f"{prefix}_{frame_idx:04d}.{output_format.lower()}"
                    output_path = output_dir / filename
                    
                    # Save frame
                    self.image_processor.save_image(
                        frame, output_path, quality=quality, optimize=True
                    )
                    
                    extracted_paths.append(output_path)
                
                return extracted_paths
                
        except Exception as e:
            raise ValidationError(f"GIF frame range extraction failed: {e}")
    
    def extract_every_nth_frame(self,
                               input_path: Union[str, Path],
                               output_dir: Union[str, Path],
                               n: int,
                               output_format: str = 'PNG',
                               quality: int = 95,
                               prefix: str = 'frame') -> List[Path]:
        """
        Extract every nth frame from GIF.
        
        Args:
            input_path: Path to input GIF file
            output_dir: Directory to save extracted frames
            n: Extract every nth frame
            output_format: Output image format
            quality: Output quality for lossy formats
            prefix: Prefix for output filenames
            
        Returns:
            List of paths to extracted frame files
        """
        if n <= 0:
            raise ValidationError("N must be positive")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    if n == 1:
                        return self._extract_single_frame(gif, output_dir, output_format, quality, prefix)
                    else:
                        raise ValidationError("Cannot extract every nth frame from single frame GIF")
                
                # Get frame count
                frame_count = gif.n_frames
                
                # Generate frame indices
                frame_indices = list(range(0, frame_count, n))
                
                # Extract frames
                return self.extract_frames(
                    input_path, output_dir, frame_indices, output_format, quality, prefix
                )
                
        except Exception as e:
            raise ValidationError(f"GIF every nth frame extraction failed: {e}")
    
    def extract_key_frames(self,
                          input_path: Union[str, Path],
                          output_dir: Union[str, Path],
                          method: str = 'first_last_middle',
                          output_format: str = 'PNG',
                          quality: int = 95,
                          prefix: str = 'keyframe') -> List[Path]:
        """
        Extract key frames from GIF using various methods.
        
        Args:
            input_path: Path to input GIF file
            output_dir: Directory to save extracted frames
            method: Key frame extraction method
            output_format: Output image format
            quality: Output quality for lossy formats
            prefix: Prefix for output filenames
            
        Returns:
            List of paths to extracted frame files
        """
        valid_methods = ['first_last_middle', 'first_last', 'middle', 'quarter_points']
        if method not in valid_methods:
            raise ValidationError(f"Invalid key frame method: {method}")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    return self._extract_single_frame(gif, output_dir, output_format, quality, prefix)
                
                # Get frame count
                frame_count = gif.n_frames
                
                # Generate key frame indices based on method
                if method == 'first_last_middle':
                    if frame_count == 1:
                        frame_indices = [0]
                    elif frame_count == 2:
                        frame_indices = [0, 1]
                    else:
                        middle = frame_count // 2
                        frame_indices = [0, middle, frame_count - 1]
                
                elif method == 'first_last':
                    frame_indices = [0, frame_count - 1]
                
                elif method == 'middle':
                    middle = frame_count // 2
                    frame_indices = [middle]
                
                elif method == 'quarter_points':
                    if frame_count < 4:
                        frame_indices = list(range(frame_count))
                    else:
                        quarter = frame_count // 4
                        frame_indices = [0, quarter, quarter * 2, quarter * 3, frame_count - 1]
                
                # Extract frames
                return self.extract_frames(
                    input_path, output_dir, frame_indices, output_format, quality, prefix
                )
                
        except Exception as e:
            raise ValidationError(f"GIF key frame extraction failed: {e}")
    
    def get_extraction_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get extraction information for GIF.
        
        Args:
            input_path: Path to input GIF file
            
        Returns:
            Dictionary with extraction information
        """
        input_path = validate_animated_file(input_path)
        
        try:
            with Image.open(input_path) as gif:
                frame_count = getattr(gif, 'n_frames', 1)
                is_animated = getattr(gif, 'is_animated', False)
                
                return {
                    'frame_count': frame_count,
                    'is_animated': is_animated,
                    'size': gif.size,
                    'width': gif.width,
                    'height': gif.height,
                    'mode': gif.mode,
                    'format': gif.format,
                    'supported_formats': SUPPORTED_IMAGE_FORMATS,
                    'extraction_methods': ['all', 'range', 'every_nth', 'key_frames'],
                    'key_frame_methods': ['first_last_middle', 'first_last', 'middle', 'quarter_points'],
                    'can_extract': True
                }
        except Exception as e:
            raise ValidationError(f"Failed to get extraction info: {e}")
    
    def _extract_single_frame(self, gif: Image.Image, output_dir: Path,
                             output_format: str, quality: int, prefix: str) -> List[Path]:
        """
        Extract single frame from non-animated GIF.
        
        Args:
            gif: PIL Image object
            output_dir: Output directory
            output_format: Output format
            quality: Output quality
            prefix: Filename prefix
            
        Returns:
            List with single extracted frame path
        """
        filename = f"{prefix}_0000.{output_format.lower()}"
        output_path = output_dir / filename
        
        self.image_processor.save_image(
            gif, output_path, quality=quality, optimize=True
        )
        
        return [output_path]


def extract_gif_frames(input_path: Union[str, Path],
                      output_dir: Union[str, Path],
                      frame_indices: Optional[List[int]] = None,
                      **kwargs) -> List[Path]:
    """
    Extract specific frames from GIF and save as static images.
    
    Args:
        input_path: Path to input GIF file
        output_dir: Directory to save extracted frames
        frame_indices: List of frame indices to extract
        **kwargs: Additional extraction parameters
        
    Returns:
        List of paths to extracted frame files
    """
    extractor = GifFrameExtractor()
    return extractor.extract_frames(input_path, output_dir, frame_indices, **kwargs)


def extract_gif_frame_range(input_path: Union[str, Path],
                           output_dir: Union[str, Path],
                           start_frame: int,
                           end_frame: int,
                           **kwargs) -> List[Path]:
    """
    Extract a range of frames from GIF.
    
    Args:
        input_path: Path to input GIF file
        output_dir: Directory to save extracted frames
        start_frame: Starting frame index
        end_frame: Ending frame index
        **kwargs: Additional extraction parameters
        
    Returns:
        List of paths to extracted frame files
    """
    extractor = GifFrameExtractor()
    return extractor.extract_frame_range(input_path, output_dir, start_frame, end_frame, **kwargs)


def extract_every_nth_gif_frame(input_path: Union[str, Path],
                               output_dir: Union[str, Path],
                               n: int,
                               **kwargs) -> List[Path]:
    """
    Extract every nth frame from GIF.
    
    Args:
        input_path: Path to input GIF file
        output_dir: Directory to save extracted frames
        n: Extract every nth frame
        **kwargs: Additional extraction parameters
        
    Returns:
        List of paths to extracted frame files
    """
    extractor = GifFrameExtractor()
    return extractor.extract_every_nth_frame(input_path, output_dir, n, **kwargs)


def extract_gif_key_frames(input_path: Union[str, Path],
                          output_dir: Union[str, Path],
                          method: str = 'first_last_middle',
                          **kwargs) -> List[Path]:
    """
    Extract key frames from GIF using various methods.
    
    Args:
        input_path: Path to input GIF file
        output_dir: Directory to save extracted frames
        method: Key frame extraction method
        **kwargs: Additional extraction parameters
        
    Returns:
        List of paths to extracted frame files
    """
    extractor = GifFrameExtractor()
    return extractor.extract_key_frames(input_path, output_dir, method, **kwargs)


def get_gif_extraction_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get extraction information for GIF.
    
    Args:
        input_path: Path to input GIF file
        
    Returns:
        Dictionary with extraction information
    """
    extractor = GifFrameExtractor()
    return extractor.get_extraction_info(input_path)


# Export all functions and classes
__all__ = [
    'GifFrameExtractor',
    'extract_gif_frames',
    'extract_gif_frame_range',
    'extract_every_nth_gif_frame',
    'extract_gif_key_frames',
    'get_gif_extraction_info'
]
