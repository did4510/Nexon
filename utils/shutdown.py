from typing import Optional, List, Callable, Coroutine
import asyncio
from datetime import datetime
from utils.logger import logger

class ShutdownManager:
    def __init__(self, bot):
        self.bot = bot
        self.shutdown_hooks: List[Callable[[], Coroutine]] = []
        self.is_shutting_down = False

    async def register_hook(self, hook: Callable[[], Coroutine]):
        """Register a shutdown hook"""
        self.shutdown_hooks.append(hook)
        logger.debug(f"Registered shutdown hook: {hook.__name__}")

    async def execute_shutdown(self, reason: Optional[str] = None):
        """Execute graceful shutdown sequence"""
        if self.is_shutting_down:
            return

        self.is_shutting_down = True
        logger.info(f"🔄 Initiating graceful shutdown... Reason: {reason or 'Not specified'}")

        try:
            # Execute all shutdown hooks
            for hook in self.shutdown_hooks:
                try:
                    await hook()
                except Exception as e:
                    logger.error(f"Error in shutdown hook {hook.__name__}: {e}")

            # Stop task manager
            if hasattr(self.bot, 'task_manager'):
                await self.bot.task_manager.stop()

            # Close database connections
            await self.bot.db.close()

            logger.info("✨ Shutdown sequence completed successfully")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
        finally:
            # Close the bot
            await self.bot.close()