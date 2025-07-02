#!/usr/bin/env python3
"""
Live Apartment Scanner - Starts real-time scanning for your profiles
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv()

async def test_real_scanning():
    """Test the real scanning system with your actual profile"""
    print("🏠 RealtyScanner - Starting LIVE Apartment Scanning")
    print("=" * 60)
    
    try:
        # Import database and scrapers
        from db import get_db
        from scrapers.yad2 import Yad2Scraper
        from analysis.content import ContentAnalyzer
        from notifications.dispatcher import NotificationDispatcher
        
        # Initialize components
        db_manager = get_db()
        
        # Ensure database is connected
        if not db_manager.connect():
            print("❌ Failed to connect to database")
            return
            
        yad2_scraper = Yad2Scraper()
        analyzer = ContentAnalyzer()
        dispatcher = NotificationDispatcher()
        
        print("✅ All components initialized")
        
        # Get your actual profile from database
        profiles = db_manager.get_active_user_profiles()
        
        if not profiles:
            print("❌ No active profiles found. Create one via the Telegram bot first!")
            return
        
        profile = profiles[0]  # Use the first active profile
        print(f"🎯 Using profile: {profile.profile_name}")
        print(f"   Budget: {profile.price.min}-{profile.price.max} ILS")
        print(f"   Rooms: {profile.rooms.min}+ rooms")
        
        # Build Yad2 search URL for Tel Aviv
        search_params = {
            'city': 'תל אביב',
            'min_price': profile.price.min,
            'max_price': profile.price.max,
            'min_rooms': profile.rooms.min,
            'property_type': 'rent'
        }
        
        print(f"\n🔍 Searching Yad2 with parameters: {search_params}")
        
        # Scan Yad2 for real listings
        print("🕷️ Starting Yad2 scan...")
        listings = await yad2_scraper.scan_listings(search_params)
        
        print(f"📊 Found {len(listings)} listings from Yad2")
        
        # Analyze each listing
        matches = []
        for i, listing in enumerate(listings, 1):
            print(f"\n📝 Analyzing listing {i}/{len(listings)}...")
            
            # Check if listing matches criteria
            is_match = analyzer.analyze_listing(listing, profile)
            
            if is_match['is_match']:
                matches.append(listing)
                print(f"✅ MATCH! Score: {is_match['score']:.2f}")
                print(f"   📍 {listing.get('location', 'N/A')}")
                print(f"   💰 {listing.get('price', 'N/A')} ILS")
                print(f"   🏠 {listing.get('rooms', 'N/A')} rooms")
            else:
                print(f"❌ No match. Reason: {is_match['reason']}")
        
        print(f"\n🎯 RESULTS: {len(matches)} matches found!")
        
        # Send notifications for matches
        if matches:
            print("\n📱 Sending Telegram notifications...")
            
            # Get Telegram chat ID from profile
            telegram_config = profile.notification_channels.telegram
            chat_id = telegram_config.telegram_chat_id
            
            if not chat_id:
                print("⚠️  No Telegram chat ID found in profile")
                return
            
            for i, match in enumerate(matches, 1):
                try:
                    # Format message
                    message = f"""🏠 New Apartment Match #{i}!

📍 Location: {match.get('location', 'N/A')}
💰 Price: {match.get('price', 'N/A')} ILS
🛏️ Rooms: {match.get('rooms', 'N/A')}
📏 Size: {match.get('size', 'N/A')} sqm

{match.get('description', '')[:200]}...

🔗 View listing: {match.get('url', '')}

⭐ Match Score: {analyzer.analyze_listing(match, profile)['score']:.2f}/1.0
"""
                    
                    # Send notification
                    success = await dispatcher.send_notification(
                        channel="telegram",
                        message=message,
                        recipient=chat_id
                    )
                    
                    if success:
                        print(f"✅ Sent notification {i} to Telegram")
                        
                        # Log in database
                        db.sent_notifications.insert_one({
                            'profileId': profile['_id'],
                            'listingId': match.get('id', 'unknown'),
                            'channel': 'telegram',
                            'recipient': chat_id,
                            'sentAt': analyzer.get_current_time(),
                            'messageContent': message[:200] + '...'
                        })
                        
                    else:
                        print(f"❌ Failed to send notification {i}")
                        
                except Exception as e:
                    print(f"❌ Error sending notification {i}: {e}")
        
        else:
            print("ℹ️  No matches found this time. The scanner will keep looking!")
        
        print("\n🎉 Live scan completed!")
        print("💡 To run continuous scanning: python scripts/run_worker.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_scanning())
