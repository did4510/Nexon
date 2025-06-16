"""
Macros cog.
Handles response templates and quick replies.
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List, Dict, Any
from datetime import datetime

from database.models import Guild, ResponseMacro
from database.manager import db_manager
from utils.embeds import create_success_embed, create_error_embed, create_info_embed
from utils.constants import *
from utils.logger import logger

class MacrosCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="macro")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def manage_macro(
        self,
        interaction: discord.Interaction,
        action: str,
        name: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None
    ):
        """Manage response macros."""
        await interaction.response.defer()

        try:
            action = action.lower()

            async with db_manager.get_session() as session:
                if action == "add":
                    if not all([name, content]):
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Missing Information",
                                "Please provide name and content for the macro."
                            )
                        )
                        return

                    # Check if macro exists
                    existing = await session.query(ResponseMacro)\
                        .filter(
                            ResponseMacro.guild_id == str(interaction.guild_id),
                            ResponseMacro.name == name
                        ).first()

                    if existing:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Already Exists",
                                f"A macro with the name '{name}' already exists."
                            )
                        )
                        return

                    # Create macro
                    macro = ResponseMacro(
                        guild_id=str(interaction.guild_id),
                        name=name,
                        content=content,
                        category=category or "General",
                        created_by=str(interaction.user.id)
                    )

                    session.add(macro)
                    await session.commit()

                    await interaction.followup.send(
                        embed=create_success_embed(
                            "Macro Created",
                            f"Successfully created macro: {name}"
                        )
                    )

                elif action == "edit":
                    if not name:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Missing Name",
                                "Please provide the name of the macro to edit."
                            )
                        )
                        return

                    # Find macro
                    macro = await session.query(ResponseMacro)\
                        .filter(
                            ResponseMacro.guild_id == str(interaction.guild_id),
                            ResponseMacro.name == name
                        ).first()

                    if not macro:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Not Found",
                                f"No macro found with name: {name}"
                            )
                        )
                        return

                    # Update macro
                    if content:
                        macro.content = content
                    if category:
                        macro.category = category

                    macro.last_edited_by = str(interaction.user.id)
                    macro.last_edited_at = datetime.utcnow()

                    await session.commit()

                    await interaction.followup.send(
                        embed=create_success_embed(
                            "Macro Updated",
                            f"Successfully updated macro: {name}"
                        )
                    )

                elif action == "delete":
                    if not name:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Missing Name",
                                "Please provide the name of the macro to delete."
                            )
                        )
                        return

                    # Find and delete macro
                    macro = await session.query(ResponseMacro)\
                        .filter(
                            ResponseMacro.guild_id == str(interaction.guild_id),
                            ResponseMacro.name == name
                        ).first()

                    if not macro:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Not Found",
                                f"No macro found with name: {name}"
                            )
                        )
                        return

                    await session.delete(macro)
                    await session.commit()

                    await interaction.followup.send(
                        embed=create_success_embed(
                            "Macro Deleted",
                            f"Successfully deleted macro: {name}"
                        )
                    )

                elif action == "view":
                    if not name:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Missing Name",
                                "Please provide the name of the macro to view."
                            )
                        )
                        return

                    # Find macro
                    macro = await session.query(ResponseMacro)\
                        .filter(
                            ResponseMacro.guild_id == str(interaction.guild_id),
                            ResponseMacro.name == name
                        ).first()

                    if not macro:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Not Found",
                                f"No macro found with name: {name}"
                            )
                        )
                        return

                    # Create embed
                    embed = create_info_embed(
                        f"Macro: {macro.name}",
                        f"Category: {macro.category}\n\n{macro.content}"
                    )

                    creator = interaction.guild.get_member(int(macro.created_by))
                    embed.add_field(
                        name="Created By",
                        value=creator.mention if creator else "Unknown",
                        inline=True
                    )

                    if macro.last_edited_by:
                        editor = interaction.guild.get_member(int(macro.last_edited_by))
                        embed.add_field(
                            name="Last Edited By",
                            value=editor.mention if editor else "Unknown",
                            inline=True
                        )

                    await interaction.followup.send(embed=embed)

                elif action == "list":
                    # Get all macros
                    query = session.query(ResponseMacro)\
                        .filter(ResponseMacro.guild_id == str(interaction.guild_id))

                    if category:
                        query = query.filter(ResponseMacro.category == category)

                    macros = await query.all()

                    if not macros:
                        await interaction.followup.send(
                            embed=create_info_embed(
                                "Macros",
                                "No macros found." + (f" in category: {category}" if category else "")
                            )
                        )
                        return

                    # Group by category
                    categories = {}
                    for macro in macros:
                        if macro.category not in categories:
                            categories[macro.category] = []
                        categories[macro.category].append(macro.name)

                    # Create embed
                    embed = create_info_embed(
                        "Available Macros",
                        "Here are all the available macros:"
                    )

                    for category_name, names in categories.items():
                        embed.add_field(
                            name=category_name,
                            value="\n".join(f"• {name}" for name in names),
                            inline=False
                        )

                    await interaction.followup.send(embed=embed)

                else:
                    await interaction.followup.send(
                        embed=create_error_embed(
                            "Invalid Action",
                            "Valid actions are: add, edit, delete, view, list"
                        )
                    )

        except Exception as e:
            logger.error(f"Error in macro management: {e}")
            await interaction.followup.send(
                embed=create_error_embed(
                    "Macro Error",
                    f"An error occurred: {str(e)}"
                )
            )

    @app_commands.command(name="r")
    async def use_macro(
        self,
        interaction: discord.Interaction,
        name: str,
        target: Optional[discord.Member] = None
    ):
        """Use a response macro."""
        try:
            async with db_manager.get_session() as session:
                # Find macro
                macro = await session.query(ResponseMacro)\
                    .filter(
                        ResponseMacro.guild_id == str(interaction.guild_id),
                        ResponseMacro.name == name
                    ).first()

                if not macro:
                    await interaction.response.send_message(
                        embed=create_error_embed(
                            "Not Found",
                            f"No macro found with name: {name}"
                        ),
                        ephemeral=True
                    )
                    return

                # Format content
                content = macro.content
                if target:
                    content = f"{target.mention} {content}"

                await interaction.response.send_message(content)

                # Update usage stats
                macro.times_used += 1
                macro.last_used_by = str(interaction.user.id)
                macro.last_used_at = datetime.utcnow()
                await session.commit()

        except Exception as e:
            logger.error(f"Error using macro: {e}")
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Macro Error",
                    f"An error occurred: {str(e)}"
                ),
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(MacrosCog(bot))