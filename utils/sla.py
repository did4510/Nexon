"""
Service Level Agreement (SLA) tracking utilities for the ticket system.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import discord
from database.models import Ticket, SLADefinition, Guild
from sqlalchemy import select
from utils.logger import logger

async def check_sla_status(ticket: Ticket, sla_def: SLADefinition) -> Dict[str, Any]:
    """
    Check ticket SLA status and return status information
    
    Args:
        ticket: The ticket to check
        sla_def: The SLA definition to check against
        
    Returns:
        Dict containing status information including:
        - status: 'breached', 'warning', or 'ok'
        - percentage: Percentage of SLA time used
        - color: Discord color for display
        - emoji: Status emoji
        - message: Status message
    """
    now = datetime.utcnow()
    elapsed = now - ticket.opened_at
    elapsed_minutes = elapsed.total_seconds() / 60

    # Response time SLA check
    if not ticket.last_staff_response_at and elapsed_minutes > sla_def.response_time:
        return {
            'status': 'breached',
            'percentage': 100,
            'color': discord.Color.red(),
            'emoji': '🔴',
            'message': 'Response time SLA breached'
        }

    # Resolution time SLA check
    percentage = min((elapsed_minutes / sla_def.resolution_time) * 100, 100)
    
    if percentage >= 100:
        return {
            'status': 'breached',
            'percentage': percentage,
            'color': discord.Color.red(),
            'emoji': '🔴',
            'message': 'Resolution time SLA breached'
        }
    elif percentage >= 75:
        return {
            'status': 'warning',
            'percentage': percentage,
            'color': discord.Color.orange(),
            'emoji': '🟡',
            'message': 'Approaching SLA breach'
        }
    
    return {
        'status': 'ok',
        'percentage': percentage,
        'color': discord.Color.green(),
        'emoji': '🟢',
        'message': 'Within SLA'
    }

def get_sla_alert_level(percentage: float) -> Dict[str, Any]:
    """
    Get SLA alert level information based on percentage
    
    Args:
        percentage: The percentage of SLA time used
        
    Returns:
        Dict containing alert level information
    """
    if percentage >= 100:
        return {
            'level': 'critical',
            'color': discord.Color.red(),
            'emoji': '🔴',
            'message': 'SLA Breached'
        }
    elif percentage >= 75:
        return {
            'level': 'warning',
            'color': discord.Color.orange(),
            'emoji': '🟡',
            'message': 'SLA Warning'
        }
    return {
        'level': 'normal',
        'color': discord.Color.green(),
        'emoji': '🟢',
        'message': 'Within SLA'
    }

async def sla_monitor(bot) -> None:
    """
    Monitor tickets for SLA breaches and send alerts
    
    Args:
        bot: The bot instance for accessing database and channels
    """
    try:
        async with bot.db.session() as session:
            # Get all active tickets
            stmt = select(Ticket).filter(
                Ticket.status.in_(['OPEN', 'IN_PROGRESS', 'PENDING_STAFF'])
            )
            result = await session.execute(stmt)
            active_tickets = result.scalars().all()

            # Check each ticket's SLA
            for ticket in active_tickets:
                # Get guild SLA settings
                guild_stmt = select(Guild).where(Guild.guild_id == ticket.guild_id)
                guild_result = await session.execute(guild_stmt)
                guild = guild_result.scalar_one_or_none()

                if not guild:
                    continue

                # Get ticket category SLA
                sla_stmt = select(SLADefinition).where(
                    SLADefinition.category_id == ticket.category_db_id
                )
                sla_result = await session.execute(sla_stmt)
                sla_def = sla_result.scalar_one_or_none()

                if not sla_def:
                    continue

                # Check SLA status
                status = await check_sla_status(ticket, sla_def)

                # Send alerts if needed
                if status['status'] in ['warning', 'breached']:
                    await send_sla_alert(bot, ticket, status, guild)

    except Exception as e:
        logger.error(f"Error in SLA monitor: {e}")

async def send_sla_alert(
    bot,
    ticket: Ticket,
    status: Dict[str, Any],
    guild: Guild
) -> None:
    """Send SLA breach alerts to configured channels"""
    try:
        # Get alert channel
        alert_channel = await bot.fetch_channel(guild.ticket_logs_channel_id)
        if not alert_channel:
            return

        # Create alert embed
        embed = discord.Embed(
            title=f"{status['emoji']} SLA Alert - Ticket #{ticket.ticket_id_display}",
            description=status['message'],
            color=status['color']
        )
        
        embed.add_field(
            name="Status",
            value=f"{status['status'].title()} ({status['percentage']:.1f}%)",
            inline=True
        )
        
        embed.add_field(
            name="Time Open",
            value=f"{(datetime.utcnow() - ticket.opened_at).total_seconds() / 3600:.1f} hours",
            inline=True
        )

        await alert_channel.send(embed=embed)

    except Exception as e:
        logger.error(f"Error sending SLA alert: {e}")

# Export the public API
__all__ = [
    'check_sla_status',
    'get_sla_alert_level',
    'sla_monitor',
    'send_sla_alert'
]