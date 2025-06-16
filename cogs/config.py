"""
Configuration cog for managing bot settings.
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List
from utils.logger import logger

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.default_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        """Initial bot setup for the server"""
        try:
            async with self.bot.db.session() as session:
                # Your setup code here
                pass
                
        except Exception as e:
            logger.error(f"Error in setup command: {e}")
            await interaction.response.send_message(
                f"{self.bot.emojis['error']} An error occurred during setup.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(ConfigCog(bot))