"""
Database models for the Nexon Support System.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import enum
import uuid
import json
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, 
    ForeignKey, JSON, Float, Text, Table
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.engine import Engine
from sqlalchemy import event
from .types import JSONBType, UUIDType

Base = declarative_base()

# Enable SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    IN_PROGRESS = "IN_PROGRESS"
    ON_HOLD = "ON_HOLD"
    PENDING_STAFF = "PENDING_STAFF"

# Association table for category-SLA rules
category_sla_rules = Table(
    'category_sla_rules',
    Base.metadata,
    Column('category_id', Integer, ForeignKey('ticket_categories.id')),
    Column('sla_id', Integer, ForeignKey('sla_definitions.id'))
)

class TicketCategory(Base):
    """Ticket category configuration."""
    __tablename__ = "ticket_categories"

    id = Column(Integer, primary_key=True)
    guild_id = Column(String, ForeignKey("guilds.guild_id"))
    name = Column(String(100))
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    guild = relationship("Guild", back_populates="categories")
    tickets = relationship("Ticket", back_populates="category")
    sla_rules = relationship(
        "SLADefinition",
        secondary=category_sla_rules,
        back_populates="categories"
    )

class SLADefinition(Base):
    __tablename__ = "sla_definitions"

    id = Column(Integer, primary_key=True)
    guild_id = Column(String, ForeignKey("guilds.guild_id"))
    name = Column(String(100))
    response_time = Column(Integer)  # Minutes
    resolution_time = Column(Integer)  # Minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    guild = relationship("Guild", back_populates="sla_definitions")
    categories = relationship(
        "TicketCategory",
        secondary=category_sla_rules,
        back_populates="sla_rules"
    )

class Guild(Base):
    """Guild configuration and settings."""
    __tablename__ = "guilds"

    guild_id = Column(String, primary_key=True)
    name = Column(String(100))
    prefix = Column(String(10), default="!")
    maintenance_mode = Column(Boolean, default=False)
    maintenance_message = Column(Text, nullable=True)
    maintenance_start = Column(DateTime, nullable=True)
    maintenance_end = Column(DateTime, nullable=True)
    maintenance_roles = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tickets = relationship("Ticket", back_populates="guild")
    categories = relationship("TicketCategory", back_populates="guild")
    staff = relationship("StaffMember", back_populates="guild")
    sla_definitions = relationship("SLADefinition", back_populates="guild")
    settings = relationship("GuildSettings", back_populates="guild", uselist=False)

class Ticket(Base):
    """Ticket information and metadata."""
    __tablename__ = "tickets"

    ticket_db_id = Column(Integer, primary_key=True)
    ticket_id_display = Column(String(20))
    guild_id = Column(String, ForeignKey("guilds.guild_id"))
    channel_id = Column(String)
    creator_id = Column(String)
    claimed_by_id = Column(String, nullable=True)
    status = Column(String, default=TicketStatus.OPEN)
    category_db_id = Column(Integer, ForeignKey("ticket_categories.category_db_id"))
    opened_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    closure_reason_text = Column(String, nullable=True)
    closure_reasons_selected = Column(JSON, nullable=True)
    transcript_url = Column(String, nullable=True)
    last_staff_response_at = Column(DateTime, nullable=True)
    last_user_response_at = Column(DateTime, nullable=True)
    initial_input_data = Column(JSON, nullable=True)
    internal_notes = Column(JSON, nullable=True)
    linked_tickets = Column(JSON, nullable=True)
    anonymous_mode = Column(Boolean, default=False)
    sentiment_score_history = Column(JSON, nullable=True)
    ai_tags = Column(JSON, nullable=True)
    ai_summary = Column(String, nullable=True)
    scheduled_followup_at = Column(DateTime, nullable=True)
    closed_by_id = Column(String, nullable=True)

    # Relationships
    guild = relationship("Guild", back_populates="tickets")
    category = relationship("TicketCategory", back_populates="tickets")
    participants = relationship("TicketParticipant", back_populates="ticket")
    feedback = relationship("TicketFeedback", back_populates="ticket")

class TicketParticipant(Base):
    """Participants in a ticket."""
    __tablename__ = "ticket_participants"

    participant_id = Column(Integer, primary_key=True)
    ticket_db_id = Column(Integer, ForeignKey("tickets.ticket_db_id"))
    user_id = Column(String)
    role = Column(String)  # 'creator', 'added_staff', 'added_user'
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ticket = relationship("Ticket", back_populates="participants")

class TicketFeedback(Base):
    """User feedback for resolved tickets."""
    __tablename__ = "ticket_feedback"

    feedback_id = Column(Integer, primary_key=True)
    ticket_db_id = Column(Integer, ForeignKey("tickets.ticket_db_id"))
    user_id = Column(String)
    rating = Column(Integer)
    comments = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ticket = relationship("Ticket", back_populates="feedback")

class StaffPerformance(Base):
    """Staff performance metrics."""
    __tablename__ = "staff_performance"

    performance_id = Column(Integer, primary_key=True)
    guild_id = Column(String, ForeignKey("guilds.guild_id"))
    staff_id = Column(String)
    tickets_handled_count = Column(Integer, default=0)
    avg_response_time_seconds = Column(Float, nullable=True)
    avg_resolution_time_seconds = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    on_duty_status = Column(Boolean, default=False)
    on_duty_since = Column(DateTime, nullable=True)

    # Relationships
    guild = relationship("Guild", back_populates="staff_stats")

class AIConfig(Base):
    __tablename__ = "ai_config"
    
    config_id = Column(Integer, primary_key=True)
    guild_id = Column(String, ForeignKey("guilds.guild_id"))
    model_name = Column(String(100))
    enabled_features = Column(JSON)  # List of enabled AI features
    api_key = Column(String, nullable=True)
    settings = Column(JSON)  # Additional AI settings

    guild = relationship("Guild", back_populates="ai_config")

class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedule"
    
    schedule_id = Column(Integer, primary_key=True)
    guild_id = Column(String, ForeignKey("guilds.guild_id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    reason = Column(String)
    announcement_sent = Column(Boolean, default=False)

    guild = relationship("Guild", back_populates="maintenance_schedules")

class Task(Base):
    """Model for background tasks"""
    __tablename__ = "tasks"
    
    task_id = Column(Integer, primary_key=True)
    guild_id = Column(String, ForeignKey("guilds.guild_id"))
    name = Column(String(100))
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    params = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    is_recurring = Column(Boolean, default=False)
    interval_minutes = Column(Integer, nullable=True)

    # Relationships
    guild = relationship("Guild", back_populates="tasks")