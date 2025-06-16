"""
Database package initialization.
"""
from .models import Base
from .manager import DatabaseManager, db_manager

# Create a global database manager instance
db_manager = DatabaseManager()

__all__ = ['Base', 'DatabaseManager', 'db_manager']
