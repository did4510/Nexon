"""Error handling utilities for the bot."""

import logging
import traceback
from typing import Optional, Union
import discord
from discord import app_commands
from discord.ext import commands
from .constants import DEFAULT_COLOR

logger = logging.getLogger(__name__)

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.", ephemeral=True)
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param.name}", ephemeral=True)
            return
        
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument provided.", ephemeral=True)
            return
        
        # Log the error
        logger.error(f"Command error: {str(error)}")
        logger.error(traceback.format_exc())
        
        # Send error message
        await ctx.send("An error occurred while processing your command.", ephemeral=True)

    @commands.Cog.listener()
    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """Handle application command errors."""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You don't have permission to use this command.",
                ephemeral=True
            )
            return
        
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
            return
        
        # Log the error
        logger.error(f"Application command error: {str(error)}")
        logger.error(traceback.format_exc())
        
        # Send error message
        if interaction.response.is_done():
            await interaction.followup.send(
                "An error occurred while processing your command.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "An error occurred while processing your command.",
                ephemeral=True
            )

def handle_error(
    error: Exception,
    interaction: Optional[discord.Interaction] = None,
    ctx: Optional[commands.Context] = None
) -> Union[discord.Embed, str]:
    """
    Handle errors and return appropriate error message.
    
    Args:
        error: The exception that occurred
        interaction: The interaction that caused the error (if any)
        ctx: The context that caused the error (if any)
    
    Returns:
        An embed or string with the error message
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    # Log the error
    logger.error(f"Error: {error_type} - {error_message}")
    logger.error(traceback.format_exc())
    
    # Create error embed
    embed = discord.Embed(
        title="Error",
        description="An error occurred while processing your request.",
        color=discord.Color.red()
    )
    
    # Add error details if in debug mode
    if hasattr(interaction, "client") and interaction.client.debug:
        embed.add_field(name="Error Type", value=error_type, inline=False)
        embed.add_field(name="Error Message", value=error_message, inline=False)
    
    return embed

async def send_error(
    error: Exception,
    interaction: Optional[discord.Interaction] = None,
    ctx: Optional[commands.Context] = None
):
    """
    Send an error message to the user.
    
    Args:
        error: The exception that occurred
        interaction: The interaction that caused the error (if any)
        ctx: The context that caused the error (if any)
    """
    error_message = handle_error(error, interaction, ctx)
    
    if interaction:
        if interaction.response.is_done():
            await interaction.followup.send(embed=error_message, ephemeral=True)
        else:
            await interaction.response.send_message(embed=error_message, ephemeral=True)
    elif ctx:
        await ctx.send(embed=error_message)

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))