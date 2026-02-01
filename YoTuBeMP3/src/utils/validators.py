"""
URL validation utilities.
"""

import re
from typing import List, Optional


class URLValidator:
    """URL validation utilities."""
    
    # YouTube URL patterns
    YOUTUBE_PATTERNS = [
        r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'^https?://(www\.)?youtube\.com/embed/[\w-]+',
        r'^https?://youtu\.be/[\w-]+',
        r'^https?://(www\.)?youtube\.com/shorts/[\w-]+',
        r'^https?://m\.youtube\.com/watch\?v=[\w-]+',
    ]
    
    @classmethod
    def validate_youtube(cls, url: str) -> bool:
        """
        Validate YouTube URL.
        
        Args:
            url: URL to validate
        
        Returns:
            True if valid YouTube URL
        """
        if not url:
            return False
        
        return any(
            re.match(pattern, url)
            for pattern in cls.YOUTUBE_PATTERNS
        )
    
    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url: YouTube URL
        
        Returns:
            Video ID or None
        """
        patterns = [
            r'(?:v=|\/)([\w-]{11})',  # Standard URL
            r'(?:youtu\.be\/)([\w-]{11})',  # Short URL
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    @classmethod
    def normalize_url(cls, url: str) -> str:
        """
        Normalize YouTube URL.
        
        Args:
            url: YouTube URL
        
        Returns:
            Normalized URL
        """
        video_id = cls.extract_video_id(url)
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        return url
    
    @classmethod
    def extract_urls(cls, text: str) -> List[str]:
        """
        Extract all YouTube URLs from text.
        
        Args:
            text: Text containing URLs
        
        Returns:
            List of YouTube URLs
        """
        urls = []
        for pattern in cls.YOUTUBE_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if not match.startswith('http'):
                    match = 'https://www.youtube.com/' + match
                urls.append(match)
        return urls
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Basic URL validation.
        
        Args:
            url: URL to validate
        
        Returns:
            True if valid URL format
        """
        pattern = r'^https?://[^\s]+$'
        return bool(re.match(pattern, url))
