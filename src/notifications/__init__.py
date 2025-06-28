"""
Notification system for RealtyScanner Agent

This module provides:
1. Base notification channel interface
2. Concrete implementations for Telegram, WhatsApp, and Email
3. Notification dispatcher for managing multiple channels
4. Message formatting utilities
"""

from .dispatcher import NotificationDispatcher
from .channels import TelegramChannel, WhatsAppChannel, EmailChannel
from .base import NotificationChannel, NotificationResult, NotificationMessage

__all__ = [
    'NotificationDispatcher',
    'TelegramChannel', 
    'WhatsAppChannel', 
    'EmailChannel',
    'NotificationChannel',
    'NotificationResult',
    'NotificationMessage'
]
