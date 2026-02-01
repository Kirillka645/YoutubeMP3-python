"""
Logging utilities.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class LoggingUtils:
    """Logging utilities."""
    
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    @staticmethod
    def setup_logging(
        level: str = 'INFO',
        log_file: Optional[Path] = None,
        verbose: bool = False
    ) -> logging.Logger:
        """
        Setup logging configuration.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional path to log file
            verbose: Enable verbose output
        
        Returns:
            Configured logger
        """
        # Convert string level to logging constant
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        if verbose:
            log_level = logging.DEBUG
        
        # Create logger
        logger = logging.getLogger('youtube_mp3_downloader')
        logger.setLevel(log_level)
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            LoggingUtils.LOG_FORMAT,
            LoggingUtils.DATE_FORMAT
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def get_log_filename() -> Path:
        """
        Get log filename with timestamp.
        
        Returns:
            Path to log file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return Path('logs') / f'download_{timestamp}.log'
    
    @staticmethod
    def log_exception(logger: logging.Logger, message: str, exc: Exception) -> None:
        """
        Log exception with context.
        
        Args:
            logger: Logger instance
            message: Context message
            exc: Exception object
        """
        logger.error(f"{message}: {exc}")
        logger.debug("Exception traceback:", exc_info=True)
