"""
GIF rearrange module.

This module provides functionality to rearrange frames within a GIF by
selecting one or more frames and moving them to new positions.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from PIL import Image

from ..utils import (
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_output_path,
    get_image_processor
)


class GifRearranger:
    """GIF frame rearrangement utility class."""
    
    def __init__(self) -> None:
        """Initialize GIF rearranger."""
        self.image_processor = get_image_processor()
    
    def rearrange_frames(self,
                        input_path: Union[str, Path],
                        output_path: Union[str, Path],
                        frame_order: List[int],
                        quality: int = 85) -> Path:
        """
        Rearrange frames in GIF according to specified order.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            frame_order: New order of frame indices (0-based)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if not frame_order:
            raise ValidationError("Frame order cannot be empty")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    raise ValidationError("Cannot rearrange frames in non-animated GIF")
                
                # Get frame count
                frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
                
                # Validate frame order
                if len(frame_order) != frame_count:
                    raise ValidationError(f"Frame order length ({len(frame_order)}) must match frame count ({frame_count})")
                
                if not all(0 <= idx < frame_count for idx in frame_order):
                    raise ValidationError("All frame indices must be within valid range")
                
                if len(set(frame_order)) != len(frame_order):
                    raise ValidationError("Frame order must contain unique indices")
                
                # Rearrange frames
                rearranged_gif = self._rearrange_frames(gif, frame_order)
                
                # Save rearranged GIF
                self.image_processor.save_image(
                    rearranged_gif, output_path, quality=quality, optimize=False
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF frame rearrangement failed: {e}")
    
    def move_frame(self,
                  input_path: Union[str, Path],
                  output_path: Union[str, Path],
                  from_index: int,
                  to_index: int,
                  quality: int = 85) -> Path:
        """
        Move a single frame from one position to another.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            from_index: Source frame index (0-based)
            to_index: Destination frame index (0-based)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    raise ValidationError("Cannot move frames in non-animated GIF")
                
                # Get frame count
                frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
                
                # Validate indices
                if not 0 <= from_index < frame_count:
                    raise ValidationError(f"Source frame index {from_index} out of range")
                
                if not 0 <= to_index < frame_count:
                    raise ValidationError(f"Destination frame index {to_index} out of range")
                
                # Create new frame order
                frame_order = list(range(frame_count))
                frame_order[from_index], frame_order[to_index] = frame_order[to_index], frame_order[from_index]
                
                # Rearrange frames
                rearranged_gif = self._rearrange_frames(gif, frame_order)
                
                # Save rearranged GIF
                self.image_processor.save_image(
                    rearranged_gif, output_path, quality=quality, optimize=False
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF frame move failed: {e}")
    
    def move_frames(self,
                   input_path: Union[str, Path],
                   output_path: Union[str, Path],
                   from_indices: List[int],
                   to_index: int,
                   quality: int = 85) -> Path:
        """
        Move multiple frames to a new position.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            from_indices: List of source frame indices (0-based)
            to_index: Destination frame index (0-based)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if not from_indices:
            raise ValidationError("No source frame indices provided")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    raise ValidationError("Cannot move frames in non-animated GIF")
                
                # Get frame count
                frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
                
                # Validate indices
                if not all(0 <= idx < frame_count for idx in from_indices):
                    raise ValidationError("All source frame indices must be within valid range")
                
                if not 0 <= to_index < frame_count:
                    raise ValidationError(f"Destination frame index {to_index} out of range")
                
                # Create new frame order
                frame_order = list(range(frame_count))
                
                # Remove source frames
                for idx in sorted(from_indices, reverse=True):
                    frame_order.pop(idx)
                
                # Insert frames at destination
                for i, idx in enumerate(from_indices):
                    insert_pos = min(to_index + i, len(frame_order))
                    frame_order.insert(insert_pos, idx)
                
                # Rearrange frames
                rearranged_gif = self._rearrange_frames(gif, frame_order)
                
                # Save rearranged GIF
                self.image_processor.save_image(
                    rearranged_gif, output_path, quality=quality, optimize=False
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF frames move failed: {e}")
    
    def duplicate_frame(self,
                      input_path: Union[str, Path],
                      output_path: Union[str, Path],
                      frame_index: int,
                      count: int = 1,
                      quality: int = 85) -> Path:
        """
        Duplicate a frame multiple times.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            frame_index: Frame index to duplicate (0-based)
            count: Number of times to duplicate
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if count <= 0:
            raise ValidationError("Duplicate count must be positive")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    raise ValidationError("Cannot duplicate frames in non-animated GIF")
                
                # Get frame count
                frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
                
                # Validate frame index
                if not 0 <= frame_index < frame_count:
                    raise ValidationError(f"Frame index {frame_index} out of range")
                
                # Create new frame order with duplicates
                frame_order = list(range(frame_count))
                
                # Insert duplicates after the original frame
                for _ in range(count):
                    frame_order.insert(frame_index + 1, frame_index)
                
                # Rearrange frames
                rearranged_gif = self._rearrange_frames(gif, frame_order)
                
                # Save rearranged GIF
                self.image_processor.save_image(
                    rearranged_gif, output_path, quality=quality, optimize=False
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF frame duplication failed: {e}")
    
    def remove_frames(self,
                     input_path: Union[str, Path],
                     output_path: Union[str, Path],
                     frame_indices: List[int],
                     quality: int = 85) -> Path:
        """
        Remove specified frames from GIF.
        
        Args:
            input_path: Path to input GIF file
            output_path: Path to output GIF file
            frame_indices: List of frame indices to remove (0-based)
            quality: Output quality (1-100)
            
        Returns:
            Path to output GIF file
        """
        # Validate inputs
        input_path = validate_animated_file(input_path)
        output_path = validate_output_path(output_path)
        
        if not frame_indices:
            raise ValidationError("No frame indices provided for removal")
        
        try:
            # Load GIF
            with Image.open(input_path) as gif:
                # Check if animated
                if not getattr(gif, 'is_animated', False):
                    raise ValidationError("Cannot remove frames from non-animated GIF")
                
                # Get frame count
                frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
                
                # Validate indices
                if not all(0 <= idx < frame_count for idx in frame_indices):
                    raise ValidationError("All frame indices must be within valid range")
                
                if len(frame_indices) >= frame_count:
                    raise ValidationError("Cannot remove all frames")
                
                # Create new frame order without removed frames
                frame_order = [i for i in range(frame_count) if i not in frame_indices]
                
                # Rearrange frames
                rearranged_gif = self._rearrange_frames(gif, frame_order)
                
                # Save rearranged GIF
                self.image_processor.save_image(
                    rearranged_gif, output_path, quality=quality, optimize=False
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"GIF frame removal failed: {e}")
    
    def get_frame_info(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get frame information for GIF.
        
        Args:
            input_path: Path to input GIF file
            
        Returns:
            Dictionary with frame information
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
                        'size': gif.size,
                        'mode': gif.mode,
                        'format': gif.format,
                        'frames': []
                    }
                
                # Get frame information
                frames = []
                durations = []
                
                for frame_idx in range(frame_count):
                    gif.seek(frame_idx)
                    duration = gif.info.get('duration', 100)  # Default 100ms
                    durations.append(duration)
                    
                    frames.append({
                        'index': frame_idx,
                        'size': gif.size,
                        'mode': gif.mode,
                        'duration': duration
                    })
                
                return {
                    'frame_count': frame_count,
                    'is_animated': True,
                    'size': gif.size,
                    'mode': gif.mode,
                    'format': gif.format,
                    'frames': frames,
                    'durations': durations,
                    'total_duration': sum(durations) / 1000.0,  # Convert to seconds
                    'loop': gif.info.get('loop', 0)
                }
        except Exception as e:
            raise ValidationError(f"Failed to get frame info: {e}")
    
    def _rearrange_frames(self, gif: Image.Image, frame_order: List[int]) -> Image.Image:
        """
        Rearrange frames in GIF.
        
        Args:
            gif: PIL Image object (GIF)
            frame_order: New order of frame indices
            
        Returns:
            Rearranged GIF
        """
        frames = []
        durations = []
        
        try:
            # Get frame count
            frame_count = getattr(gif, 'n_frames', 1) if hasattr(gif, 'n_frames') else 1
            
            # Load frames in new order
            for frame_idx in frame_order:
                gif.seek(frame_idx)
                frame = gif.copy()
                frames.append(frame)
                
                # Get frame duration - try multiple sources
                duration = 100  # Default 100ms
                if 'duration' in gif.info:
                    duration = gif.info['duration']
                elif hasattr(gif, 'info') and 'duration' in gif.info:
                    duration = gif.info['duration']
                elif hasattr(gif, 'duration'):
                    duration = gif.duration
                
                durations.append(duration)
            
            # Create new GIF with proper frame handling
            if frames:
                # Create a new GIF with the rearranged frames
                new_gif = frames[0].copy()
                
                # Debug: Print frame count
                print(f"Debug: Creating GIF with {len(frames)} frames")
                print(f"Debug: Durations: {durations}")
                
                # Save with proper GIF parameters
                new_gif.save(
                    'temp_rearrange.gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=gif.info.get('loop', 0),
                    optimize=False,  # Disable optimization to prevent frame loss
                    disposal=2,  # Restore to background
                    transparency=0  # No transparency
                )
                
                # Load the saved GIF and return
                result_gif = Image.open('temp_rearrange.gif')
                
                # Debug: Check result frame count
                result_frames = getattr(result_gif, 'n_frames', 1)
                print(f"Debug: Result GIF has {result_frames} frames")
                
                # Clean up temp file
                import os
                try:
                    os.remove('temp_rearrange.gif')
                except:
                    pass
                
                return result_gif
            else:
                return gif.copy()
                
        except Exception as e:
            # Fallback to original GIF
            return gif.copy()


def rearrange_gif_frames(input_path: Union[str, Path],
                        output_path: Union[str, Path],
                        frame_order: List[int],
                        quality: int = 85) -> Path:
    """
    Rearrange frames in GIF according to specified order.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        frame_order: New order of frame indices (0-based)
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    rearranger = GifRearranger()
    return rearranger.rearrange_frames(input_path, output_path, frame_order, quality)


def move_gif_frame(input_path: Union[str, Path],
                  output_path: Union[str, Path],
                  from_index: int,
                  to_index: int,
                  quality: int = 85) -> Path:
    """
    Move a single frame from one position to another.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        from_index: Source frame index (0-based)
        to_index: Destination frame index (0-based)
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    rearranger = GifRearranger()
    return rearranger.move_frame(input_path, output_path, from_index, to_index, quality)


def move_gif_frames(input_path: Union[str, Path],
                   output_path: Union[str, Path],
                   from_indices: List[int],
                   to_index: int,
                   quality: int = 85) -> Path:
    """
    Move multiple frames to a new position.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        from_indices: List of source frame indices (0-based)
        to_index: Destination frame index (0-based)
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    rearranger = GifRearranger()
    return rearranger.move_frames(input_path, output_path, from_indices, to_index, quality)


def duplicate_gif_frame(input_path: Union[str, Path],
                       output_path: Union[str, Path],
                       frame_index: int,
                       count: int = 1,
                       quality: int = 85) -> Path:
    """
    Duplicate a frame multiple times.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        frame_index: Frame index to duplicate (0-based)
        count: Number of times to duplicate
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    rearranger = GifRearranger()
    return rearranger.duplicate_frame(input_path, output_path, frame_index, count, quality)


def remove_gif_frames(input_path: Union[str, Path],
                     output_path: Union[str, Path],
                     frame_indices: List[int],
                     quality: int = 85) -> Path:
    """
    Remove specified frames from GIF.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path to output GIF file
        frame_indices: List of frame indices to remove (0-based)
        quality: Output quality (1-100)
        
    Returns:
        Path to output GIF file
    """
    rearranger = GifRearranger()
    return rearranger.remove_frames(input_path, output_path, frame_indices, quality)


def get_gif_frame_info(input_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get frame information for GIF.
    
    Args:
        input_path: Path to input GIF file
        
    Returns:
        Dictionary with frame information
    """
    rearranger = GifRearranger()
    return rearranger.get_frame_info(input_path)


# Export all functions and classes
__all__ = [
    'GifRearranger',
    'rearrange_gif_frames',
    'move_gif_frame',
    'move_gif_frames',
    'duplicate_gif_frame',
    'remove_gif_frames',
    'get_gif_frame_info'
]
