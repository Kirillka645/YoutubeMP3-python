"""
YouTube audio downloader using yt-dlp.
"""

import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Optional, Any

from yt_dlp import YoutubeDL, DownloadError
from yt_dlp.utils import ExtractorError

from ..config.settings import Settings
from ..config.proxies import ProxyManager


@dataclass
class DownloadProgress:
    """Download progress information."""
    filename: str = ""
    percent: float = 0.0
    speed: str = ""
    eta: str = ""
    status: str = "starting"


@dataclass
class VideoInfo:
    """Video information."""
    title: str
    url: str
    duration: int  # seconds
    thumbnail: str
    uploader: str
    view_count: int
    like_count: int
    formats: list = field(default_factory=list)
    
    @property
    def duration_str(self) -> str:
        """Get duration as string."""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"


class YouTubeDownloader:
    """
    Main class for downloading audio from YouTube.
    
    Args:
        settings: Application settings
        proxy_manager: Proxy manager instance
    """
    
    def __init__(
        self,
        settings: Optional[Settings] = None,
        proxy_manager: Optional[ProxyManager] = None
    ):
        self.settings = settings or Settings.from_env()
        self.proxy_manager = proxy_manager or ProxyManager()
        self.progress_hook: Optional[Callable[[Dict[str, Any]], None]] = None
        self._ydl = None
    
    def _get_ytdl_options(self, bitrate: int = 192) -> Dict[str, Any]:
        """
        Get yt-dlp options.
        
        Args:
            bitrate: Audio bitrate for MP3 conversion
        
        Returns:
            Dict with yt-dlp options
        """
        proxy = self.proxy_manager.get_proxy_string()
        
        options = {
            'format': 'bestaudio[ext=webm]',
            'outtmpl': '%(title)s.%(ext)s',
            'writethumbnail': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'no_warnings': True,
            'quiet': True,
            'no_color': False,
            'socket_timeout': self.settings.connection_timeout,
            'retries': 3,
            'fragment_retries': 3,
            'extractor_retries': 3,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': str(bitrate),
            }],
            'progress_hooks': [],
        }
        
        if proxy:
            options['proxy'] = proxy
            options['force_ipv4'] = True
        
        if self.progress_hook:
            options['progress_hooks'].append(self.progress_hook)
        
        return options
    
    def set_progress_hook(self, hook: Callable[[Dict[str, Any]], None]) -> None:
        """
        Set progress callback.
        
        Args:
            hook: Callback function
        """
        self.progress_hook = hook
    
    def get_video_info(self, url: str) -> VideoInfo:
        """
        Get video information without downloading.
        
        Args:
            url: YouTube video URL
        
        Returns:
            VideoInfo object
        """
        ydl_opts = self._get_ytdl_options()
        ydl_opts['quiet'] = True
        ydl_opts['simulate'] = True
        
        proxy = self.proxy_manager.get_proxy_string()
        if proxy:
            ydl_opts['proxy'] = proxy
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return VideoInfo(
                title=info.get('title', 'Unknown'),
                url=url,
                duration=info.get('duration', 0),
                thumbnail=info.get('thumbnail', ''),
                uploader=info.get('uploader', 'Unknown'),
                view_count=info.get('view_count', 0),
                like_count=info.get('like_count', 0),
                formats=info.get('formats', [])
            )
    
    def download(
        self,
        url: str,
        output_path: Path,
        bitrate: int = 192,
        add_metadata: bool = True
    ) -> Path:
        """
        Download audio from YouTube and convert to MP3.
        
        Args:
            url: YouTube video URL
            output_path: Output directory path
            bitrate: Audio bitrate (128, 192, 320)
            add_metadata: Whether to add metadata to file
        
        Returns:
            Path to downloaded MP3 file
        """
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if not self.settings.validate_bitrate(bitrate):
            bitrate = self.settings.default_bitrate
        
        ydl_opts = self._get_ytdl_options(bitrate)
        ydl_opts['outtmpl'] = str(output_path / '%(title)s.%(ext)s')
        
        proxy = self.proxy_manager.get_proxy_string()
        if proxy:
            ydl_opts['proxy'] = proxy
        
        # Add metadata postprocessor
        if add_metadata:
            ydl_opts['postprocessors'].append({
                'key': 'MetadataParser',
                'actions': [
                    ('title', None, '%(title)s'),
                    ('artist', None, '%(uploader)s'),
                    ('album', None, 'YouTube'),
                ],
            })
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Get the downloaded file path
            filename = ydl.prepare_filename(info)
            base_name = os.path.splitext(filename)[0]
            mp3_path = Path(f"{base_name}.mp3")
            
            return mp3_path
    
    def download_with_retry(
        self,
        url: str,
        output_path: Path,
        bitrate: int = 192,
        max_retries: int = 3
    ) -> Optional[Path]:
        """
        Download with automatic proxy rotation on failure.
        
        Args:
            url: YouTube video URL
            output_path: Output directory path
            bitrate: Audio bitrate
            max_retries: Maximum number of retries
        
        Returns:
            Path to downloaded file or None
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return self.download(url, output_path, bitrate)
            except (DownloadError, ExtractorError) as e:
                last_error = str(e) or repr(e)
                
                # Try to rotate proxy
                if self.proxy_manager.has_proxies():
                    self.proxy_manager.rotate_proxy()
                    continue
                
                break
            except Exception as e:
                last_error = f"{type(e).__name__}: {str(e) or repr(e)}"
                # Fallback to subprocess on first error
                if attempt == 0:
                    result = self.download_with_subprocess(url, output_path, bitrate)
                    if result:
                        return result
                break
        
        # Try subprocess as last resort
        result = self.download_with_subprocess(url, output_path, bitrate)
        if result:
            return result
        
        raise DownloadError(f"Failed after {max_retries} attempts: {last_error}")
    
    def download_with_subprocess(
        self,
        url: str,
        output_path: Path,
        bitrate: int = 192
    ) -> Optional[Path]:
        """
        Download using yt-dlp subprocess (fallback when Python library fails).
        """
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Build command
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '-f', 'bestaudio[ext=webm]',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', f'{bitrate}K',
            '-o', str(output_path / '%(title)s.%(ext)s'),
        ]
        
        # Add proxy if configured
        proxy = self.proxy_manager.get_proxy_string()
        if proxy:
            cmd.extend(['--proxy', proxy])
        
        cmd.append(url)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                # Find the downloaded MP3 file
                for f in output_path.glob('*.mp3'):
                    return f
            else:
                # Try to find any file that might have been created
                for f in output_path.glob('*'):
                    if f.suffix.lower() in ['.mp3', '.webm', '.m4a']:
                        return f
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate YouTube URL.
        
        Args:
            url: URL to validate
        
        Returns:
            True if valid YouTube URL
        """
        youtube_regex = r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$'
        return bool(re.match(youtube_regex, url))
