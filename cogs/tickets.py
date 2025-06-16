import logging
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path
from datetime import datetime
import asyncio
from sqlalchemy import select, update, func
import os
import jinja2
import aiofiles

from utils.logger import logger
from utils.emojis import TICKET, STATUS

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.models import Ticket, TicketCategory, Guild, TicketParticipant, TicketFeedback, StaffPerformance
from database import db_manager
from utils.constants import *
from utils.transcript import transcript_generator
from utils.embeds import create_success_embed, create_error_embed, create_ticket_embed
from utils.enums import TicketStatus
from utils.views import (
    SupportPanelView,
    TicketActionsView,
    TicketCreationModal,
    TicketCloseModal,
    InternalNoteModal
)
from utils.ai import analyze_sentiment, generate_ticket_tags
from utils.sla import check_sla_status, get_sla_alert_level

class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def ticket(self, interaction: discord.Interaction):
        """Create a new support ticket"""
        try:
            async with self.bot.db.session() as session:
                # Get guild settings
                guild_settings = await session.get(Guild, str(interaction.guild_id))
                if not guild_settings:
                    await interaction.response.send_message(
                        "This server hasn't been configured yet. Please ask an administrator to set up the ticket system.",
                        ephemeral=True
                    )
                    return

                # Get available categories
                stmt = select(TicketCategory).where(
                    TicketCategory.guild_id == str(interaction.guild_id)
                )
                result = await session.execute(stmt)
                categories = result.scalars().all()

                if not categories:
                    await interaction.response.send_message(
                        "No ticket categories have been set up yet. Please ask an administrator to configure ticket categories.",
                        ephemeral=True
                    )
                    return

                # Show category selection
                view = CategorySelectView(self.bot, categories)
                await interaction.response.send_message(
                    "Please select a ticket category:",
                    view=view,
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            await interaction.response.send_message(
                f"{STATUS['error']} An error occurred while creating your ticket.",
                ephemeral=True
            )

class CategorySelectView(discord.ui.View):
    def __init__(self, bot, categories):
        super().__init__(timeout=300)
        self.bot = bot
        self.add_category_buttons(categories)

    def add_category_buttons(self, categories):
        for category in categories:
            button = discord.ui.Button(
                label=category.name,
                emoji=category.emoji,
                style=discord.ButtonStyle.primary,
                custom_id=f"category_{category.category_db_id}"
            )
            button.callback = self.category_button_callback
            self.add_item(button)

        # Add anonymous ticket option if enabled
        anonymous_button = discord.ui.Button(
            label="Anonymous Ticket",
            emoji="🕵️",
            style=discord.ButtonStyle.secondary,
            custom_id="anonymous_ticket"
        )
        anonymous_button.callback = self.anonymous_button_callback
        self.add_item(anonymous_button)

    async def category_button_callback(self, interaction: discord.Interaction):
        try:
            category_id = interaction.custom_id.split("_")[1]
            async with db_manager.session() as session:
                category = await session.get(TicketCategory, str(category_id))
                if not category:
                    await interaction.response.send_message(
                        "Category not found.",
                        ephemeral=True
                    )
                    return

                # Create modal with category-specific fields
                modal = TicketCreationModal(category)
                await interaction.response.send_modal(modal)
        except Exception as e:
            logger.error(f"Error in category button callback: {e}")
            await interaction.response.send_message(
                "An error occurred while processing your selection. Please try again.",
                ephemeral=True
            )

    async def anonymous_button_callback(self, interaction: discord.Interaction):
        async with db_manager.session() as session:
            guild_settings = await session.get(Guild, str(interaction.guild_id))
            if not guild_settings or not guild_settings.allow_anonymous_tickets:
                await interaction.response.send_message(
                    "Anonymous tickets are not enabled on this server.",
                    ephemeral=True
                )
                return

            # Show category selection for anonymous ticket
            stmt = select(TicketCategory).where(
                TicketCategory.guild_id == str(interaction.guild_id),
                TicketCategory.allow_anonymous == True
            )
            result = await session.execute(stmt)
            categories = result.scalars().all()

            if not categories:
                await interaction.response.send_message(
                    "No categories available for anonymous tickets.",
                    ephemeral=True
                )
                return

            view = CategorySelectView(self.bot, categories)
            await interaction.response.send_message(
                "Select a category for your anonymous ticket:",
                view=view,
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(TicketsCog(bot))