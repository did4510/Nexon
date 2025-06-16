import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from .models import Base
from utils.logger import logger

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self._session_maker = None
        self.initialized = False
        
        # Create data directory
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        self.db_url = "sqlite+aiosqlite:///data/bot.db"

    async def initialize_database(self):
        """Initialize database connection and create tables"""
        if not self.initialized:
            try:
                self.engine = create_async_engine(
                    self.db_url,
                    echo=False,
                    poolclass=NullPool
                )
                
                self._session_maker = async_sessionmaker(
                    self.engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
                
                async with self.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                
                self.initialized = True
                logger.info("✨ Database initialized successfully")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize database: {e}")
                raise

    async def get_session(self) -> AsyncSession:
        """Get a new database session"""
        if not self.initialized:
            await self.initialize_database()
        return self._session_maker()

    @asynccontextmanager
    async def session(self):
        """Get a database session as an async context manager"""
        if not self.initialized:
            await self.initialize_database()
            
        session = await self.get_session()
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            self.initialized = False

# Create global instance
db_manager = DatabaseManager()