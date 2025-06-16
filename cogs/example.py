import discord
from discord import app_commands
from discord.ext import commands
from utils.logger import logger

class ExampleCog(commands.Cog):
    """Example cog to demonstrate basic functionality"""
    
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        """Simple ping command to test bot responsiveness"""
        await interaction.response.send_message(
            f"🏓 Pong! Latency: {round(self.bot.latency * 1000)}ms",
            ephemeral=True
        )

    async def cleanup(self):
        """Cleanup resources when cog unloads"""
        logger.info("Cleaning up Example cog...")

    async def cog_load(self):
        """Register shutdown task when cog loads"""
        await self.bot.shutdown_manager.register_shutdown_task(self.cleanup)

async def setup(bot):
    await bot.add_cog(ExampleCog(bot))