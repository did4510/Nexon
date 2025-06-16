import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Define custom theme for rich console
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red",
    "critical": "red bold",
    "debug": "green",
    "ticket": "blue",
    "staff": "magenta",
    "database": "yellow",
    "api": "cyan",
})

# Initialize rich console
console = Console(theme=custom_theme)

class CustomFormatter(logging.Formatter):
    """Custom formatter with colors and emojis"""
    
    FORMATS = {
        logging.DEBUG: "🔍 {message}",
        logging.INFO: "ℹ️  {message}",
        logging.WARNING: "⚠️ {message}",
        logging.ERROR: "❌  {message}",
        logging.CRITICAL: "💥 {message}",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, style="{")
        return formatter.format(record)

def setup_logging():
    """Configure logging for the bot"""
    
    # Get log level from environment or default to INFO
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Create main logger
    logger = logging.getLogger("nexon")
    logger.setLevel(getattr(logging, log_level))
    
    # Prevent duplicate logging
    if logger.handlers:
        return logger

    # Console handler with rich formatting
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True
    )
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOGS_DIR / "nexon.log",
        maxBytes=5_242_880,  # 5MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    logger.addHandler(file_handler)

    # Separate handlers for different log types
    handlers = {
        "tickets": logging.handlers.RotatingFileHandler(
            filename=LOGS_DIR / "tickets.log",
            maxBytes=5_242_880,
            backupCount=5,
            encoding="utf-8"
        ),
        "staff": logging.handlers.RotatingFileHandler(
            filename=LOGS_DIR / "staff.log",
            maxBytes=5_242_880,
            backupCount=5,
            encoding="utf-8"
        ),
        "database": logging.handlers.RotatingFileHandler(
            filename=LOGS_DIR / "database.log",
            maxBytes=5_242_880,
            backupCount=5,
            encoding="utf-8"
        ),
        "api": logging.handlers.RotatingFileHandler(
            filename=LOGS_DIR / "api.log",
            maxBytes=5_242_880,
            backupCount=5,
            encoding="utf-8"
        )
    }

    # Configure each handler
    for name, handler in handlers.items():
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        logger.addHandler(handler)

    return logger

# Create specialized loggers
def get_logger(name: str) -> logging.Logger:
    """Get a specialized logger for different components"""
    logger = logging.getLogger(f"nexon.{name}")
    return logger

# Logging decorators
def log_ticket_activity(func):
    """Decorator to log ticket-related activities"""
    async def wrapper(*args, **kwargs):
        logger = get_logger("tickets")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Ticket activity: {func.__name__} | Args: {args} | Kwargs: {kwargs}")
            return result
        except Exception as e:
            logger.error(f"Ticket error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper

def log_staff_activity(func):
    """Decorator to log staff-related activities"""
    async def wrapper(*args, **kwargs):
        logger = get_logger("staff")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Staff activity: {func.__name__} | Args: {args} | Kwargs: {kwargs}")
            return result
        except Exception as e:
            logger.error(f"Staff error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper

def log_database_activity(func):
    """Decorator to log database operations"""
    async def wrapper(*args, **kwargs):
        logger = get_logger("database")
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Database operation: {func.__name__} | Args: {args} | Kwargs: {kwargs}")
            return result
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper

def log_api_activity(func):
    """Decorator to log API calls"""
    async def wrapper(*args, **kwargs):
        logger = get_logger("api")
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"API call: {func.__name__} | Args: {args} | Kwargs: {kwargs}")
            return result
        except Exception as e:
            logger.error(f"API error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper 