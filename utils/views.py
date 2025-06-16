"""
UI components for the ticket system.
Includes buttons, select menus, and modals for ticket management.
"""
import discord
from discord.ui import Button, View, Select, Modal, TextInput
from typing import Optional, List, Dict, Any
from .constants import *
from database.models import TicketStatus

class ConfirmButton(Button):
    def __init__(self, *, style=discord.ButtonStyle.green, label="Confirm", emoji="✅", **kwargs):
        super().__init__(style=style, label=label, emoji=emoji, **kwargs)

class CancelButton(Button):
    def __init__(self, *, style=discord.ButtonStyle.red, label="Cancel", emoji="❌", **kwargs):
        super().__init__(style=style, label=label, emoji=emoji, **kwargs)

class TicketCreationModal(Modal):
    def __init__(self, category_name: str, fields: List[Dict[str, Any]]):
        super().__init__(title=f"Create {category_name} Ticket")
        
        # Add fields from category configuration
        for field in fields:
            self.add_item(
                TextInput(
                    label=field["label"],
                    placeholder=field.get("placeholder", ""),
                    required=field.get("required", True),
                    style=discord.TextStyle.long if field.get("style") == "paragraph" else discord.TextStyle.short,
                    min_length=field.get("min_length", 1),
                    max_length=field.get("max_length", 4000)
                )
            )

class TicketCloseModal(Modal):
    reason = TextInput(
        label="Closure Reason",
        placeholder="Please provide a reason for closing this ticket...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    def __init__(self):
        super().__init__(title="Close Ticket")

class InternalNoteModal(Modal):
    note = TextInput(
        label="Internal Note",
        placeholder="Add a private note visible only to staff...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=2000
    )

    def __init__(self):
        super().__init__(title="Add Internal Note")

class FeedbackModal(Modal):
    comments = TextInput(
        label="Additional Comments",
        placeholder="Please share any additional feedback about your support experience...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=1000
    )

    def __init__(self, rating: int):
        super().__init__(title=f"Ticket Feedback - {rating} Stars")
        self.rating = rating

class SupportPanelView(View):
    def __init__(self, categories: List[Dict[str, Any]]):
        super().__init__(timeout=None)  # Persistent view
        
        # Add category buttons
        for category in categories:
            self.add_item(
                Button(
                    style=discord.ButtonStyle.primary,
                    label=category["name"],
                    emoji=category["emoji"],
                    custom_id=f"ticket_create_{category['id']}"
                )
            )
            
        # Add anonymous ticket button if enabled
        if any(cat.get("allow_anonymous") for cat in categories):
            self.add_item(
                Button(
                    style=discord.ButtonStyle.secondary,
                    label="Anonymous Ticket",
                    emoji="🕵️",
                    custom_id="ticket_create_anonymous"
                )
            )

class TicketActionsView(View):
    def __init__(self, is_staff: bool = False):
        super().__init__(timeout=None)
        
        # User buttons
        self.add_item(
            Button(
                style=discord.ButtonStyle.danger,
                label="Close Ticket",
                emoji=EMOJI_LOCK,
                custom_id="ticket_close"
            )
        )
        
        # Staff-only buttons
        if is_staff:
            self.add_item(
                Button(
                    style=discord.ButtonStyle.primary,
                    label="Claim",
                    emoji=EMOJI_STAFF,
                    custom_id="ticket_claim"
                )
            )
            self.add_item(
                Button(
                    style=discord.ButtonStyle.secondary,
                    label="Status",
                    emoji=EMOJI_INFO,
                    custom_id="ticket_status"
                )
            )
            self.add_item(
                Button(
                    style=discord.ButtonStyle.secondary,
                    label="Internal Note",
                    emoji=EMOJI_PIN,
                    custom_id="ticket_note"
                )
            )
            self.add_item(
                Button(
                    style=discord.ButtonStyle.secondary,
                    label="Macros",
                    emoji=EMOJI_SETTINGS,
                    custom_id="ticket_macros"
                )
            )

class TicketStatusSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=status.value,
                emoji="🔵" if status == TicketStatus.OPEN else
                      "⏳" if status in (TicketStatus.PENDING_USER, TicketStatus.PENDING_STAFF) else
                      "🔨" if status == TicketStatus.IN_PROGRESS else
                      "⚠️" if status == TicketStatus.ESCALATED else
                      "✅" if status == TicketStatus.RESOLVED else
                      "🔒" if status == TicketStatus.CLOSED else "❓",
                value=status.value
            )
            for status in TicketStatus
        ]
        
        super().__init__(
            placeholder="Select ticket status...",
            min_values=1,
            max_values=1,
            options=options
        )

class MacroSelect(Select):
    def __init__(self, macros: List[Dict[str, Any]]):
        options = [
            discord.SelectOption(
                label=macro["name"],
                description=macro["content"][:100] + "..." if len(macro["content"]) > 100 else macro["content"],
                value=str(macro["macro_id"])
            )
            for macro in macros
        ]
        
        super().__init__(
            placeholder="Select a macro response...",
            min_values=1,
            max_values=1,
            options=options
        )

class FeedbackView(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Add star rating buttons
        for i in range(1, 6):
            self.add_item(
                Button(
                    style=discord.ButtonStyle.secondary,
                    label="★" * i,
                    custom_id=f"feedback_{i}"
                )
            )

class PaginationView(View):
    def __init__(self, *, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        
        self.add_item(
            Button(
                style=discord.ButtonStyle.secondary,
                emoji=EMOJI_BACK,
                custom_id="pagination_prev"
            )
        )
        self.add_item(
            Button(
                style=discord.ButtonStyle.secondary,
                emoji=EMOJI_NEXT,
                custom_id="pagination_next"
            )
        ) 