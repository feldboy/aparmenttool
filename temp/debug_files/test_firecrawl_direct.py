#!/usr/bin/env python3
"""
Test Firecrawl scraper directly
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_firecrawl_scraper():
    """Test Firecrawl scraper directly"""
    print("🔥 Testing Firecrawl Yad2 Scraper")
    print("=" * 35)
    
    # Load environment
    load_dotenv(".env.scraping")
    
    try:
        from src.scrapers.firecrawl_yad2 import FirecrawlYad2Scraper
        
        # Initialize scraper
        print("Initializing Firecrawl scraper...")
        scraper = FirecrawlYad2Scraper()
        print("✅ Firecrawl scraper initialized")
        
        # Test URL
        test_url = "https://www.yad2.co.il/realestate/rent?priceMin=4000&priceMax=8000&rooms=2.0-4.0&city=5000&propertyGroup=1"
        print(f"🔍 Test URL: {test_url}")
        
        # Test scraping
        print("\n🚀 Starting Firecrawl scraping test...")
        print("   This may take 60-120 seconds due to anti-bot protection...")
        
        listings = scraper.scrape_listings(test_url, max_listings=3)
        
        if listings:
            print(f"🎉 SUCCESS! Found {len(listings)} listings with Firecrawl")
            print("\n📋 Sample listings:")
            for i, listing in enumerate(listings[:3]):
                print(f"\n   {i+1}. {listing.title}")
                print(f"      Price: {listing.price} ₪" if listing.price else "      Price: Not specified")
                print(f"      Location: {listing.location}")
                print(f"      Rooms: {listing.rooms}" if listing.rooms else "      Rooms: Not specified")
                print(f"      URL: {listing.url}")
        else:
            print("❌ No listings found with Firecrawl")
            print("   Possible causes:")
            print("   - Firecrawl API issues")
            print("   - ShieldSquare protection is too strong")
            print("   - Website structure has changed")
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure firecrawl-py is installed: pip install firecrawl-py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_firecrawl_scraper()
