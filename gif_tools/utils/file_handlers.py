"""
File handling utilities for GIF-Tools.

This module provides file I/O operations, temporary file management,
and file format detection used throughout the GIF-Tools library.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .constants import MIME_TYPES, SUPPORTED_ANIMATED_FORMATS, SUPPORTED_IMAGE_FORMATS, SUPPORTED_VIDEO_FORMATS
from .validation import ValidationError, validate_file_path


class FileHandler:
    """File handling utility class."""
    
    def __init__(self, temp_dir: Optional[Union[str, Path]] = None):
        """
        Initialize file handler.
        
        Args:
            temp_dir: Custom temporary directory path
        """
        self.temp_dir = Path(temp_dir) if temp_dir else None
        self._temp_files: List[Path] = []
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup temporary files."""
        self.cleanup()
    
    def get_temp_file(self, suffix: str = '.tmp', prefix: str = 'gif_tools_') -> Path:
        """
        Create a temporary file.
        
        Args:
            suffix: File suffix
            prefix: File prefix
            
        Returns:
            Path to temporary file
        """
        if self.temp_dir:
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            temp_file = tempfile.NamedTemporaryFile(
                suffix=suffix,
                prefix=prefix,
                dir=self.temp_dir,
                delete=False
            )
        else:
            temp_file = tempfile.NamedTemporaryFile(
                suffix=suffix,
                prefix=prefix,
                delete=False
            )
        
        temp_path = Path(temp_file.name)
        temp_file.close()
        self._temp_files.append(temp_path)
        return temp_path
    
    def get_temp_dir(self, prefix: str = 'gif_tools_') -> Path:
        """
        Create a temporary directory.
        
        Args:
            prefix: Directory prefix
            
        Returns:
            Path to temporary directory
        """
        if self.temp_dir:
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            temp_dir = tempfile.mkdtemp(prefix=prefix, dir=self.temp_dir)
        else:
            temp_dir = tempfile.mkdtemp(prefix=prefix)
        
        temp_path = Path(temp_dir)
        self._temp_files.append(temp_path)
        return temp_path
    
    def cleanup(self):
        """Clean up all temporary files and directories."""
        for temp_path in self._temp_files:
            try:
                if temp_path.is_file():
                    temp_path.unlink()
                elif temp_path.is_dir():
                    shutil.rmtree(temp_path)
            except (OSError, PermissionError):
                # Ignore cleanup errors
                pass
        
        self._temp_files.clear()
    
    def copy_file(self, src: Union[str, Path], dst: Union[str, Path]) -> Path:
        """
        Copy a file.
        
        Args:
            src: Source file path
            dst: Destination file path
            
        Returns:
            Destination path
        """
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            raise ValidationError(f"Source file not found: {src_path}")
        
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        return dst_path
    
    def move_file(self, src: Union[str, Path], dst: Union[str, Path]) -> Path:
        """
        Move a file.
        
        Args:
            src: Source file path
            dst: Destination file path
            
        Returns:
            Destination path
        """
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            raise ValidationError(f"Source file not found: {src_path}")
        
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))
        return dst_path
    
    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except (OSError, PermissionError):
            return False
    
    def get_file_size(self, file_path: Union[str, Path]) -> int:
        """
        Get file size in bytes.
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in bytes
        """
        path = Path(file_path)
        if not path.exists():
            raise ValidationError(f"File not found: {path}")
        
        return path.stat().st_size
    
    def get_file_extension(self, file_path: Union[str, Path]) -> str:
        """
        Get file extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            File extension (with dot)
        """
        return Path(file_path).suffix.lower()
    
    def get_mime_type(self, file_path: Union[str, Path]) -> str:
        """
        Get MIME type for file.
        
        Args:
            file_path: Path to file
            
        Returns:
            MIME type string
        """
        extension = self.get_file_extension(file_path)
        return MIME_TYPES.get(extension, 'application/octet-stream')
    
    def is_image_file(self, file_path: Union[str, Path]) -> bool:
        """
        Check if file is an image.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is an image
        """
        extension = self.get_file_extension(file_path)
        return extension in SUPPORTED_IMAGE_FORMATS
    
    def is_video_file(self, file_path: Union[str, Path]) -> bool:
        """
        Check if file is a video.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is a video
        """
        extension = self.get_file_extension(file_path)
        return extension in SUPPORTED_VIDEO_FORMATS
    
    def is_animated_file(self, file_path: Union[str, Path]) -> bool:
        """
        Check if file is an animated format.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is animated
        """
        extension = self.get_file_extension(file_path)
        return extension in SUPPORTED_ANIMATED_FORMATS
    
    def ensure_directory(self, dir_path: Union[str, Path]) -> Path:
        """
        Ensure directory exists.
        
        Args:
            dir_path: Path to directory
            
        Returns:
            Directory path
        """
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def list_files(self, dir_path: Union[str, Path], 
                   pattern: str = '*', 
                   recursive: bool = False) -> List[Path]:
        """
        List files in directory.
        
        Args:
            dir_path: Directory path
            pattern: File pattern to match
            recursive: Whether to search recursively
            
        Returns:
            List of file paths
        """
        path = Path(dir_path)
        if not path.exists() or not path.is_dir():
            raise ValidationError(f"Directory not found: {path}")
        
        if recursive:
            return list(path.rglob(pattern))
        else:
            return list(path.glob(pattern))
    
    def get_unique_filename(self, file_path: Union[str, Path]) -> Path:
        """
        Get unique filename if file exists.
        
        Args:
            file_path: Original file path
            
        Returns:
            Unique file path
        """
        path = Path(file_path)
        if not path.exists():
            return path
        
        counter = 1
        while True:
            new_path = path.parent / f"{path.stem}_{counter}{path.suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    def backup_file(self, file_path: Union[str, Path], 
                   backup_suffix: str = '.bak') -> Path:
        """
        Create backup of file.
        
        Args:
            file_path: Path to file
            backup_suffix: Backup file suffix
            
        Returns:
            Backup file path
        """
        path = Path(file_path)
        if not path.exists():
            raise ValidationError(f"File not found: {path}")
        
        backup_path = path.with_suffix(path.suffix + backup_suffix)
        return self.copy_file(path, backup_path)
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get comprehensive file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        if not path.exists():
            raise ValidationError(f"File not found: {path}")
        
        stat = path.stat()
        return {
            'path': str(path.absolute()),
            'name': path.name,
            'stem': path.stem,
            'suffix': path.suffix,
            'extension': path.suffix.lower(),
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'is_file': path.is_file(),
            'is_dir': path.is_dir(),
            'mime_type': self.get_mime_type(path),
            'is_image': self.is_image_file(path),
            'is_video': self.is_video_file(path),
            'is_animated': self.is_animated_file(path)
        }


def get_file_handler(temp_dir: Optional[Union[str, Path]] = None) -> FileHandler:
    """
    Get a file handler instance.
    
    Args:
        temp_dir: Custom temporary directory path
        
    Returns:
        FileHandler instance
    """
    return FileHandler(temp_dir)


def create_temp_file(suffix: str = '.tmp', 
                    prefix: str = 'gif_tools_',
                    temp_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Create a temporary file.
    
    Args:
        suffix: File suffix
        prefix: File prefix
        temp_dir: Custom temporary directory path
        
    Returns:
        Path to temporary file
    """
    with FileHandler(temp_dir) as handler:
        return handler.get_temp_file(suffix, prefix)


def create_temp_dir(prefix: str = 'gif_tools_',
                   temp_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Create a temporary directory.
    
    Args:
        prefix: Directory prefix
        temp_dir: Custom temporary directory path
        
    Returns:
        Path to temporary directory
    """
    with FileHandler(temp_dir) as handler:
        return handler.get_temp_dir(prefix)


def cleanup_temp_files(temp_paths: List[Union[str, Path]]):
    """
    Clean up temporary files.
    
    Args:
        temp_paths: List of temporary file/directory paths
    """
    for temp_path in temp_paths:
        try:
            path = Path(temp_path)
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
        except (OSError, PermissionError):
            # Ignore cleanup errors
            pass


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get file extension.
    
    Args:
        file_path: Path to file
        
    Returns:
        File extension (with dot)
    """
    return Path(file_path).suffix.lower()


def get_mime_type(file_path: Union[str, Path]) -> str:
    """
    Get MIME type for file.
    
    Args:
        file_path: Path to file
        
    Returns:
        MIME type string
    """
    extension = get_file_extension(file_path)
    return MIME_TYPES.get(extension, 'application/octet-stream')


def is_supported_file(file_path: Union[str, Path]) -> bool:
    """
    Check if file is supported by GIF-Tools.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file is supported
    """
    extension = get_file_extension(file_path)
    return (extension in SUPPORTED_IMAGE_FORMATS or 
            extension in SUPPORTED_VIDEO_FORMATS or 
            extension in SUPPORTED_ANIMATED_FORMATS)


def get_supported_extensions() -> List[str]:
    """
    Get list of all supported file extensions.
    
    Returns:
        List of supported extensions
    """
    return (SUPPORTED_IMAGE_FORMATS + 
            SUPPORTED_VIDEO_FORMATS + 
            SUPPORTED_ANIMATED_FORMATS)


# Export all functions and classes
__all__ = [
    'FileHandler',
    'get_file_handler',
    'create_temp_file',
    'create_temp_dir',
    'cleanup_temp_files',
    'get_file_extension',
    'get_mime_type',
    'is_supported_file',
    'get_supported_extensions'
]
