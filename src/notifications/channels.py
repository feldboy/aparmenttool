"""
Concrete notification channel implementations
"""

import os
import logging
from typing import Dict, Any, Optional
from .base import NotificationChannel, NotificationMessage, NotificationResult, NotificationStatus

logger = logging.getLogger(__name__)

class TelegramChannel(NotificationChannel):
    """Telegram notification channel using Bot API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("Telegram", config)
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
    def validate_config(self) -> bool:
        """Validate Telegram configuration"""
        if not self.bot_token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
            return False
        
        if not self.config.get('telegram_chat_id'):
            logger.error("telegram_chat_id not provided in configuration")
            return False
            
        return True
    
    def send(self, message: NotificationMessage, recipient: str) -> NotificationResult:
        """Send notification via Telegram Bot API"""
        if not self.is_enabled():
            return NotificationResult(
                status=NotificationStatus.FAILED,
                error_message="Telegram channel is disabled"
            )
        
        if not self.validate_config():
            return NotificationResult(
                status=NotificationStatus.FAILED,
                error_message="Invalid Telegram configuration"
            )
        
        try:
            # For now, simulate sending - in production this would use telegram-bot library
            formatted_message = self.format_message(message)
            
            # Simulate API call
            logger.info("🤖 [TELEGRAM SIMULATION] Sending message to chat_id: %s", recipient)
            logger.info("📱 Message content: %s", formatted_message)
            
            # In production, this would be:
            # import telegram
            # bot = telegram.Bot(token=self.bot_token)
            # response = bot.send_message(chat_id=recipient, text=formatted_message, parse_mode='HTML')
            # return NotificationResult(status=NotificationStatus.SUCCESS, message_id=str(response.message_id))
            
            result = NotificationResult(
                status=NotificationStatus.SUCCESS,
                message_id="telegram_sim_" + str(hash(formatted_message))[:8],
                metadata={"channel": "telegram", "recipient": recipient}
            )
            
            self.log_result(result, recipient)
            return result
            
        except Exception as e:
            result = NotificationResult(
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )
            self.log_result(result, recipient)
            return result
    
    def format_message(self, message: NotificationMessage) -> str:
        """Format message for Telegram with HTML parsing"""
        # Use enhanced formatting if metadata contains rich information
        if message.metadata and 'match_score' in message.metadata:
            from telegram_bot.utils import format_property_message
            try:
                # Convert NotificationMessage to property data format
                property_data = {
                    'listing_id': message.metadata.get('listing_id', 'unknown'),
                    'title': message.title.replace('🔥 ', '').replace('⭐ ', '').replace('👍 ', ''),
                    'price': message.metadata.get('price'),
                    'rooms': message.metadata.get('rooms'),
                    'location': message.metadata.get('location', ''),
                    'description': message.content,
                    'url': message.url,
                    'image_url': message.image_url,
                    'match_confidence': message.metadata.get('confidence', 'medium'),
                    'match_score': message.metadata.get('match_score', 0),
                    'match_reasons': message.metadata.get('reasons', [])
                }
                return format_property_message(property_data)
            except ImportError:
                # Fallback to simple formatting if bot utils not available
                pass
        
        # Original simple formatting
        formatted = f"🏠 <b>{message.title}</b>\n\n{message.content}"
        
        if message.url:
            formatted += f"\n\n🔗 <a href='{message.url}'>View Listing</a>"
        
        return formatted

class WhatsAppChannel(NotificationChannel):
    """WhatsApp notification channel using Twilio API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("WhatsApp", config)
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
        
    def validate_config(self) -> bool:
        """Validate WhatsApp/Twilio configuration"""
        if not self.account_sid or not self.auth_token:
            logger.error("TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN environment variables not set")
            return False
        
        if not self.config.get('whatsapp_phone_number'):
            logger.error("whatsapp_phone_number not provided in configuration")
            return False
            
        return True
    
    def send(self, message: NotificationMessage, recipient: str) -> NotificationResult:
        """Send notification via Twilio WhatsApp API"""
        if not self.is_enabled():
            return NotificationResult(
                status=NotificationStatus.FAILED,
                error_message="WhatsApp channel is disabled"
            )
        
        if not self.validate_config():
            return NotificationResult(
                status=NotificationStatus.FAILED,
                error_message="Invalid WhatsApp configuration"
            )
        
        try:
            # For now, simulate sending - in production this would use Twilio client
            formatted_message = self.format_message(message)
            
            # Simulate API call
            logger.info("📱 [WHATSAPP SIMULATION] Sending message to: %s", recipient)
            logger.info("📱 Message content: %s", formatted_message)
            
            # In production, this would be:
            # from twilio.rest import Client
            # client = Client(self.account_sid, self.auth_token)
            # message_obj = client.messages.create(
            #     body=formatted_message,
            #     from_=self.whatsapp_from,
            #     to=f"whatsapp:{recipient}"
            # )
            # return NotificationResult(status=NotificationStatus.SUCCESS, message_id=message_obj.sid)
            
            result = NotificationResult(
                status=NotificationStatus.SUCCESS,
                message_id="whatsapp_sim_" + str(hash(formatted_message))[:8],
                metadata={"channel": "whatsapp", "recipient": recipient}
            )
            
            self.log_result(result, recipient)
            return result
            
        except Exception as e:
            result = NotificationResult(
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )
            self.log_result(result, recipient)
            return result

class EmailChannel(NotificationChannel):
    """Email notification channel using SendGrid API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("Email", config)
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = config.get('from_email', 'noreply@realtyscanner.com')
        
    def validate_config(self) -> bool:
        """Validate Email/SendGrid configuration"""
        if not self.sendgrid_api_key:
            logger.error("SENDGRID_API_KEY environment variable not set")
            return False
        
        if not self.config.get('email_address'):
            logger.error("email_address not provided in configuration")
            return False
            
        return True
    
    def send(self, message: NotificationMessage, recipient: str) -> NotificationResult:
        """Send notification via SendGrid Email API"""
        if not self.is_enabled():
            return NotificationResult(
                status=NotificationStatus.FAILED,
                error_message="Email channel is disabled"
            )
        
        if not self.validate_config():
            return NotificationResult(
                status=NotificationStatus.FAILED,
                error_message="Invalid Email configuration"
            )
        
        try:
            # For now, simulate sending - in production this would use SendGrid client
            formatted_message = self.format_message(message)
            
            # Simulate API call
            logger.info("📧 [EMAIL SIMULATION] Sending email to: %s", recipient)
            logger.info("📧 Subject: %s", message.title)
            logger.info("📧 Message content: %s", formatted_message)
            
            # In production, this would be:
            # import sendgrid
            # from sendgrid.helpers.mail import Mail
            # sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
            # mail = Mail(
            #     from_email=self.from_email,
            #     to_emails=recipient,
            #     subject=message.title,
            #     html_content=self.format_html_message(message)
            # )
            # response = sg.send(mail)
            # return NotificationResult(status=NotificationStatus.SUCCESS, message_id=response.headers.get('X-Message-Id'))
            
            result = NotificationResult(
                status=NotificationStatus.SUCCESS,
                message_id="email_sim_" + str(hash(formatted_message))[:8],
                metadata={"channel": "email", "recipient": recipient}
            )
            
            self.log_result(result, recipient)
            return result
            
        except Exception as e:
            result = NotificationResult(
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )
            self.log_result(result, recipient)
            return result
    
    def format_message(self, message: NotificationMessage) -> str:
        """Format message for Email (plain text version)"""
        formatted = f"{message.title}\n\n{message.content}"
        
        if message.url:
            formatted += f"\n\nView Listing: {message.url}"
            
        return formatted
    
    def format_html_message(self, message: NotificationMessage) -> str:
        """Format message for Email (HTML version)"""
        html = f"""
        <html>
        <body>
            <h2>🏠 {message.title}</h2>
            <p>{message.content}</p>
        """
        
        if message.url:
            html += f'<p><a href="{message.url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Listing</a></p>'
        
        if message.image_url:
            html += f'<p><img src="{message.image_url}" alt="Property Image" style="max-width: 400px; height: auto;"></p>'
        
        html += """
        </body>
        </html>
        """
        
        return html
