"""
Script to initialize default knowledge base articles.
"""
import asyncio
import sys
from pathlib import Path
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.manager import DatabaseManager
from database.models import KnowledgeBase, Guild
from utils.logger import get_logger

logger = get_logger("init_kb")

DEFAULT_ARTICLES = [
    {
        "title": "Getting Started Guide",
        "content": """
# Getting Started Guide

Welcome to our support system! This guide will help you understand how to use our ticket system effectively.

## Creating a Ticket

1. Go to the support channel
2. Click the appropriate category button
3. Fill out the required information
4. Wait for a staff member to assist you

## Ticket Categories

- **General Support**: For general questions and assistance
- **Technical Support**: For technical issues and troubleshooting
- **Account Support**: For account-related issues
- **Bug Reports**: For reporting bugs and technical issues
- **Feature Requests**: For suggesting new features
- **User Reports**: For reporting user violations

## Best Practices

1. Be clear and concise in your description
2. Provide all requested information
3. Be patient while waiting for a response
4. Stay active in your ticket

## Response Times

Our team typically responds within:
- Critical issues: 30 minutes
- Technical issues: 1 hour
- General inquiries: 2 hours

## Need More Help?

Don't hesitate to ask for clarification if you need it!
        """.strip(),
        "category": "Getting Started",
        "keywords": ["start", "guide", "help", "introduction", "tutorial", "new"]
    },
    {
        "title": "Common Technical Issues",
        "content": """
# Common Technical Issues

This guide covers frequently encountered technical issues and their solutions.

## Connection Issues

1. Check your internet connection
2. Restart your device
3. Clear your cache
4. Try a different browser

## Account Access

1. Reset your password
2. Check your email for verification
3. Enable/disable 2FA
4. Contact support if issues persist

## Application Errors

1. Update to the latest version
2. Clear application data
3. Reinstall if necessary
4. Check system requirements

## Performance Issues

1. Check system resources
2. Close unnecessary applications
3. Update your drivers
4. Verify minimum requirements
        """.strip(),
        "category": "Troubleshooting",
        "keywords": ["technical", "issues", "problems", "errors", "troubleshoot", "fix"]
    },
    {
        "title": "Security Best Practices",
        "content": """
# Security Best Practices

Keep your account and data secure by following these guidelines.

## Password Security

1. Use strong, unique passwords
2. Enable two-factor authentication
3. Never share your password
4. Change passwords regularly

## Account Protection

1. Monitor account activity
2. Log out from shared devices
3. Keep email address updated
4. Review connected applications

## Reporting Security Issues

1. Contact support immediately
2. Document suspicious activity
3. Change passwords if compromised
4. Enable additional security features

## Privacy Tips

1. Review privacy settings
2. Be careful with personal information
3. Verify email communications
4. Report suspicious behavior
        """.strip(),
        "category": "Security",
        "keywords": ["security", "safety", "protection", "privacy", "password", "2fa"]
    },
    {
        "title": "Frequently Asked Questions",
        "content": """
# Frequently Asked Questions

Common questions and their answers.

## General Questions

**Q: How do I create a ticket?**
A: Click the appropriate category button in the support channel and fill out the form.

**Q: How long until I get a response?**
A: Response times vary by category, typically between 30 minutes to 2 hours.

**Q: Can I have multiple tickets?**
A: Yes, but we recommend focusing on one issue at a time.

## Technical Questions

**Q: What information should I include in a bug report?**
A: Include steps to reproduce, expected behavior, actual behavior, and any error messages.

**Q: How do I update my settings?**
A: Navigate to the settings panel and select the options you want to modify.

## Account Questions

**Q: How do I reset my password?**
A: Use the password reset option on the login page.

**Q: How do I enable 2FA?**
A: Go to account settings and look for the security section.
        """.strip(),
        "category": "FAQ",
        "keywords": ["faq", "questions", "answers", "help", "common", "general"]
    }
]

async def init_kb(guild_id: str = None):
    """Initialize default knowledge base articles for specified guild or all guilds"""
    db = DatabaseManager()
    
    try:
        await db.initialize_database()
        
        async with db.Session as session:
            # Get target guilds
            if guild_id:
                guilds = [await session.get(Guild, guild_id)]
                if not guilds[0]:
                    logger.error(f"Guild {guild_id} not found in database.")
                    return
            else:
                result = await session.execute("SELECT * FROM guilds")
                guilds = result.all()
                
                if not guilds:
                    logger.warning("No guilds found in database.")
                    return

            for guild in guilds:
                logger.info(f"Processing guild: {guild.guild_id}")
                
                # Check existing articles
                result = await session.execute(
                    "SELECT COUNT(*) FROM knowledge_base WHERE guild_id = :guild_id",
                    {"guild_id": guild.guild_id}
                )
                count = result.scalar()
                
                if count > 0:
                    logger.info(f"Guild {guild.guild_id} already has {count} KB articles.")
                    continue

                # Create default articles
                for article_data in DEFAULT_ARTICLES:
                    article = KnowledgeBase(
                        article_id=uuid.uuid4(),
                        guild_id=guild.guild_id,
                        title=article_data["title"],
                        content=article_data["content"],
                        category=article_data["category"],
                        keywords=article_data["keywords"],
                        created_by="SYSTEM",
                        created_at=datetime.utcnow()
                    )
                    session.add(article)
                
                await session.commit()
                logger.info(f"✨ Created {len(DEFAULT_ARTICLES)} KB articles for guild {guild.guild_id}")

        logger.info("✨ Default knowledge base articles initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing knowledge base: {e}")
        raise
    finally:
        await db.close()

def main():
    """Main entry point"""
    try:
        # Get guild ID from command line if provided
        guild_id = sys.argv[1] if len(sys.argv) > 1 else None
        asyncio.run(init_kb(guild_id))
    except KeyboardInterrupt:
        logger.info("Knowledge base initialization interrupted.")
    except Exception as e:
        logger.error(f"Failed to initialize knowledge base: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 