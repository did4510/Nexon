"""
Utility functions for handling Discord permissions and role checks.
"""

import discord
from typing import List
from database import db_manager
from database.models import Guild, TicketCategory

def has_staff_role(user: discord.Member, staff_role_ids: List[int]) -> bool:
    """Check if a user has any of the specified staff roles."""
    return any(role.id in staff_role_ids for role in user.roles)

async def has_category_staff_role(interaction: discord.Interaction, category_id: int) -> bool:
    """
    Check if a user has staff role for a specific ticket category.
    
    Args:
        interaction: The Discord interaction to check permissions for
        category_id: The ID of the ticket category to check
        
    Returns:
        bool: True if the user has a staff role for the category, False otherwise
    """
    async with db_manager.get_session() as session:
        # Get category
        category = await session.get(TicketCategory, category_id)
        if not category:
            return False
            
        # Check if user has any staff role for this category
        return has_staff_role(interaction.user, category.staff_role_ids)

__all__ = ['has_staff_role', 'has_category_staff_role']