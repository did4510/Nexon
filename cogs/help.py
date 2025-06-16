"""
Help command cog.
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from datetime import datetime
from sqlalchemy import select

from database import db_manager
from database.models import Guild
from utils.embeds import create_success_embed, create_error_embed, create_info_embed
from utils.logger import logger

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help")
    async def help_command(
        self,
        interaction: discord.Interaction,
        command: Optional[str] = None
    ):
        """Show help information about commands."""
        await interaction.response.defer()

        try:
            async with db_manager.Session() as session:
                # Get guild settings
                guild = await session.get(Guild, str(interaction.guild_id))
                if not guild:
                    await interaction.followup.send(
                        embed=create_error_embed(
                            "Setup Required",
                            "Please run /setup first to configure the bot."
                        )
                    )
                    return

                if command:
                    # Show help for specific command
                    cmd = self.bot.tree.get_command(command)
                    if not cmd:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Not Found",
                                f"Command '{command}' not found."
                            )
                        )
                        return

                    embed = discord.Embed(
                        title=f"Help: /{command}",
                        description=cmd.description or "No description available.",
                        color=discord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )

                    if cmd.parameters:
                        params = []
                        for param in cmd.parameters:
                            required = "Required" if param.required else "Optional"
                            params.append(f"• **{param.name}** ({required}): {param.description}")
                        embed.add_field(
                            name="Parameters",
                            value="\n".join(params),
                            inline=False
                        )

                else:
                    # Show general help
                    embed = discord.Embed(
                        title="📚 Command Help",
                        description="Here are all available commands:",
                        color=discord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )

                    # Group commands by cog
                    commands_by_cog = {}
                    for cmd in self.bot.tree.get_commands():
                        cog_name = cmd.module.split('.')[-1].title() if cmd.module else "Other"
                        if cog_name not in commands_by_cog:
                            commands_by_cog[cog_name] = []
                        commands_by_cog[cog_name].append(cmd)

                    for cog_name, commands in commands_by_cog.items():
                        value = []
                        for cmd in commands:
                            value.append(f"• **/{cmd.name}** - {cmd.description}")
                        embed.add_field(
                            name=cog_name,
                            value="\n".join(value),
                            inline=False
                        )

                    embed.set_footer(text="Use /help <command> for detailed information about a specific command.")

                await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error showing help: {e}")
            await interaction.followup.send(
                embed=create_error_embed(
                    "Error",
                    "An error occurred while showing help information."
                )
            )

async def setup(bot):
    """Load the HelpCog."""
    await bot.add_cog(HelpCog(bot))