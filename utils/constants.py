import os
from pathlib import Path

# Bot Information
BOT_NAME = "Nexon"
BOT_VERSION = "1.0.0"
BOT_DESCRIPTION = "A powerful Discord ticket and support system"
DEFAULT_PREFIX = "!"

# File Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
COGS_DIR = BASE_DIR / "cogs"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/nexon.db")

# Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
APPLICATION_ID = os.getenv("APPLICATION_ID")

# Ticket System
MAX_TICKETS_PER_USER = 3
TICKET_CLOSE_DELAY = 5  # seconds
TICKET_CATEGORIES = [
    "General Support",
    "Technical Issues",
    "Billing Support",
    "Account Issues",
    "Other"
]

# Colors
COLORS = {
    "PRIMARY": 0x3498db,    # Blue
    "SUCCESS": 0x2ecc71,    # Green
    "ERROR": 0xe74c3c,      # Red
    "WARNING": 0xf1c40f,    # Yellow
    "INFO": 0x95a5a6,       # Gray
}

# Emojis
EMOJIS = {
    "SUCCESS": "✅",
    "ERROR": "❌",
    "WARNING": "⚠️",
    "INFO": "ℹ️",
    "TICKET": "🎫",
    "SUPPORT": "👥",
    "TIME": "⏰",
    "GEAR": "⚙️",
    "ONLINE": "🟢",
    "OFFLINE": "⭕",
    "LOCK": "🔒",
    "UNLOCK": "🔓",
    "PIN": "📌",
    "STAR": "⭐",
    "MAIL": "📧",
    "BELL": "🔔",
    "CHART": "📊",
    "BOOK": "📚",
    "TOOLS": "🛠️",
    "LINK": "🔗",
    "CALENDAR": "📅",
    "CLOCK": "🕐",
    "SEARCH": "🔍",
    "TAG": "🏷️",
    "FOLDER": "📁",
    "DOCUMENT": "📄",
    "PENCIL": "✏️",
    "TRASH": "🗑️",
    "REFRESH": "🔄",
    "CHECK": "✔️",
    "CROSS": "❌",
    "PLUS": "➕",
    "MINUS": "➖",
    "ARROW_RIGHT": "➡️",
    "ARROW_LEFT": "⬅️",
    "ARROW_UP": "⬆️",
    "ARROW_DOWN": "⬇️"
}

# Timeouts (in seconds)
TIMEOUTS = {
    "BUTTON": 300,        # 5 minutes
    "MODAL": 300,         # 5 minutes
    "SELECT": 300,        # 5 minutes
    "TICKET_INACTIVE": 604800  # 7 days
}

# Default settings
DEFAULT_SETTINGS = {
    "THEME_COLOR": COLORS["PRIMARY"],
    "LANGUAGE": "en",
    "TICKET_PREFIX": "ticket-",
    "MAX_TICKETS_PER_USER": 3,
    "MAX_TICKET_AGE_DAYS": 30,
    "MAINTENANCE_MODE": False,
    "MAINTENANCE_MESSAGE": "The ticket system is currently under maintenance. Please try again later."
}

# Required Bot Permissions
BOT_PERMISSIONS = [
    "manage_channels",
    "manage_roles",
    "manage_messages",
    "read_messages",
    "send_messages",
    "embed_links",
    "attach_files",
    "read_message_history",
    "add_reactions",
    "use_external_emojis"
]

# Create necessary directories
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
TRANSCRIPTS_DIR.mkdir(exist_ok=True)

# Ticket statuses
TICKET_STATUS = {
    "OPEN": "open",
    "PENDING_USER": "pending_user",
    "PENDING_STAFF": "pending_staff",
    "IN_PROGRESS": "in_progress",
    "ESCALATED": "escalated",
    "RESOLVED": "resolved",
    "CLOSED": "closed"
}

# Default colors
DEFAULT_COLOR = 0x5865F2  # Discord Blurple
SUCCESS_COLOR = 0x2ecc71
ERROR_COLOR = 0xe74c3c
WARNING_COLOR = 0xf1c40f

# Emojis
TICKET_EMOJI = "🎫"
SUPPORT_EMOJI = "💬"
STAFF_EMOJI = "👥"
ADMIN_EMOJI = "⚙️"
SUCCESS_EMOJI = "✅"
ERROR_EMOJI = "❌"
WARNING_EMOJI = "⚠️"

# Permissions
STAFF_PERMISSIONS = [
    "manage_messages",
    "read_messages",
    "send_messages",
    "embed_links",
    "attach_files",
    "read_message_history"
]

ADMIN_PERMISSIONS = [
    "manage_channels",
    "manage_roles",
    "manage_messages",
    "read_messages",
    "send_messages",
    "embed_links",
    "attach_files",
    "read_message_history"
]

# Cache Settings
CACHE_TTL = 300  # 5 minutes

# Ticket Settings
MAX_ACTIVE_TICKETS = 3
TICKET_NAME_FORMAT = "ticket-{}"
TRANSCRIPT_RETENTION_DAYS = 30

# File paths
PATHS = {
    "DATA": "data",
    "LOGS": "logs",
    "TRANSCRIPTS": "data/transcripts",
    "CONFIG": "config"
}

# Time Constants
SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = 86400

# Limits
MAX_EMBED_DESCRIPTION = 4096
MAX_EMBED_FIELD_VALUE = 1024
MAX_EMBED_FIELDS = 25
MAX_EMBED_TITLE = 256
MAX_MESSAGE_LENGTH = 2000

# Emoji constants
EMOJI_SUCCESS = "✅"
EMOJI_ERROR = "❌"
EMOJI_WARNING = "⚠️"
EMOJI_INFO = "ℹ️"
EMOJI_LOADING = "⏳"
EMOJI_TICKET = "🎫"
EMOJI_LOCK = "🔒"
EMOJI_UNLOCK = "🔓"
EMOJI_PIN = "📌"
EMOJI_TRASH = "🗑️"
EMOJI_ARCHIVE = "📂"
EMOJI_STAFF = "👮"
EMOJI_USER = "👤"
EMOJI_SETTINGS = "⚙️"
EMOJI_HELP = "❓"
EMOJI_BACK = "⬅️"
EMOJI_NEXT = "➡️"

# Color constants
COLOR_SUCCESS = 0x2ecc71  # Green
COLOR_ERROR = 0xe74c3c    # Red
COLOR_WARNING = 0xf1c40f  # Yellow
COLOR_INFO = 0x3498db     # Blue
COLOR_DEFAULT = 0x7289da  # Discord Blurple

# Time constants
SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = 86400
SECONDS_IN_WEEK = 604800

# Message constants
MAX_EMBED_DESCRIPTION = 4096
MAX_EMBED_FIELD_VALUE = 1024
MAX_EMBED_FIELDS = 25

# Ticket constants
MAX_TICKETS_PER_USER = 3
TICKET_CLOSE_TIMEOUT = 72  # Hours
TICKET_AUTO_ARCHIVE_DAYS = 7
MAX_TRANSCRIPT_MESSAGES = 5000

# Permission constants
STAFF_PERMISSIONS = [
    "view_channel",
    "send_messages",
    "embed_links",
    "attach_files",
    "read_message_history",
    "add_reactions",
    "use_external_emojis",
    "manage_messages",
    "manage_channels"
]

USER_PERMISSIONS = [
    "view_channel",
    "send_messages",
    "embed_links",
    "attach_files",
    "read_message_history",
    "add_reactions",
    "use_external_emojis"
]