#!/usr/bin/env python3
"""
Telegram Bot Runner for RealtyScanner Agent

This script starts the Telegram bot for property notifications and user interaction.

Usage:
    python src/telegram_bot/run_bot.py [--mode polling|webhook] [--port 8443]

Environment Variables:
    TELEGRAM_BOT_TOKEN - Required: Your bot token from @BotFather
    WEBHOOK_URL - Required for webhook mode: Your webhook URL
"""

import sys
import os
import argparse
import asyncio
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram_bot.bot import RealtyBot, init_bot
from telegram_bot import setup_handlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def run_bot_polling():
    """Run bot in polling mode (for development)"""
    logger.info("🤖 Starting RealtyScanner Telegram Bot in polling mode...")
    
    try:
        bot = await init_bot()
        logger.info("✅ Bot initialized successfully")
        
        logger.info("🔄 Starting polling...")
        await bot.start_polling()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        raise
    finally:
        logger.info("🔄 Cleaning up...")

async def run_bot_webhook(webhook_url: str, port: int = 8443):
    """Run bot in webhook mode (for production)"""
    logger.info(f"🤖 Starting RealtyScanner Telegram Bot in webhook mode...")
    logger.info(f"🔗 Webhook URL: {webhook_url}")
    logger.info(f"📡 Port: {port}")
    
    try:
        bot = await init_bot()
        logger.info("✅ Bot initialized successfully")
        
        logger.info("🔄 Starting webhook...")
        await bot.start_webhook(webhook_url, port)
        
    except KeyboardInterrupt:
        logger.info("⏹️ Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        raise
    finally:
        logger.info("🔄 Cleaning up...")

def validate_environment():
    """Validate required environment variables"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN environment variable not set")
        logger.error("💡 Get your bot token from @BotFather on Telegram")
        return False
    
    logger.info("✅ Environment validation passed")
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="RealtyScanner Telegram Bot")
    parser.add_argument(
        "--mode", 
        choices=["polling", "webhook"], 
        default="polling",
        help="Bot mode: polling for development, webhook for production"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8443,
        help="Port for webhook mode (default: 8443)"
    )
    parser.add_argument(
        "--webhook-url",
        help="Webhook URL for webhook mode (overrides WEBHOOK_URL env var)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🐛 Debug logging enabled")
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    logger.info("🏠 RealtyScanner Telegram Bot")
    logger.info("=" * 50)
    
    try:
        if args.mode == "polling":
            asyncio.run(run_bot_polling())
        else:
            webhook_url = args.webhook_url or os.getenv("WEBHOOK_URL")
            if not webhook_url:
                logger.error("❌ Webhook URL required for webhook mode")
                logger.error("💡 Set WEBHOOK_URL environment variable or use --webhook-url")
                sys.exit(1)
            
            asyncio.run(run_bot_webhook(webhook_url, args.port))
            
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
