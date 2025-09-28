"""
GIF merge module.

This module provides functionality to merge multiple GIFs or images into a single
animated GIF with support for horizontal/vertical stacking and timing control.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from PIL import Image

from ..utils import (
    DEFAULT_MERGE,
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_batch_input,
    validate_output_path,
    get_image_processor
)


class GifMerger:
    """GIF merge utility class."""
    
    def __init__(self):
        """Initialize GIF merger."""
        self.image_processor = get_image_processor()
    
    def merge(self,
              input_paths: List[Union[str, Path]],
              output_path: Union[str, Path],
              direction: str = 'horizontal',
              spacing: int = 0,
              background_color: Tuple[int, int, int, int] = (0, 0, 0, 0),
              align: str = 'center',
              frame_duration: int = 100,
              loop_count: int = 0,
              quality: int = 85) -> Path:
        """
        Merge multiple GIFs or images into a single animated GIF.
        
        Args:
            input_paths: List of input file paths
            output_path: Path to output GIF file
            direction: Merge direction ('horizontal' or 'vertical')
            spacing: Spacing between merged items
            background_color: Background color (RGBA tuple)
            align: Alignment ('center', 'top', 'bottom', 'left', 'right')
            frame_duration: Frame duration in milliseconds
            loop_count: Loop count (0 for infinite)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        if not input_paths:
            raise ValidationError("No input files provided")
        
        if len(input_paths) > 10:  # Reasonable limit
            raise ValidationError("Too many input files (max 10)")
        
        input_paths = validate_batch_input(input_paths)
        output_path = validate_output_path(output_path)
        
        if direction not in ['horizontal', 'vertical']:
            raise ValidationError(f"Invalid direction: {direction}")
        
        if align not in ['center', 'top', 'bottom', 'left', 'right']:
            raise ValidationError(f"Invalid alignment: {align}")
        
        try:
            # Load all input files
            loaded_files = self._load_input_files(input_paths)
            
            # Merge files
            merged_gif = self._merge_files(
                loaded_files, direction, spacing, background_color, align, frame_duration
            )
            
            # Save merged GIF
            self.image_processor.save_image(
                merged_gif, output_path, quality=quality, optimize=True
            )
            
            # Apply loop count if not infinite
            if loop_count > 0:
                self._apply_loop_count(output_path, loop_count)
            
            return output_path
            
        except Exception as e:
            raise ValidationError(f"GIF merge failed: {e}")
    
    def merge_horizontal(self,
                        input_paths: List[Union[str, Path]],
                        output_path: Union[str, Path],
                        spacing: int = 0,
                        background_color: Tuple[int, int, int, int] = (0, 0, 0, 0),
                        align: str = 'center',
                        **kwargs) -> Path:
        """
        Merge files horizontally.
        
        Args:
            input_paths: List of input file paths
            output_path: Path to output GIF file
            spacing: Spacing between files
            background_color: Background color
            align: Vertical alignment
            **kwargs: Additional merge parameters
            
        Returns:
            Path to output GIF file
        """
        return self.merge(
            input_paths, output_path, 'horizontal', spacing,
            background_color, align, **kwargs
        )
    
    def merge_vertical(self,
                      input_paths: List[Union[str, Path]],
                      output_path: Union[str, Path],
                      spacing: int = 0,
                      background_color: Tuple[int, int, int, int] = (0, 0, 0, 0),
                      align: str = 'center',
                      **kwargs) -> Path:
        """
        Merge files vertically.
        
        Args:
            input_paths: List of input file paths
            output_path: Path to output GIF file
            spacing: Spacing between files
            background_color: Background color
            align: Horizontal alignment
            **kwargs: Additional merge parameters
            
        Returns:
            Path to output GIF file
        """
        return self.merge(
            input_paths, output_path, 'vertical', spacing,
            background_color, align, **kwargs
        )
    
    def merge_with_timing(self,
                         input_paths: List[Union[str, Path]],
                         output_path: Union[str, Path],
                         frame_durations: List[int],
                         direction: str = 'horizontal',
                         **kwargs) -> Path:
        """
        Merge files with custom frame durations.
        
        Args:
            input_paths: List of input file paths
            output_path: Path to output GIF file
            frame_durations: List of frame durations in milliseconds
            direction: Merge direction
            **kwargs: Additional merge parameters
            
        Returns:
            Path to output GIF file
        """
        if len(frame_durations) != len(input_paths):
            raise ValidationError("Frame durations must match number of input files")
        
        # Load all input files
        loaded_files = self._load_input_files(input_paths)
        
        # Merge with custom timing
        merged_gif = self._merge_files_with_timing(
            loaded_files, direction, frame_durations, **kwargs
        )
        
        # Save merged GIF
        self.image_processor.save_image(
            merged_gif, output_path, quality=kwargs.get('quality', 85), optimize=True
        )
        
        return output_path
    
    def get_merge_info(self, input_paths: List[Union[str, Path]]) -> Dict[str, Any]:
        """
        Get merge information for input files.
        
        Args:
            input_paths: List of input file paths
            
        Returns:
            Dictionary with merge information
        """
        if not input_paths:
            raise ValidationError("No input files provided")
        
        input_paths = validate_batch_input(input_paths)
        
        try:
            loaded_files = self._load_input_files(input_paths)
            
            # Calculate total dimensions
            total_width = sum(file['width'] for file in loaded_files)
            total_height = sum(file['height'] for file in loaded_files)
            max_width = max(file['width'] for file in loaded_files)
            max_height = max(file['height'] for file in loaded_files)
            
            # Calculate frame counts
            frame_counts = [file['frame_count'] for file in loaded_files]
            max_frames = max(frame_counts)
            total_frames = sum(frame_counts)
            
            return {
                'file_count': len(loaded_files),
                'files': loaded_files,
                'total_width': total_width,
                'total_height': total_height,
                'max_width': max_width,
                'max_height': max_height,
                'frame_counts': frame_counts,
                'max_frames': max_frames,
                'total_frames': total_frames,
                'estimated_size': {
                    'horizontal': (total_width, max_height),
                    'vertical': (max_width, total_height)
                }
            }
        except Exception as e:
            raise ValidationError(f"Failed to get merge info: {e}")
    
    def _load_input_files(self, input_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Load all input files and extract information.
        
        Args:
            input_paths: List of input file paths
            
        Returns:
            List of file information dictionaries
        """
        loaded_files = []
        
        for path in input_paths:
            try:
                with Image.open(path) as img:
                    # Get basic info
                    file_info = {
                        'path': str(path),
                        'width': img.width,
                        'height': img.height,
                        'mode': img.mode,
                        'format': img.format,
                        'is_animated': getattr(img, 'is_animated', False),
                        'frame_count': getattr(img, 'n_frames', 1),
                        'frames': [],
                        'durations': []
                    }
                    
                    # Load frames if animated
                    if file_info['is_animated']:
                        for frame_idx in range(file_info['frame_count']):
                            img.seek(frame_idx)
                            file_info['frames'].append(img.copy())
                            duration = img.info.get('duration', 100)
                            file_info['durations'].append(duration)
                    else:
                        # Single frame
                        file_info['frames'].append(img.copy())
                        file_info['durations'].append(100)
                    
                    loaded_files.append(file_info)
                    
            except Exception as e:
                raise ValidationError(f"Failed to load file {path}: {e}")
        
        return loaded_files
    
    def _merge_files(self, loaded_files: List[Dict[str, Any]], 
                    direction: str, spacing: int, background_color: Tuple[int, int, int, int],
                    align: str, frame_duration: int) -> Image.Image:
        """
        Merge loaded files into a single GIF.
        
        Args:
            loaded_files: List of loaded file information
            direction: Merge direction
            spacing: Spacing between files
            background_color: Background color
            align: Alignment
            frame_duration: Frame duration
            
        Returns:
            Merged GIF
        """
        # Calculate output dimensions
        if direction == 'horizontal':
            output_width = sum(file['width'] for file in loaded_files) + spacing * (len(loaded_files) - 1)
            output_height = max(file['height'] for file in loaded_files)
        else:  # vertical
            output_width = max(file['width'] for file in loaded_files)
            output_height = sum(file['height'] for file in loaded_files) + spacing * (len(loaded_files) - 1)
        
        # Create output frames
        max_frames = max(file['frame_count'] for file in loaded_files)
        output_frames = []
        output_durations = []
        
        for frame_idx in range(max_frames):
            # Create frame canvas
            frame = Image.new('RGBA', (output_width, output_height), background_color)
            
            # Position files
            current_pos = 0
            for file_info in loaded_files:
                # Get frame (cycle if needed)
                frame_idx_mod = frame_idx % file_info['frame_count']
                file_frame = file_info['frames'][frame_idx_mod]
                
                # Calculate position
                if direction == 'horizontal':
                    x = current_pos
                    y = self._calculate_y_position(file_frame.height, output_height, align)
                else:  # vertical
                    x = self._calculate_x_position(file_frame.width, output_width, align)
                    y = current_pos
                
                # Paste frame
                if file_frame.mode == 'RGBA':
                    frame.paste(file_frame, (x, y), file_frame)
                else:
                    frame.paste(file_frame, (x, y))
                
                # Update position
                if direction == 'horizontal':
                    current_pos += file_frame.width + spacing
                else:  # vertical
                    current_pos += file_frame.height + spacing
            
            output_frames.append(frame)
            output_durations.append(frame_duration)
        
        # Create output GIF
        if output_frames:
            output_gif = output_frames[0].copy()
            output_gif.save(
                'temp_merge.gif',
                save_all=True,
                append_images=output_frames[1:],
                duration=output_durations,
                loop=0,
                optimize=True
            )
            
            # Load the saved GIF
            return Image.open('temp_merge.gif')
        else:
            raise ValidationError("No frames to merge")
    
    def _merge_files_with_timing(self, loaded_files: List[Dict[str, Any]], 
                                direction: str, frame_durations: List[int],
                                **kwargs) -> Image.Image:
        """
        Merge files with custom timing.
        
        Args:
            loaded_files: List of loaded file information
            direction: Merge direction
            frame_durations: List of frame durations
            **kwargs: Additional parameters
            
        Returns:
            Merged GIF
        """
        # Calculate output dimensions
        if direction == 'horizontal':
            output_width = sum(file['width'] for file in loaded_files)
            output_height = max(file['height'] for file in loaded_files)
        else:  # vertical
            output_width = max(file['width'] for file in loaded_files)
            output_height = sum(file['height'] for file in loaded_files)
        
        # Create output frames
        output_frames = []
        output_durations = []
        
        for file_idx, file_info in enumerate(loaded_files):
            for frame_idx, frame in enumerate(file_info['frames']):
                # Create frame canvas
                canvas = Image.new('RGBA', (output_width, output_height), (0, 0, 0, 0))
                
                # Calculate position
                if direction == 'horizontal':
                    x = sum(loaded_files[i]['width'] for i in range(file_idx))
                    y = (output_height - frame.height) // 2
                else:  # vertical
                    x = (output_width - frame.width) // 2
                    y = sum(loaded_files[i]['height'] for i in range(file_idx))
                
                # Paste frame
                if frame.mode == 'RGBA':
                    canvas.paste(frame, (x, y), frame)
                else:
                    canvas.paste(frame, (x, y))
                
                output_frames.append(canvas)
                output_durations.append(frame_durations[file_idx])
        
        # Create output GIF
        if output_frames:
            output_gif = output_frames[0].copy()
            output_gif.save(
                'temp_merge_timing.gif',
                save_all=True,
                append_images=output_frames[1:],
                duration=output_durations,
                loop=0,
                optimize=True
            )
            
            # Load the saved GIF
            return Image.open('temp_merge_timing.gif')
        else:
            raise ValidationError("No frames to merge")
    
    def _calculate_x_position(self, frame_width: int, canvas_width: int, align: str) -> int:
        """Calculate X position for alignment."""
        if align == 'left':
            return 0
        elif align == 'right':
            return canvas_width - frame_width
        else:  # center
            return (canvas_width - frame_width) // 2
    
    def _calculate_y_position(self, frame_height: int, canvas_height: int, align: str) -> int:
        """Calculate Y position for alignment."""
        if align == 'top':
            return 0
        elif align == 'bottom':
            return canvas_height - frame_height
        else:  # center
            return (canvas_height - frame_height) // 2
    
    def _apply_loop_count(self, gif_path: Path, loop_count: int):
        """Apply loop count to GIF."""
        try:
            with Image.open(gif_path) as gif:
                gif.save(
                    gif_path,
                    save_all=True,
                    append_images=list(gif),
                    loop=loop_count,
                    optimize=True
                )
        except Exception:
            # If loop count application fails, continue without it
            pass


def merge_gifs(input_paths: List[Union[str, Path]],
              output_path: Union[str, Path],
              direction: str = 'horizontal',
              spacing: int = 0,
              background_color: Tuple[int, int, int, int] = (0, 0, 0, 0),
              align: str = 'center',
              frame_duration: int = 100,
              loop_count: int = 0,
              quality: int = 85) -> Path:
    """
    Merge multiple GIFs or images into a single animated GIF.
    
    Args:
        input_paths: List of input file paths
        output_path: Path to output GIF file
        direction: Merge direction ('horizontal' or 'vertical')
        spacing: Spacing between merged items
        background_color: Background color (RGBA tuple)
        align: Alignment ('center', 'top', 'bottom', 'left', 'right')
        frame_duration: Frame duration in milliseconds
        loop_count: Loop count (0 for infinite)
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    merger = GifMerger()
    return merger.merge(
        input_paths, output_path, direction, spacing,
        background_color, align, frame_duration, loop_count, quality
    )


def merge_gifs_horizontal(input_paths: List[Union[str, Path]],
                         output_path: Union[str, Path],
                         **kwargs) -> Path:
    """
    Merge files horizontally.
    
    Args:
        input_paths: List of input file paths
        output_path: Path to output GIF file
        **kwargs: Additional merge parameters
        
    Returns:
        Path to output GIF file
    """
    merger = GifMerger()
    return merger.merge_horizontal(input_paths, output_path, **kwargs)


def merge_gifs_vertical(input_paths: List[Union[str, Path]],
                       output_path: Union[str, Path],
                       **kwargs) -> Path:
    """
    Merge files vertically.
    
    Args:
        input_paths: List of input file paths
        output_path: Path to output GIF file
        **kwargs: Additional merge parameters
        
    Returns:
        Path to output GIF file
    """
    merger = GifMerger()
    return merger.merge_vertical(input_paths, output_path, **kwargs)


def merge_gifs_with_timing(input_paths: List[Union[str, Path]],
                          output_path: Union[str, Path],
                          frame_durations: List[int],
                          direction: str = 'horizontal',
                          **kwargs) -> Path:
    """
    Merge files with custom frame durations.
    
    Args:
        input_paths: List of input file paths
        output_path: Path to output GIF file
        frame_durations: List of frame durations in milliseconds
        direction: Merge direction
        **kwargs: Additional merge parameters
        
    Returns:
        Path to output GIF file
    """
    merger = GifMerger()
    return merger.merge_with_timing(
        input_paths, output_path, frame_durations, direction, **kwargs
    )


def get_merge_info(input_paths: List[Union[str, Path]]) -> Dict[str, Any]:
    """
    Get merge information for input files.
    
    Args:
        input_paths: List of input file paths
        
    Returns:
        Dictionary with merge information
    """
    merger = GifMerger()
    return merger.get_merge_info(input_paths)


# Export all functions and classes
__all__ = [
    'GifMerger',
    'merge_gifs',
    'merge_gifs_horizontal',
    'merge_gifs_vertical',
    'merge_gifs_with_timing',
    'get_merge_info'
]
