"""Core module for downloading and converting audio."""

from .downloader import YouTubeDownloader, DownloadProgress
from .converter import AudioConverter
from .metadata import AudioMetadata

__all__ = [
    "YouTubeDownloader",
    "DownloadProgress",
    "AudioConverter",
    "AudioMetadata",
]
