#!/usr/bin/env python3
"""
Save Firecrawl response to analyze HTML structure
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scrapers.firecrawl_yad2 import FirecrawlYad2Scraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_firecrawl_response():
    """Save Firecrawl response for analysis"""
    print("🔥 Fetching and saving Firecrawl response...")
    
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
    print(f"📍 URL: {search_url}")
    
    # Get raw Firecrawl response
    scraped_data = scraper._scrape_with_firecrawl(search_url)
    
    if scraped_data:
        html_content = scraped_data.get("html", "")
        
        # Save HTML content
        with open("firecrawl_yad2_response.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Save full JSON response
        with open("firecrawl_yad2_response.json", "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved HTML response ({len(html_content)} chars) to firecrawl_yad2_response.html")
        print(f"💾 Saved JSON response to firecrawl_yad2_response.json")
        
        # Quick analysis
        print(f"\n📊 Quick Analysis:")
        print(f"  HTML size: {len(html_content)} characters")
        print(f"  Contains 'validate.perfdrive.com': {'validate.perfdrive.com' in html_content}")
        print(f"  Contains 'feed-item': {'feed-item' in html_content}")
        print(f"  Contains 'feeditem': {'feeditem' in html_content}")
        print(f"  Contains 'item-id': {'item-id' in html_content}")
        print(f"  Contains 'listing': {'listing' in html_content}")
        print(f"  Contains href links: {html_content.count('href=')}")
        print(f"  Contains ₪ symbol: {'₪' in html_content}")
        
    else:
        print("❌ Failed to get Firecrawl response")

if __name__ == "__main__":
    save_firecrawl_response()
