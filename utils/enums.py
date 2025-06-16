"""
Enums used throughout the bot.
"""
from enum import Enum, auto

class TicketStatus(str, Enum):
    """Enum for ticket statuses"""
    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"
    ON_HOLD = "on_hold"
    RESOLVED = "resolved"
    ARCHIVED = "archived"
    DELETED = "deleted"

class StaffRole(str, Enum):
    """Enum for staff roles"""
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    TRAINEE = "trainee"

class TicketType(str, Enum):
    """Enum for ticket types"""
    SUPPORT = "support"
    REPORT = "report"
    FEEDBACK = "feedback"
    INQUIRY = "inquiry"
    OTHER = "other"

class TicketPriority(str, Enum):
    """Enum for ticket priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketAction(str, Enum):
    """Enum for ticket actions"""
    CREATE = "create"
    CLOSE = "close"
    REOPEN = "reopen"
    CLAIM = "claim"
    UNCLAIM = "unclaim"
    ADD_USER = "add_user"
    REMOVE_USER = "remove_user"
    ADD_NOTE = "add_note"
    EDIT_NOTE = "edit_note"
    DELETE_NOTE = "delete_note"
    TRANSFER = "transfer"
    ARCHIVE = "archive"
    DELETE = "delete"

    def __str__(self):
        return self.value

    @classmethod
    def from_str(cls, status_str: str):
        """Convert a string to a TicketStatus enum value"""
        try:
            return cls(status_str)
        except ValueError:
            return cls.OPEN  # Default to OPEN if invalid status 