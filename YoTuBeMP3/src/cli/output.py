"""
CLI output formatting with colors.
"""

import sys
from typing import Optional
from datetime import datetime
from pathlib import Path

try:
    from colorama import Fore, Style, init
    init(autoreset=True, strip=True)
    HAS_COLORS = True
except ImportError:
    HAS_COLORS = False
    Fore = Style = type('Dummy', (), {'RESET_ALL': '', 'RED': '', 'GREEN': '', 'YELLOW': '', 
                                       'BLUE': '', 'CYAN': '', 'WHITE': '', 'MAGENTA': ''})


class CLIOutput:
    """Formatted CLI output."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def print_header(self, text: str) -> None:
        """Print header."""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}\n")
    
    def print_success(self, text: str) -> None:
        """Print success message."""
        print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")
    
    def print_error(self, text: str) -> None:
        """Print error message."""
        print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}", file=sys.stderr)
    
    def print_warning(self, text: str) -> None:
        """Print warning message."""
        print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")
    
    def print_info(self, text: str) -> None:
        """Print info message."""
        print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")
    
    def print_progress(self, text: str, end: str = '\r') -> None:
        """Print progress message."""
        print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}", end=end, flush=True)
    
    def print_video_info(
        self,
        title: str,
        uploader: str,
        duration: str,
        view_count: str,
        thumbnail: Optional[str] = None
    ) -> None:
        """Print video information."""
        print(f"{Fore.MAGENTA}🎵 {Style.BRIGHT}{title}{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}Автор:{Style.RESET_ALL} {uploader}")
        print(f"   {Fore.CYAN}Длительность:{Style.RESET_ALL} {duration}")
        print(f"   {Fore.CYAN}Просмотры:{Style.RESET_ALL} {view_count}")
        print()
    
    def print_download_start(self, filename: str, bitrate: int) -> None:
        """Print download start message."""
        print(f"{Fore.BLUE}📥 {Style.BRIGHT}Скачивание:{Style.RESET_ALL} {filename}")
        print(f"   {Fore.CYAN}Битрейт:{Style.RESET_ALL} {bitrate} kbps")
        print()
    
    def print_download_progress(
        self,
        percent: float,
        speed: str,
        eta: str,
        filename: str
    ) -> None:
        """Print download progress."""
        bar_width = 30
        filled = int(bar_width * percent / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        progress = f"{Fore.CYAN}[{Style.BRIGHT}{bar}{Style.RESET_ALL}{Fore.CYAN}] {percent:.1f}%{Style.RESET_ALL}"
        status = f"{Fore.GREEN}{speed}{Style.RESET_ALL} | {Fore.YELLOW}ETA: {eta}{Style.RESET_ALL}"
        
        print(f"\r{progress} {status}  {filename}", end='\r', flush=True)
    
    def print_download_complete(self, filepath: Path, filesize: str) -> None:
        """Print download complete message."""
        print()
        print(f"{Fore.GREEN}✅ {Style.BRIGHT}Готово!{Style.RESET_ALL}")
        print(f"   {Fore.CYAN}Файл:{Style.RESET_ALL} {filepath}")
        print(f"   {Fore.CYAN}Размер:{Style.RESET_ALL} {filesize}")
        print()
    
    def print_ffmpeg_info(self, version: str) -> None:
        """Print FFmpeg info."""
        print(f"{Fore.CYAN}FFmpeg версия:{Style.RESET_ALL} {version}")
    
    def print_proxy_info(self, proxy: str) -> None:
        """Print proxy info."""
        print(f"{Fore.CYAN}Используется прокси:{Style.RESET_ALL} {proxy}")
    
    def print_format_list(self, formats: list) -> None:
        """Print available formats."""
        print(f"\n{Fore.CYAN}Доступные форматы:{Style.RESET_ALL}")
        print("-" * 60)
        
        for fmt in formats[:10]:  # Show first 10 formats
            ext = fmt.get('ext', 'unknown')
            note = fmt.get('format_note', '')
            fmt_id = fmt.get('format_id', '')
            print(f"  {fmt_id:>5} | {ext:>5} | {note}")
        
        print("-" * 60)
    
    def print_verbose(self, text: str) -> None:
        """Print verbose debug info."""
        if self.verbose:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"{Fore.BLUE}[{timestamp}]{Style.RESET_ALL} {text}")
    
    def print_section(self, title: str) -> None:
        """Print section header."""
        separator = '─' * 50
        print(f"\n{Fore.CYAN}{separator}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(50)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{separator}{Style.RESET_ALL}\n")
    
    def print_stats(self, stats: dict) -> None:
        """Print download statistics."""
        print(f"{Fore.CYAN}📊 Статистика:{Style.RESET_ALL}")
        for key, value in stats.items():
            print(f"   {key}: {value}")
