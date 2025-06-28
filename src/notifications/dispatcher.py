"""
Notification dispatcher for managing multiple notification channels
"""

import logging
from typing import Dict, List, Optional, Any
from .base import NotificationChannel, NotificationMessage, NotificationResult, NotificationStatus
from .channels import TelegramChannel, WhatsAppChannel, EmailChannel

logger = logging.getLogger(__name__)

class NotificationDispatcher:
    """
    Central dispatcher for managing notification channels and sending messages
    """
    
    def __init__(self):
        self.channels: Dict[str, NotificationChannel] = {}
        
    def register_channel(self, channel_name: str, channel: NotificationChannel):
        """Register a notification channel"""
        self.channels[channel_name] = channel
        logger.info("Registered notification channel: %s", channel_name)
    
    def configure_from_profile(self, notification_config: Dict[str, Any]):
        """
        Configure notification channels from a user profile configuration
        
        Args:
            notification_config: Dictionary with channel configurations
                {
                    "telegram": {"enabled": True, "telegram_chat_id": "123456"},
                    "whatsapp": {"enabled": False, "whatsapp_phone_number": "+972501234567"},
                    "email": {"enabled": False, "email_address": "user@example.com"}
                }
        """
        # Clear existing channels
        self.channels.clear()
        
        # Configure Telegram
        if 'telegram' in notification_config:
            telegram_config = notification_config['telegram']
            if telegram_config.get('enabled', False):
                telegram_channel = TelegramChannel(telegram_config)
                self.register_channel('telegram', telegram_channel)
        
        # Configure WhatsApp
        if 'whatsapp' in notification_config:
            whatsapp_config = notification_config['whatsapp']
            if whatsapp_config.get('enabled', False):
                whatsapp_channel = WhatsAppChannel(whatsapp_config)
                self.register_channel('whatsapp', whatsapp_channel)
        
        # Configure Email
        if 'email' in notification_config:
            email_config = notification_config['email']
            if email_config.get('enabled', False):
                email_channel = EmailChannel(email_config)
                self.register_channel('email', email_channel)
        
        logger.info("Configured %d notification channels", len(self.channels))
    
    def send_notification(self, message: NotificationMessage, 
                         channels: Optional[List[str]] = None) -> Dict[str, NotificationResult]:
        """
        Send a notification message through specified channels
        
        Args:
            message: The notification message to send
            channels: List of channel names to use (if None, uses all enabled channels)
            
        Returns:
            Dictionary mapping channel names to their NotificationResult
        """
        if channels is None:
            channels = list(self.channels.keys())
        
        results = {}
        
        for channel_name in channels:
            if channel_name not in self.channels:
                logger.warning("Unknown notification channel: %s", channel_name)
                results[channel_name] = NotificationResult(
                    status=NotificationStatus.FAILED,
                    error_message=f"Unknown channel: {channel_name}"
                )
                continue
            
            channel = self.channels[channel_name]
            
            if not channel.is_enabled():
                logger.info("Skipping disabled channel: %s", channel_name)
                results[channel_name] = NotificationResult(
                    status=NotificationStatus.FAILED,
                    error_message=f"Channel {channel_name} is disabled"
                )
                continue
            
            # Get recipient from channel config
            recipient = self._get_recipient_for_channel(channel_name, channel.config)
            if not recipient:
                logger.error("No recipient configured for channel: %s", channel_name)
                results[channel_name] = NotificationResult(
                    status=NotificationStatus.FAILED,
                    error_message=f"No recipient configured for {channel_name}"
                )
                continue
            
            # Send notification
            try:
                result = channel.send(message, recipient)
                results[channel_name] = result
            except Exception as e:
                logger.exception("Unexpected error sending notification via %s", channel_name)
                results[channel_name] = NotificationResult(
                    status=NotificationStatus.FAILED,
                    error_message=f"Unexpected error: {str(e)}"
                )
        
        return results
    
    def _get_recipient_for_channel(self, channel_name: str, config: Dict[str, Any]) -> Optional[str]:
        """Extract recipient information from channel configuration"""
        if channel_name == 'telegram':
            return config.get('telegram_chat_id')
        elif channel_name == 'whatsapp':
            return config.get('whatsapp_phone_number')
        elif channel_name == 'email':
            return config.get('email_address')
        else:
            return None
    
    def send_test_notification(self) -> Dict[str, NotificationResult]:
        """Send a test notification through all configured channels"""
        test_message = NotificationMessage(
            title="RealtyScanner Test Notification",
            content="This is a test message to verify your notification channels are working correctly.",
            url="https://example.com/test-listing",
            priority="normal"
        )
        
        logger.info("Sending test notification through %d channels", len(self.channels))
        return self.send_notification(test_message)
    
    def validate_all_channels(self) -> Dict[str, bool]:
        """Validate configuration for all registered channels"""
        validation_results = {}
        
        for channel_name, channel in self.channels.items():
            try:
                is_valid = channel.validate_config()
                validation_results[channel_name] = is_valid
                
                if is_valid:
                    logger.info("Channel %s configuration is valid", channel_name)
                else:
                    logger.error("Channel %s configuration is invalid", channel_name)
                    
            except Exception as e:
                logger.exception("Error validating channel %s", channel_name)
                validation_results[channel_name] = False
        
        return validation_results
    
    def get_channel_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status information for all channels"""
        status = {}
        
        for channel_name, channel in self.channels.items():
            status[channel_name] = {
                'enabled': channel.is_enabled(),
                'valid_config': channel.validate_config(),
                'name': channel.name
            }
        
        return status

# Global dispatcher instance
notification_dispatcher = NotificationDispatcher()

def get_notification_dispatcher() -> NotificationDispatcher:
    """Get the global notification dispatcher instance"""
    return notification_dispatcher
