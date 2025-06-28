#!/usr/bin/env python3
"""
Simple test to verify Telegram bot token and basic functionality
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_telegram_bot():
    """Test basic Telegram bot functionality"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return False
    
    print(f"✅ Found Telegram bot token: {token[:10]}...")
    
    try:
        # Try to import and test telegram functionality
        from telegram import Bot
        
        bot = Bot(token=token)
        
        # Test bot info
        bot_info = await bot.get_me()
        print("✅ Bot connected successfully!")
        print(f"   Bot name: {bot_info.first_name}")
        print(f"   Bot username: @{bot_info.username}")
        print(f"   Bot ID: {bot_info.id}")
        
        return True
        
    except ImportError:
        print("❌ python-telegram-bot not installed")
        print("   Run: pip install python-telegram-bot")
        return False
    except (ConnectionError, TimeoutError, ValueError) as e:
        print(f"❌ Bot connection failed: {e}")
        return False

def test_environment():
    """Test all environment variables"""
    print("🏠 RealtyScanner Environment Test")
    print("=" * 40)
    
    # Test essential variables
    essential_vars = {
        'SECRET_KEY': '✅ Security key configured',
        'MONGODB_URI': '✅ MongoDB connection configured', 
        'TELEGRAM_BOT_TOKEN': '✅ Telegram bot configured'
    }
    
    for var, message in essential_vars.items():
        value = os.getenv(var)
        if value and not value.startswith('your_'):
            print(message)
        else:
            print(f"❌ {var} not configured")
    
    print()

async def main():
    test_environment()
    
    print("🤖 Testing Telegram Bot Connection...")
    print("-" * 40)
    
    success = await test_telegram_bot()
    
    if success:
        print("\n🎉 All tests passed!")
        print("\n🚀 Ready to start RealtyScanner!")
        print("\nNext steps:")
        print("1. Start the Telegram bot: python src/telegram_bot/run_bot.py")
        print("2. Start the web dashboard: python src/web/run_server.py") 
        print("3. Send /start to your bot on Telegram")
    else:
        print("\n⚠️  Some tests failed. Please check configuration.")

if __name__ == "__main__":
    asyncio.run(main())
