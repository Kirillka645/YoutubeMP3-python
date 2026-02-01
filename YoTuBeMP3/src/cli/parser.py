"""
Command-line argument parser.
"""

import argparse
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class CLIArgs:
    """Parsed CLI arguments."""
    url: str
    bitrate: int = 192
    output: Path = Path('./output')
    proxy: Optional[str] = None
    proxy_file: Optional[Path] = None
    verbose: bool = False
    list_formats: bool = False
    no_metadata: bool = False
    normalize: bool = False
    ffmpeg_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    
    parser = argparse.ArgumentParser(
        description='YouTube MP3 Downloader - скачивание аудио с YouTube в формате MP3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры использования:
  %(prog)s "https://youtube.com/watch?v=example" - скачивание с битрейтом 192 kbps
  %(prog)s "https://youtube.com/watch?v=example" -b 320 - скачивание с битрейтом 320 kbps
  %(prog)s "https://youtube.com/watch?v=example" -o ./music - сохранение в ./music
  %(prog)s "https://youtube.com/watch?v=example" --proxy http://proxy:8080 - с прокси

Поддерживаемые битрейты: 128, 192, 320 kbps

Требования:
  - FFmpeg должен быть установлен и доступен в PATH
        '''
    )
    
    parser.add_argument(
        'url',
        help='URL видео YouTube'
    )
    
    parser.add_argument(
        '-b', '--bitrate',
        type=int,
        choices=[128, 192, 320],
        default=192,
        help='Битрейт MP3 (128, 192, 320). По умолчанию: 192'
    )
    
    # Default to Downloads folder
    downloads_path = Path(os.path.join(os.path.expanduser('~'), 'Downloads'))
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=downloads_path,
        help='Путь для сохранения файлов. По умолчанию: ~/Downloads'
    )
    
    parser.add_argument(
        '-p', '--proxy',
        type=str,
        help='Прокси-сервер (формат: http://user:pass@host:port)'
    )
    
    parser.add_argument(
        '--proxy-file',
        type=Path,
        help='Файл со списком прокси (по одному на строку)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Подробный вывод (debug mode)'
    )
    
    parser.add_argument(
        '--list-formats',
        action='store_true',
        help='Показать доступные форматы видео'
    )
    
    parser.add_argument(
        '--no-metadata',
        action='store_true',
        help='Не добавлять метаданные к MP3 файлу'
    )
    
    parser.add_argument(
        '--normalize',
        action='store_true',
        help='Нормализовать громкость аудио'
    )
    
    parser.add_argument(
        '--ffmpeg-path',
        type=str,
        help='Путь к исполняемому файлу FFmpeg'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


def parse_args(args: Optional[list] = None) -> CLIArgs:
    """
    Parse command-line arguments.
    
    Args:
        args: Arguments list (uses sys.argv if None)
    
    Returns:
        CLIArgs object
    """
    parser = create_parser()
    parsed = parser.parse_args(args)
    
    return CLIArgs(
        url=parsed.url,
        bitrate=parsed.bitrate,
        output=parsed.output,
        proxy=parsed.proxy,
        proxy_file=parsed.proxy_file,
        verbose=parsed.verbose,
        list_formats=parsed.list_formats,
        no_metadata=parsed.no_metadata,
        normalize=parsed.normalize,
        ffmpeg_path=parsed.ffmpeg_path,
    )
