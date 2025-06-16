"""
Startup utilities for the bot.
"""
from .banner import display_banner, get_startup_info
from .logger import setup_logging, get_logger
from .emojis import STATUS

def initialize_bot():
    """Initialize the bot's logging and display startup information."""
    # Configure logging
    setup_logging()
    logger = get_logger("nexon")
    
    # Display banner
    display_banner()
    
    # Log startup information
    startup_info = get_startup_info()
    for key, value in startup_info.items():
        logger.info(f"{STATUS['loading']} {key}: {value}")
    
    return logger 