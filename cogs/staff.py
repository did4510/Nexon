import logging
import discord
from discord import app_commands
from discord.ext import commands, tasks
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import select

from utils.logger import logger
from database.models import Guild, StaffPerformance, Ticket
from database import db_manager
from utils.embeds import create_success_embed, create_error_embed, create_info_embed
from utils.enums import TicketStatus

class DutyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Start Shift", style=discord.ButtonStyle.success, emoji="🟢", custom_id="start_shift")
    async def start_shift(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_duty(interaction, True)

    @discord.ui.button(label="End Shift", style=discord.ButtonStyle.danger, emoji="🔴", custom_id="end_shift")
    async def end_shift(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_duty(interaction, False)

    async def toggle_duty(self, interaction: discord.Interaction, on_duty: bool):
        try:
            async with db_manager.Session() as session:
                staff = await session.get(StaffPerformance, (str(interaction.guild_id), str(interaction.user.id)))
                if not staff:
                    staff = StaffPerformance(
                        guild_id=str(interaction.guild_id),
                        staff_id=str(interaction.user.id),
                        on_duty=on_duty,
                        on_duty_since=datetime.utcnow() if on_duty else None
                    )
                    session.add(staff)
                else:
                    staff.on_duty = on_duty
                    staff.on_duty_since = datetime.utcnow() if on_duty else None

                await session.commit()

                await interaction.response.send_message(
                    f"You are now {'on' if on_duty else 'off'} duty!",
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"Error toggling duty status: {e}")
            await interaction.response.send_message(
                "An error occurred while updating your duty status.",
                ephemeral=True
            )

class StaffCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()
        self.performance_update_task.start()

    def cog_unload(self):
        self.performance_update_task.cancel()

    @tasks.loop(minutes=15)
    async def performance_update_task(self):
        """Update staff performance metrics periodically"""
        try:
            async with db_manager.Session() as session:
                # Get all active staff members
                stmt = select(StaffPerformance)
                result = await session.execute(stmt)
                staff_members = result.scalars().all()

                for staff in staff_members:
                    # Update response times
                    stmt = select(Ticket).where(
                        Ticket.claimed_by_id == staff.staff_id,
                        Ticket.status == TicketStatus.CLOSED
                    )
                    result = await session.execute(stmt)
                    tickets = result.scalars().all()

                    total_response_time = timedelta()
                    total_resolution_time = timedelta()
                    ticket_count = len(tickets)

                    for ticket in tickets:
                        if ticket.first_staff_response_at and ticket.opened_at:
                            total_response_time += ticket.first_staff_response_at - ticket.opened_at
                        if ticket.closed_at and ticket.opened_at:
                            total_resolution_time += ticket.closed_at - ticket.opened_at

                    if ticket_count > 0:
                        staff.avg_response_time = total_response_time.total_seconds() / ticket_count
                        staff.avg_resolution_time = total_resolution_time.total_seconds() / ticket_count

                    # Update other metrics
                    staff.tickets_handled_count = ticket_count
                    staff.last_updated = datetime.utcnow()

                await session.commit()

        except Exception as e:
            logger.error(f"Error updating staff performance: {e}")

    @app_commands.command(name="staffview")  # Renamed from 'staff'
    @app_commands.checks.has_permissions(administrator=True)
    async def view_staff(
        self,
        interaction: discord.Interaction,
        action: str,
        role: discord.Role,
        category: Optional[str] = None
    ):
        """Manage staff roles and permissions."""
        await interaction.response.defer()

        try:
            async with db_manager.Session() as session:
                guild = await session.get(Guild, str(interaction.guild_id))
                if not guild:
                    await interaction.followup.send(
                        embed=create_error_embed(
                            "Setup Required",
                            "Please run /setup first to configure the ticket system."
                        )
                    )
                    return

                action = action.lower()

                if action == "add":
                    # Add staff role
                    if not guild.default_staff_role_ids:
                        guild.default_staff_role_ids = []

                    if str(role.id) in guild.default_staff_role_ids:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Already Added",
                                f"{role.mention} is already a staff role."
                            )
                        )
                        return

                    guild.default_staff_role_ids.append(str(role.id))

                    await session.commit()

                    await interaction.followup.send(
                        embed=create_success_embed(
                            "Staff Role Added",
                            f"Successfully added {role.mention} as a staff role."
                        )
                    )

                elif action == "remove":
                    # Remove staff role
                    if not guild.default_staff_role_ids or str(role.id) not in guild.default_staff_role_ids:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Not Found",
                                f"{role.mention} is not a staff role."
                            )
                        )
                        return

                    guild.default_staff_role_ids.remove(str(role.id))

                    await session.commit()

                    await interaction.followup.send(
                        embed=create_success_embed(
                            "Staff Role Removed",
                            f"Successfully removed {role.mention} from staff roles."
                        )
                    )

                elif action == "list":
                    # List staff roles
                    if not guild.default_staff_role_ids:
                        await interaction.followup.send(
                            embed=create_info_embed(
                                "Staff Roles",
                                "No staff roles have been configured."
                            )
                        )
                        return

                    roles = []
                    for role_id in guild.default_staff_role_ids:
                        role = interaction.guild.get_role(int(role_id))
                        if role:
                            roles.append(role.mention)

                    await interaction.followup.send(
                        embed=create_info_embed(
                            "Staff Roles",
                            "The following roles have staff permissions:\n" + "\n".join(roles)
                        )
                    )

                else:
                    await interaction.followup.send(
                        embed=create_error_embed(
                            "Invalid Action",
                            "Valid actions are: add, remove, list"
                        )
                    )

        except Exception as e:
            logger.error(f"Error managing staff roles: {e}")
            await interaction.followup.send(
                embed=create_error_embed(
                    "Error",
                    "An error occurred while managing staff roles."
                )
            )

    @app_commands.command(name="performance")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def view_performance(
        self,
        interaction: discord.Interaction,
        staff_member: Optional[discord.Member] = None
    ):
        """View staff performance metrics."""
        await interaction.response.defer()

        try:
            async with db_manager.Session() as session:
                if staff_member:
                    # View specific staff member's performance
                    staff = await session.get(StaffPerformance, (str(interaction.guild_id), str(staff_member.id)))
                    if not staff:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Not Found",
                                f"No performance data found for {staff_member.mention}"
                            )
                        )
                        return

                    embed = discord.Embed(
                        title=f"Staff Performance - {staff_member.display_name}",
                        color=discord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )

                    embed.add_field(
                        name="Tickets Handled",
                        value=str(staff.tickets_handled_count),
                        inline=True
                    )
                    embed.add_field(
                        name="Average Response Time",
                        value=f"{staff.avg_response_time:.1f} seconds" if staff.avg_response_time else "N/A",
                        inline=True
                    )
                    embed.add_field(
                        name="Average Resolution Time",
                        value=f"{staff.avg_resolution_time:.1f} seconds" if staff.avg_resolution_time else "N/A",
                        inline=True
                    )
                    embed.add_field(
                        name="Status",
                        value="🟢 On Duty" if staff.on_duty else "🔴 Off Duty",
                        inline=True
                    )
                    if staff.on_duty and staff.on_duty_since:
                        embed.add_field(
                            name="On Duty Since",
                            value=staff.on_duty_since.strftime("%Y-%m-%d %H:%M UTC"),
                            inline=True
                        )

                    await interaction.followup.send(embed=embed)

                else:
                    # View all staff performance
                    stmt = select(StaffPerformance).where(
                        StaffPerformance.guild_id == str(interaction.guild_id)
                    )
                    result = await session.execute(stmt)
                    staff_members = result.scalars().all()

                    if not staff_members:
                        await interaction.followup.send(
                            embed=create_info_embed(
                                "Staff Performance",
                                "No staff performance data available."
                            )
                        )
                        return

                    embed = discord.Embed(
                        title="Staff Performance Overview",
                        color=discord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )

                    for staff in staff_members:
                        member = interaction.guild.get_member(int(staff.staff_id))
                        if member:
                            status = "🟢" if staff.on_duty else "🔴"
                            value = (
                                f"Tickets: {staff.tickets_handled_count}\n"
                                f"Avg Response: {staff.avg_response_time:.1f}s\n"
                                f"Avg Resolution: {staff.avg_resolution_time:.1f}s\n"
                                f"Status: {status}"
                            )
                            embed.add_field(
                                name=member.display_name,
                                value=value,
                                inline=True
                            )

                    await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error viewing staff performance: {e}")
            await interaction.followup.send(
                embed=create_error_embed(
                    "Error",
                    "An error occurred while retrieving staff performance data."
                )
            )

async def setup(bot):
    """Load the StaffCog."""
    await bot.add_cog(StaffCog(bot))