"""
Embed templates for the ticket system.
"""
import discord
from typing import Optional, List, Dict, Any
from datetime import datetime
from .constants import *

def create_base_embed(
    title: str,
    description: str,
    color: Optional[int] = None,
    footer_text: Optional[str] = None,
    thumbnail_url: Optional[str] = None
) -> discord.Embed:
    """Create a base embed with consistent styling."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color or COLORS.DEFAULT,
        timestamp=datetime.utcnow()
    )
    
    if footer_text:
        embed.set_footer(text=footer_text)
    
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    return embed

def create_error_embed(
    title: str = "Error",
    description: str = "An error occurred.",
    footer_text: Optional[str] = None
) -> discord.Embed:
    """Create an error embed."""
    return create_base_embed(
        title=f"{EMOJI_ERROR} {title}",
        description=description,
        color=COLORS.ERROR,
        footer_text=footer_text
    )

def create_success_embed(
    title: str = "Success",
    description: str = "Operation completed successfully.",
    footer_text: Optional[str] = None
) -> discord.Embed:
    """Create a success embed."""
    return create_base_embed(
        title=f"{EMOJI_SUCCESS} {title}",
        description=description,
        color=COLORS.SUCCESS,
        footer_text=footer_text
    )

def create_info_embed(
    title: str = "Information",
    description: str = "",
    footer_text: Optional[str] = None
) -> discord.Embed:
    """Create an info embed."""
    return create_base_embed(
        title=f"{EMOJI_INFO} {title}",
        description=description,
        color=COLORS.INFO,
        footer_text=footer_text
    )

def create_support_panel_embed(
    guild_name: str,
    categories: List[Dict[str, Any]],
    theme_color: Optional[int] = None
) -> discord.Embed:
    """Create the support panel embed."""
    description = (
        f"Welcome to {guild_name}'s Support System!\n\n"
        "To create a ticket, click one of the buttons below corresponding to your issue category.\n"
        "Our support team will assist you as soon as possible.\n\n"
        "__Available Categories:__\n"
    )
    
    for category in categories:
        description += f"\n{category['emoji']} **{category['name']}**\n{category['description']}"
    
    return create_base_embed(
        title=f"{EMOJI_SUPPORT} Support Panel",
        description=description,
        color=theme_color or COLORS.DEFAULT
    )

def create_ticket_embed(
    ticket_id: str,
    creator: discord.Member,
    category: str,
    initial_message: str,
    is_anonymous: bool = False,
    theme_color: Optional[int] = None
) -> discord.Embed:
    """Create the initial ticket embed."""
    embed = create_base_embed(
        title=f"{EMOJI_TICKET} Ticket #{ticket_id}",
        description=(
            f"**Category:** {category}\n"
            f"**Created by:** {'Anonymous' if is_anonymous else creator.mention}\n"
            f"**Status:** {EMOJI_OPEN} Open\n\n"
            "__Initial Message:__\n"
            f"{initial_message}"
        ),
        color=theme_color or COLORS.DEFAULT
    )
    
    if not is_anonymous:
        embed.set_thumbnail(url=creator.display_avatar.url)
    
    embed.set_footer(text=f"Ticket ID: {ticket_id}")
    return embed

def create_ticket_closed_embed(
    ticket_id: str,
    closed_by: discord.Member,
    reason: str,
    transcript_url: Optional[str] = None
) -> discord.Embed:
    """Create the ticket closed embed."""
    description = (
        f"**Closed by:** {closed_by.mention}\n"
        f"**Reason:** {reason}\n"
    )
    
    if transcript_url:
        description += f"\n[Click here to view the transcript]({transcript_url})"
    
    return create_base_embed(
        title=f"{EMOJI_LOCK} Ticket #{ticket_id} Closed",
        description=description,
        color=COLORS.WARNING
    )

def create_ticket_claimed_embed(
    ticket_id: str,
    staff_member: discord.Member
) -> discord.Embed:
    """Create the ticket claimed embed."""
    return create_base_embed(
        title=f"{EMOJI_STAFF} Ticket #{ticket_id} Claimed",
        description=f"This ticket has been claimed by {staff_member.mention}.",
        color=COLORS.INFO
    )

def create_ticket_status_embed(
    ticket_id: str,
    status: str,
    updated_by: discord.Member
) -> discord.Embed:
    """Create the ticket status update embed."""
    emoji = {
        "OPEN": EMOJI_OPEN,
        "PENDING_USER": EMOJI_PENDING,
        "PENDING_STAFF": EMOJI_PENDING,
        "IN_PROGRESS": EMOJI_PROGRESS,
        "ESCALATED": EMOJI_ESCALATED,
        "RESOLVED": EMOJI_RESOLVED,
        "CLOSED": EMOJI_LOCK
    }.get(status, EMOJI_INFO)
    
    return create_base_embed(
        title=f"{emoji} Ticket Status Updated",
        description=(
            f"**Ticket:** #{ticket_id}\n"
            f"**New Status:** {status}\n"
            f"**Updated by:** {updated_by.mention}"
        ),
        color=COLORS.INFO
    )

def create_internal_note_embed(
    ticket_id: str,
    staff_member: discord.Member,
    note: str
) -> discord.Embed:
    """Create an internal note embed."""
    return create_base_embed(
        title=f"{EMOJI_PIN} Internal Note",
        description=(
            f"**Staff Member:** {staff_member.mention}\n"
            f"**Note:**\n{note}"
        ),
        color=COLORS.STAFF,
        footer_text=f"Ticket #{ticket_id}"
    )

def create_feedback_request_embed(
    ticket_id: str,
    guild_name: str
) -> discord.Embed:
    """Create a feedback request embed."""
    return create_base_embed(
        title=f"{EMOJI_FEEDBACK} Support Feedback",
        description=(
            f"Thank you for using {guild_name}'s support system!\n\n"
            "Please rate your support experience by clicking one of the star ratings below.\n"
            "Your feedback helps us improve our support quality."
        ),
        color=COLORS.DEFAULT,
        footer_text=f"Ticket #{ticket_id}"
    )

def create_feedback_received_embed(
    ticket_id: str,
    rating: int,
    comments: Optional[str] = None
) -> discord.Embed:
    """Create a feedback received embed."""
    description = f"**Rating:** {'★' * rating}{'☆' * (5 - rating)}"
    if comments:
        description += f"\n\n**Comments:**\n{comments}"
    
    return create_base_embed(
        title=f"{EMOJI_FEEDBACK} Feedback Received",
        description=description,
        color=COLORS.SUCCESS,
        footer_text=f"Ticket #{ticket_id}"
    )

def create_stats_embed(
    title: str,
    stats: Dict[str, Any],
    footer_text: Optional[str] = None
) -> discord.Embed:
    """Create a statistics embed."""
    embed = create_base_embed(
        title=f"{EMOJI_STATS} {title}",
        description="",
        color=COLORS.INFO,
        footer_text=footer_text
    )
    
    for key, value in stats.items():
        embed.add_field(name=key, value=value, inline=True)
    
    return embed

def create_help_embed(
    title: str,
    commands: List[Dict[str, str]],
    page: int,
    total_pages: int
) -> discord.Embed:
    """Create a help embed."""
    description = "Here are the available commands:\n\n"
    
    for cmd in commands:
        description += (
            f"**/{cmd['name']}**\n"
            f"{cmd['description']}\n"
            f"Usage: `{cmd['usage']}`\n\n"
        )
    
    return create_base_embed(
        title=f"{EMOJI_HELP} {title}",
        description=description,
        color=COLORS.INFO,
        footer_text=f"Page {page}/{total_pages}"
    )

def create_maintenance_embed(message: str) -> discord.Embed:
    """Create a maintenance mode embed."""
    return create_base_embed(
        title=f"{EMOJI_MAINTENANCE} Maintenance Mode",
        description=(
            "The ticket system is currently under maintenance.\n\n"
            f"**Message from staff:**\n{message}"
        ),
        color=COLORS.WARNING
    )

def create_sla_alert_embed(
    ticket_id: str,
    sla_type: str,
    time_elapsed: str
) -> discord.Embed:
    """Create an SLA violation alert embed."""
    return create_base_embed(
        title=f"{EMOJI_WARNING} SLA Alert",
        description=(
            f"**Ticket:** #{ticket_id}\n"
            f"**Alert Type:** {sla_type} SLA Exceeded\n"
            f"**Time Elapsed:** {time_elapsed}"
        ),
        color=COLORS.ERROR
    )