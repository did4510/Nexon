"""
Task manager for handling background tasks.
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
from database.models import Ticket, Guild, TicketStatus, StaffPerformance, TicketCategory
from database import db_manager
from utils.sla import sla_monitor
from utils.ai_features import ai_features
import discord
from sqlalchemy import select, func, and_
from utils.constants import *
from utils.logger import get_logger

logger = get_logger("task_manager")

class TaskManager:
    def __init__(self, bot):
        self.bot = bot
        self.tasks = []
        self.is_running = False
        self.db_initialized = False
        self.logger = get_logger("task_manager")

    async def initialize(self):
        """Initialize the task manager"""
        try:
            # Wait for database to be ready
            await self.wait_for_database()
            
            # Start background tasks
            await self.start()
            
            self.logger.info("Task manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize task manager: {e}")
            raise

    async def wait_for_database(self, timeout: int = 60):
        """Wait for database to be initialized"""
        start_time = datetime.utcnow()
        while not self.db_initialized:
            try:
                async with db_manager.Session() as session:
                    # Try a simple query to check if database is ready
                    stmt = select(func.count()).select_from(Guild)
                    await session.execute(stmt)
                    self.db_initialized = True
                    self.logger.info("Database connection established")
                    break
            except Exception as e:
                if (datetime.utcnow() - start_time).total_seconds() > timeout:
                    raise TimeoutError("Database initialization timeout")
                self.logger.warning(f"Waiting for database... ({e})")
                await asyncio.sleep(1)

    async def initialize_tasks(self):
        """Initialize all periodic tasks"""
        # Wait for database to be ready
        await self.wait_for_database()
        
        self.tasks.extend([
            asyncio.create_task(self.monitor_tickets()),
            asyncio.create_task(self.update_staff_metrics()),
            asyncio.create_task(self.process_scheduled_followups()),
            asyncio.create_task(self.auto_close_tickets()),
            asyncio.create_task(self.update_staff_performance())
        ])

    async def start(self):
        """Start all background tasks"""
        if self.is_running:
            return

        self.is_running = True
        await self.initialize_tasks()
        self.logger.info("Task manager started")

    async def shutdown(self):
        """Shutdown all background tasks"""
        if not self.is_running:
            return

        self.is_running = False
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
            self.tasks.clear()
        
        self.logger.info("Task manager stopped")

    async def monitor_tickets(self):
        """Monitor tickets for SLA breaches and updates"""
        while self.is_running:
            try:
                async with db_manager.session() as session:
                    # Get all open tickets
                    stmt = select(Ticket).where(Ticket.status == TicketStatus.OPEN)
                    result = await session.execute(stmt)
                    tickets = result.scalars().all()

                    for ticket in tickets:
                        # Check SLA status
                        alert_level = await sla_monitor.check_sla_status(ticket)
                        if alert_level > 0:
                            await self.handle_sla_breach(ticket, alert_level)

                        # Update AI analysis if needed
                        if ticket.last_message_at and ticket.last_ai_analysis_at:
                            if ticket.last_message_at > ticket.last_ai_analysis_at:
                                await ai_features.analyze_ticket(ticket)

            except Exception as e:
                self.logger.error(f"Error in ticket monitoring task: {e}")

            await asyncio.sleep(60)  # Check every minute

    async def update_staff_metrics(self):
        """Update staff performance metrics"""
        while self.is_running:
            try:
                async with db_manager.session() as session:
                    # Get all staff members
                    stmt = select(StaffPerformance)
                    result = await session.execute(stmt)
                    staff_metrics = result.scalars().all()

                    for metrics in staff_metrics:
                        await self.update_staff_stats(metrics)

            except Exception as e:
                self.logger.error(f"Error in staff metrics task: {e}")

            await asyncio.sleep(300)  # Update every 5 minutes

    async def process_scheduled_followups(self):
        """Process scheduled ticket followups"""
        while self.is_running:
            try:
                async with db_manager.session() as session:
                    # Get tickets with scheduled followups
                    now = datetime.utcnow()
                    stmt = select(Ticket).where(
                        Ticket.scheduled_followup_at <= now,
                        Ticket.status != TicketStatus.CLOSED
                    )
                    result = await session.execute(stmt)
                    tickets = result.scalars().all()

                    for ticket in tickets:
                        await self.handle_followup(ticket)

            except Exception as e:
                self.logger.error(f"Error in followup task: {e}")

            await asyncio.sleep(60)  # Check every minute

    async def auto_close_tickets(self):
        """Auto-close inactive tickets"""
        while self.is_running:
            try:
                async with db_manager.session() as session:
                    # Get guild settings and inactive tickets
                    stmt = select(Guild)
                    result = await session.execute(stmt)
                    guilds = result.scalars().all()

                    for guild in guilds:
                        if guild.auto_close_hours > 0:
                            inactive_time = datetime.utcnow() - timedelta(hours=guild.auto_close_hours)
                            stmt = select(Ticket).where(
                                Ticket.guild_id == str(guild.id),
                                Ticket.status == TicketStatus.OPEN,
                                Ticket.last_message_at <= inactive_time
                            )
                            result = await session.execute(stmt)
                            tickets = result.scalars().all()

                            for ticket in tickets:
                                await self.auto_close_ticket(ticket)

            except Exception as e:
                self.logger.error(f"Error in auto-close task: {e}")

            await asyncio.sleep(3600)  # Check every hour

    async def update_staff_performance(self):
        """Update staff performance statistics"""
        while self.is_running:
            try:
                async with db_manager.session() as session:
                    # Get all staff performance records
                    stmt = select(StaffPerformance)
                    result = await session.execute(stmt)
                    staff_records = result.scalars().all()

                    for record in staff_records:
                        await self.update_performance_stats(record)

            except Exception as e:
                self.logger.error(f"Error in performance update task: {e}")

            await asyncio.sleep(1800)  # Update every 30 minutes

    async def handle_sla_breach(self, ticket: Ticket, alert_level: int):
        """Handle SLA breach for a ticket"""
        try:
            channel = self.bot.get_channel(int(ticket.channel_id))
            if not channel:
                return

            # Get SLA information
            sla_info = await sla_monitor.get_sla_info(ticket)
            
            # Create alert embed
            embed = discord.Embed(
                title="⚠️ SLA Alert",
                description=f"This ticket has exceeded the response time SLA.\n\n**Time Elapsed:** {sla_info['elapsed_time']}\n**SLA Target:** {sla_info['sla_target']}",
                color=discord.Color.red()
            )

            # Add alert-specific information
            if alert_level == 1:
                embed.add_field(name="Alert Level", value="Warning - Approaching SLA breach")
            elif alert_level == 2:
                embed.add_field(name="Alert Level", value="Critical - SLA breached")

            # Send alert
            await channel.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error handling SLA breach for ticket {ticket.ticket_id_display}: {e}")

    async def handle_followup(self, ticket: Ticket):
        """Handle scheduled followup for a ticket"""
        try:
            channel = self.bot.get_channel(int(ticket.channel_id))
            if not channel:
                return

            # Create followup message
            embed = discord.Embed(
                title="📅 Scheduled Followup",
                description="This is a scheduled followup for your ticket. Please provide any updates or let us know if you need further assistance.",
                color=discord.Color.blue()
            )

            # Send followup
            await channel.send(embed=embed)

            # Update ticket
            async with db_manager.session() as session:
                ticket.scheduled_followup_at = None
                session.add(ticket)
                await session.commit()

        except Exception as e:
            self.logger.error(f"Error handling followup for ticket {ticket.ticket_id_display}: {e}")

    async def auto_close_ticket(self, ticket: Ticket):
        """Auto-close an inactive ticket"""
        try:
            channel = self.bot.get_channel(int(ticket.channel_id))
            if not channel:
                return

            # Create closure message
            embed = discord.Embed(
                title="🔒 Ticket Auto-Closed",
                description="This ticket has been automatically closed due to inactivity. You can create a new ticket if you need further assistance.",
                color=discord.Color.orange()
            )

            # Send message and close ticket
            await channel.send(embed=embed)
            
            # Update ticket status
            async with db_manager.session() as session:
                ticket.status = TicketStatus.CLOSED
                ticket.closed_at = datetime.utcnow()
                ticket.closure_reason_text = "Auto-closed due to inactivity"
                session.add(ticket)
                await session.commit()

        except Exception as e:
            self.logger.error(f"Error auto-closing ticket {ticket.ticket_id_display}: {e}")

    async def update_performance_stats(self, record: StaffPerformance):
        """Update performance statistics for a staff member"""
        try:
            async with db_manager.session() as session:
                # Get tickets handled by this staff member
                stmt = select(Ticket).where(
                    Ticket.claimed_by_id == str(record.staff_id),
                    Ticket.status == TicketStatus.CLOSED
                )
                result = await session.execute(stmt)
                tickets = result.scalars().all()

                # Calculate metrics
                total_response_time = 0
                total_resolution_time = 0
                ticket_count = len(tickets)

                for ticket in tickets:
                    if ticket.last_staff_response_at and ticket.opened_at:
                        response_time = (ticket.last_staff_response_at - ticket.opened_at).total_seconds()
                        total_response_time += response_time

                    if ticket.closed_at and ticket.opened_at:
                        resolution_time = (ticket.closed_at - ticket.opened_at).total_seconds()
                        total_resolution_time += resolution_time

                # Update record
                if ticket_count > 0:
                    record.avg_response_time_seconds = total_response_time / ticket_count
                    record.avg_resolution_time_seconds = total_resolution_time / ticket_count
                    record.tickets_handled_count = ticket_count
                    session.add(record)
                    await session.commit()

        except Exception as e:
            self.logger.error(f"Error updating performance stats for staff {record.staff_id}: {e}")

    async def update_staff_stats(self, metrics: StaffPerformance):
        """Update statistics for a staff member"""
        try:
            async with db_manager.session() as session:
                # Get recent tickets
                stmt = select(Ticket).where(
                    Ticket.claimed_by_id == str(metrics.staff_id),
                    Ticket.closed_at >= datetime.utcnow() - timedelta(days=30)
                )
                result = await session.execute(stmt)
                tickets = result.scalars().all()

                # Calculate metrics
                response_times = []
                resolution_times = []

                for ticket in tickets:
                    if ticket.last_staff_response_at and ticket.opened_at:
                        response_time = (ticket.last_staff_response_at - ticket.opened_at).total_seconds()
                        response_times.append(response_time)

                    if ticket.closed_at and ticket.opened_at:
                        resolution_time = (ticket.closed_at - ticket.opened_at).total_seconds()
                        resolution_times.append(resolution_time)

                # Update metrics
                if response_times:
                    metrics.avg_response_time_seconds = sum(response_times) / len(response_times)
                if resolution_times:
                    metrics.avg_resolution_time_seconds = sum(resolution_times) / len(resolution_times)

                session.add(metrics)
                await session.commit()

        except Exception as e:
            self.logger.error(f"Error updating stats for staff {metrics.staff_id}: {e}") 