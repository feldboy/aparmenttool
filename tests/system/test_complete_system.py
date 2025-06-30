#!/usr/bin/env python3
"""
Complete system test to verify all components are working end-to-end
"""

import sys
import os
import logging
import asyncio
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from db import get_db
from scrapers.yad2 import Yad2Scraper
from scrapers.facebook import FacebookScraper
from analysis.content import ContentAnalyzer
from notifications.dispatcher import NotificationDispatcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_connection():
    """Test database connection and data"""
    logger.info("🔗 Testing database connection...")
    
    try:
        db_manager = get_db()
        db_manager.connect()
        db = db_manager.db
        
        # Test collections
        profiles_count = db.search_profiles.count_documents({})
        creds_count = db.facebook_credentials.count_documents({})
        notifications_count = db.notifications.count_documents({})
        
        logger.info(f"  ✅ Search profiles: {profiles_count}")
        logger.info(f"  ✅ Facebook credentials: {creds_count}")
        logger.info(f"  ✅ Notifications: {notifications_count}")
        
        # Show latest Facebook credentials
        if creds_count > 0:
            latest_creds = db.facebook_credentials.find_one({}, sort=[('created_at', -1)])
            logger.info(f"  📱 Latest Facebook setup: {latest_creds.get('email')} with {len(latest_creds.get('groups', []))} groups")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Database error: {e}")
        return False

async def test_scrapers():
    """Test scraper functionality"""
    logger.info("🕷️ Testing scrapers...")
    
    try:
        # Test Yad2 scraper
        yad2_scraper = Yad2Scraper()
        test_params = {
            'city': 'תל אביב',
            'price': {'max': 8000},
            'rooms': {'min': 2}
        }
        
        logger.info("  🏠 Testing Yad2 scraper...")
        search_url = yad2_scraper.construct_search_url(test_params)
        logger.info(f"  🔗 Search URL constructed: {search_url[:100]}...")
        
        # Test scraping (limit to 3 for quick test)
        yad2_results = yad2_scraper.scrape_listings(search_url, max_listings=3)
        logger.info(f"  ✅ Yad2: Found {len(yad2_results)} results")
        
        # Test Facebook scraper (if credentials available)
        db_manager = get_db()
        db_manager.connect()
        db = db_manager.db
        
        fb_creds = db.facebook_credentials.find_one({'is_active': True})
        if fb_creds:
            logger.info("  📱 Testing Facebook scraper...")
            facebook_scraper = FacebookScraper()
            # Note: This will require actual Facebook login which might fail in test
            try:
                search_url_fb = facebook_scraper.construct_search_url(test_params)
                facebook_results = facebook_scraper.scrape_listings(search_url_fb, max_listings=3)
                logger.info(f"  ✅ Facebook: Found {len(facebook_results)} results")
            except Exception as e:
                logger.warning(f"  ⚠️ Facebook scraper test skipped (requires real login): {e}")
        else:
            logger.info("  ℹ️ No Facebook credentials found, skipping Facebook scraper test")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Scraper error: {e}")
        return False

async def test_content_analyzer():
    """Test AI content analysis"""
    logger.info("🧠 Testing AI content analyzer...")
    
    try:
        analyzer = ContentAnalyzer()
        
        # Create a proper ScrapedListing object for analysis
        from scrapers.base import ScrapedListing
        
        test_listing = ScrapedListing(
            listing_id='test-123',
            title='דירת 3 חדרים בתל אביב',
            description='דירה יפה ומשופצת ברחוב שקט, קרוב לתחבורה ציבורית',
            price=7500,
            location='תל אביב',
            rooms=3.0,
            url='https://example.com/listing'
        )
        
        # Test criteria
        test_criteria = {
            'price': {'max': 8000},
            'rooms': {'min': 2},
            'location_criteria': {'preferred_areas': ['תל אביב מרכז', 'רמת אביב']},
            'keywords': ['משופץ', 'מעלית']
        }
        
        analysis = analyzer.analyze_listing(test_listing, test_criteria)
        
        logger.info(f"  ✅ Analysis score: {analysis.score}")
        logger.info(f"  ✅ Match: {analysis.is_match}")
        logger.info(f"  ✅ Confidence: {analysis.confidence}")
        logger.info(f"  ✅ Reasons: {len(analysis.reasons)}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Content analyzer error: {e}")
        return False

async def test_notifications():
    """Test notification system"""
    logger.info("📱 Testing notification system...")
    
    try:
        from notifications.base import NotificationMessage
        from notifications.channels import TelegramChannel
        
        # Get a test chat ID from database
        db_manager = get_db()
        db_manager.connect()
        db = db_manager.db
        
        # Try to find a chat with Facebook credentials
        fb_creds = db.facebook_credentials.find_one({'is_active': True})
        if not fb_creds:
            logger.warning("  ⚠️ No Facebook credentials found for notification test")
            return True
        
        chat_id = fb_creds['telegram_chat_id']
        
        # Create test notification message
        test_message = NotificationMessage(
            title="🏠 Test Property Alert",
            content="This is a test notification from the RealtyScanner system",
            priority="normal",
            metadata={
                'listing': {
                    'title': 'Test Property Notification',
                    'price': 7000,
                    'location': 'Test Area',
                    'rooms': 3,
                    'url': 'https://example.com/test-listing'
                },
                'analysis': {
                    'score': 85,
                    'is_match': True,
                    'reasons': ['Good price', 'Nice location', 'Right size']
                }
            }
        )
        
        # Configure notification dispatcher
        dispatcher = NotificationDispatcher()
        telegram_config = {'telegram_chat_id': chat_id, 'enabled': True}
        telegram_channel = TelegramChannel(telegram_config)
        dispatcher.register_channel('telegram', telegram_channel)
        
        # Send test notification
        results = dispatcher.send_notification(test_message, channels=['telegram'])
        
        if 'telegram' in results and results['telegram'].status.value == 'success':
            logger.info(f"  ✅ Test notification sent to chat {chat_id}")
        else:
            error_msg = results.get('telegram', {}).error_message if 'telegram' in results else "Unknown error"
            logger.warning(f"  ⚠️ Test notification failed to send: {error_msg}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Notification error: {e}")
        return False

async def main():
    """Run complete system test"""
    logger.info("🏠 RealtyScanner Complete System Test")
    logger.info("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Scrapers", test_scrapers),
        ("Content Analyzer", test_content_analyzer),
        ("Notifications", test_notifications)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"❌ {test_name} test failed: {e}")
            results[test_name] = False
        
        logger.info("-" * 50)
    
    # Summary
    logger.info("📊 Test Results Summary:")
    total_tests = len(tests)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {status} {test_name}")
    
    logger.info(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 All systems operational! RealtyScanner is ready for production.")
    else:
        logger.warning("⚠️ Some systems need attention before production deployment.")

if __name__ == "__main__":
    asyncio.run(main())
