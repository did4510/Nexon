"""
Transcript generation utilities.
Handles HTML and text transcript generation for tickets.
"""
import discord
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import aiofiles
import json
from jinja2 import Environment, FileSystemLoader

from database.models import Ticket
from utils.logger import logger

class TranscriptGenerator:
    def __init__(self):
        """Initialize transcript generator."""
        self.env = Environment(
            loader=FileSystemLoader("templates"),
            autoescape=True
        )
        self.template = self.env.get_template("transcript.html")
    
    async def generate_html(
        self,
        channel: discord.TextChannel,
        ticket: Ticket,
        messages: Optional[List[discord.Message]] = None
    ) -> str:
        """
        Generate an HTML transcript of a ticket.
        
        Args:
            channel: The ticket channel
            ticket: The ticket object
            messages: Optional list of messages (if already fetched)
            
        Returns:
            Path to the generated HTML file
        """
        try:
            # Get messages if not provided
            if not messages:
                messages = []
                async for message in channel.history(limit=None, oldest_first=True):
                    messages.append(message)
            
            # Prepare message data
            message_data = []
            for msg in messages:
                # Skip system messages
                if not msg.author:
                    continue
                
                # Get attachments
                attachments = []
                for attachment in msg.attachments:
                    if attachment.content_type and attachment.content_type.startswith("image/"):
                        attachments.append({
                            "url": attachment.url,
                            "filename": attachment.filename,
                            "is_image": True
                        })
                    else:
                        attachments.append({
                            "url": attachment.url,
                            "filename": attachment.filename,
                            "is_image": False
                        })
                
                # Get embeds
                embeds = []
                for embed in msg.embeds:
                    embed_data = {
                        "title": embed.title,
                        "description": embed.description,
                        "color": f"#{embed.color:06x}" if embed.color else None,
                        "fields": [
                            {
                                "name": field.name,
                                "value": field.value,
                                "inline": field.inline
                            }
                            for field in embed.fields
                        ],
                        "footer": embed.footer.text if embed.footer else None,
                        "timestamp": embed.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") if embed.timestamp else None,
                        "thumbnail": embed.thumbnail.url if embed.thumbnail else None,
                        "image": embed.image.url if embed.image else None,
                        "author": {
                            "name": embed.author.name,
                            "icon_url": embed.author.icon_url
                        } if embed.author else None
                    }
                    embeds.append(embed_data)
                
                # Create message entry
                message_data.append({
                    "id": str(msg.id),
                    "content": msg.content,
                    "author": {
                        "name": msg.author.display_name,
                        "avatar_url": str(msg.author.display_avatar.url),
                        "bot": msg.author.bot,
                        "color": f"#{msg.author.color:06x}" if msg.author.color.value else None
                    },
                    "timestamp": msg.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "attachments": attachments,
                    "embeds": embeds,
                    "edited": msg.edited_at.strftime("%Y-%m-%d %H:%M:%S UTC") if msg.edited_at else None,
                    "reference": str(msg.reference.message_id) if msg.reference else None
                })
            
            # Prepare template data
            template_data = {
                "ticket": {
                    "id": ticket.ticket_id_display,
                    "created_at": ticket.opened_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "closed_at": ticket.closed_at.strftime("%Y-%m-%d %H:%M:%S UTC") if ticket.closed_at else None,
                    "creator": ticket.creator_name,
                    "category": ticket.category_name,
                    "status": ticket.status
                },
                "channel": {
                    "name": channel.name,
                    "id": str(channel.id),
                    "created_at": channel.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                },
                "guild": {
                    "name": channel.guild.name,
                    "icon_url": str(channel.guild.icon.url) if channel.guild.icon else None
                },
                "messages": message_data,
                "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            
            # Ensure transcripts directory exists
            os.makedirs("data/transcripts", exist_ok=True)
            
            # Generate HTML file
            transcript_path = f"data/transcripts/ticket-{ticket.ticket_id_display}.html"
            async with aiofiles.open(transcript_path, "w", encoding="utf-8") as f:
                await f.write(self.template.render(**template_data))
            
            # Also save raw data for future reference
            data_path = f"data/transcripts/ticket-{ticket.ticket_id_display}.json"
            async with aiofiles.open(data_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(template_data, indent=2))
            
            return transcript_path
        except Exception as e:
            logger.error(f"Error generating transcript: {e}")
            raise
    
    async def generate_text(
        self,
        channel: discord.TextChannel,
        ticket: Ticket,
        messages: Optional[List[discord.Message]] = None
    ) -> str:
        """
        Generate a plain text transcript of a ticket.
        
        Args:
            channel: The ticket channel
            ticket: The ticket object
            messages: Optional list of messages (if already fetched)
            
        Returns:
            Path to the generated text file
        """
        try:
            # Get messages if not provided
            if not messages:
                messages = []
                async for message in channel.history(limit=None, oldest_first=True):
                    messages.append(message)
            
            # Ensure transcripts directory exists
            os.makedirs("data/transcripts", exist_ok=True)
            
            # Generate text file
            transcript_path = f"data/transcripts/ticket-{ticket.ticket_id_display}.txt"
            async with aiofiles.open(transcript_path, "w", encoding="utf-8") as f:
                # Write header
                await f.write(f"Ticket Transcript #{ticket.ticket_id_display}\n")
                await f.write("=" * 50 + "\n\n")
                
                await f.write(f"Created by: {ticket.creator_name}\n")
                await f.write(f"Category: {ticket.category_name}\n")
                await f.write(f"Created at: {ticket.opened_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
                if ticket.closed_at:
                    await f.write(f"Closed at: {ticket.closed_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
                await f.write(f"Status: {ticket.status}\n\n")
                
                await f.write("Messages:\n")
                await f.write("-" * 50 + "\n\n")
                
                # Write messages
                for msg in messages:
                    if not msg.author:
                        continue
                    
                    # Write message header
                    await f.write(f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}] {msg.author.display_name}:\n")
                    
                    # Write content
                    if msg.content:
                        await f.write(f"{msg.content}\n")
                    
                    # Write attachments
                    if msg.attachments:
                        await f.write("\nAttachments:\n")
                        for attachment in msg.attachments:
                            await f.write(f"- {attachment.filename}: {attachment.url}\n")
                    
                    # Write embeds
                    if msg.embeds:
                        await f.write("\nEmbeds:\n")
                        for embed in msg.embeds:
                            if embed.title:
                                await f.write(f"Title: {embed.title}\n")
                            if embed.description:
                                await f.write(f"Description: {embed.description}\n")
                            if embed.fields:
                                await f.write("Fields:\n")
                                for field in embed.fields:
                                    await f.write(f"- {field.name}: {field.value}\n")
                    
                    # Add spacing between messages
                    await f.write("\n")
            
            return transcript_path
        except Exception as e:
            logger.error(f"Error generating text transcript: {e}")
            raise

# Create singleton instance
transcript_generator = TranscriptGenerator() 