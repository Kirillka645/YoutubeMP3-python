"""
YouTube MP3 Downloader

Python-приложение для скачивания аудио с YouTube в формате MP3.
Поддержка битрейтов 128, 192, 320 kbps.
Оптимизировано для использования в РФ с поддержкой прокси.
"""

__version__ = "1.0.0"
__author__ = "YouTube MP3 Downloader Team"

from .core.downloader import YouTubeDownloader
from .core.converter import AudioConverter
from .config.settings import Settings

__all__ = [
    "YouTubeDownloader",
    "AudioConverter", 
    "Settings",
    "__version__",
]
