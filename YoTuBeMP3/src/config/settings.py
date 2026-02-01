"""
Configuration settings for YouTube MP3 Downloader.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Settings:
    """Application settings."""
    
    # Supported bitrates
    BITRATES: Dict[str, int] = field(default_factory=lambda: {
        '128': 128,
        '192': 192,
        '320': 320
    })
    
    # Default format
    DEFAULT_FORMAT: str = 'mp3'
    
    # Output directory
    output_dir: Path = Path('./output')
    
    # FFmpeg path
    ffmpeg_path: str = 'ffmpeg'
    
    # Timeout settings
    download_timeout: int = 300  # seconds
    connection_timeout: int = 30  # seconds
    
    # Proxy settings
    proxy: Optional[str] = None
    proxy_file: Optional[str] = None
    
    # Logging level
    log_level: str = 'INFO'
    
    # Default bitrate
    default_bitrate: int = 192
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """Create settings from environment variables."""
        return cls(
            output_dir=Path(os.getenv('OUTPUT_DIR', './output')),
            ffmpeg_path=os.getenv('FFMPEG_PATH', 'ffmpeg'),
            download_timeout=int(os.getenv('DOWNLOAD_TIMEOUT', 300)),
            connection_timeout=int(os.getenv('CONNECTION_TIMEOUT', 30)),
            proxy=os.getenv('PROXY', None),
            proxy_file=os.getenv('PROXY_FILE', None),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            default_bitrate=int(os.getenv('DEFAULT_BITRATE', 192)),
        )
    
    def get_bitrate(self, bitrate: Optional[int] = None) -> int:
        """Get bitrate value, fallback to default."""
        if bitrate is None:
            return self.default_bitrate
        if bitrate in self.BITRATES.values():
            return bitrate
        return self.default_bitrate
    
    def validate_bitrate(self, bitrate: int) -> bool:
        """Validate bitrate value."""
        return bitrate in self.BITRATES.values()
