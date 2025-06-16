"""
Banner and startup information display utilities.
"""
import platform
import psutil
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import discord
from datetime import datetime
from typing import Dict, Any, List

# Define color codes
COLORS = {
    'blue': '\033[94m',
    'cyan': '\033[96m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'red': '\033[91m',
    'magenta': '\033[95m',
    'bold': '\033[1m',
    'end': '\033[0m',
    'reset': '\033[0m'
}

NEXON_BANNER = f"""
{COLORS['cyan']}{COLORS['bold']}
    ███╗   ██╗███████╗██╗  ██╗ ██████╗ ███╗   ██╗
    ████╗  ██║██╔════╝╚██╗██╔╝██╔═══██╗████╗  ██║
    ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║██╔██╗ ██║
    ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║██║╚██╗██║
    ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝██║ ╚████║
    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
{COLORS['end']}
{COLORS['green']}  🎫 Advanced Discord Ticket & Support System 🤖{COLORS['end']}
"""

def print_banner(version: str, discord_version: str = discord.__version__) -> None:
    """Print a beautiful Nexon-themed startup banner"""
    console = Console()
    
    # Create banner text
    banner_text = Text()
    banner_text.append(NEXON_BANNER, style="bright_blue")
    banner_text.append("\n")
    
    # Add version and discord.py version
    banner_text.append(f"Version: {version}", style="cyan")
    banner_text.append(" | ", style="dim")
    banner_text.append(f"Discord.py: {discord.__version__}", style="magenta")
    banner_text.append("\n")
    
    # Current time
    current_time = datetime.now().strftime("%H:%M:%S")
    banner_text.append(f"Started at: {current_time}", style="green")
    
    # Create panel
    panel = Panel(
        banner_text,
        border_style="bright_blue",
        subtitle="✨ Next-Gen Support System by Darsh",
        subtitle_align="right"
    )
    
    # Print with spacing
    console.print("\n")
    console.print(panel)
    console.print("\n")

def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    return {
        'python_version': platform.python_version(),
        'os_name': platform.system(),
        'os_version': platform.version(),
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'discord_version': discord.__version__,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    }

def format_system_info(info: Dict[str, Any]) -> str:
    """Format system information for display."""
    return f"""
{COLORS['yellow']}System Information:{COLORS['end']}
• Python: v{info['python_version']}
• OS: {info['os_name']} {info['os_version']}
• CPU Usage: {info['cpu_usage']}%
• Memory Usage: {info['memory_usage']}%
• Discord.py: v{info['discord_version']}
• Started: {info['timestamp']}
"""

def display_banner() -> None:
    """Display the NEXON banner and system information."""
    print(BANNER)
    print(format_system_info(get_system_info()))

def get_startup_info() -> List[str]:
    """Get formatted startup information"""
    return [
        "🔄 Initializing bot...",
        "🔄 Connecting to database...",
        "🔄 Loading extensions...",
        "🔄 Syncing commands...",
        "🔄 Connecting to Discord..."
    ]

def get_progress_bar(progress: float, width: int = 40) -> str:
    """Create a colorful progress bar."""
    filled = int(width * progress)
    empty = width - filled
    bar = f"{COLORS['green']}{'#' * filled}{COLORS['red']}{'-' * empty}{COLORS['reset']}"
    percentage = f"{int(progress * 100)}%"
    return f"[{bar}] {percentage}"

def print_startup_sequence() -> None:
    """Print a beautiful startup sequence."""
    messages = [
        "[*] Initializing systems...",
        "[*] Configuring modules...",
        "[*] Establishing connections...",
        "[*] Loading components...",
        "[*] Powering up services..."
    ]
    
    print("\n" * 2)
    print(BANNER)
    print(f"\n{COLORS['cyan']}{'-' * 60}{COLORS['reset']}")
    
    for i, message in enumerate(messages, 1):
        progress = i / len(messages)
        sys.stdout.write(f"\r{message} {get_progress_bar(progress)}")
        sys.stdout.flush()
    
    print("\n\n" + f"{COLORS['green']}[+] System initialization complete! [+]{COLORS['reset']}\n")

def get_status_indicator(status: bool) -> str:
    """Get a colorful status indicator."""
    return f"{COLORS['green']}[+]{COLORS['reset']}" if status else f"{COLORS['red']}[-]{COLORS['reset']}"

def format_section_header(title: str) -> str:
    """Format a section header with decorative elements."""
    return f"\n{COLORS['cyan']}+{'-' * (len(title) + 4)}+\n| {COLORS['yellow']}{title}{COLORS['cyan']} |\n+{'-' * (len(title) + 4)}+{COLORS['reset']}\n"

def format_stat_line(label: str, value: str, color: str = 'reset') -> str:
    """Format a statistics line with proper spacing and color."""
    return f"{COLORS['cyan']}|{COLORS['reset']} {label}: {COLORS[color]}{value}{COLORS['reset']}"

def format_guild_info(name: str, members: int, channels: int) -> str:
    """Format guild information with proper indentation and styling."""
    return (
        f"{COLORS['cyan']}+-{COLORS['magenta']}{name}{COLORS['reset']}\n"
        f"{COLORS['cyan']}|  +-{COLORS['reset']} Members: {members}\n"
        f"{COLORS['cyan']}|  +-{COLORS['reset']} Channels: {channels}"
    )

def get_time_of_day_greeting() -> str:
    """Get a time-appropriate greeting."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "[Morning]"
    elif 12 <= hour < 17:
        return "[Afternoon]"
    elif 17 <= hour < 21:
        return "[Evening]"
    else:
        return "[Night]"

__all__ = [
    'print_banner',
    'get_startup_info',
    'get_system_info',
    'format_system_info',
    'print_startup_sequence'
]