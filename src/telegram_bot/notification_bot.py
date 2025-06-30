"""
Simplified Telegram bot for NOTIFICATION-ONLY purposes
No interactive commands, no management features - pure notification delivery
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional
from telegram import Bot

logger = logging.getLogger(__name__)

class NotificationBot:
    """Simple Telegram bot for sending property notifications only"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the notification-only Telegram bot
        
        Args:
            token: Telegram bot token (if None, will read from TELEGRAM_BOT_TOKEN env var)
        """
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("Telegram bot token is required. Set TELEGRAM_BOT_TOKEN environment variable.")
        
        self.bot = Bot(token=self.token)
        
    async def send_property_notification(self, chat_id: str, property_data: Dict[str, Any]) -> bool:
        """
        Send a property notification to a specific chat
        
        Args:
            chat_id: Telegram chat ID
            property_data: Property listing data
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            message = self._format_property_message(property_data)
            
            # Send message with optional photo
            if property_data.get('image_url'):
                await self._send_with_photo(chat_id, message, property_data['image_url'])
            else:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=False
                )
            
            logger.info(f"✅ Sent property notification to chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send property notification to chat {chat_id}: {e}")
            return False
            
    async def _send_with_photo(self, chat_id: str, message: str, image_url: str):
        """Send notification with photo"""
        try:
            await self.bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption=message,
                parse_mode='HTML'
            )
        except Exception as e:
            # Fallback to text-only message if photo fails
            logger.warning(f"Failed to send photo, falling back to text: {e}")
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
    
    def _format_property_message(self, property_data: Dict[str, Any]) -> str:
        """Format property data into a notification message"""
        source = property_data.get('source', 'Unknown')
        price = property_data.get('price', 'N/A')
        rooms = property_data.get('rooms', 'N/A')
        location = property_data.get('location', 'N/A')
        url = property_data.get('url', '')
        description = property_data.get('description', '')
        
        # Format price
        if isinstance(price, (int, float)) and price > 0:
            price_str = f"{price:,} ₪"
        else:
            price_str = str(price)
        
        # Create message
        message = f"""🏠 <b>דירה חדשה נמצאה!</b>

💰 <b>מחיר:</b> {price_str}
🏠 <b>חדרים:</b> {rooms}
📍 <b>מיקום:</b> {location}
📱 <b>מקור:</b> {source}"""

        # Add description if available (truncated)
        if description and len(description.strip()) > 0:
            desc_preview = description.strip()[:100]
            if len(description) > 100:
                desc_preview += "..."
            message += f"\n\n📝 <b>תיאור:</b> {desc_preview}"
        
        # Add link if available
        if url:
            message += f"\n\n🔗 <a href='{url}'>צפה בדירה</a>"
        
        message += f"\n\n📅 <b>זמן:</b> {property_data.get('timestamp', 'עכשיו')}"
        
        return message
    
    async def send_system_notification(self, chat_id: str, message: str, message_type: str = "info") -> bool:
        """
        Send system notifications (errors, status updates, etc.)
        
        Args:
            chat_id: Telegram chat ID
            message: Message text
            message_type: Type of message (info, warning, error, success)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Format based on message type
            icons = {
                "info": "ℹ️",
                "warning": "⚠️", 
                "error": "❌",
                "success": "✅"
            }
            
            icon = icons.get(message_type, "📢")
            formatted_message = f"{icon} <b>RealtyScanner</b>\n\n{message}"
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=formatted_message,
                parse_mode='HTML'
            )
            
            logger.info(f"✅ Sent system notification to chat {chat_id}: {message_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send system notification to chat {chat_id}: {e}")
            return False
    
    async def test_connection(self, chat_id: str) -> bool:
        """
        Test if the bot can send messages to a specific chat
        
        Args:
            chat_id: Telegram chat ID to test
            
        Returns:
            bool: True if connection works, False otherwise
        """
        try:
            test_message = "🧪 <b>Test Connection</b>\n\nTelegram bot connection is working properly!"
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=test_message,
                parse_mode='HTML'
            )
            
            logger.info(f"✅ Test message sent successfully to chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Test message failed for chat {chat_id}: {e}")
            return False

# Global notification bot instance
notification_bot = None

def get_notification_bot() -> NotificationBot:
    """Get the global notification bot instance"""
    global notification_bot
    if notification_bot is None:
        notification_bot = NotificationBot()
    return notification_bot

async def send_property_alert(chat_id: str, property_data: Dict[str, Any]) -> bool:
    """
    Convenience function to send a property alert
    
    Args:
        chat_id: Telegram chat ID
        property_data: Property listing data
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    bot = get_notification_bot()
    return await bot.send_property_notification(chat_id, property_data)

async def send_system_alert(chat_id: str, message: str, message_type: str = "info") -> bool:
    """
    Convenience function to send a system alert
    
    Args:
        chat_id: Telegram chat ID  
        message: Message text
        message_type: Type of message (info, warning, error, success)
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    bot = get_notification_bot()
    return await bot.send_system_notification(chat_id, message, message_type)

async def test_telegram_connection(chat_id: str) -> bool:
    """
    Test Telegram connection for a specific chat ID
    
    Args:
        chat_id: Telegram chat ID to test
        
    Returns:
        bool: True if connection works, False otherwise
    """
    bot = get_notification_bot()
    return await bot.test_connection(chat_id)
