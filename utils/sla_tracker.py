"""
SLA tracking utilities.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from database import db_manager
from database.models import Ticket, SLADefinition, StaffPerformance
from sqlalchemy import select
from sqlalchemy.types import TicketStatus
from utils.logger import get_logger

logger = get_logger("sla")

class SLATracker:
    def __init__(self):
        self.alert_threshold = 0.8  # Alert at 80% of SLA time

    async def check_ticket_sla(self, ticket_id: str) -> Dict:
        """Check if a ticket is within SLA"""
        try:
            async with db_manager.session() as session:
                # Get ticket and its SLA definition
                ticket = await session.get(Ticket, ticket_id)
                if not ticket:
                    return {"error": "Ticket not found"}

                sla_def = await session.get(SLADefinition, ticket.category_id)
                if not sla_def:
                    return {"error": "No SLA definition found for category"}

                # Calculate time differences
                now = datetime.utcnow()
                time_since_creation = now - ticket.opened_at
                time_since_last_staff = now - ticket.last_staff_response_at if ticket.last_staff_response_at else time_since_creation
                time_since_last_user = now - ticket.last_user_response_at if ticket.last_user_response_at else time_since_creation

                # Check response SLA
                response_sla_breached = time_since_creation > timedelta(minutes=sla_def.response_sla_minutes)
                response_sla_warning = time_since_creation > timedelta(minutes=sla_def.response_sla_minutes * self.alert_threshold)

                # Check resolution SLA
                resolution_sla_breached = time_since_creation > timedelta(minutes=sla_def.resolution_sla_minutes)

                return {
                    "ticket_id": ticket_id,
                    "response_sla_breached": response_sla_breached,
                    "response_sla_warning": response_sla_warning,
                    "resolution_sla_breached": resolution_sla_breached,
                    "time_since_creation": time_since_creation,
                    "time_since_last_staff": time_since_last_staff,
                    "time_since_last_user": time_since_last_user
                }

        except Exception as e:
            logger.error(f"Error checking ticket SLA: {e}")
            return {"error": str(e)}

    async def get_breached_tickets(self, guild_id: str) -> List[Dict]:
        """Get all tickets that have breached SLA"""
        try:
            async with db_manager.get_session() as session:
                # Get all open tickets
                stmt = select(Ticket).where(
                    Ticket.status == TicketStatus.OPEN,
                    Ticket.guild_id == str(guild_id)
                )
                result = await session.execute(stmt)
                tickets = result.scalars().all()

                breached_tickets = []
                for ticket in tickets:
                    sla_status = await self.check_ticket_sla(ticket.id)
                    if sla_status.get("response_sla_breached") or \
                       sla_status.get("resolution_sla_breached"):
                        breached_tickets.append(sla_status)

                return breached_tickets
        except Exception as e:
            logger.error(f"Error getting breached tickets: {e}")
            return []

    async def update_staff_performance(self, staff_id: str, guild_id: str) -> None:
        """Update staff performance metrics based on SLA compliance"""
        try:
            async with db_manager.get_session() as session:
                # Get staff's tickets
                stmt = select(Ticket).where(
                    Ticket.guild_id == str(guild_id),
                    Ticket.claimed_by_id == staff_id,
                    Ticket.closed_at.isnot(None)
                )
                result = await session.execute(stmt)
                tickets = result.scalars().all()

                if not tickets:
                    return

                # Calculate metrics
                total_tickets = len(tickets)
                total_response_time = 0
                total_resolution_time = 0
                sla_compliant = 0

                for ticket in tickets:
                    # Calculate response time
                    if ticket.last_staff_response_at:
                        response_time = (ticket.last_staff_response_at - ticket.opened_at).total_seconds()
                        total_response_time += response_time

                    # Calculate resolution time
                    resolution_time = (ticket.closed_at - ticket.opened_at).total_seconds()
                    total_resolution_time += resolution_time

                    # Check SLA compliance
                    sla_status = await self.check_ticket_sla(ticket.id)
                    if not sla_status.get("response_sla_breached"):
                        sla_compliant += 1

                # Update staff performance
                performance = await session.get(StaffPerformance, (guild_id, staff_id))
                if not performance:
                    performance = StaffPerformance(
                        guild_id=guild_id,
                        staff_id=staff_id
                    )
                    session.add(performance)

                performance.tickets_handled_count = total_tickets
                performance.avg_response_time_seconds = total_response_time / total_tickets
                performance.avg_resolution_time_seconds = total_resolution_time / total_tickets
                performance.sla_compliance_rate = sla_compliant / total_tickets
                performance.last_updated = datetime.utcnow()

                await session.commit()
        except Exception as e:
            logger.error(f"Error updating staff performance: {e}")

    async def get_staff_sla_stats(self, staff_id: str, guild_id: str) -> Dict:
        """Get SLA statistics for a staff member"""
        try:
            async with db_manager.get_session() as session:
                performance = await session.get(StaffPerformance, (guild_id, staff_id))
                if not performance:
                    return {"error": "No performance data found"}

                return {
                    "staff_id": staff_id,
                    "tickets_handled": performance.tickets_handled_count,
                    "avg_response_time": performance.avg_response_time_seconds / 60,  # Convert to minutes
                    "avg_resolution_time": performance.avg_resolution_time_seconds / 60,  # Convert to minutes
                    "sla_compliance_rate": performance.sla_compliance_rate,
                    "last_updated": performance.last_updated
                }
        except Exception as e:
            logger.error(f"Error getting staff SLA stats: {e}")
            return {"error": str(e)}

# Create singleton instance
sla_tracker = SLATracker() 