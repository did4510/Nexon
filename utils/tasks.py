import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy import select
from database.models import Ticket, Guild, TicketStatus, StaffPerformance
from utils.logger import logger

class TaskManager:
    def __init__(self, bot):
        self.bot = bot
        self.tasks = []
        self.is_running = False

    async def update_staff_performance(self):
        """Update staff performance metrics periodically"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Use proper session handling
                async with self.bot.db.session() as session:
                    # Get all guilds
                    stmt = select(Guild)
                    result = await session.execute(stmt)
                    guilds = result.scalars().all()
                    
                    for guild in guilds:
                        # Update performance metrics
                        await self._update_guild_performance(session, guild)
                    
            except asyncio.CancelledError:
                logger.info("Staff performance task cancelled")
                break
            except Exception as e:
                logger.error(f"Error updating staff performance: {e}")

    async def check_maintenance(self):
        """Check scheduled maintenance tasks"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                async with self.bot.db.session() as session:
                    # Get maintenance schedules
                    stmt = select(Guild).where(Guild.maintenance_mode == True)
                    result = await session.execute(stmt)
                    maintenance_guilds = result.scalars().all()
                    
                    for guild in maintenance_guilds:
                        await self._process_maintenance(session, guild)
                    
            except asyncio.CancelledError:
                logger.info("Maintenance check task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in maintenance check task: {e}")

    async def _update_guild_performance(self, session, guild):
        """Update performance metrics for a specific guild"""
        try:
            # Implement your performance tracking logic here
            pass
        except Exception as e:
            logger.error(f"Error updating guild {guild.guild_id} performance: {e}")

    async def _process_maintenance(self, session, guild):
        """Process maintenance for a specific guild"""
        try:
            # Implement your maintenance logic here
            pass
        except Exception as e:
            logger.error(f"Error processing maintenance for guild {guild.guild_id}: {e}")

    async def initialize(self):
        """Initialize and start background tasks"""
        try:
            # Ensure database is initialized first
            await self.bot.db.initialize_database()
            
            # Create tasks
            self.tasks.extend([
                asyncio.create_task(self.update_staff_performance()),
                asyncio.create_task(self.check_maintenance())
            ])
            
            self.is_running = True
            logger.info("✨ Task manager started")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize task manager: {e}")
            raise

    async def stop(self):
        """Stop all running tasks"""
        self.is_running = False
        
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
        logger.info("🔌 Task manager stopped")

async def initialize(bot) -> TaskManager:
    """Initialize and return a task manager instance"""
    manager = TaskManager(bot)
    await manager.initialize()
    return manager