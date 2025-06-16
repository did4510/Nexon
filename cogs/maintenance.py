"""
Maintenance mode cog for managing server maintenance.
"""
import discord
from discord import app_commands
from discord.ext import commands, tasks
from typing import Optional
import sys
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import select

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.models import Guild, MaintenanceSchedule
from database.connection import db_manager
from utils.constants import *
from utils.embeds import create_success_embed, create_error_embed, create_info_embed
from utils.logger import logger

class MaintenanceCog(commands.Cog, name="Maintenance"):
    def __init__(self, bot):
        self.bot = bot
        self.maintenance_mode = False
        self.maintenance_message = None
        self.scheduled_maintenance = None
        self.check_maintenance.start()

    def cog_unload(self):
        self.check_maintenance.cancel()

    @tasks.loop(minutes=1)
    async def check_maintenance(self):
        """Check for scheduled maintenance windows and activate/deactivate as needed"""
        try:
            async with db_manager.Session() as session:
                # Get active maintenance schedules
                now = datetime.utcnow()
                schedules = await session.execute(
                    select(MaintenanceSchedule).where(
                        MaintenanceSchedule.is_active == True,
                        MaintenanceSchedule.start_time <= now,
                        MaintenanceSchedule.end_time > now
                    )
                )
                schedules = schedules.scalars().all()

                for schedule in schedules:
                    if not self.maintenance_mode:
                        # Activate maintenance mode
                        self.maintenance_mode = True
                        self.scheduled_maintenance = schedule
                        guild = self.bot.get_guild(int(schedule.guild_id))
                        if guild:
                            channel = guild.system_channel or guild.text_channels[0]
                            embed = create_info_embed(
                                "🔧 Maintenance Mode Active",
                                f"Scheduled maintenance is now in progress:\n\n{schedule.description}\n\n"
                                f"End Time: {schedule.end_time.strftime('%Y-%m-%d %H:%M UTC')}"
                            )
                            await channel.send(embed=embed)
                            logger.info(f"Activated maintenance mode in guild {guild.id}")

                # Check if current maintenance should end
                if self.scheduled_maintenance and self.scheduled_maintenance.end_time <= now:
                    self.maintenance_mode = False
                    guild = self.bot.get_guild(int(self.scheduled_maintenance.guild_id))
                    if guild:
                        channel = guild.system_channel or guild.text_channels[0]
                        embed = create_info_embed(
                            "✅ Maintenance Complete",
                            "Scheduled maintenance has been completed. All systems are now operational."
                        )
                        await channel.send(embed=embed)
                        logger.info(f"Deactivated maintenance mode in guild {guild.id}")
                    self.scheduled_maintenance = None

        except Exception as e:
            logger.error(f"Error in maintenance check task: {e}")

    @app_commands.command(name="schedule")
    @app_commands.describe(
        start_time="When maintenance starts (format: YYYY-MM-DD HH:MM)",
        duration="Duration in hours",
        description="Description of the maintenance"
    )
    async def schedule_maintenance(
        self,
        interaction: discord.Interaction,
        start_time: str,
        duration: float,
        description: str
    ):
        """Schedule a maintenance window"""
        try:
            # Parse start time
            start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            if start < datetime.utcnow():
                await interaction.response.send_message(
                    embed=create_error_embed("Start time must be in the future."),
                    ephemeral=True
                )
                return

            # Calculate end time
            end = start + timedelta(hours=duration)

            async with db_manager.Session() as session:
                # Check if guild exists
                guild = await session.get(Guild, str(interaction.guild_id))
                if not guild:
                    await interaction.response.send_message(
                        embed=create_error_embed("This server is not set up for ticket management."),
                        ephemeral=True
                    )
                    return

                # Create maintenance schedule
                maintenance = MaintenanceSchedule(
                    guild_id=str(interaction.guild_id),
                    start_time=start,
                    end_time=end,
                    description=description,
                    created_by=str(interaction.user.id),
                    affected_services=["tickets", "support"]  # Default affected services
                )
                session.add(maintenance)
                await session.commit()

                # Create response embed
                embed = create_success_embed(
                    "Maintenance Scheduled",
                    f"🔧 A maintenance window has been scheduled:\n\n"
                    f"📅 Start: {start.strftime('%Y-%m-%d %H:%M UTC')}\n"
                    f"⏱️ Duration: {duration} hours\n"
                    f"🔚 End: {end.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
                    f"📝 Description: {description}"
                )

                await interaction.response.send_message(embed=embed)

        except ValueError:
            await interaction.response.send_message(
                embed=create_error_embed("Invalid date format. Use YYYY-MM-DD HH:MM"),
                ephemeral=True
            )

    @app_commands.command(name="list")
    async def list_maintenance(self, interaction: discord.Interaction):
        """List all scheduled maintenance windows"""
        async with db_manager.Session() as session:
            # Get all maintenance schedules for this guild
            schedules = await session.execute(
                select(MaintenanceSchedule).where(
                    MaintenanceSchedule.guild_id == str(interaction.guild_id),
                    MaintenanceSchedule.is_active == True
                ).order_by(MaintenanceSchedule.start_time)
            )
            schedules = schedules.scalars().all()

            if not schedules:
                await interaction.response.send_message(
                    embed=create_info_embed("No maintenance windows scheduled."),
                    ephemeral=True
                )
                return

            # Create embed with maintenance list
            embed = discord.Embed(
                title="🔧 Scheduled Maintenance Windows",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )

            for schedule in schedules:
                duration = (schedule.end_time - schedule.start_time).total_seconds() / 3600
                embed.add_field(
                    name=f"📅 {schedule.start_time.strftime('%Y-%m-%d %H:%M UTC')}",
                    value=(
                        f"⏱️ Duration: {duration:.1f} hours\n"
                        f"🔚 End: {schedule.end_time.strftime('%Y-%m-%d %H:%M UTC')}\n"
                        f"📝 {schedule.description}"
                    ),
                    inline=False
                )

            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cancel")
    @app_commands.describe(
        schedule_id="ID of the maintenance window to cancel"
    )
    async def cancel_maintenance(
        self,
        interaction: discord.Interaction,
        schedule_id: str
    ):
        """Cancel a scheduled maintenance window"""
        async with db_manager.Session() as session:
            # Get the maintenance schedule
            schedule = await session.get(MaintenanceSchedule, schedule_id)

            if not schedule or schedule.guild_id != str(interaction.guild_id):
                await interaction.response.send_message(
                    embed=create_error_embed("Maintenance window not found."),
                    ephemeral=True
                )
                return

            if not schedule.is_active:
                await interaction.response.send_message(
                    embed=create_error_embed("This maintenance window is already cancelled."),
                    ephemeral=True
                )
                return

            # Cancel the maintenance
            schedule.is_active = False
            await session.commit()

            await interaction.response.send_message(
                embed=create_success_embed(
                    "Maintenance Cancelled",
                    f"🚫 The maintenance window scheduled for {schedule.start_time.strftime('%Y-%m-%d %H:%M UTC')} has been cancelled."
                )
            )

    @app_commands.command(name="maintenance")
    @app_commands.checks.has_permissions(administrator=True)
    async def manage_maintenance(
        self,
        interaction: discord.Interaction,
        action: str,
        message: Optional[str] = None,
        duration: Optional[int] = None
    ):
        """Manage bot maintenance mode."""
        await interaction.response.defer()

        try:
            action = action.lower()

            if action == "start":
                if self.maintenance_mode:
                    await interaction.followup.send(
                        embed=create_error_embed(
                            "Already Active",
                            "Maintenance mode is already active."
                        )
                    )
                    return

                self.maintenance_mode = True
                self.maintenance_message = message or "System is under maintenance. Please try again later."

                # Create maintenance embed
                embed = create_info_embed(
                    "🔧 Maintenance Mode Active",
                    self.maintenance_message
                )
                if duration:
                    end_time = datetime.utcnow() + timedelta(minutes=duration)
                    embed.add_field(
                        name="Expected Duration",
                        value=f"⏱️ {duration} minutes (until {end_time.strftime('%H:%M UTC')})"
                    )

                await interaction.followup.send(embed=embed)
                logger.info(f"Maintenance mode activated in guild {interaction.guild_id}")

            elif action == "stop":
                if not self.maintenance_mode:
                    await interaction.followup.send(
                        embed=create_error_embed(
                            "Not Active",
                            "Maintenance mode is not active."
                        )
                    )
                    return

                self.maintenance_mode = False
                self.maintenance_message = None

                await interaction.followup.send(
                    embed=create_success_embed(
                        "✅ Maintenance Complete",
                        "Maintenance mode has been deactivated. All systems are now operational."
                    )
                )
                logger.info(f"Maintenance mode deactivated in guild {interaction.guild_id}")

            elif action == "status":
                if self.maintenance_mode:
                    embed = create_info_embed(
                        "🔧 Maintenance Status",
                        f"Maintenance mode is currently active.\nMessage: {self.maintenance_message}"
                    )
                else:
                    embed = create_info_embed(
                        "✅ Maintenance Status",
                        "Maintenance mode is not active."
                    )
                await interaction.followup.send(embed=embed)

            else:
                await interaction.followup.send(
                    embed=create_error_embed(
                        "Invalid Action",
                        "Valid actions are: start, stop, status"
                    )
                )

        except Exception as e:
            logger.error(f"Error in maintenance management: {e}")
            await interaction.followup.send(
                embed=create_error_embed(
                    "Maintenance Error",
                    f"An error occurred: {str(e)}"
                )
            )

async def setup(bot):
    await bot.add_cog(MaintenanceCog(bot))