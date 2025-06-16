"""
Utility module for generating ticket transcripts.
This module provides access to the transcript generation functionality.
"""

from typing import Optional, List, Dict
from discord import TextChannel
from cogs.transcript import Transcript
import os
import logging
from datetime import datetime
from pathlib import Path
import jinja2
from database.connection import db_manager
from database.models import Ticket, TicketParticipant
import aiofiles
import html

logger = logging.getLogger(__name__)

class TranscriptGenerator:
    def __init__(self):
        self.transcript_dir = Path("data/transcripts")
        self.transcript_dir.mkdir(parents=True, exist_ok=True)

    async def generate(self, channel: TextChannel, ticket_id: str) -> str:
        """Generate a transcript of the ticket conversation."""
        try:
            # Create transcript filename
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            filename = f"ticket-{ticket_id}-{timestamp}.html"
            filepath = self.transcript_dir / filename

            # Collect messages
            messages = []
            async for message in channel.history(limit=None, oldest_first=True):
                if not message.author.bot:  # Skip bot messages
                    # Format message content
                    content = message.content
                    for attachment in message.attachments:
                        content += f"\n[Attachment: {attachment.filename}]({attachment.url})"

                    messages.append({
                        "author": {
                            "name": message.author.display_name,
                            "avatar_url": str(message.author.display_avatar.url)
                        },
                        "content": content,
                        "timestamp": message.created_at.replace(tzinfo=None),  # Remove timezone info
                        "is_staff": any(role.name.lower() in ["staff", "support", "admin", "moderator"] for role in message.author.roles)
                    })

            # Generate HTML content
            template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Ticket Transcript - {{ ticket_id }}</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            line-height: 1.6; 
            margin: 0; 
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }
        .message { 
            margin-bottom: 20px; 
            padding: 15px; 
            border-radius: 8px; 
            background: #fff;
            border: 1px solid #eee;
        }
        .message.staff { 
            background: #e3f2fd; 
        }
        .author { 
            font-weight: bold;
            margin-bottom: 5px;
        }
        .timestamp { 
            color: #666; 
            font-size: 0.8em; 
        }
        .content { 
            margin-top: 10px;
            white-space: pre-wrap;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Ticket Transcript - {{ ticket_id }}</h1>
            <p>Generated on {{ timestamp }}</p>
        </div>
        
        <div class="messages">
            {% for message in messages %}
            <div class="message {% if message.is_staff %}staff{% endif %}">
                <div class="author">{{ message.author.name }}</div>
                <div class="timestamp">{{ message.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC') }}</div>
                <div class="content">{{ message.content }}</div>
            </div>
            {% endfor %}
        </div>

        <div class="footer">
            <p>End of transcript</p>
        </div>
    </div>
</body>
</html>
            """

            # Render template
            template = jinja2.Template(template)
            html_content = template.render(
                ticket_id=ticket_id,
                timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                messages=messages
            )

            # Save transcript
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(html_content)

            return str(filepath)

        except Exception as e:
            logger.error(f"Error generating transcript: {e}")
            return None

# Create a global instance
transcript_generator = TranscriptGenerator()

async def generate_transcript(channel: TextChannel, bot) -> Optional[str]:
    """
    Generate a transcript for a Discord channel.
    
    Args:
        channel: The Discord text channel to generate a transcript for
        bot: The bot instance to use for transcript generation
        
    Returns:
        Optional[str]: Path to the generated transcript file, or None if generation failed
    """
    transcript_cog = Transcript(bot)
    return await transcript_cog.generate_transcript(channel)

__all__ = ['generate_transcript'] 