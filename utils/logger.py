import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

# Nexon theme for logging
NEXON_THEME = Theme({
    "info": "bright_blue",
    "warning": "yellow",
    "error": "red bold",
    "success": "green",
    "debug": "magenta",
    "loading": "cyan"
})

console = Console(theme=NEXON_THEME)

def get_logger(name: str = "nexon", level: Optional[int] = None) -> logging.Logger:
    """Get or create a logger instance"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Set log level
        level = level or logging.INFO
        logger.setLevel(level)

        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Create console handler with Rich
        console_handler = RichHandler(
            rich_tracebacks=True,
            console=console,
            show_time=True,
            show_path=False
        )
        console_handler.setLevel(logging.INFO)

        # Create file handler
        log_file = log_dir / f"nexon-{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s %(message)s',
            datefmt='%H:%M:%S'
        )

        # Set formatters
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

# Create default logger instance
logger = get_logger()

__all__ = ['logger', 'get_logger']