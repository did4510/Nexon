"""
Script to initialize the database.
"""
import asyncio
import os
from pathlib import Path
from database.connection import db_manager
from database.models import Guild, TicketCategory, SLADefinition
from utils.logger import logger

async def create_default_data(session):
    """Create default data for testing"""
    try:
        # Create default SLA definitions
        default_sla = SLADefinition(
            name="Standard SLA",
            response_time=30,  # 30 minutes
            resolution_time=1440  # 24 hours
        )
        session.add(default_sla)
        
        # Create default ticket categories
        default_category = TicketCategory(
            name="General Support",
            description="General support inquiries"
        )
        default_category.sla_rules.append(default_sla)
        session.add(default_category)
        
        await session.commit()
        logger.info("✅ Created default data")
        
    except Exception as e:
        logger.error(f"❌ Error creating default data: {e}")
        await session.rollback()
        raise

async def init_database():
    """Initialize the database"""
    try:
        # Ensure data directory exists
        Path("data").mkdir(exist_ok=True)
        
        # Initialize database
        await db_manager.initialize_database()
        
        # Create default data
        async with db_manager.session() as session:
            await create_default_data(session)
            
        logger.info("✅ Database initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise
    finally:
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(init_database())