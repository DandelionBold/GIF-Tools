"""
GIF batch processing module.

This module provides functionality to process multiple GIF files at once
with various operations and batch management features.
"""

import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from PIL import Image

from ..utils import (
    SUPPORTED_ANIMATED_FORMATS,
    SUCCESS_MESSAGES,
    ValidationError,
    validate_animated_file,
    validate_output_path,
    get_image_processor
)


class GifBatchProcessor:
    """GIF batch processing utility class."""
    
    def __init__(self):
        """Initialize GIF batch processor."""
        self.image_processor = get_image_processor()
        self._supported_formats = SUPPORTED_ANIMATED_FORMATS
    
    def process_batch(self,
                     input_dir: Union[str, Path],
                     output_dir: Union[str, Path],
                     operation: str,
                     **kwargs) -> Dict[str, Any]:
        """
        Process multiple GIF files with specified operation.
        
        Args:
            input_dir: Directory containing input GIF files
            output_dir: Directory to save processed files
            operation: Operation to perform on each file
            **kwargs: Additional operation parameters
            
        Returns:
            Dictionary with batch processing results
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        if not input_dir.exists():
            raise ValidationError(f"Input directory does not exist: {input_dir}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get list of GIF files
        gif_files = self._get_gif_files(input_dir)
        
        if not gif_files:
            raise ValidationError(f"No GIF files found in {input_dir}")
        
        # Process files
        results = {
            'total_files': len(gif_files),
            'processed_files': 0,
            'failed_files': 0,
            'success_files': [],
            'failed_files': [],
            'operation': operation,
            'input_dir': str(input_dir),
            'output_dir': str(output_dir)
        }
        
        for gif_file in gif_files:
            try:
                # Process single file
                result = self._process_single_file(gif_file, output_dir, operation, **kwargs)
                
                if result['success']:
                    results['processed_files'] += 1
                    results['success_files'].append(result)
                else:
                    results['failed_files'] += 1
                    results['failed_files'].append(result)
                    
            except Exception as e:
                results['failed_files'] += 1
                results['failed_files_list'].append({
                    'input_file': str(gif_file),
                    'success': False,
                    'error': str(e),
                    'output_file': None
                })
        
        return results
    
    def resize_batch(self,
                    input_dir: Union[str, Path],
                    output_dir: Union[str, Path],
                    width: int,
                    height: int,
                    **kwargs) -> Dict[str, Any]:
        """
        Resize all GIF files in batch.
        
        Args:
            input_dir: Directory containing input GIF files
            output_dir: Directory to save resized files
            width: Target width
            height: Target height
            **kwargs: Additional resize parameters
            
        Returns:
            Dictionary with batch processing results
        """
        return self.process_batch(
            input_dir, output_dir, 'resize', width=width, height=height, **kwargs
        )
    
    def optimize_batch(self,
                      input_dir: Union[str, Path],
                      output_dir: Union[str, Path],
                      quality: int = 85,
                      **kwargs) -> Dict[str, Any]:
        """
        Optimize all GIF files in batch.
        
        Args:
            input_dir: Directory containing input GIF files
            output_dir: Directory to save optimized files
            quality: Optimization quality
            **kwargs: Additional optimization parameters
            
        Returns:
            Dictionary with batch processing results
        """
        return self.process_batch(
            input_dir, output_dir, 'optimize', quality=quality, **kwargs
        )
    
    def convert_format_batch(self,
                            input_dir: Union[str, Path],
                            output_dir: Union[str, Path],
                            target_format: str,
                            **kwargs) -> Dict[str, Any]:
        """
        Convert format of all GIF files in batch.
        
        Args:
            input_dir: Directory containing input GIF files
            output_dir: Directory to save converted files
            target_format: Target format
            **kwargs: Additional conversion parameters
            
        Returns:
            Dictionary with batch processing results
        """
        return self.process_batch(
            input_dir, output_dir, 'convert_format', target_format=target_format, **kwargs
        )
    
    def add_text_batch(self,
                      input_dir: Union[str, Path],
                      output_dir: Union[str, Path],
                      text: str,
                      **kwargs) -> Dict[str, Any]:
        """
        Add text to all GIF files in batch.
        
        Args:
            input_dir: Directory containing input GIF files
            output_dir: Directory to save text-added files
            text: Text to add
            **kwargs: Additional text parameters
            
        Returns:
            Dictionary with batch processing results
        """
        return self.process_batch(
            input_dir, output_dir, 'add_text', text=text, **kwargs
        )
    
    def custom_batch(self,
                    input_dir: Union[str, Path],
                    output_dir: Union[str, Path],
                    operation_func: Callable[[Path, Path], Path],
                    **kwargs) -> Dict[str, Any]:
        """
        Process batch with custom operation function.
        
        Args:
            input_dir: Directory containing input GIF files
            output_dir: Directory to save processed files
            operation_func: Custom operation function
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with batch processing results
        """
        # Validate inputs
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        if not input_dir.exists():
            raise ValidationError(f"Input directory does not exist: {input_dir}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get list of GIF files
        gif_files = self._get_gif_files(input_dir)
        
        if not gif_files:
            raise ValidationError(f"No GIF files found in {input_dir}")
        
        # Process files
        results = {
            'total_files': len(gif_files),
            'processed_files': 0,
            'failed_files': 0,
            'success_files': [],
            'failed_files_list': [],
            'operation': 'custom',
            'input_dir': str(input_dir),
            'output_dir': str(output_dir)
        }
        
        for gif_file in gif_files:
            try:
                # Generate output filename
                output_filename = f"processed_{gif_file.name}"
                output_path = output_dir / output_filename
                
                # Call custom operation function
                result_path = operation_func(gif_file, output_path, **kwargs)
                
                results['processed_files'] += 1
                results['success_files'].append({
                    'input_file': str(gif_file),
                    'success': True,
                    'output_file': str(result_path),
                    'error': None
                })
                
            except Exception as e:
                results['failed_files'] += 1
                results['failed_files_list'].append({
                    'input_file': str(gif_file),
                    'success': False,
                    'error': str(e),
                    'output_file': None
                })
        
        return results
    
    def get_batch_info(self, input_dir: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about files in directory for batch processing.
        
        Args:
            input_dir: Directory to analyze
            
        Returns:
            Dictionary with batch information
        """
        input_dir = Path(input_dir)
        
        if not input_dir.exists():
            raise ValidationError(f"Directory does not exist: {input_dir}")
        
        # Get list of GIF files
        gif_files = self._get_gif_files(input_dir)
        
        # Analyze files
        file_info = []
        total_size = 0
        
        for gif_file in gif_files:
            try:
                with Image.open(gif_file) as gif:
                    file_size = gif_file.stat().st_size
                    total_size += file_size
                    
                    file_info.append({
                        'filename': gif_file.name,
                        'size': file_size,
                        'width': gif.width,
                        'height': gif.height,
                        'frame_count': getattr(gif, 'n_frames', 1),
                        'is_animated': getattr(gif, 'is_animated', False),
                        'format': gif.format
                    })
            except Exception as e:
                file_info.append({
                    'filename': gif_file.name,
                    'size': 0,
                    'width': 0,
                    'height': 0,
                    'frame_count': 0,
                    'is_animated': False,
                    'format': 'unknown',
                    'error': str(e)
                })
        
        return {
            'input_dir': str(input_dir),
            'total_files': len(gif_files),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'file_info': file_info,
            'supported_operations': [
                'resize', 'optimize', 'convert_format', 'add_text', 'custom'
            ],
            'supported_formats': self._supported_formats
        }
    
    def _get_gif_files(self, directory: Path) -> List[Path]:
        """
        Get list of GIF files in directory.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of GIF file paths
        """
        gif_files = []
        
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ['.gif', '.webp', '.apng']:
                gif_files.append(file_path)
        
        return sorted(gif_files)
    
    def _process_single_file(self, input_file: Path, output_dir: Path,
                            operation: str, **kwargs) -> Dict[str, Any]:
        """
        Process a single file with specified operation.
        
        Args:
            input_file: Input file path
            output_dir: Output directory
            operation: Operation to perform
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with processing result
        """
        try:
            # Generate output filename
            output_filename = f"{operation}_{input_file.stem}{input_file.suffix}"
            output_path = output_dir / output_filename
            
            # Perform operation
            if operation == 'resize':
                from .resize import resize_gif
                result_path = resize_gif(input_file, output_path, **kwargs)
            elif operation == 'optimize':
                from .optimize import optimize_gif
                result_path = optimize_gif(input_file, output_path, **kwargs)
            elif operation == 'convert_format':
                from .format_conversion import convert_gif_format
                result_path = convert_gif_format(input_file, output_path, **kwargs)
            elif operation == 'add_text':
                from .add_text import add_text_to_gif
                result_path = add_text_to_gif(input_file, output_path, **kwargs)
            else:
                raise ValidationError(f"Unknown operation: {operation}")
            
            return {
                'input_file': str(input_file),
                'success': True,
                'output_file': str(result_path),
                'error': None
            }
            
        except Exception as e:
            return {
                'input_file': str(input_file),
                'success': False,
                'output_file': None,
                'error': str(e)
            }


def process_gif_batch(input_dir: Union[str, Path],
                     output_dir: Union[str, Path],
                     operation: str,
                     **kwargs) -> Dict[str, Any]:
    """
    Process multiple GIF files with specified operation.
    
    Args:
        input_dir: Directory containing input GIF files
        output_dir: Directory to save processed files
        operation: Operation to perform on each file
        **kwargs: Additional operation parameters
        
    Returns:
        Dictionary with batch processing results
    """
    processor = GifBatchProcessor()
    return processor.process_batch(input_dir, output_dir, operation, **kwargs)


def resize_gif_batch(input_dir: Union[str, Path],
                    output_dir: Union[str, Path],
                    width: int,
                    height: int,
                    **kwargs) -> Dict[str, Any]:
    """
    Resize all GIF files in batch.
    
    Args:
        input_dir: Directory containing input GIF files
        output_dir: Directory to save resized files
        width: Target width
        height: Target height
        **kwargs: Additional resize parameters
        
    Returns:
        Dictionary with batch processing results
    """
    processor = GifBatchProcessor()
    return processor.resize_batch(input_dir, output_dir, width, height, **kwargs)


def optimize_gif_batch(input_dir: Union[str, Path],
                      output_dir: Union[str, Path],
                      quality: int = 85,
                      **kwargs) -> Dict[str, Any]:
    """
    Optimize all GIF files in batch.
    
    Args:
        input_dir: Directory containing input GIF files
        output_dir: Directory to save optimized files
        quality: Optimization quality
        **kwargs: Additional optimization parameters
        
    Returns:
        Dictionary with batch processing results
    """
    processor = GifBatchProcessor()
    return processor.optimize_batch(input_dir, output_dir, quality, **kwargs)


def convert_format_gif_batch(input_dir: Union[str, Path],
                            output_dir: Union[str, Path],
                            target_format: str,
                            **kwargs) -> Dict[str, Any]:
    """
    Convert format of all GIF files in batch.
    
    Args:
        input_dir: Directory containing input GIF files
        output_dir: Directory to save converted files
        target_format: Target format
        **kwargs: Additional conversion parameters
        
    Returns:
        Dictionary with batch processing results
    """
    processor = GifBatchProcessor()
    return processor.convert_format_batch(input_dir, output_dir, target_format, **kwargs)


def add_text_gif_batch(input_dir: Union[str, Path],
                      output_dir: Union[str, Path],
                      text: str,
                      **kwargs) -> Dict[str, Any]:
    """
    Add text to all GIF files in batch.
    
    Args:
        input_dir: Directory containing input GIF files
        output_dir: Directory to save text-added files
        text: Text to add
        **kwargs: Additional text parameters
        
    Returns:
        Dictionary with batch processing results
    """
    processor = GifBatchProcessor()
    return processor.add_text_batch(input_dir, output_dir, text, **kwargs)


def custom_gif_batch(input_dir: Union[str, Path],
                    output_dir: Union[str, Path],
                    operation_func: Callable,
                    **kwargs) -> Dict[str, Any]:
    """
    Process batch with custom operation function.
    
    Args:
        input_dir: Directory containing input GIF files
        output_dir: Directory to save processed files
        operation_func: Custom operation function
        **kwargs: Additional parameters
        
    Returns:
        Dictionary with batch processing results
    """
    processor = GifBatchProcessor()
    return processor.custom_batch(input_dir, output_dir, operation_func, **kwargs)


def get_gif_batch_info(input_dir: Union[str, Path]) -> Dict[str, Any]:
    """
    Get information about files in directory for batch processing.
    
    Args:
        input_dir: Directory to analyze
        
    Returns:
        Dictionary with batch information
    """
    processor = GifBatchProcessor()
    return processor.get_batch_info(input_dir)


# Export all functions and classes
__all__ = [
    'GifBatchProcessor',
    'process_gif_batch',
    'resize_gif_batch',
    'optimize_gif_batch',
    'convert_format_gif_batch',
    'add_text_gif_batch',
    'custom_gif_batch',
    'get_gif_batch_info'
]
