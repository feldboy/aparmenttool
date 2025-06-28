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
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configure logging
log_dir = os.getenv('LOG_DIR', '/app/logs')
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
            from db import get_database
            from notifications.dispatcher import NotificationDispatcher
            
            # Initialize database connection
            self.db = get_database()
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
            
            # Get active profiles from database
            profiles_collection = self.db.user_profiles
            active_profiles = profiles_collection.find({"isActive": True})
            
            profile_count = 0
            total_matches = 0
            
            for profile in active_profiles:
                try:
                    profile_count += 1
                    logger.info(f"Processing profile: {profile.get('profileName', 'Unknown')}")
                    
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
        # Simulate scraping for now (actual implementation would use Yad2Scraper)
        logger.info(f"Scanning Yad2 for profile: {profile['profileName']}")
        
        # Placeholder - return empty list for now
        return []
    
    async def scan_facebook_for_profile(self, profile: Dict[str, Any]):
        """Scan Facebook for a specific profile"""
        # Simulate scraping for now (actual implementation would use FacebookScraper)
        logger.info(f"Scanning Facebook for profile: {profile['profileName']}")
        
        # Placeholder - return empty list for now
        return []
    
    async def analyze_listings(self, profile: Dict[str, Any], listings: list):
        """Analyze listings against profile criteria"""
        if not self.content_analyzer or not listings:
            return []
        
        matches = []
        for listing in listings:
            try:
                # Simulate content analysis
                is_match = await self.simulate_content_analysis(profile, listing)
                if is_match:
                    matches.append(listing)
            except Exception as e:
                logger.error(f"Error analyzing listing: {e}")
                continue
        
        return matches
    
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
            self.db.admin.command('ping')
            
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
    os.makedirs('/app/logs', exist_ok=True)
    
    # Run the worker
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
