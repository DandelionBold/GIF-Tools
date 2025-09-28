"""
Video to GIF conversion module.

This module provides functionality to convert video files to animated GIFs
with customizable settings for quality, frame rate, and duration.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image

from ..utils import (
    DEFAULT_DURATION,
    DEFAULT_FPS,
    DEFAULT_QUALITY,
    SUCCESS_MESSAGES,
    ValidationError,
    validate_duration,
    validate_fps,
    validate_output_path,
    validate_video_file,
    get_file_handler
)


class VideoToGifConverter:
    """Video to GIF conversion utility class."""
    
    def __init__(self) -> None:
        """Initialize video to GIF converter."""
        self._temp_files: List[Path] = []
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup temporary files."""
        self.cleanup()
    
    def convert(self,
                video_path: Union[str, Path],
                output_path: Union[str, Path],
                fps: int = DEFAULT_FPS,
                duration: Optional[float] = None,
                start_time: float = 0.0,
                quality: int = DEFAULT_QUALITY,
                width: Optional[int] = None,
                height: Optional[int] = None,
                optimize: bool = True,
                loop_count: int = 0) -> Path:
        """
        Convert video to GIF.
        
        Args:
            video_path: Path to input video file
            output_path: Path to output GIF file
            fps: Frames per second for output GIF
            duration: Duration of GIF in seconds (None for full video)
            start_time: Start time in seconds
            quality: GIF quality (1-100)
            width: Output width (maintains aspect ratio if height not specified)
            height: Output height (maintains aspect ratio if width not specified)
            optimize: Whether to optimize the GIF
            loop_count: Number of loops (0 for infinite)
            
        Returns:
            Path to output GIF file
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        video_path = validate_video_file(video_path)
        output_path = validate_output_path(output_path)
        fps = validate_fps(fps)
        quality = max(1, min(100, quality))
        
        if duration is not None:
            duration = validate_duration(duration)
        
        if start_time < 0:
            raise ValidationError("Start time must be non-negative")
        
        try:
            # Load video
            with VideoFileClip(str(video_path)) as video:
                # Get video properties (using available methods)
                try:
                    video_duration = getattr(video, 'duration', 30.0)  # Default 30 seconds
                except:
                    video_duration = 30.0
                
                try:
                    video_fps = getattr(video, 'fps', fps)
                except:
                    video_fps = fps
                
                # Validate video duration
                if start_time >= video_duration:
                    raise ValidationError(
                        f"Start time ({start_time}s) exceeds video duration ({video_duration}s)"
                    )
                
                # Calculate actual duration
                if duration is None:
                    actual_duration = video_duration - start_time
                else:
                    actual_duration = min(duration, video_duration - start_time)
                
                if actual_duration <= 0:
                    raise ValidationError("Invalid duration after start time")
                
                # Set video segment
                if start_time > 0 or actual_duration < video_duration:
                    video = video.subclipped(start_time, start_time + actual_duration)
                
                # Resize if needed
                if width or height:
                    video = self._resize_video(video, width, height)
                
                # Convert to GIF
                output_path = self._convert_to_gif(
                    video, output_path, fps, quality, optimize, loop_count
                )
                
                return output_path
                
        except Exception as e:
            raise ValidationError(f"Video conversion failed: {e}")
        finally:
            self.cleanup()
    
    def convert_with_preview(self,
                           video_path: Union[str, Path],
                           output_path: Union[str, Path],
                           preview_frames: int = 10,
                           **kwargs) -> Tuple[Path, List[Image.Image]]:
        """
        Convert video to GIF with frame preview.
        
        Args:
            video_path: Path to input video file
            output_path: Path to output GIF file
            preview_frames: Number of preview frames to extract
            **kwargs: Additional conversion parameters
            
        Returns:
            Tuple of (output_path, preview_frames)
        """
        # Validate inputs
        video_path = validate_video_file(video_path)
        output_path = validate_output_path(output_path)
        
        if preview_frames <= 0:
            raise ValidationError("Preview frames must be positive")
        
        try:
            # Load video
            with VideoFileClip(str(video_path)) as video:
                # Extract preview frames
                preview_images = self._extract_preview_frames(
                    video, preview_frames, kwargs.get('start_time', 0.0)
                )
                
                # Convert to GIF
                gif_path = self.convert(video_path, output_path, **kwargs)
                
                return gif_path, preview_images
                
        except Exception as e:
            raise ValidationError(f"Video conversion with preview failed: {e}")
    
    def get_video_info(self, video_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get video information.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        video_path = validate_video_file(video_path)
        
        try:
            with VideoFileClip(str(video_path)) as video:
                # Get video properties with fallbacks
                duration = getattr(video, 'duration', 30.0)
                fps = getattr(video, 'fps', 10.0)
                width = getattr(video, 'w', 640)
                height = getattr(video, 'h', 480)
                
                return {
                    'duration': duration,
                    'fps': fps,
                    'size': (width, height),
                    'width': width,
                    'height': height,
                    'aspect_ratio': width / height if height > 0 else 1.0,
                    'has_audio': getattr(video, 'audio', None) is not None,
                    'file_size': Path(video_path).stat().st_size,
                    'format': getattr(video, 'filename', '').split('.')[-1].lower() if getattr(video, 'filename', None) else 'unknown'
                }
        except Exception as e:
            raise ValidationError(f"Failed to get video info: {e}")
    
    def _resize_video(self, video: VideoFileClip, 
                     width: Optional[int], height: Optional[int]) -> VideoFileClip:
        """
        Resize video clip.
        
        Args:
            video: Video clip to resize
            width: Target width
            height: Target height
            
        Returns:
            Resized video clip
        """
        if width and height:
            return video.resized((width, height))
        elif width:
            return video.resized(width=width)
        elif height:
            return video.resized(height=height)
        else:
            return video
    
    def _convert_to_gif(self, video: VideoFileClip, 
                       output_path: Path, fps: int, quality: int,
                       optimize: bool, loop_count: int) -> Path:
        """
        Convert video clip to GIF.
        
        Args:
            video: Video clip to convert
            output_path: Output file path
            fps: Frames per second
            quality: GIF quality
            optimize: Whether to optimize
            loop_count: Loop count
            
        Returns:
            Output file path
        """
        try:
            # Write GIF
            video.write_gif(
                str(output_path),
                fps=fps,
                opt='OptimizeTransparency' if optimize else None,
                program='ffmpeg',
                verbose=False,
                logger=None
            )
            
            # Apply loop count if not infinite
            if loop_count > 0:
                self._apply_loop_count(output_path, loop_count)
            
            return output_path
            
        except Exception as e:
            raise ValidationError(f"GIF conversion failed: {e}")
    
    def _extract_preview_frames(self, video: VideoFileClip, 
                               frame_count: int, start_time: float) -> List[Image.Image]:
        """
        Extract preview frames from video.
        
        Args:
            video: Video clip
            frame_count: Number of frames to extract
            start_time: Start time for extraction
            
        Returns:
            List of PIL Image objects
        """
        try:
            # Calculate frame times
            duration = video.duration - start_time
            frame_times = [
                start_time + (i * duration / (frame_count - 1))
                for i in range(frame_count)
            ]
            
            # Extract frames
            frames = []
            for time in frame_times:
                frame = video.get_frame(time)
                # Convert numpy array to PIL Image
                image = Image.fromarray(frame)
                frames.append(image)
            
            return frames
            
        except Exception as e:
            raise ValidationError(f"Frame extraction failed: {e}")
    
    def _apply_loop_count(self, gif_path: Path, loop_count: int):
        """
        Apply loop count to GIF.
        
        Args:
            gif_path: Path to GIF file
            loop_count: Number of loops
        """
        try:
            # Load GIF
            with Image.open(gif_path) as gif:
                # Save with loop count
                gif.save(
                    gif_path,
                    save_all=True,
                    append_images=list(gif),
                    loop=loop_count,
                    optimize=True
                )
        except Exception as e:
            # If loop count application fails, continue without it
            # Log the error for debugging purposes
            print(f"Warning: Could not apply loop count: {e}")
    
    def cleanup(self):
        """Clean up temporary files."""
        for temp_file in self._temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except (OSError, PermissionError):
                pass
        
        self._temp_files.clear()


def convert_video_to_gif(video_path: Union[str, Path],
                        output_path: Union[str, Path],
                        fps: int = DEFAULT_FPS,
                        duration: Optional[float] = None,
                        start_time: float = 0.0,
                        quality: int = DEFAULT_QUALITY,
                        width: Optional[int] = None,
                        height: Optional[int] = None,
                        optimize: bool = True,
                        loop_count: int = 0) -> Path:
    """
    Convert video to GIF.
    
    Args:
        video_path: Path to input video file
        output_path: Path to output GIF file
        fps: Frames per second for output GIF
        duration: Duration of GIF in seconds (None for full video)
        start_time: Start time in seconds
        quality: GIF quality (1-100)
        width: Output width (maintains aspect ratio if height not specified)
        height: Output height (maintains aspect ratio if width not specified)
        optimize: Whether to optimize the GIF
        loop_count: Number of loops (0 for infinite)
        
    Returns:
        Path to output GIF file
    """
    with VideoToGifConverter() as converter:
        return converter.convert(
            video_path, output_path, fps, duration, start_time,
            quality, width, height, optimize, loop_count
        )


def convert_video_to_gif_with_preview(video_path: Union[str, Path],
                                    output_path: Union[str, Path],
                                    preview_frames: int = 10,
                                    **kwargs) -> Tuple[Path, List[Image.Image]]:
    """
    Convert video to GIF with frame preview.
    
    Args:
        video_path: Path to input video file
        output_path: Path to output GIF file
        preview_frames: Number of preview frames to extract
        **kwargs: Additional conversion parameters
        
    Returns:
        Tuple of (output_path, preview_frames)
    """
    with VideoToGifConverter() as converter:
        return converter.convert_with_preview(
            video_path, output_path, preview_frames, **kwargs
        )


def get_video_info(video_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get video information.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with video information
    """
    with VideoToGifConverter() as converter:
        return converter.get_video_info(video_path)


# Export all functions and classes
__all__ = [
    'VideoToGifConverter',
    'convert_video_to_gif',
    'convert_video_to_gif_with_preview',
    'get_video_info'
]
