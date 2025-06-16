import logging
import platform
import psutil
import discord
from discord import app_commands
from discord.ext import commands
from utils.embeds import create_base_embed
from utils.constants import EMOJIS, COLORS
from database.connection import db_manager

logger = logging.getLogger(__name__)

class BotMetrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.launch_time = discord.utils.utcnow()

    @app_commands.command(name="metrics")
    async def show_metrics(self, interaction: discord.Interaction):
        """Display current bot statistics and performance metrics."""
        # Get system information
        process = psutil.Process()
        memory_info = process.memory_info()

        # Calculate bot metrics
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)

        # Get database status
        db_status = "Connected" if db_manager.is_connected() else "Disconnected"

        # Create embed
        embed = create_base_embed(
            title="Bot Statistics",
            description=f"{EMOJIS['INFO']} Current bot performance metrics",
            color=COLORS['INFO']
        )

        # System Information
        embed.add_field(
            name="System",
            value=(
                f"**CPU Usage:** {psutil.cpu_percent()}%\n"
                f"**Memory Usage:** {memory_info.rss / 1024 / 1024:.2f} MB\n"
                f"**Python Version:** {platform.python_version()}\n"
                f"**Discord.py Version:** {discord.__version__}"
            ),
            inline=False
        )

        # Bot Information
        embed.add_field(
            name="Bot",
            value=(
                f"**Latency:** {round(self.bot.latency * 1000)}ms\n"
                f"**Guilds:** {len(self.bot.guilds)}\n"
                f"**Total Members:** {total_members}\n"
                f"**Total Channels:** {total_channels}"
            ),
            inline=False
        )

        # Database Status
        embed.add_field(
            name="Database",
            value=(
                f"**Status:** {db_status}\n"
                f"**Type:** {db_manager.get_db_type()}"
            ),
            inline=False
        )

        # Uptime
        uptime = discord.utils.utcnow() - self.bot.launch_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        embed.add_field(
            name="Uptime",
            value=f"{days}d {hours}h {minutes}m {seconds}s",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        """Log bot startup information."""
        logger.info(f"Bot is ready! Logged in as {self.bot.user}")
        logger.info(f"Running on {platform.system()} {platform.release()}")
        logger.info(f"Python version: {platform.python_version()}")
        logger.info(f"Discord.py version: {discord.__version__}")
        logger.info(f"Bot is in {len(self.bot.guilds)} guilds:")
        for guild in self.bot.guilds:
            logger.info(f"- {guild.name} (ID: {guild.id})")
            logger.info(f"  • Members: {len(guild.members)}")
            logger.info(f"  • Channels: {len(guild.channels)}")
            logger.info(f"  • Owner: {guild.owner} (ID: {guild.owner_id})")

async def setup(bot):
    await bot.add_cog(BotMetrics(bot))