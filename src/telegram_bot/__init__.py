"""
Telegram Bot for RealtyScanner Agent

This module provides an interactive Telegram bot that allows users to:
1. Receive property notifications
2. Manage their search profiles
3. Configure notification settings
4. View notification history
"""

from .bot import RealtyBot
from .handlers import setup_handlers
from .utils import format_property_message

__all__ = [
    'RealtyBot',
    'setup_handlers', 
    'format_property_message'
]
