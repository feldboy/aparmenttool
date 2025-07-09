#!/usr/bin/env python3
"""
Quick Demo: Live Apartment Scanning
Shows real-time apartment scanning and Telegram notifications
"""

import os
import sys
import asyncio
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv()

async def demo_live_scanning():
    """Demo live apartment scanning with real Telegram notifications"""
    
    print("🏠 RealtyScanner LIVE Demo")
    print("=" * 40)
    print("This demo will:")
    print("1. 🕷️ Scan Yad2 for new apartments")
    print("2. 🤖 AI analyze and filter results") 
    print("3. 📱 Send real notifications to your Telegram bot")
    print()
    
    # Import components
    try:
        from db import get_db
        from scrapers.yad2 import Yad2Scraper
        from analysis.content import ContentAnalyzer
        from notifications.dispatcher import NotificationDispatcher
        from telegram import Bot
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Initialize components
    print("🔧 Initializing components...")
    db = get_db()
    scraper = Yad2Scraper()
    analyzer = ContentAnalyzer()
    dispatcher = NotificationDispatcher()
    
    # Get or create a test profile
    print("👤 Setting up user profile...")
    
    # Create a test profile
    test_profile = {
        'profile_name': 'Live Demo Profile',
        'location_criteria': {
            'city': 'תל אביב - יפו',
            'neighborhoods': ['מרכז העיר', 'דיזנגוף', 'רוטשילד'],
            'streets': []
        },
        'price': {'min': 3000, 'max': 8000},
        'rooms': {'min': 1.0, 'max': 3.0},
        'property_type': ['דירה', 'סטודיו'],
        'notification_channels': {
            'telegram': {
                'enabled': True,
                'chat_id': '@aparmntesbot'  # Your bot will figure out the chat ID
            }
        },
        'is_active': True
    }
    
    print(f"✅ Profile: {test_profile['profile_name']}")
    print(f"💰 Price: {test_profile['price']['min']}-{test_profile['price']['max']} ILS")
    print(f"🏠 Rooms: {test_profile['rooms']['min']}-{test_profile['rooms']['max']}")
    print(f"📍 City: {test_profile['location_criteria']['city']}")
    print()
    
    # Start scanning loop
    print("🕷️ Starting live scan...")
    print("⏰ Scanning every 30 seconds (demo mode)")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    scan_count = 0
    try:
        while True:
            scan_count += 1
            print(f"🔄 Scan #{scan_count} - {time.strftime('%H:%M:%S')}")
            
            try:
                # 1. Scrape Yad2
                print("  🕷️ Scraping Yad2...")
                listings = await scraper.scrape_listings(test_profile)
                print(f"  📥 Found {len(listings)} listings")
                
                # 2. Filter and analyze
                new_matches = []
                for listing in listings:
                    # Check if already in database
                    existing = db.get_scanned_listing(listing.listing_id)
                    if existing:
                        continue
                    
                    # Analyze content
                    analysis = analyzer.analyze_listing(listing, test_profile)
                    if analysis.is_match:
                        new_matches.append((listing, analysis))
                        # Store in database
                        db.store_scanned_listing(listing)
                
                print(f"  🎯 New matches: {len(new_matches)}")
                
                # 3. Send notifications
                if new_matches:
                    for listing, analysis in new_matches:
                        print(f"  📱 Sending notification for: {listing.title[:50]}...")
                        
                        # Format message
                        message = f"""🏠 <b>New Apartment Found!</b>

💰 <b>{listing.price} ILS/month</b>
🏠 {listing.rooms} rooms
📍 {listing.location}

{listing.description[:200]}...

<a href="{listing.url}">🔗 View Listing</a>"""
                        
                        # Send via Telegram
                        try:
                            bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
                            # For demo, we'll send to the channel - in real use, 
                            # you'd send to specific user chat IDs from the database
                            await bot.send_message(
                                chat_id=os.getenv('DEMO_CHAT_ID', '@aparmntesbot'),
                                text=message,
                                parse_mode='HTML'
                            )
                            print("  ✅ Notification sent!")
                        except Exception as e:
                            print(f"  ❌ Notification failed: {e}")
                
                else:
                    print("  😴 No new matches this scan")
                
            except Exception as e:
                print(f"  ❌ Scan error: {e}")
            
            print()
            
            # Wait for next scan
            await asyncio.sleep(30)  # 30 seconds for demo
            
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
        print(f"📊 Completed {scan_count} scans")

if __name__ == "__main__":
    print("🚀 Starting RealtyScanner Live Demo...")
    print("📱 Make sure your Telegram bot is running!")
    print()
    
    # Check if bot token is configured
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("❌ TELEGRAM_BOT_TOKEN not configured")
        print("💡 Please set up your .env file first")
        sys.exit(1)
    
    asyncio.run(demo_live_scanning())
