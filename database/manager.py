"""
Database manager for handling database connections and operations.
"""
import os
from pathlib import Path
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy import text
from .models import Base

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        """Initialize the database manager."""
        self.logger = logging.getLogger("database")
        self._engine = None
        self._session_factory = None
        self._initialized = False
        
        # Get database URL from environment or use default SQLite
        self.db_url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///data/nexon.db')
        
        # Ensure data directory exists for SQLite
        if 'sqlite' in self.db_url:
            data_dir = Path('data')
            data_dir.mkdir(exist_ok=True)
    
    async def initialize_database(self):
        """Initialize the database connection and create tables."""
        try:
            # Create async engine
            self._engine = create_async_engine(
                self.db_url,
                poolclass=AsyncAdaptedQueuePool,
                pool_size=20,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                echo=False
            )
            
            # Create session factory
            self._session_factory = sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create all tables
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self._initialized = True
            self.logger.info("Successfully initialized database connection")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    @property
    def session(self) -> AsyncSession:
        """Get a new database session."""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        return self._session_factory()

    @property
    def Session(self):
        """Get the session factory for compatibility with existing code."""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        return self._session_factory

    async def get_session(self) -> AsyncSession:
        """Get a new database session asynchronously."""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        return self._session_factory()
    
    async def close(self):
        """Close all database connections."""
        if self._engine:
            await self._engine.dispose()
            self.logger.info("Database connection closed")
    
    async def get_guild_settings(self, guild_id: str) -> dict:
        """Get settings for a specific guild."""
        async with self.session as session:
            result = await session.execute(
                text("SELECT * FROM guilds WHERE guild_id = :guild_id"),
                {"guild_id": guild_id}
            )
            settings = result.mappings().first()
            return dict(settings) if settings else None
    
    async def update_guild_settings(self, guild_id: str, settings: dict) -> bool:
        """Update settings for a specific guild."""
        try:
            async with self.session as session:
                # Build the update query dynamically based on provided settings
                update_fields = ", ".join([f"{k} = :{k}" for k in settings.keys()])
                query = text(f"UPDATE guilds SET {update_fields} WHERE guild_id = :guild_id")
                
                # Add guild_id to parameters
                params = {**settings, "guild_id": guild_id}
                
                await session.execute(query, params)
                await session.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to update guild settings: {e}")
            return False
    
    async def create_ticket(self, ticket_data: dict) -> str:
        """Create a new ticket and return its ID."""
        try:
            async with self.session as session:
                # Get next ticket counter for the guild
                result = await session.execute(
                    text("UPDATE guilds SET ticket_counter = ticket_counter + 1 WHERE guild_id = :guild_id RETURNING ticket_counter"),
                    {"guild_id": ticket_data["guild_id"]}
                )
                counter = result.scalar()
                
                # Format ticket ID
                ticket_data["ticket_id_display"] = f"#{counter:04d}"
                
                # Insert ticket
                columns = ", ".join(ticket_data.keys())
                values = ", ".join(f":{k}" for k in ticket_data.keys())
                query = text(f"INSERT INTO tickets ({columns}) VALUES ({values}) RETURNING ticket_db_id")
                
                result = await session.execute(query, ticket_data)
                ticket_db_id = result.scalar()
                
                await session.commit()
                return ticket_db_id
        except Exception as e:
            self.logger.error(f"Failed to create ticket: {e}")
            raise
    
    async def get_ticket(self, ticket_db_id: str) -> dict:
        """Get ticket information by ID."""
        async with self.session as session:
            result = await session.execute(
                text("SELECT * FROM tickets WHERE ticket_db_id = :ticket_db_id"),
                {"ticket_db_id": ticket_db_id}
            )
            ticket = result.mappings().first()
            return dict(ticket) if ticket else None
    
    async def update_ticket(self, ticket_db_id: str, update_data: dict) -> bool:
        """Update ticket information."""
        try:
            async with self.session as session:
                update_fields = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
                query = text(f"UPDATE tickets SET {update_fields} WHERE ticket_db_id = :ticket_db_id")
                
                params = {**update_data, "ticket_db_id": ticket_db_id}
                await session.execute(query, params)
                await session.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to update ticket: {e}")
            return False
    
    async def get_active_tickets(self, guild_id: str) -> list:
        """Get all active tickets for a guild."""
        async with self.session as session:
            result = await session.execute(
                text("SELECT * FROM tickets WHERE guild_id = :guild_id AND status != 'closed' ORDER BY opened_at DESC"),
                {"guild_id": guild_id}
            )
            return [dict(row) for row in result.mappings()]
    
    async def get_staff_tickets(self, staff_id: str) -> list:
        """Get all tickets claimed by a staff member."""
        async with self.session as session:
            result = await session.execute(
                text("SELECT * FROM tickets WHERE claimed_by_id = :staff_id ORDER BY opened_at DESC"),
                {"staff_id": staff_id}
            )
            return [dict(row) for row in result.mappings()]
    
    async def add_ticket_participant(self, ticket_db_id: str, user_id: str, role: str) -> bool:
        """Add a participant to a ticket."""
        try:
            async with self.session as session:
                await session.execute(
                    text("""
                        INSERT INTO ticket_participants (ticket_db_id, user_id, role)
                        VALUES (:ticket_db_id, :user_id, :role)
                    """),
                    {"ticket_db_id": ticket_db_id, "user_id": user_id, "role": role}
                )
                await session.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to add ticket participant: {e}")
            return False
    
    async def get_ticket_participants(self, ticket_db_id: str) -> list:
        """Get all participants of a ticket."""
        async with self.session as session:
            result = await session.execute(
                text("SELECT * FROM ticket_participants WHERE ticket_db_id = :ticket_db_id"),
                {"ticket_db_id": ticket_db_id}
            )
            return [dict(row) for row in result.mappings()]
    
    async def add_internal_note(self, ticket_db_id: str, staff_id: str, note: str) -> bool:
        """Add an internal note to a ticket."""
        try:
            async with self.session as session:
                await session.execute(
                    text("""
                        INSERT INTO ticket_notes (ticket_db_id, staff_id, note, created_at)
                        VALUES (:ticket_db_id, :staff_id, :note, CURRENT_TIMESTAMP)
                    """),
                    {"ticket_db_id": ticket_db_id, "staff_id": staff_id, "note": note}
                )
                await session.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to add internal note: {e}")
            return False
    
    async def add_ticket_feedback(self, ticket_db_id: str, user_id: str, rating: int, comments: str = None) -> bool:
        """Add feedback for a ticket."""
        try:
            async with self.session as session:
                await session.execute(
                    text("""
                        INSERT INTO ticket_feedback (ticket_db_id, user_id, rating, comments, submitted_at)
                        VALUES (:ticket_db_id, :user_id, :rating, :comments, CURRENT_TIMESTAMP)
                    """),
                    {"ticket_db_id": ticket_db_id, "user_id": user_id, "rating": rating, "comments": comments}
                )
                await session.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to add ticket feedback: {e}")
            return False
    
    async def update_staff_performance(self, guild_id: str, staff_id: str, metrics: dict) -> bool:
        """Update staff performance metrics."""
        try:
            async with self.session as session:
                update_fields = ", ".join([f"{k} = :{k}" for k in metrics.keys()])
                query = text(f"""
                    INSERT INTO staff_performance (guild_id, staff_id, {', '.join(metrics.keys())})
                    VALUES (:guild_id, :staff_id, {', '.join(f':{k}' for k in metrics.keys())})
                    ON CONFLICT (guild_id, staff_id) DO UPDATE SET {update_fields}
                """)
                
                params = {**metrics, "guild_id": guild_id, "staff_id": staff_id}
                await session.execute(query, params)
                await session.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to update staff performance: {e}")
            return False

# Create a global instance of the database manager
db_manager = DatabaseManager()