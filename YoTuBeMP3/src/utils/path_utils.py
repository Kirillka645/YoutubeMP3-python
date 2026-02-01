"""
Path manipulation utilities.
"""

import os
import re
from pathlib import Path
from typing import List, Optional


class PathUtils:
    """Path manipulation utilities."""
    
    INVALID_FILENAME_CHARS = r'<>:"/\\|?*\0'
    
    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 255) -> str:
        """
        Sanitize filename for safe file system usage.
        
        Args:
            filename: Original filename
            max_length: Maximum filename length
        
        Returns:
            Sanitized filename
        """
        # Replace invalid characters
        result = filename
        for char in PathUtils.INVALID_FILENAME_CHARS:
            result = result.replace(char, '_')
        
        # Remove control characters
        result = ''.join(c for c in result if ord(c) >= 32)
        
        # Trim whitespace
        result = result.strip()
        
        # Limit length
        if len(result) > max_length:
            # Try to cut at word boundary
            result = result[:max_length]
            last_space = result.rfind(' ')
            if last_space > max_length * 0.8:
                result = result[:last_space]
        
        # Handle empty result
        if not result:
            result = 'unknown'
        
        return result
    
    @staticmethod
    def get_file_size(path: Path) -> Optional[int]:
        """
        Get file size in bytes.
        
        Args:
            path: Path to file
        
        Returns:
            File size in bytes or None if error
        """
        try:
            return path.stat().st_size
        except (OSError, FileNotFoundError):
            return None
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size to human readable format.
        
        Args:
            size_bytes: Size in bytes
        
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        
        return f"{size_bytes:.2f} TB"
    
    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """
        Ensure directory exists.
        
        Args:
            path: Directory path
        
        Returns:
            Path object
        """
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def find_file(directory: Path, filename: str) -> Optional[Path]:
        """
        Find file in directory and subdirectories.
        
        Args:
            directory: Search directory
            filename: Filename to find
        
        Returns:
            Path to file or None
        """
        try:
            for root, dirs, files in os.walk(directory):
                if filename in files:
                    return Path(root) / filename
        except OSError:
            pass
        
        return None
    
    @staticmethod
    def get_unique_path(path: Path) -> Path:
        """
        Get unique path by adding number suffix if file exists.
        
        Args:
            path: Original path
        
        Returns:
            Unique path
        """
        if not path.exists():
            return path
        
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1
        
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    @staticmethod
    def get_output_filename(title: str, bitrate: int, extension: str = 'mp3') -> str:
        """
        Generate output filename from video title.
        
        Args:
            title: Video title
            bitrate: Audio bitrate
            extension: File extension
        
        Returns:
            Sanitized filename
        """
        clean_title = PathUtils.sanitize_filename(title)
        return f"{clean_title}_{bitrate}kbps.{extension}"
    
    @staticmethod
    def cleanup_temp_files(directory: Path, pattern: str = '*.temp') -> int:
        """
        Clean up temporary files.
        
        Args:
            directory: Directory to clean
            pattern: File pattern to match
        
        Returns:
            Number of deleted files
        """
        count = 0
        try:
            for file in directory.glob(pattern):
                try:
                    file.unlink()
                    count += 1
                except OSError:
                    pass
        except OSError:
            pass
        
        return count
