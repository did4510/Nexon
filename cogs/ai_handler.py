"""
AI handler cog.
Handles AI features like sentiment analysis, tag generation, and auto-responses.
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List, Dict, Any
from datetime import datetime

from database.models import Guild, Ticket, AIConfig
from database.manager import db_manager
from utils.embeds import create_success_embed, create_error_embed, create_info_embed
from utils.ai import analyze_sentiment, generate_ticket_tags, analyze_common_issues
from utils.constants import *
from utils.logger import logger

class AIHandlerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ai")
    @app_commands.checks.has_permissions(administrator=True)
    async def manage_ai(
        self,
        interaction: discord.Interaction,
        action: str,
        feature: Optional[str] = None,
        value: Optional[str] = None
    ):
        """Manage AI features."""
        await interaction.response.defer()

        try:
            action = action.lower()

            async with db_manager.get_session() as session:
                # Get or create AI config
                config = await session.query(AIConfig)\
                    .filter(AIConfig.guild_id == str(interaction.guild_id))\
                    .first()

                if not config:
                    config = AIConfig(guild_id=str(interaction.guild_id))
                    session.add(config)

                if action == "enable":
                    if not feature:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Missing Feature",
                                "Please specify which feature to enable."
                            )
                        )
                        return

                    feature = feature.lower()

                    if feature == "sentiment":
                        config.sentiment_analysis_enabled = True
                        message = "Sentiment analysis enabled"
                    elif feature == "tags":
                        config.tag_generation_enabled = True
                        message = "Automatic tag generation enabled"
                    elif feature == "suggestions":
                        config.kb_suggestions_enabled = True
                        message = "Knowledge base suggestions enabled"
                    elif feature == "autoresponse":
                        config.auto_responses_enabled = True
                        message = "Automatic responses enabled"
                    else:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Invalid Feature",
                                "Valid features are: sentiment, tags, suggestions, autoresponse"
                            )
                        )
                        return

                    await session.commit()

                    await interaction.followup.send(
                        embed=create_success_embed(
                            "Feature Enabled",
                            message
                        )
                    )

                elif action == "disable":
                    if not feature:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Missing Feature",
                                "Please specify which feature to disable."
                            )
                        )
                        return

                    feature = feature.lower()

                    if feature == "sentiment":
                        config.sentiment_analysis_enabled = False
                        message = "Sentiment analysis disabled"
                    elif feature == "tags":
                        config.tag_generation_enabled = False
                        message = "Automatic tag generation disabled"
                    elif feature == "suggestions":
                        config.kb_suggestions_enabled = False
                        message = "Knowledge base suggestions disabled"
                    elif feature == "autoresponse":
                        config.auto_responses_enabled = False
                        message = "Automatic responses disabled"
                    else:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Invalid Feature",
                                "Valid features are: sentiment, tags, suggestions, autoresponse"
                            )
                        )
                        return

                    await session.commit()

                    await interaction.followup.send(
                        embed=create_success_embed(
                            "Feature Disabled",
                            message
                        )
                    )

                elif action == "config":
                    if not all([feature, value]):
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Missing Information",
                                "Please specify both feature and value."
                            )
                        )
                        return

                    feature = feature.lower()

                    if feature == "threshold":
                        try:
                            threshold = float(value)
                            if not 0 <= threshold <= 1:
                                raise ValueError
                            config.sentiment_threshold = threshold
                            message = f"Sentiment threshold set to {threshold}"
                        except ValueError:
                            await interaction.followup.send(
                                embed=create_error_embed(
                                    "Invalid Value",
                                    "Threshold must be a number between 0 and 1"
                                )
                            )
                            return
                    elif feature == "model":
                        config.ai_model = value
                        message = f"AI model set to {value}"
                    elif feature == "api_key":
                        config.api_key = value
                        message = "API key updated"
                    else:
                        await interaction.followup.send(
                            embed=create_error_embed(
                                "Invalid Feature",
                                "Valid features are: threshold, model, api_key"
                            )
                        )
                        return

                    await session.commit()

                    await interaction.followup.send(
                        embed=create_success_embed(
                            "Configuration Updated",
                            message
                        )
                    )

                elif action == "status":
                    # Create status embed
                    embed = create_info_embed(
                        "AI Features Status",
                        "Current status of AI features:"
                    )

                    features = {
                        "Sentiment Analysis": config.sentiment_analysis_enabled,
                        "Tag Generation": config.tag_generation_enabled,
                        "KB Suggestions": config.kb_suggestions_enabled,
                        "Auto Responses": config.auto_responses_enabled
                    }

                    status_text = "\n".join(
                        f"{name}: {'✅ Enabled' if enabled else '❌ Disabled'}"
                        for name, enabled in features.items()
                    )

                    embed.add_field(
                        name="Features",
                        value=status_text,
                        inline=False
                    )

                    # Add configuration
                    config_text = [
                        f"Sentiment Threshold: {config.sentiment_threshold or 'Not set'}",
                        f"AI Model: {config.ai_model or 'Default'}",
                        f"API Key: {'Configured' if config.api_key else 'Not set'}"
                    ]

                    embed.add_field(
                        name="Configuration",
                        value="\n".join(config_text),
                        inline=False
                    )

                    await interaction.followup.send(embed=embed)

                else:
                    await interaction.followup.send(
                        embed=create_error_embed(
                            "Invalid Action",
                            "Valid actions are: enable, disable, config, status"
                        )
                    )

        except Exception as e:
            logger.error(f"Error in AI management: {e}")
            await interaction.followup.send(
                embed=create_error_embed(
                    "AI Management Error",
                    f"An error occurred: {str(e)}"
                )
            )

    @app_commands.command(name="analyze")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def analyze_ticket(
        self,
        interaction: discord.Interaction,
        ticket_id: str
    ):
        """Analyze a ticket using AI features."""
        await interaction.response.defer()

        try:
            async with db_manager.get_session() as session:
                # Get ticket
                ticket = await session.query(Ticket)\
                    .filter(
                        Ticket.guild_id == str(interaction.guild_id),
                        Ticket.ticket_id == ticket_id
                    ).first()

                if not ticket:
                    await interaction.followup.send(
                        embed=create_error_embed(
                            "Not Found",
                            f"No ticket found with ID: {ticket_id}"
                        )
                    )
                    return

                # Get AI config
                config = await session.query(AIConfig)\
                    .filter(AIConfig.guild_id == str(interaction.guild_id))\
                    .first()

                if not config:
                    await interaction.followup.send(
                        embed=create_error_embed(
                            "AI Not Configured",
                            "Please configure AI features first using /ai config"
                        )
                    )
                    return

                # Create analysis embed
                embed = create_info_embed(
                    f"Ticket Analysis - #{ticket_id}",
                    "Here's what I found:"
                )

                # Sentiment analysis
                if config.sentiment_analysis_enabled:
                    sentiment = await analyze_sentiment(ticket.content)
                    embed.add_field(
                        name="Sentiment Analysis",
                        value=f"Score: {sentiment:.2%} positive",
                        inline=False
                    )

                # Tag generation
                if config.tag_generation_enabled:
                    tags = await generate_ticket_tags(ticket.content)
                    embed.add_field(
                        name="Generated Tags",
                        value=", ".join(tags) if tags else "No tags generated",
                        inline=False
                    )

                # Common issues analysis
                issues = await analyze_common_issues(ticket.content)
                if issues:
                    embed.add_field(
                        name="Identified Issues",
                        value="\n".join(f"• {issue}" for issue in issues),
                        inline=False
                    )

                await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error analyzing ticket: {e}")
            await interaction.followup.send(
                embed=create_error_embed(
                    "Analysis Error",
                    f"An error occurred: {str(e)}"
                )
            )

async def setup(bot):
    await bot.add_cog(AIHandlerCog(bot))