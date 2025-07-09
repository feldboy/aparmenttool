#!/usr/bin/env python3
"""
Test the fixed Firecrawl configuration for Yad2 scraping
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scrapers.firecrawl_yad2 import FirecrawlYad2Scraper

def test_yad2_scraping():
    """Test Yad2 scraping with fixed configuration"""
    print("🏠 Testing Yad2 Scraping with Firecrawl")
    print("=" * 40)
    
    # Load environment
    load_dotenv(".env.scraping")
    
    try:
        # Initialize scraper
        scraper = FirecrawlYad2Scraper()
        print("✅ Scraper initialized")
        
        # Create test profile
        profile = {
            "location_criteria": {"city": "תל אביב"},
            "price": {"min": 4000, "max": 8000},
            "rooms": {"min": 2.0, "max": 4.0},
            "property_type": ["דירה"]
        }
        
        # Construct search URL
        search_url = scraper.construct_search_url(profile)
        print(f"🔍 Search URL: {search_url}")
        
        # Test scraping
        print("\n🚀 Starting scraping test...")
        print("   This may take 30-60 seconds...")
        
        listings = scraper.scrape_listings(search_url, max_listings=5)
        
        if listings:
            print(f"🎉 SUCCESS! Found {len(listings)} listings")
            print("\n📋 Sample listings:")
            
            for i, listing in enumerate(listings[:3]):
                print(f"\n   {i+1}. {listing.title}")
                print(f"      Price: {listing.price} ₪" if listing.price else "      Price: Not specified")
                print(f"      Location: {listing.location}")
                print(f"      Rooms: {listing.rooms}" if listing.rooms else "      Rooms: Not specified")
                print(f"      URL: {listing.url}")
        else:
            print("❌ No listings found")
            print("   This could mean:")
            print("   - ShieldSquare protection is still active")
            print("   - Search criteria are too restrictive")
            print("   - Website structure has changed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_yad2_scraping()
