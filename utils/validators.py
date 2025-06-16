 """
Input validation utilities.
Handles validation of user inputs and configuration values.
"""
from typing import Optional, List, Dict, Any, Union, Tuple
import re
import emoji
import discord
from datetime import datetime, timedelta

from utils.logger import logger

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_ticket_title(title: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a ticket title.
        
        Args:
            title: The title to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check length
            if len(title) < 3:
                return False, "Title must be at least 3 characters long."
            if len(title) > 100:
                return False, "Title must be no longer than 100 characters."
            
            # Check for invalid characters
            if re.search(r'[<>{}[\]\\]', title):
                return False, "Title contains invalid characters."
            
            return True, None
        except Exception as e:
            logger.error(f"Error validating ticket title: {e}")
            return False, "An error occurred while validating the title."
    
    @staticmethod
    def validate_ticket_content(content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate ticket content.
        
        Args:
            content: The content to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check length
            if len(content) < 10:
                return False, "Content must be at least 10 characters long."
            if len(content) > 4000:
                return False, "Content must be no longer than 4000 characters."
            
            # Check for meaningful content
            words = content.split()
            if len(words) < 3:
                return False, "Please provide more detailed information."
            
            return True, None
        except Exception as e:
            logger.error(f"Error validating ticket content: {e}")
            return False, "An error occurred while validating the content."
    
    @staticmethod
    def validate_category_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a category name.
        
        Args:
            name: The name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check length
            if len(name) < 2:
                return False, "Category name must be at least 2 characters long."
            if len(name) > 32:
                return False, "Category name must be no longer than 32 characters."
            
            # Check for invalid characters
            if re.search(r'[<>{}[\]\\]', name):
                return False, "Category name contains invalid characters."
            
            return True, None
        except Exception as e:
            logger.error(f"Error validating category name: {e}")
            return False, "An error occurred while validating the category name."
    
    @staticmethod
    def validate_emoji(emoji_str: str) -> Tuple[bool, Optional[str]]:
        """
        Validate an emoji.
        
        Args:
            emoji_str: The emoji to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if custom emoji
            if re.match(r'<a?:[a-zA-Z0-9_]+:[0-9]+>', emoji_str):
                return True, None
            
            # Check if Unicode emoji
            if emoji.is_emoji(emoji_str):
                return True, None
            
            return False, "Please provide a valid emoji."
        except Exception as e:
            logger.error(f"Error validating emoji: {e}")
            return False, "An error occurred while validating the emoji."
    
    @staticmethod
    def validate_hex_color(color: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a hex color code.
        
        Args:
            color: The color code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check format
            if not re.match(r'^#[0-9a-fA-F]{6}$', color):
                return False, "Please provide a valid hex color code (e.g., #7289DA)."
            
            return True, None
        except Exception as e:
            logger.error(f"Error validating color code: {e}")
            return False, "An error occurred while validating the color code."
    
    @staticmethod
    def validate_time_input(time_str: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Validate a time input string (e.g., "1h", "30m", "2d").
        
        Args:
            time_str: The time string to validate
            
        Returns:
            Tuple of (is_valid, error_message, minutes)
        """
        try:
            # Check format
            match = re.match(r'^(\d+)([mhd])$', time_str.lower())
            if not match:
                return False, "Please provide a valid time (e.g., 30m, 1h, 2d).", None
            
            value, unit = match.groups()
            value = int(value)
            
            # Convert to minutes
            if unit == 'm':
                minutes = value
            elif unit == 'h':
                minutes = value * 60
            else:  # days
                minutes = value * 1440
            
            # Validate range
            if minutes < 1:
                return False, "Time must be at least 1 minute.", None
            if minutes > 43200:  # 30 days
                return False, "Time cannot exceed 30 days.", None
            
            return True, None, minutes
        except Exception as e:
            logger.error(f"Error validating time input: {e}")
            return False, "An error occurred while validating the time input.", None
    
    @staticmethod
    def validate_channel_type(
        channel: discord.abc.GuildChannel,
        required_type: Union[discord.ChannelType, List[discord.ChannelType]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a channel's type.
        
        Args:
            channel: The channel to validate
            required_type: Required channel type(s)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if isinstance(required_type, list):
                if channel.type not in required_type:
                    type_names = [t.name for t in required_type]
                    return False, f"Channel must be one of: {', '.join(type_names)}"
            else:
                if channel.type != required_type:
                    return False, f"Channel must be a {required_type.name} channel."
            
            return True, None
        except Exception as e:
            logger.error(f"Error validating channel type: {e}")
            return False, "An error occurred while validating the channel type."
    
    @staticmethod
    def validate_role_hierarchy(
        role: discord.Role,
        member: discord.Member
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a role's position in the hierarchy.
        
        Args:
            role: The role to validate
            member: The member to check against
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if role is higher than member's highest role
            if role >= member.top_role:
                return False, "You cannot manage roles higher than or equal to your highest role."
            
            # Check if role is higher than bot's highest role
            if role >= member.guild.me.top_role:
                return False, "I cannot manage roles higher than my highest role."
            
            return True, None
        except Exception as e:
            logger.error(f"Error validating role hierarchy: {e}")
            return False, "An error occurred while validating the role hierarchy."
    
    @staticmethod
    def validate_message_content(content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate message content.
        
        Args:
            content: The content to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check length
            if len(content) < 1:
                return False, "Message content cannot be empty."
            if len(content) > 2000:
                return False, "Message content must be no longer than 2000 characters."
            
            return True, None
        except Exception as e:
            logger.error(f"Error validating message content: {e}")
            return False, "An error occurred while validating the message content."
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a URL.
        
        Args:
            url: The URL to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Basic URL validation
            if not re.match(r'^https?://', url):
                return False, "URL must start with http:// or https://"
            
            # Check length
            if len(url) > 2048:
                return False, "URL is too long."
            
            return True, None
        except Exception as e:
            logger.error(f"Error validating URL: {e}")
            return False, "An error occurred while validating the URL."
    
    @staticmethod
    def validate_webhook_url(url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a Discord webhook URL.
        
        Args:
            url: The webhook URL to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check Discord webhook URL format
            if not re.match(r'^https://(?:ptb\.|canary\.)?discord\.com/api/webhooks/\d+/.+$', url):
                return False, "Please provide a valid Discord webhook URL."
            
            return True, None
        except Exception as e:
            logger.error(f"Error validating webhook URL: {e}")
            return False, "An error occurred while validating the webhook URL."

# Create singleton instance
input_validator = InputValidator()