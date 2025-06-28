"""
Base notification channel interface and common utilities
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class NotificationStatus(str, Enum):
    """Status of notification delivery"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"

@dataclass
class NotificationResult:
    """Result of a notification send attempt"""
    status: NotificationStatus
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    sent_at: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.sent_at is None:
            self.sent_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class NotificationMessage:
    """Structured notification message"""
    title: str
    content: str
    url: Optional[str] = None
    image_url: Optional[str] = None
    priority: str = "normal"  # low, normal, high
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class NotificationChannel(ABC):
    """Abstract base class for notification channels"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', False)
        
    @abstractmethod
    def send(self, message: NotificationMessage, recipient: str) -> NotificationResult:
        """
        Send a notification message to the specified recipient
        
        Args:
            message: The notification message to send
            recipient: The recipient identifier (chat_id, phone, email, etc.)
            
        Returns:
            NotificationResult indicating success/failure
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the channel configuration is correct
        
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
    
    def is_enabled(self) -> bool:
        """Check if this channel is enabled"""
        return self.enabled
    
    def format_message(self, message: NotificationMessage) -> str:
        """
        Format a notification message for this channel
        Default implementation - channels can override for custom formatting
        """
        formatted = f"🏠 {message.title}\n\n{message.content}"
        
        if message.url:
            formatted += f"\n\n🔗 {message.url}"
            
        return formatted
    
    def log_result(self, result: NotificationResult, recipient: str):
        """Log the notification result"""
        if result.status == NotificationStatus.SUCCESS:
            logger.info(f"[{self.name}] Successfully sent notification to {recipient} (ID: {result.message_id})")
        else:
            logger.error(f"[{self.name}] Failed to send notification to {recipient}: {result.error_message}")
