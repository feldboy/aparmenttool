"""
Main Telegram bot implementation for RealtyScanner Agent
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

logger = logging.getLogger(__name__)

class RealtyBot:
    """Interactive Telegram bot for property notifications and profile management"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the Telegram bot
        
        Args:
            token: Telegram bot token (if None, will read from TELEGRAM_BOT_TOKEN env var)
        """
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("Telegram bot token is required. Set TELEGRAM_BOT_TOKEN environment variable.")
        
        self.application = None
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self):
        """Initialize the bot application"""
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Setup command and message handlers"""
        from .handlers import (
            start_command, help_command, profile_command, 
            settings_command, notifications_command, handle_callback_query,
            handle_message
        )
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("profile", profile_command))
        self.application.add_handler(CommandHandler("settings", settings_command))
        self.application.add_handler(CommandHandler("notifications", notifications_command))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(handle_callback_query))
        
        # Message handler for text input
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
    async def start_webhook(self, webhook_url: str, port: int = 8443):
        """Start bot with webhook (for production)"""
        await self.application.bot.set_webhook(url=f"{webhook_url}/webhook")
        await self.application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="/webhook",
            webhook_url=f"{webhook_url}/webhook"
        )
        
    async def start_polling(self):
        """Start bot with polling (for development)"""
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Keep the bot running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await self.stop()
        
    async def stop(self):
        """Stop the bot"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
            
    async def send_property_notification(self, chat_id: str, property_data: Dict[str, Any]):
        """
        Send a property notification to a specific chat
        
        Args:
            chat_id: Telegram chat ID
            property_data: Property listing data
        """
        try:
            from .utils import format_property_message, create_property_keyboard
            
            message = format_property_message(property_data)
            keyboard = create_property_keyboard(property_data)
            
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(f"✅ Sent property notification to chat {chat_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send property notification to chat {chat_id}: {e}")
            
    def get_user_session(self, user_id: str) -> Dict[str, Any]:
        """Get or create user session data"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'state': 'idle',
                'profile_data': {},
                'last_action': None
            }
        return self.user_sessions[user_id]
        
    def update_user_session(self, user_id: str, updates: Dict[str, Any]):
        """Update user session data"""
        session = self.get_user_session(user_id)
        session.update(updates)

# Global bot instance
realty_bot = None

def get_bot() -> RealtyBot:
    """Get the global bot instance"""
    global realty_bot
    if realty_bot is None:
        realty_bot = RealtyBot()
    return realty_bot

async def init_bot() -> RealtyBot:
    """Initialize and return the global bot instance"""
    bot = get_bot()
    await bot.initialize()
    return bot
