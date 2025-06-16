# Create new file: utils/transcript.py
import logging
import discord
from discord import app_commands
from discord.ext import commands
import markdown
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class Transcript(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.transcript_dir = Path("data/transcripts")
        self.transcript_dir.mkdir(parents=True, exist_ok=True)

    async def generate_transcript(self, channel: discord.TextChannel) -> str:
        """Generate an HTML transcript of a ticket channel."""
        try:
            # Create transcript content
            content = []
            content.append(f"# Ticket Transcript: {channel.name}")
            content.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

            # Fetch messages
            async for message in channel.history(limit=None, oldest_first=True):
                # Skip bot messages except for system messages
                if message.author.bot and not message.flags.system:
                    continue

                # Format message
                timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
                author = message.author.display_name
                content.append(f"## {author} - {timestamp}")

                # Add message content
                if message.content:
                    content.append(message.content)

                # Add attachments
                if message.attachments:
                    content.append("\n**Attachments:**")
                    for attachment in message.attachments:
                        content.append(f"- {attachment.url}")

                content.append("")  # Add blank line between messages

            # Convert to HTML
            html_content = markdown.markdown("\n".join(content))

            # Add basic styling
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Ticket Transcript - {channel.name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #5865F2; }}
                    h2 {{ color: #2C2F33; margin-top: 20px; }}
                    a {{ color: #5865F2; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

            # Save transcript
            transcript_path = self.transcript_dir / f"{channel.name}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.html"
            transcript_path.write_text(html, encoding='utf-8')

            return str(transcript_path)

        except Exception as e:
            logger.error(f"Failed to generate transcript: {str(e)}")
            raise

    @app_commands.command(name="transcript")
    @app_commands.default_permissions(manage_messages=True)
    async def transcript_command(self, interaction: discord.Interaction):
        """Generate a transcript of the current ticket channel."""
        if not interaction.channel.name.startswith('ticket-'):
            await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            transcript_path = await self.generate_transcript(interaction.channel)

            # Create embed
            embed = discord.Embed(
                title="Ticket Transcript Generated",
                description=f"Transcript has been saved to: `{transcript_path}`",
                color=discord.Color.green()
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error generating transcript: {str(e)}")
            await interaction.followup.send(
                "Failed to generate transcript. Please try again later.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Transcript(bot))