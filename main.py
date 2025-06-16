"""
Main entry point for the Nexon Discord bot.
This module initializes and runs the bot with all necessary configurations.
"""
import os
import sys
import platform
import asyncio
import discord
from discord.ext import commands
from pathlib import Path
from dotenv import load_dotenv
from database.connection import db_manager
from utils.logger import logger
from utils.banner import print_banner
from utils.tasks import initialize
from utils.shutdown import ShutdownManager

VERSION = "1.0.0"

class NexonBot(commands.Bot):
    """
    Main bot class for Nexon Support System.
    Handles command processing, events, and bot lifecycle.
    """
    
    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True

        # Initialize base bot
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,
            description="Nexon Support System - Advanced Discord Ticket Management"
        )
        
        # Bot configuration
        self.db = db_manager
        self.version = VERSION
        self.shutdown_manager = ShutdownManager(self)  # Add this line
        self._bot_emojis = {
            'success': '✨',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'loading': '🔄',
            'online': '🟢',
            'idle': '🟡',
            'dnd': '🔴',
            'offline': '⚫',
            'shutdown': '🔌',
            'ticket': '🎫',
            'staff': '👮',
            'settings': '⚙️',
            'database': '💾',
            'maintenance': '🔧'
        }
        
        # Show startup banner
        print_banner(VERSION)

    @property
    def emojis(self):
        """Get bot emojis dictionary"""
        return self._bot_emojis

    async def setup_hook(self):
        """Initialize bot configuration and load extensions"""
        try:
            # Initialize database first
            logger.info(f"{self.emojis['loading']} Initializing database...")
            await self.db.initialize_database()
            logger.info(f"{self.emojis['success']} Database initialized")
            
            # Initialize task manager
            logger.info(f"{self.emojis['loading']} Starting task manager...")
            self.task_manager = await initialize(self)
            logger.info(f"{self.emojis['success']} Task manager initialized")
            
            # Load extensions
            logger.info(f"{self.emojis['loading']} Loading extensions...")
            await self._load_extensions()
            
        except Exception as e:
            logger.error(f"{self.emojis['error']} Critical error during setup: {e}")
            raise

    async def _load_extensions(self):
        """Load all extensions from the cogs directory"""
        cogs_dir = Path("cogs")
        for cog_file in cogs_dir.glob("*.py"):
            if not cog_file.name.startswith("_"):
                try:
                    await self.load_extension(f"cogs.{cog_file.stem}")
                    logger.info(f"{self.emojis['success']} Loaded extension: {cog_file.name}")
                except Exception as e:
                    logger.error(f"{self.emojis['error']} Failed to load extension {cog_file.name}: {e}")

    async def close(self):
        """Cleanup and close the bot"""
        logger.info(f"{self.emojis['shutdown']} Bot is shutting down...")
        
        try:
            # Stop task manager
            if hasattr(self, 'task_manager'):
                await self.task_manager.stop()
                
            # Close database connection
            await self.db.close()
            
        except Exception as e:
            logger.error(f"{self.emojis['error']} Error during shutdown: {e}")
        finally:
            await super().close()

async def main():
    """Main entry point for the bot"""
    try:
        # Load environment variables
        load_dotenv()
        token = os.getenv("DISCORD_TOKEN")
        
        if not token:
            raise ValueError("No Discord token found in environment variables")
        
        # Create bot instance
        bot = NexonBot()
        
        # Set up Windows-specific handlers
        if platform.system() == 'Windows':
            import win32api
            def handler(type):
                bot.should_exit = True
                return True
            win32api.SetConsoleCtrlHandler(handler, True)
        
        # Start the bot
        async with bot:
            await bot.start(token)
            
    except Exception as e:
        logger.error(f"{bot.emojis['error'] if 'bot' in locals() else '❌'} Failed to start bot: {e}")
        raise
    finally:
        if 'bot' in locals():
            await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested via keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
