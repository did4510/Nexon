from typing import Dict, Any
import discord

NEXON_THEME = {
    'primary': discord.Color.from_rgb(88, 101, 242),    # Discord Blurple
    'success': discord.Color.from_rgb(87, 242, 135),    # Emerald Green
    'error': discord.Color.from_rgb(237, 66, 69),       # Soft Red
    'warning': discord.Color.from_rgb(254, 231, 92),    # Warm Yellow
    'info': discord.Color.from_rgb(88, 101, 242),       # Light Blue
    'inactive': discord.Color.from_rgb(114, 118, 125)   # Gray
}

EMOJIS = {
    'success': '✨',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'loading': '🔄',
    'online': '🟢',
    'idle': '🟡',
    'dnd': '🔴',
    'offline': '⚫'
}

def create_embed(
    title: str,
    description: str = None,
    color_type: str = 'primary'
) -> discord.Embed:
    """Create a themed embed"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=NEXON_THEME[color_type]
    )
    return embed