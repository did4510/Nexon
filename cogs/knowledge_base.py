import logging
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List
from sqlalchemy import select
from utils.logger import logger
from database.models import KnowledgeBase

class KnowledgeBaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kb")
    @app_commands.describe(query="The article to search for")
    async def search_kb(self, interaction: discord.Interaction, query: str):
        """Search the knowledge base"""
        try:
            async with self.bot.db.session() as session:
                # Search for articles
                stmt = select(KnowledgeBase).where(
                    KnowledgeBase.guild_id == str(interaction.guild_id),
                    KnowledgeBase.title.ilike(f"%{query}%")
                )
                result = await session.execute(stmt)
                articles = result.scalars().all()

                if not articles:
                    await interaction.response.send_message(
                        f"{self.bot.emojis['error']} No articles found matching your query.",
                        ephemeral=True
                    )
                    return

                # Create embed with results
                embed = discord.Embed(
                    title="📚 Knowledge Base Results",
                    description=f"Found {len(articles)} articles matching '{query}'",
                    color=discord.Color.blue()
                )
                
                for article in articles[:5]:  # Show top 5 results
                    embed.add_field(
                        name=article.title,
                        value=f"{article.content[:100]}...",
                        inline=False
                    )

                await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            await interaction.response.send_message(
                f"{self.bot.emojis['error']} An error occurred while searching.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(KnowledgeBaseCog(bot))