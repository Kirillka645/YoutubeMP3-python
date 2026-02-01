"""
Audio converter using FFmpeg.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class AudioMetadata:
    """Audio file metadata."""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    track: Optional[str] = None
    cover: Optional[Path] = None
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for FFmpeg."""
        result = {}
        if self.title:
            result['title'] = self.title
        if self.artist:
            result['artist'] = self.artist
        if self.album:
            result['album'] = self.album
        if self.genre:
            result['genre'] = self.genre
        if self.year:
            result['year'] = str(self.year)
        if self.track:
            result['track'] = self.track
        return result


class AudioConverter:
    """
    Audio converter using FFmpeg.
    
    Args:
        ffmpeg_path: Path to ffmpeg executable
    """
    
    def __init__(self, ffmpeg_path: str = 'ffmpeg'):
        self.ffmpeg_path = ffmpeg_path
    
    def check_ffmpeg(self) -> bool:
        """
        Check if FFmpeg is available.
        
        Returns:
            True if FFmpeg is installed
        """
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def get_ffmpeg_version(self) -> Optional[str]:
        """
        Get FFmpeg version.
        
        Returns:
            Version string or None
        """
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                first_line = result.stdout.split('\n')[0]
                return first_line
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return None
    
    def convert_to_mp3(
        self,
        input_file: Path,
        output_file: Path,
        bitrate: int = 192,
        metadata: Optional[AudioMetadata] = None,
        overwrite: bool = False
    ) -> bool:
        """
        Convert audio to MP3 with specified bitrate.
        
        Args:
            input_file: Input audio/video file path
            output_file: Output MP3 file path
            bitrate: Audio bitrate (128, 192, 320)
            metadata: Audio metadata to add
            overwrite: Whether to overwrite output file
        
        Returns:
            True if conversion successful
        """
        input_file = Path(input_file)
        output_file = Path(output_file)
        
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.ffmpeg_path,
            '-y' if overwrite else '-n',
            '-i', str(input_file),
            '-codec:a', 'libmp3lame',
            f'-b:a', f'{bitrate}k',
            '-q:a', '2',
        ]
        
        # Add metadata
        if metadata:
            metadata_dict = metadata.to_dict()
            for key, value in metadata_dict.items():
                cmd.extend(['-metadata', f'{key}={value}'])
        
        cmd.append(str(output_file))
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            raise TimeoutError("FFmpeg conversion timed out")
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"FFmpeg error: {e}")
    
    def extract_audio(
        self,
        video_file: Path,
        output_file: Path,
        bitrate: int = 192,
        metadata: Optional[AudioMetadata] = None
    ) -> bool:
        """
        Extract audio from video file.
        
        Args:
            video_file: Input video file path
            output_file: Output audio file path
            bitrate: Audio bitrate
            metadata: Audio metadata
        
        Returns:
            True if extraction successful
        """
        return self.convert_to_mp3(video_file, output_file, bitrate, metadata)
    
    def get_audio_info(self, audio_file: Path) -> Dict[str, Any]:
        """
        Get audio file information using ffprobe.
        
        Args:
            audio_file: Path to audio file
        
        Returns:
            Dict with audio information
        """
        try:
            result = subprocess.run(
                [
                    'ffprobe',
                    '-v', 'quiet',
                    '-print_format', 'json',
                    '-show_format',
                    '-show_streams',
                    str(audio_file)
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
        except (subprocess.SubprocessError, FileNotFoundError, json.JSONDecodeError):
            pass
        
        return {}
    
    def normalize_audio(
        self,
        input_file: Path,
        output_file: Path,
        target_level: float = -1.0
    ) -> bool:
        """
        Normalize audio level.
        
        Args:
            input_file: Input audio file
            output_file: Output audio file
            target_level: Target loudness level in dB
        
        Returns:
            True if normalization successful
        """
        cmd = [
            self.ffmpeg_path,
            '-y',
            '-i', str(input_file),
            '-af', f'loudnorm=I={target_level}:TP=-1.5:LRA=11',
            '-codec:a', 'libmp3lame',
            '-b:a', '192k',
            str(output_file)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, TimeoutError):
            return False
    
    @staticmethod
    def get_supported_bitrates() -> List[int]:
        """Get list of supported bitrates."""
        return [128, 192, 320]
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """
        Format duration in seconds to HH:MM:SS.
        
        Args:
            seconds: Duration in seconds
        
        Returns:
            Formatted duration string
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
