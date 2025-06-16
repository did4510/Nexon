"""Localization utilities for the bot."""

import json
from pathlib import Path
from typing import Dict, Any

# Default language
DEFAULT_LANGUAGE = "en"

# Load translations
TRANSLATIONS: Dict[str, Dict[str, Any]] = {}

def load_translations():
    """Load all translation files from the translations directory."""
    translations_dir = Path("translations")
    if not translations_dir.exists():
        translations_dir.mkdir(parents=True)
        # Create default English translation file
        create_default_translation()
    
    for file in translations_dir.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                lang = file.stem
                TRANSLATIONS[lang] = json.load(f)
        except Exception as e:
            print(f"Error loading translation file {file}: {e}")

def create_default_translation():
    """Create the default English translation file."""
    default_translations = {
        "ticket": {
            "created": "Ticket created successfully!",
            "closed": "Ticket closed successfully!",
            "error": "An error occurred while processing your ticket.",
            "not_found": "Ticket not found.",
            "already_exists": "You already have an open ticket.",
            "max_reached": "You have reached the maximum number of open tickets."
        },
        "staff": {
            "claimed": "Ticket claimed successfully!",
            "unclaimed": "Ticket unclaimed successfully!",
            "added": "User added to ticket successfully!",
            "removed": "User removed from ticket successfully!"
        },
        "errors": {
            "permission": "You don't have permission to do that.",
            "invalid_category": "Invalid ticket category.",
            "invalid_status": "Invalid ticket status.",
            "database_error": "A database error occurred."
        }
    }
    
    with open("translations/en.json", "w", encoding="utf-8") as f:
        json.dump(default_translations, f, indent=4)

def get_text(key: str, language: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """
    Get a translated text by key.
    
    Args:
        key: The translation key (e.g., "ticket.created")
        language: The language code (e.g., "en", "es")
        **kwargs: Format arguments for the translation string
    
    Returns:
        The translated text, or the key if translation not found
    """
    if not TRANSLATIONS:
        load_translations()
    
    # Get translation for the specified language, fall back to English
    translation = TRANSLATIONS.get(language, TRANSLATIONS.get(DEFAULT_LANGUAGE, {}))
    
    # Split the key into parts and traverse the translation dict
    parts = key.split(".")
    current = translation
    
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part, key)
        else:
            return key
    
    # If we found a string, format it with any provided kwargs
    if isinstance(current, str):
        try:
            return current.format(**kwargs)
        except KeyError:
            return current
    
    return key

# Initialize translations
load_translations()