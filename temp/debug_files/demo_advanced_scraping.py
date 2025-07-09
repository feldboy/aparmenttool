#!/usr/bin/env python3
"""
Demo script for advanced Yad2 scraping with ShieldSquare bypass

This script demonstrates how to use the FirecrawlYad2Scraper to
bypass ShieldSquare protection and scrape Yad2 listings.
"""

import os
import sys
import time
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scrapers.firecrawl_yad2 import FirecrawlYad2Scraper
from src.scrapers.config import ScrapingConfig
from src.scrapers.captcha_solver import get_captcha_solver, detect_captcha_type
from src.db import get_db

def load_environment():
    """Load environment variables"""
    # Load main .env file
    load_dotenv()
    
    # Load scraping-specific .env file
    load_dotenv(".env.scraping")
    
    print("🔧 Environment loaded")

def create_test_profile():
    """Create a test user profile for scraping"""
    profile = {
        "profile_name": "Demo Profile",
        "location_criteria": {
            "city": "תל אביב",
            "neighborhoods": ["רמת אביב", "פלורנטין", "נווה צדק"],
            "streets": []
        },
        "price": {
            "min": 4000,
            "max": 8000
        },
        "rooms": {
            "min": 2.0,
            "max": 4.0
        },
        "property_type": ["דירה", "סטודיו"],
        "scan_targets": {
            "yad2_url": None,  # Will be constructed
            "facebook_group_ids": []
        },
        "notification_channels": {
            "telegram": {"enabled": False},
            "whatsapp": {"enabled": False},
            "email": {"enabled": False}
        }
    }
    
    return profile

def demonstrate_firecrawl_scraping():
    """Demonstrate Firecrawl-based scraping"""
    print("\n🔥 Firecrawl Scraping Demo")
    print("=" * 50)
    
    # Check if Firecrawl is configured
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    if not firecrawl_key:
        print("❌ Firecrawl API key not found in environment")
        print("   Please run: python setup_advanced_scraping.py")
        return
    
    # Create scraper instance
    try:
        scraper = FirecrawlYad2Scraper(
            firecrawl_api_key=firecrawl_key,
            proxy_config=get_proxy_config()
        )
        print("✅ Firecrawl scraper initialized")
    except Exception as e:
        print(f"❌ Error initializing scraper: {e}")
        return
    
    # Create test profile
    profile = create_test_profile()
    
    # Construct search URL
    search_url = scraper.construct_search_url(profile)
    print(f"🔍 Search URL: {search_url}")
    
    # Start scraping
    print("🚀 Starting scraping process...")
    print("   This may take 30-60 seconds due to anti-detection measures...")
    
    start_time = time.time()
    
    try:
        listings = scraper.scrape_listings(search_url, max_listings=10)
        
        elapsed_time = time.time() - start_time
        print(f"⏱️  Scraping completed in {elapsed_time:.2f} seconds")
        
        if listings:
            print(f"✅ Successfully scraped {len(listings)} listings!")
            
            # Display first few listings
            for i, listing in enumerate(listings[:3]):
                print(f"\n📋 Listing {i+1}:")
                print(f"   ID: {listing.listing_id}")
                print(f"   Title: {listing.title}")
                print(f"   Price: {listing.price} ₪" if listing.price else "   Price: Not specified")
                print(f"   Rooms: {listing.rooms}" if listing.rooms else "   Rooms: Not specified")
                print(f"   Location: {listing.location}")
                print(f"   URL: {listing.url}")
            
            if len(listings) > 3:
                print(f"\n... and {len(listings) - 3} more listings")
            
            # Save to database if available
            save_to_database(listings)
            
        else:
            print("❌ No listings found")
            print("   This might indicate:")
            print("   - ShieldSquare protection is still active")
            print("   - Search criteria are too restrictive")
            print("   - Website structure has changed")
            
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        print("   This might indicate:")
        print("   - ShieldSquare protection detected the bot")
        print("   - Network connectivity issues")
        print("   - Firecrawl API issues")

def get_proxy_config():
    """Get proxy configuration from environment"""
    proxy_endpoints = os.getenv("PROXY_ENDPOINTS")
    if not proxy_endpoints:
        return None
    
    return {
        "type": os.getenv("PROXY_TYPE", "residential"),
        "endpoints": proxy_endpoints.split(","),
        "username": os.getenv("PROXY_USERNAME"),
        "password": os.getenv("PROXY_PASSWORD")
    }

def save_to_database(listings):
    """Save scraped listings to database"""
    try:
        db = get_db()
        if not db.client:
            print("⚠️  Database not available - skipping save")
            return
        
        saved_count = 0
        for listing in listings:
            # Check if listing already exists
            if not db.is_listing_seen(listing.listing_id, "Yad2"):
                # Create ScannedListing object
                from src.db import ScannedListing, ListingSource
                import hashlib
                
                # Create content hash
                content_hash = hashlib.sha256(
                    f"{listing.title}_{listing.price}_{listing.location}".encode()
                ).hexdigest()
                
                scanned_listing = ScannedListing(
                    listing_id=listing.listing_id,
                    source=ListingSource.YAD2,
                    content_hash=content_hash,
                    url=listing.url or "",
                    raw_data=listing.raw_data or {}
                )
                
                db.add_scanned_listing(scanned_listing)
                saved_count += 1
        
        print(f"💾 Saved {saved_count} new listings to database")
        
    except Exception as e:
        print(f"❌ Error saving to database: {e}")

def demonstrate_captcha_handling():
    """Demonstrate CAPTCHA handling capabilities"""
    print("\n🤖 CAPTCHA Handling Demo")
    print("=" * 50)
    
    captcha_api_key = os.getenv("CAPTCHA_API_KEY")
    if not captcha_api_key:
        print("⚠️  CAPTCHA solver not configured")
        print("   CAPTCHA challenges will be logged but not solved")
        return
    
    solver_type = os.getenv("CAPTCHA_SOLVER", "2captcha")
    print(f"✅ CAPTCHA solver configured: {solver_type}")
    
    # Test balance check
    from src.scrapers.config import CaptchaConfig, CaptchaSolver
    
    try:
        config = CaptchaConfig(
            solver=CaptchaSolver(solver_type),
            api_key=captcha_api_key
        )
        
        solver = get_captcha_solver(config)
        if solver:
            balance = solver.get_balance()
            if balance is not None:
                print(f"💰 Account balance: ${balance:.2f}")
            else:
                print("⚠️  Could not check account balance")
        
    except Exception as e:
        print(f"❌ Error checking CAPTCHA solver: {e}")

def demonstrate_proxy_rotation():
    """Demonstrate proxy rotation capabilities"""
    print("\n🌐 Proxy Rotation Demo")
    print("=" * 50)
    
    proxy_config = get_proxy_config()
    if not proxy_config:
        print("⚠️  No proxy configuration found")
        print("   Scraping will use direct connection")
        return
    
    print(f"✅ Proxy type: {proxy_config['type']}")
    print(f"✅ Proxy endpoints: {len(proxy_config['endpoints'])}")
    
    # Test proxy connectivity (simplified)
    import requests
    
    for i, endpoint in enumerate(proxy_config['endpoints'][:3]):  # Test first 3
        try:
            proxy_dict = {
                'http': f"http://{proxy_config['username']}:{proxy_config['password']}@{endpoint}",
                'https': f"https://{proxy_config['username']}:{proxy_config['password']}@{endpoint}"
            }
            
            response = requests.get(
                "http://httpbin.org/ip",
                proxies=proxy_dict,
                timeout=10
            )
            
            if response.status_code == 200:
                ip_info = response.json()
                print(f"✅ Proxy {i+1}: {ip_info.get('origin', 'Unknown IP')}")
            else:
                print(f"❌ Proxy {i+1}: Connection failed")
                
        except Exception as e:
            print(f"❌ Proxy {i+1}: {str(e)}")

def show_configuration_summary():
    """Show current configuration summary"""
    print("\n📋 Configuration Summary")
    print("=" * 50)
    
    # Firecrawl
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    print(f"🔥 Firecrawl API: {'✅ Configured' if firecrawl_key else '❌ Not configured'}")
    
    # Proxy
    proxy_endpoints = os.getenv("PROXY_ENDPOINTS")
    print(f"🌐 Proxy Service: {'✅ Configured' if proxy_endpoints else '❌ Not configured'}")
    
    # CAPTCHA
    captcha_key = os.getenv("CAPTCHA_API_KEY")
    print(f"🤖 CAPTCHA Solver: {'✅ Configured' if captcha_key else '❌ Not configured'}")
    
    # Database
    try:
        db = get_db()
        db_status = "✅ Connected" if db.client else "❌ Not connected"
    except:
        db_status = "❌ Not available"
    print(f"💾 Database: {db_status}")
    
    # Behavioral settings
    min_interval = os.getenv("MIN_REQUEST_INTERVAL", "2.0")
    max_interval = os.getenv("MAX_REQUEST_INTERVAL", "8.0")
    print(f"⏱️  Request Interval: {min_interval}-{max_interval} seconds")
    
    print("\n📊 Anti-Detection Features:")
    features = [
        ("User-Agent Rotation", os.getenv("ROTATE_USER_AGENTS", "true")),
        ("Header Randomization", os.getenv("RANDOMIZE_HEADERS", "true")),
        ("Human Behavior Simulation", os.getenv("SIMULATE_HUMAN_BEHAVIOR", "true")),
        ("Bot Pattern Avoidance", os.getenv("AVOID_BOT_PATTERNS", "true"))
    ]
    
    for feature, enabled in features:
        status = "✅ Enabled" if enabled.lower() == "true" else "❌ Disabled"
        print(f"   {feature}: {status}")

def main():
    """Main demo function"""
    print("🚀 Advanced Yad2 Scraping Demo")
    print("ShieldSquare Bypass with Firecrawl")
    print("=" * 50)
    
    # Load environment
    load_environment()
    
    # Show configuration
    show_configuration_summary()
    
    # Check if minimum requirements are met
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    if not firecrawl_key:
        print("\n❌ Firecrawl API key not found!")
        print("   Please run: python setup_advanced_scraping.py")
        return
    
    # Interactive menu
    while True:
        print("\n🎛️  Choose a demo:")
        print("1. 🔥 Firecrawl Scraping Demo")
        print("2. 🤖 CAPTCHA Handling Demo")
        print("3. 🌐 Proxy Rotation Demo")
        print("4. 📋 Configuration Summary")
        print("5. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            demonstrate_firecrawl_scraping()
        elif choice == "2":
            demonstrate_captcha_handling()
        elif choice == "3":
            demonstrate_proxy_rotation()
        elif choice == "4":
            show_configuration_summary()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
