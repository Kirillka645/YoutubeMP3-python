"""
Metadata handling for audio files.
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class AudioMetadata:
    """Audio file metadata."""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    album_artist: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    track: Optional[str] = None
    disc_number: Optional[str] = None
    comment: Optional[str] = None
    copyright: Optional[str] = None
    encoded_by: Optional[str] = None
    cover: Optional[bytes] = None
    
    @classmethod
    def from_youtube_info(cls, info: Dict) -> 'AudioMetadata':
        """
        Create metadata from YouTube video info.
        
        Args:
            info: YouTube video info dict
        
        Returns:
            AudioMetadata object
        """
        return cls(
            title=info.get('title'),
            artist=info.get('uploader'),
            album='YouTube',
            genre='YouTube',
            year=None,
            track=None,
            comment=f"Downloaded from YouTube: {info.get('webpage_url')}",
            copyright=None,
            encoded_by='YouTube MP3 Downloader',
        )
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for FFmpeg."""
        result = {}
        mapping = {
            'title': 'title',
            'artist': 'artist',
            'album': 'album',
            'album_artist': 'album_artist',
            'genre': 'genre',
            'year': 'date',
            'track': 'track',
            'disc_number': 'disc',
            'comment': 'comment',
            'copyright': 'copyright',
            'encoded_by': 'encoded_by',
        }
        
        for field, key in mapping.items():
            value = getattr(self, field, None)
            if value:
                result[key] = str(value)
        
        return result
