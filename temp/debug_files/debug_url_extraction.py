#!/usr/bin/env python3
"""
Debug script to test URL extraction from Yad2 scraper
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scrapers.yad2 import Yad2Scraper
from scrapers.firecrawl_yad2 import FirecrawlYad2Scraper
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_yad2_scraper():
    """Test the basic Yad2 scraper"""
    print("🕷️ Testing basic Yad2 scraper...")
    
    scraper = Yad2Scraper()
    
    # Test URL construction
    profile_config = {
        'price': {'min': 3000, 'max': 8000},
        'rooms': {'min': 2, 'max': 4},
        'location_criteria': {'city': 'תל אביב'},
        'property_type': ['דירה']
    }
    
    search_url = scraper.construct_search_url(profile_config)
    print(f"📍 Constructed search URL: {search_url}")
    
    # Try to scrape listings
    listings = scraper.scrape_listings(search_url, max_listings=5)
    print(f"🏠 Found {len(listings)} listings")
    
    for i, listing in enumerate(listings, 1):
        print(f"\n📋 Listing {i}:")
        print(f"  ID: {listing.listing_id}")
        print(f"  Title: {listing.title}")
        print(f"  Price: {listing.price}")
        print(f"  URL: {listing.url}")
        print(f"  Location: {listing.location}")
        
        if not listing.url:
            print("  ⚠️ WARNING: No URL extracted!")
            print(f"  Raw HTML snippet: {listing.raw_data.get('html_snippet', 'N/A')[:200]}...")

def test_firecrawl_scraper():
    """Test the Firecrawl Yad2 scraper"""
    print("\n🔥 Testing Firecrawl Yad2 scraper...")
    
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("❌ No FIRECRAWL_API_KEY found in environment")
        return
    
    scraper = FirecrawlYad2Scraper(firecrawl_api_key=api_key)
    
    # Test URL construction
    profile_config = {
        'price': {'min': 3000, 'max': 8000},
        'rooms': {'min': 2, 'max': 4},
        'location_criteria': {'city': 'תל אביב'},
        'property_type': ['דירה']
    }
    
    search_url = scraper.construct_search_url(profile_config)
    print(f"📍 Constructed search URL: {search_url}")
    
    # Try to scrape listings
    listings = scraper.scrape_listings(search_url, max_listings=5)
    print(f"🏠 Found {len(listings)} listings")
    
    for i, listing in enumerate(listings, 1):
        print(f"\n📋 Listing {i}:")
        print(f"  ID: {listing.listing_id}")
        print(f"  Title: {listing.title}")
        print(f"  Price: {listing.price}")
        print(f"  URL: {listing.url}")
        print(f"  Location: {listing.location}")
        
        if not listing.url:
            print("  ⚠️ WARNING: No URL extracted!")
            print(f"  Raw HTML snippet: {listing.raw_data.get('html_snippet', 'N/A')[:200]}...")

if __name__ == "__main__":
    print("🔍 Debugging Yad2 URL extraction...")
    print("=" * 50)
    
    try:
        test_yad2_scraper()
        test_firecrawl_scraper()
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
