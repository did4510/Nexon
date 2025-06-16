"""
Staff duty management commands.
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import sys
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import select

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.models import Guild, StaffDuty, StaffPerformance
from database import db_manager
from utils.constants import *
from utils.embeds import create_success_embed, create_error_embed, create_info_embed
from utils.logger import logger

class DutyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="duty")
    async def toggle_duty(
        self,
        interaction: discord.Interaction,
        status: str
    ):
        """Toggle staff duty status."""
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

                # Check if user is staff
                if not any(
                    str(role.id) in guild.staff_role_ids
                    for role in interaction.user.roles
                ):
                    await interaction.followup.send(
                        embed=create_error_embed(
                            "Permission Denied",
                            "You must be a staff member to use this command."
                        )
                    )
                    return

                # Get staff record
                staff = await session.get(StaffPerformance, (str(interaction.guild_id), str(interaction.user.id)))
                if not staff:
                    staff = StaffPerformance(
                        guild_id=str(interaction.guild_id),
                        staff_id=str(interaction.user.id)
                    )
                    session.add(staff)

                # Update status
                status = status.lower()
                if status == "on":
                    staff.on_duty = True
                    staff.on_duty_since = datetime.utcnow()
                    message = "You are now on duty!"
                elif status == "off":
                    staff.on_duty = False
                    staff.on_duty_since = None
                    message = "You are now off duty!"
                else:
                    await interaction.followup.send(
                        embed=create_error_embed(
                            "Invalid Status",
                            "Status must be either 'on' or 'off'."
                        )
                    )
                    return

                await session.commit()

                # Create response embed
                embed = create_success_embed(
                    "Duty Status Updated",
                    message
                )

                await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error toggling duty status: {e}")
            await interaction.followup.send(
                embed=create_error_embed(
                    "Error",
                    "An error occurred while updating duty status."
                )
            )

    @app_commands.command(name="staff")
    async def list_staff(
        self,
        interaction: discord.Interaction
    ):
        """List all staff members and their duty status."""
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

                # Get all staff members
                stmt = select(StaffPerformance).where(
                    StaffPerformance.guild_id == str(interaction.guild_id)
                )
                result = await session.execute(stmt)
                staff_members = result.scalars().all()

                # Create embed
                embed = discord.Embed(
                    title="👥 Staff Members",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )

                for staff in staff_members:
                    member = interaction.guild.get_member(int(staff.staff_id))
                    if member:
                        status = "🟢 On Duty" if staff.on_duty else "🔴 Off Duty"
                        value = f"Status: {status}"
                        if staff.on_duty and staff.on_duty_since:
                            value += f"\nOn duty since: {staff.on_duty_since.strftime('%Y-%m-%d %H:%M UTC')}"
                        embed.add_field(
                            name=member.display_name,
                            value=value,
                            inline=True
                        )

                await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error listing staff: {e}")
            await interaction.followup.send(
                embed=create_error_embed(
                    "Error",
                    "An error occurred while listing staff members."
                )
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(DutyCog(bot))