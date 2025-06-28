#!/usr/bin/env python3
"""
Epic 4 Demo: Run Telegram Bot and Web Dashboard

This script demonstrates how to start both the Telegram bot and web dashboard
for Epic 4 features.

Prerequisites:
1. Set TELEGRAM_BOT_TOKEN environment variable
2. Set SECRET_KEY environment variable
3. Optional: Set SENDGRID_API_KEY for email notifications

Usage:
    # Run both services
    python scripts/demo_epic4.py

    # Run only bot
    python scripts/demo_epic4.py --bot-only

    # Run only web
    python scripts/demo_epic4.py --web-only
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def setup_environment():
    """Set up environment variables for demo"""
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("⚠️  TELEGRAM_BOT_TOKEN not set. Using demo token for testing.")
        os.environ["TELEGRAM_BOT_TOKEN"] = "demo_bot_token_12345"
    
    if not os.getenv("SECRET_KEY"):
        print("⚠️  SECRET_KEY not set. Using demo key for testing.")
        os.environ["SECRET_KEY"] = "demo-secret-key-epic4-realty-scanner"
    
    print(f"🔑 Using bot token: {os.getenv('TELEGRAM_BOT_TOKEN')[:10]}...")
    print(f"🔐 Using secret key: {os.getenv('SECRET_KEY')[:10]}...")

async def run_telegram_bot():
    """Run the Telegram bot"""
    print("\n🤖 Starting Telegram Bot...")
    print("=" * 50)
    
    try:
        from telegram_bot.run_bot import main as run_bot
        print("✅ Bot modules loaded successfully")
        print("🚀 Starting bot server...")
        print("📱 Bot will listen for incoming messages")
        print("💬 Try sending /start to the bot")
        
        # In demo mode, we'll just simulate
        print("\n📋 Available bot commands:")
        print("   /start     - Welcome message and setup")
        print("   /profile   - Manage search profiles")
        print("   /settings  - Bot settings and preferences")
        print("   /notifications - View notification history")
        print("   /help      - Show help information")
        
        # For demo, we don't actually start the bot to avoid blocking
        print("\n🎯 Bot is ready to receive commands!")
        print("   (In production, call await run_bot() here)")
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

def run_web_dashboard():
    """Run the web dashboard"""
    print("\n🌐 Starting Web Dashboard...")
    print("=" * 50)
    
    try:
        import uvicorn
        from web.run_server import create_server
        
        print("✅ Web modules loaded successfully")
        print("🚀 Starting web server...")
        print("🌐 Dashboard will be available at http://localhost:8000")
        
        # For demo, we show what would happen
        print("\n📋 Available web endpoints:")
        print("   GET  /              - Dashboard home")
        print("   GET  /dashboard     - Main dashboard interface")
        print("   POST /auth/login    - User authentication")
        print("   GET  /api/profiles  - Get user profiles")
        print("   POST /api/profiles  - Create/update profiles")
        print("   GET  /api/notifications - Get notification history")
        print("   WS   /ws            - Real-time WebSocket updates")
        
        print("\n🎯 Web dashboard is ready!")
        print("   (In production, call uvicorn.run(app) here)")
        
        # For actual deployment:
        # uvicorn.run("web.app:app", host="0.0.0.0", port=8000, reload=True)
        
    except Exception as e:
        print(f"❌ Error starting web server: {e}")

async def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description="Epic 4 Demo")
    parser.add_argument("--bot-only", action="store_true", help="Run only the bot")
    parser.add_argument("--web-only", action="store_true", help="Run only the web dashboard")
    args = parser.parse_args()
    
    print("🏠 RealtyScanner Agent - Epic 4 Demo")
    print("=" * 60)
    print("🎉 Multi-platform Property Notification System")
    print()
    
    setup_environment()
    
    if args.bot_only:
        await run_telegram_bot()
    elif args.web_only:
        run_web_dashboard()
    else:
        # Run both
        await run_telegram_bot()
        run_web_dashboard()
        
        print("\n" + "=" * 60)
        print("🎉 Epic 4 Demo Complete!")
        print()
        print("🚀 To run in production:")
        print("   1. Set proper TELEGRAM_BOT_TOKEN from @BotFather")
        print("   2. Set secure SECRET_KEY for JWT tokens") 
        print("   3. Configure database connection (MongoDB)")
        print("   4. Set up webhook for Telegram bot")
        print("   5. Deploy web dashboard with proper domain")
        print()
        print("📚 See docs/Epic4_Implementation_Guide.md for details")

if __name__ == "__main__":
    asyncio.run(main())
