"""
Utility functions and modules for the bot.
"""
import logging
from rich.logging import RichHandler

def setup_logging():
    """Configure the logging system."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

def get_logger(name: str = "nexon") -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name) 