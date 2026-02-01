"""
Main entry point for YouTube MP3 Downloader.
"""

import sys
import io
from pathlib import Path

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from .cli.parser import parse_args
from .cli.output import CLIOutput
from .config.settings import Settings
from .config.proxies import ProxyManager
from .core.downloader import YouTubeDownloader
from .core.converter import AudioConverter
from .utils.logging_utils import LoggingUtils
from .utils.path_utils import PathUtils


def main():
    """Main application entry point."""
    # Parse arguments
    args = parse_args()
    
    # Setup output
    output = CLIOutput(verbose=args.verbose)
    
    # Setup logging
    log_file = LoggingUtils.get_log_filename()
    logger = LoggingUtils.setup_logging(
        level='DEBUG' if args.verbose else 'INFO',
        log_file=log_file,
        verbose=args.verbose
    )
    
    # Load settings
    settings = Settings.from_env()
    settings.default_bitrate = args.bitrate
    
    if args.ffmpeg_path:
        settings.ffmpeg_path = args.ffmpeg_path
    
    # Setup proxy manager
    proxy_manager = ProxyManager()
    
    if args.proxy:
        proxy_manager.add_proxy(args.proxy)
        output.print_proxy_info(args.proxy)
    
    if args.proxy_file:
        count = proxy_manager.load_proxies(str(args.proxy_file))
        output.print_info(f"Загружено прокси: {count}")
    
    # Setup converter
    converter = AudioConverter(ffmpeg_path=settings.ffmpeg_path)
    
    # Check FFmpeg
    output.print_section("Проверка FFmpeg")
    if converter.check_ffmpeg():
        version = converter.get_ffmpeg_version()
        output.print_ffmpeg_info(version or "Unknown")
    else:
        output.print_error("FFmpeg не найден! Установите FFmpeg и добавьте его в PATH.")
        output.print_info("Windows: choco install ffmpeg")
        output.print_info("Linux: sudo apt install ffmpeg")
        output.print_info("macOS: brew install ffmpeg")
        sys.exit(1)
    
    # Validate URL
    output.print_section("Валидация URL")
    if not YouTubeDownloader.validate_url(args.url):
        output.print_error("Невалидный YouTube URL")
        sys.exit(1)
    
    output.print_success(f"URL валиден")
    
    # Initialize downloader
    downloader = YouTubeDownloader(settings, proxy_manager)
    
    # Get video info
    output.print_section("Информация о видео")
    try:
        video_info = downloader.get_video_info(args.url)
        output.print_video_info(
            title=video_info.title,
            uploader=video_info.uploader,
            duration=video_info.duration_str,
            view_count=f"{video_info.view_count:,}",
            thumbnail=video_info.thumbnail
        )
        logger.info(f"Video: {video_info.title} by {video_info.uploader}")
    except Exception as e:
        output.print_error(f"Не удалось получить информацию: {e}")
        logger.error(f"Failed to get video info: {e}")
        sys.exit(1)
    
    # List formats if requested
    if args.list_formats:
        output.print_section("Доступные форматы")
        output.print_format_list(video_info.formats)
    
    # Download
    output.print_section("Скачивание")
    output.print_download_start(video_info.title, args.bitrate)
    
    try:
        output_path = PathUtils.ensure_directory(args.output)
        output_file = output_path / PathUtils.get_output_filename(
            video_info.title, args.bitrate
        )
        
        # Set progress hook
        def progress_hook(data):
            if data.get('status') == 'downloading':
                percent = data.get('downloaded_bytes', 0) / data.get('total_bytes', 1) * 100
                speed = data.get('speed', 0)
                eta = data.get('eta', 0)
                filename = data.get('filename', '')
                
                if speed:
                    speed_str = f"{speed / 1024 / 1024:.1f} MB/s"
                else:
                    speed_str = "N/A"
                
                if eta:
                    eta_str = f"{eta}s"
                else:
                    eta_str = "N/A"
                
                output.print_download_progress(percent, speed_str, eta_str, filename)
        
        downloader.set_progress_hook(progress_hook)
        
        # Download with proxy rotation
        result_file = downloader.download_with_retry(
            url=args.url,
            output_path=output_path,
            bitrate=args.bitrate,
            max_retries=3
        )
        
        # Normalize if requested
        if args.normalize and result_file:
            output.print_info("Нормализация аудио...")
            normalized_file = PathUtils.get_unique_path(result_file)
            if converter.normalize_audio(result_file, normalized_file):
                result_file = normalized_file
        
        # Get file size
        if result_file:
            filesize = PathUtils.get_file_size(result_file)
            filesize_str = PathUtils.format_file_size(filesize) if filesize else "Unknown"
            output.print_download_complete(result_file, filesize_str)
            logger.info(f"Download complete: {result_file}")
        else:
            output.print_error("Не удалось скачать файл")
            sys.exit(1)
    
    except Exception as e:
        output.print_error(f"Ошибка скачивания: {e}")
        logger.error(f"Download failed: {e}")
        sys.exit(1)
    
    output.print_section("Готово!")
    output.print_success("Аудио успешно скачано!")


if __name__ == '__main__':
    main()
