from database.models import Guild, TicketCategory, Ticket
from utils.enums import TicketStatus
from discord.ext import commands
import discord
import logging

logger = logging.getLogger(__name__)

class TicketManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def setup_guild_defaults(self, guild_id: str):
        """Set up default guild settings and categories if they don't exist"""
        async with self.bot.db.session() as session:
            # Check if guild exists
            guild = await session.get(Guild, guild_id)
            if not guild:
                logger.info(f"Creating default settings for guild {guild_id}")
                guild = await Guild.create_default_settings(session, guild_id)

            # Check if categories exist
            categories = await session.query(TicketCategory).filter_by(guild_id=guild_id).all()
            if not categories:
                logger.info(f"Creating default categories for guild {guild_id}")
                await TicketCategory.create_default_categories(session, guild_id)

            await session.commit()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Create default settings when bot joins a new guild"""
        await self.setup_guild_defaults(str(guild.id))

async def setup(bot: commands.Bot):
    """Load the TicketManager cog."""
    await bot.add_cog(TicketManager(bot)) 