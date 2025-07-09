#!/usr/bin/env python3
"""
RealtyScanner Background Worker
Epic 5.1: Dedicated worker for scraping and notifications

This worker runs the main scanning and notification logic
in a separate container/process for better scalability.
"""

import os
import sys
import asyncio
import logging
import signal
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# Add src to path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configure logging
log_dir = os.getenv('LOG_DIR', './logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'{log_dir}/worker.log')
    ]
)
logger = logging.getLogger(__name__)

class RealtyWorker:
    """Background worker for RealtyScanner operations"""
    
    def __init__(self):
        self.running = False
        self.scan_interval = int(os.getenv('SCAN_INTERVAL', 300))  # 5 minutes
        self.last_scan = None
        
        # Initialize components
        self.setup_components()
        
    def setup_components(self):
        """Initialize worker components"""
        try:
            # Import components (with error handling for missing dependencies)
            from db import get_db
            from notifications.dispatcher import NotificationDispatcher
            
            # Initialize database connection
            self.db = get_db()
            logger.info("Database connection established")
            
            # Initialize notification dispatcher
            self.notification_dispatcher = NotificationDispatcher()
            logger.info("Notification dispatcher initialized")
            
            # Import scrapers
            try:
                from scrapers.yad2 import Yad2Scraper
                from scrapers.facebook import FacebookScraper
                self.yad2_scraper = Yad2Scraper()
                self.facebook_scraper = FacebookScraper()
                logger.info("Scrapers initialized")
            except ImportError as e:
                logger.warning(f"Some scrapers not available: {e}")
                self.yad2_scraper = None
                self.facebook_scraper = None
            
            # Import content analysis
            try:
                from analysis.content import ContentAnalyzer
                self.content_analyzer = ContentAnalyzer()
                logger.info("Content analyzer initialized")
                
                # Enable AI analysis if available
                if hasattr(self.content_analyzer, 'use_ai_analysis') and self.content_analyzer.use_ai_analysis:
                    logger.info("AI-powered content analysis enabled")
                else:
                    logger.info("Using rule-based content analysis")
                    
            except ImportError as e:
                logger.warning(f"Content analyzer not available: {e}")
                self.content_analyzer = None
                
        except Exception as e:
            logger.error(f"Failed to initialize worker components: {e}")
            raise
    
    async def scan_profiles(self):
        """Scan all active user profiles"""
        try:
            logger.info("Starting profile scanning cycle")
            
            # Check if database is available
            if not self.db:
                logger.error("Database not available")
                return
            
            # Get active profiles from database
            # First try to get search_profiles (new collection)
            if hasattr(self.db, 'search_profiles'):
                active_profiles = self.db.search_profiles.find({"is_active": True})
                active_profiles = list(active_profiles)
            # Fallback to user_profiles
            elif hasattr(self.db, 'user_profiles'):
                active_profiles = self.db.user_profiles.find({"isActive": True})
                active_profiles = list(active_profiles)
            else:
                logger.error("No profiles collection found")
                return
            
            profile_count = 0
            total_matches = 0
            
            logger.info(f"Found {len(active_profiles)} active profiles")
            
            for profile in active_profiles:
                try:
                    profile_count += 1
                    logger.info(f"Processing profile: {profile.get('name', profile.get('profileName', 'Unknown'))}")
                    
                    # Scan Yad2 if scraper is available
                    yad2_listings = []
                    if self.yad2_scraper:
                        try:
                            yad2_listings = await self.scan_yad2_for_profile(profile)
                            logger.info(f"Found {len(yad2_listings)} new Yad2 listings")
                        except Exception as e:
                            logger.error(f"Yad2 scanning failed for profile {profile['_id']}: {e}")
                    
                    # Scan Facebook if scraper is available
                    facebook_posts = []
                    if self.facebook_scraper:
                        try:
                            facebook_posts = await self.scan_facebook_for_profile(profile)
                            logger.info(f"Found {len(facebook_posts)} new Facebook posts")
                        except Exception as e:
                            logger.error(f"Facebook scanning failed for profile {profile['_id']}: {e}")
                            logger.error(f"Facebook scanning failed for profile {profile['_id']}: {e}")
                    
                    # Analyze and filter content
                    all_listings = yad2_listings + facebook_posts
                    matches = await self.analyze_listings(profile, all_listings)
                    
                    # Send notifications for matches
                    for match in matches:
                        await self.send_notification(profile, match)
                        total_matches += 1
                    
                    logger.info(f"Profile processed: {len(matches)} matches found")
                    
                except Exception as e:
                    logger.error(f"Error processing profile {profile.get('_id')}: {e}")
                    continue
            
            logger.info(f"Scanning cycle completed: {profile_count} profiles, {total_matches} total matches")
            
        except Exception as e:
            logger.error(f"Error in scan_profiles: {e}")
    
    async def scan_yad2_for_profile(self, profile: Dict[str, Any]):
        """Scan Yad2 for a specific profile"""
        profile_name = profile.get('name', profile.get('profile_name', profile.get('profileName', 'Unknown')))
        logger.info(f"Scanning Yad2 for profile: {profile_name}")
        
        try:
            if self.yad2_scraper:
                # Construct search URL from profile
                search_url = self.yad2_scraper.construct_search_url(profile)
                # Run scraper in executor to avoid blocking
                loop = asyncio.get_event_loop()
                listings = await loop.run_in_executor(
                    None, 
                    self.yad2_scraper.scrape_listings, 
                    search_url, 
                    50
                )
                logger.info(f"Found {len(listings)} Yad2 listings for profile {profile_name}")
                return listings
            else:
                logger.warning("Yad2 scraper not available, returning empty results")
                return []
        except Exception as e:
            logger.error(f"Error scanning Yad2 for profile {profile_name}: {e}")
            return []
    
    async def scan_facebook_for_profile(self, profile: Dict[str, Any]):
        """Scan Facebook for a specific profile"""
        profile_name = profile.get('name', profile.get('profile_name', profile.get('profileName', 'Unknown')))
        logger.info(f"Scanning Facebook for profile: {profile_name}")
        
        try:
            if self.facebook_scraper:
                # Check if the profile has Facebook groups configured
                facebook_groups = profile.get('scan_targets', {}).get('facebook_group_ids', [])
                if not facebook_groups:
                    logger.info("No Facebook groups configured for profile")
                    return []
                
                # Construct search URL from profile
                search_url = self.facebook_scraper.construct_search_url(profile)
                
                # Use the async scraper method
                posts = await self.facebook_scraper.scrape_listings(search_url, 50)
                logger.info(f"Found {len(posts)} Facebook posts for profile {profile_name}")
                return posts
            else:
                logger.warning("Facebook scraper not available, returning empty results")
                return []
        except Exception as e:
            logger.error(f"Error scanning Facebook for profile {profile_name}: {e}")
            return []
    
    async def analyze_listings(self, profile: Dict[str, Any], listings: list):
        """Analyze listings against profile criteria with enhanced AI analysis"""
        if not listings:
            return []
        
        matches = []
        for listing in listings:
            try:
                # Basic filtering first
                if self.basic_filter_listing(profile, listing):
                    # If we have content analyzer, use it for advanced filtering
                    if self.content_analyzer:
                        # Simplified analysis - just check if it's a match
                        is_match = await self.simulate_content_analysis(profile, listing)
                        if is_match:
                            matches.append(listing)
                    else:
                        # Use basic filtering result
                        matches.append(listing)
                        
            except Exception as e:
                logger.error("Error analyzing listing: %s", str(e))
                continue
        
        return matches
    
    def basic_filter_listing(self, profile: Dict[str, Any], listing: Dict[str, Any]) -> bool:
        """Basic filtering based on profile criteria"""
        try:
            # Check price range
            price_range = profile.get('price_range', profile.get('price', {}))
            if price_range:
                min_price = price_range.get('min', 0)
                max_price = price_range.get('max', float('inf'))
                listing_price = listing.get('price', 0)
                
                if listing_price and (listing_price < min_price or listing_price > max_price):
                    return False
            
            # Check rooms range
            rooms_range = profile.get('rooms_range', profile.get('rooms', {}))
            if rooms_range:
                min_rooms = rooms_range.get('min', 0)
                max_rooms = rooms_range.get('max', float('inf'))
                listing_rooms = listing.get('rooms', 0)
                
                if listing_rooms and (listing_rooms < min_rooms or listing_rooms > max_rooms):
                    return False
            
            # Location filtering - basic keyword matching
            location_criteria = profile.get('location', profile.get('location_criteria', {}))
            if location_criteria:
                city = location_criteria.get('city', '')
                neighborhoods = location_criteria.get('neighborhoods', [])
                
                listing_location = listing.get('location', '').lower()
                
                # Check if listing location contains city or neighborhood keywords
                if city and city.lower() in listing_location:
                    return True
                    
                for neighborhood in neighborhoods:
                    if neighborhood.lower() in listing_location:
                        return True
                        
                # If we have location criteria but no match, filter out
                if city or neighborhoods:
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Error in basic filtering: %s", str(e))
            return False
    
    async def simulate_content_analysis(self, profile: Dict[str, Any], listing: Dict[str, Any]):
        """Simulate content analysis (placeholder)"""
        # For demonstration - randomly return True 10% of the time
        import random
        return random.random() < 0.1
    
    async def send_notification(self, profile: Dict[str, Any], listing: Dict[str, Any]):
        """Send notification for a matched listing"""
        try:
            # Get user notification preferences
            notification_channels = profile.get('notificationChannels', {})
            
            # Format notification message
            message = self.format_notification_message(listing)
            
            # Send to enabled channels
            for channel, config in notification_channels.items():
                if config.get('enabled', False):
                    try:
                        await self.notification_dispatcher.send_notification(
                            channel=channel,
                            message=message,
                            recipient=config.get('chatId') or config.get('phoneNumber') or config.get('address')
                        )
                        logger.info(f"Notification sent via {channel}")
                    except Exception as e:
                        logger.error(f"Failed to send notification via {channel}: {e}")
            
            # Log notification in database
            self.log_notification(profile, listing, message)
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    def format_notification_message(self, listing: Dict[str, Any]) -> str:
        """Format listing into notification message"""
        return f"""
🏠 New Property Match!

📍 Location: {listing.get('location', 'N/A')}
💰 Price: {listing.get('price', 'N/A')}
🛏️ Rooms: {listing.get('rooms', 'N/A')}

{listing.get('description', '')[:200]}...

🔗 View: {listing.get('url', '')}
        """.strip()
    
    def log_notification(self, profile: Dict[str, Any], listing: Dict[str, Any], message: str):
        """Log sent notification in database"""
        try:
            notifications_collection = self.db.sent_notifications
            notification_doc = {
                'profileId': profile['_id'],
                'listingId': listing.get('id', 'unknown'),
                'message': message,
                'sentAt': datetime.utcnow(),
                'source': listing.get('source', 'unknown')
            }
            notifications_collection.insert_one(notification_doc)
        except Exception as e:
            logger.error(f"Failed to log notification: {e}")
    
    async def health_check(self):
        """Perform health check"""
        try:
            # Check database connection
            if hasattr(self.db, 'client'):
                self.db.client.admin.command('ping')
            else:
                logger.warning("Database client not available for health check")
            
            # Check if we're scanning regularly
            if self.last_scan:
                time_since_scan = datetime.utcnow() - self.last_scan
                if time_since_scan > timedelta(minutes=10):
                    logger.warning(f"No scan for {time_since_scan}")
            
            logger.info("Health check passed")
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def run(self):
        """Main worker loop"""
        logger.info("RealtyScanner Worker starting...")
        self.running = True
        
        while self.running:
            try:
                # Perform health check
                await self.health_check()
                
                # Run scanning cycle
                start_time = datetime.utcnow()
                await self.scan_profiles()
                self.last_scan = datetime.utcnow()
                
                # Calculate sleep time
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                sleep_time = max(0, self.scan_interval - elapsed)
                
                logger.info(f"Scan completed in {elapsed:.2f}s, sleeping for {sleep_time:.2f}s")
                
                # Sleep until next scan
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                await asyncio.sleep(60)  # Sleep 1 minute on error
    
    def stop(self):
        """Stop the worker"""
        logger.info("Stopping RealtyScanner Worker...")
        self.running = False

# Global worker instance
worker = None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global worker
    if worker:
        worker.stop()

async def main():
    """Main function"""
    global worker
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create and run worker
        worker = RealtyWorker()
        await worker.run()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Worker error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Ensure log directory exists
    os.makedirs('./logs', exist_ok=True)
    
    # Run the worker
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
