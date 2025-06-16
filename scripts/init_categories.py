"""
Script to initialize default ticket categories and SLA definitions.
"""
import asyncio
import sys
from pathlib import Path
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.manager import DatabaseManager
from database.models import TicketCategory, Guild, SLADefinition
from utils.logger import get_logger

logger = get_logger("init_categories")

DEFAULT_CATEGORIES = [
    {
        "name": "General Support",
        "description": "General questions and assistance",
        "emoji": "❓",
        "modal_fields": [
            {
                "id": "subject",
                "label": "Subject",
                "style": "short",
                "required": True,
                "placeholder": "Brief description of your issue"
            },
            {
                "id": "description",
                "label": "Description",
                "style": "paragraph",
                "required": True,
                "placeholder": "Please provide details about your issue"
            }
        ],
        "initial_message_template": (
            "Thank you for creating a ticket! A staff member will assist you shortly.\n\n"
            "**Category:** General Support\n"
            "**Created by:** {user_mention}\n"
            "**Ticket ID:** {ticket_id}\n\n"
            "Please provide any additional information that might help us assist you better."
        ),
        "sla": {
            "response": 120,    # 2 hours
            "resolution": 1440  # 24 hours
        }
    },
    {
        "name": "Technical Support",
        "description": "Technical issues and troubleshooting",
        "emoji": "🔧",
        "modal_fields": [
            {
                "id": "subject",
                "label": "Subject",
                "style": "short",
                "required": True,
                "placeholder": "Brief description of the technical issue"
            },
            {
                "id": "platform",
                "label": "Platform/Device",
                "style": "short",
                "required": True,
                "placeholder": "OS/Device you're using (e.g., Windows 10, iPhone 13)"
            },
            {
                "id": "description",
                "label": "Description",
                "style": "paragraph",
                "required": True,
                "placeholder": "Please describe the technical issue in detail"
            },
            {
                "id": "steps",
                "label": "Steps to Reproduce",
                "style": "paragraph",
                "required": False,
                "placeholder": "Steps to reproduce the issue (if applicable)"
            }
        ],
        "initial_message_template": (
            "Thank you for reporting this technical issue! Our support team will assist you shortly.\n\n"
            "**Category:** Technical Support\n"
            "**Created by:** {user_mention}\n"
            "**Ticket ID:** {ticket_id}\n\n"
            "While you wait:\n"
            "1. Check if restarting the application helps\n"
            "2. Make sure you're using the latest version\n"
            "3. Have any error messages ready to share"
        ),
        "sla": {
            "response": 60,     # 1 hour
            "resolution": 720   # 12 hours
        }
    },
    {
        "name": "Account Support",
        "description": "Account-related issues and requests",
        "emoji": "👤",
        "modal_fields": [
            {
                "id": "subject",
                "label": "Subject",
                "style": "short",
                "required": True,
                "placeholder": "Brief description of your account issue"
            },
            {
                "id": "account_id",
                "label": "Account ID/Username",
                "style": "short",
                "required": True,
                "placeholder": "Your account identifier"
            },
            {
                "id": "description",
                "label": "Description",
                "style": "paragraph",
                "required": True,
                "placeholder": "Please describe your account issue in detail"
            },
            {
                "id": "verification",
                "label": "Verification Info",
                "style": "paragraph",
                "required": False,
                "placeholder": "Any additional info to verify account ownership"
            }
        ],
        "initial_message_template": (
            "Thank you for contacting account support! We'll help you shortly.\n\n"
            "**Category:** Account Support\n"
            "**Created by:** {user_mention}\n"
            "**Ticket ID:** {ticket_id}\n\n"
            "🔒 For your security, never share your password or 2FA codes."
        ),
        "sla": {
            "response": 30,     # 30 minutes
            "resolution": 360   # 6 hours
        }
    },
    {
        "name": "Report User",
        "description": "Report violations or concerning behavior",
        "emoji": "🚨",
        "modal_fields": [
            {
                "id": "subject",
                "label": "Subject",
                "style": "short",
                "required": True,
                "placeholder": "Brief description of the report"
            },
            {
                "id": "reported_user",
                "label": "Reported User",
                "style": "short",
                "required": True,
                "placeholder": "ID or Username of reported user"
            },
            {
                "id": "description",
                "label": "Description",
                "style": "paragraph",
                "required": True,
                "placeholder": "Please provide details about the incident"
            },
            {
                "id": "evidence",
                "label": "Evidence",
                "style": "paragraph",
                "required": False,
                "placeholder": "Links to screenshots or other evidence"
            }
        ],
        "initial_message_template": (
            "Thank you for submitting a report. Our moderation team will review it shortly.\n\n"
            "**Category:** User Report\n"
            "**Created by:** {user_mention}\n"
            "**Ticket ID:** {ticket_id}\n\n"
            "🛡️ All reports are handled confidentially and investigated thoroughly."
        ),
        "sla": {
            "response": 30,     # 30 minutes
            "resolution": 240   # 4 hours
        }
    },
    {
        "name": "Bug Report",
        "description": "Report bugs and technical issues",
        "emoji": "🐛",
        "modal_fields": [
            {
                "id": "subject",
                "label": "Bug Title",
                "style": "short",
                "required": True,
                "placeholder": "Brief description of the bug"
            },
            {
                "id": "version",
                "label": "Version",
                "style": "short",
                "required": True,
                "placeholder": "Version where bug occurs"
            },
            {
                "id": "description",
                "label": "Description",
                "style": "paragraph",
                "required": True,
                "placeholder": "Please describe the bug in detail"
            },
            {
                "id": "steps",
                "label": "Steps to Reproduce",
                "style": "paragraph",
                "required": True,
                "placeholder": "1. Go to...\n2. Click on...\n3. Observe..."
            },
            {
                "id": "expected",
                "label": "Expected Behavior",
                "style": "paragraph",
                "required": True,
                "placeholder": "What should happen?"
            }
        ],
        "initial_message_template": (
            "Thank you for reporting this bug! Our development team will investigate.\n\n"
            "**Category:** Bug Report\n"
            "**Created by:** {user_mention}\n"
            "**Ticket ID:** {ticket_id}\n\n"
            "🔍 We'll investigate and keep you updated on our findings."
        ),
        "sla": {
            "response": 120,    # 2 hours
            "resolution": 2880  # 48 hours
        }
    },
    {
        "name": "Feature Request",
        "description": "Suggest new features or improvements",
        "emoji": "💡",
        "modal_fields": [
            {
                "id": "subject",
                "label": "Feature Name",
                "style": "short",
                "required": True,
                "placeholder": "Brief name for your feature suggestion"
            },
            {
                "id": "description",
                "label": "Description",
                "style": "paragraph",
                "required": True,
                "placeholder": "Please describe the feature you'd like to suggest"
            },
            {
                "id": "use_case",
                "label": "Use Case",
                "style": "paragraph",
                "required": True,
                "placeholder": "How and when would this feature be used?"
            },
            {
                "id": "benefit",
                "label": "Benefit",
                "style": "paragraph",
                "required": True,
                "placeholder": "How would this feature benefit users?"
            }
        ],
        "initial_message_template": (
            "Thank you for your feature suggestion! We'll review it carefully.\n\n"
            "**Category:** Feature Request\n"
            "**Created by:** {user_mention}\n"
            "**Ticket ID:** {ticket_id}\n\n"
            "💭 We appreciate your input in making our service better!"
        ),
        "sla": {
            "response": 240,    # 4 hours
            "resolution": 4320  # 72 hours
        }
    }
]

async def init_categories(guild_id: str = None):
    """Initialize default ticket categories for specified guild or all guilds"""
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
                
                # Check existing categories
                result = await session.execute(
                    "SELECT COUNT(*) FROM ticket_categories WHERE guild_id = :guild_id",
                    {"guild_id": guild.guild_id}
                )
                count = result.scalar()
                
                if count > 0:
                    logger.info(f"Guild {guild.guild_id} already has {count} categories.")
                    continue

                # Create default categories and SLAs
                for cat_data in DEFAULT_CATEGORIES:
                    # Create category
                    category = TicketCategory(
                        category_db_id=uuid.uuid4(),
                        guild_id=guild.guild_id,
                        name=cat_data["name"],
                        description=cat_data["description"],
                        emoji=cat_data["emoji"],
                        modal_fields=cat_data["modal_fields"],
                        initial_message_template=cat_data["initial_message_template"]
                    )
                    session.add(category)
                    await session.flush()  # Get the ID
                    
                    # Create SLA definition
                    sla = SLADefinition(
                        sla_id=uuid.uuid4(),
                        guild_id=guild.guild_id,
                        category_db_id=category.category_db_id,
                        response_sla_minutes=cat_data["sla"]["response"],
                        resolution_sla_minutes=cat_data["sla"]["resolution"]
                    )
                    session.add(sla)
                
                await session.commit()
                logger.info(f"✨ Created {len(DEFAULT_CATEGORIES)} categories for guild {guild.guild_id}")

        logger.info("✨ Default categories initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing categories: {e}")
        raise
    finally:
        await db.close()

def main():
    """Main entry point"""
    try:
        # Get guild ID from command line if provided
        guild_id = sys.argv[1] if len(sys.argv) > 1 else None
        asyncio.run(init_categories(guild_id))
    except KeyboardInterrupt:
        logger.info("Category initialization interrupted.")
    except Exception as e:
        logger.error(f"Failed to initialize categories: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 