#!/usr/bin/env python3
"""
Test different Yad2 URLs to find the correct format
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_yad2_urls():
    """Test different Yad2 URL formats"""
    print("🔗 Testing Different Yad2 URL Formats")
    print("=" * 40)
    
    # Load environment
    load_dotenv(".env.scraping")
    
    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
    if not firecrawl_api_key:
        print("❌ FIRECRAWL_API_KEY not found in environment")
        return
    
    # Test different URL formats
    test_urls = [
        # Current format from scraper
        "https://www.yad2.co.il/realestate/rent?priceMin=4000&priceMax=8000&rooms=2.0-4.0&city=5000&propertyGroup=1",
        
        # Simplified format
        "https://www.yad2.co.il/realestate/rent?city=5000",
        
        # Most basic rental URL
        "https://www.yad2.co.il/realestate/rent",
        
        # Alternative format
        "https://www.yad2.co.il/realestate/rent?topArea=2&area=14&city=5000",
        
        # Tel Aviv specific
        "https://www.yad2.co.il/realestate/rent?topArea=2&area=14&city=5000&rooms=2-4&price=4000-8000"
    ]
    
    for i, test_url in enumerate(test_urls):
        print(f"\n🔗 Testing URL {i+1}: {test_url}")
        
        try:
            # Configure Firecrawl request
            config = {
                "pageOptions": {
                    "waitFor": 5000,
                    "screenshot": False,
                    "includeHtml": True,
                    "onlyMainContent": False
                }
            }
            
            # Make request to Firecrawl
            firecrawl_url = "https://api.firecrawl.dev/v0/scrape"
            payload = {
                "url": test_url,
                **config
            }
            
            headers = {
                "Authorization": f"Bearer {firecrawl_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(firecrawl_url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    data = result.get("data", {})
                    html_content = data.get("html", "")
                    
                    # Parse HTML
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Check page title
                    title = soup.find('title')
                    page_title = title.get_text() if title else "No title"
                    print(f"   📄 Page title: {page_title}")
                    
                    # Check if we're on a search results page
                    if "השכרה" in page_title or "rent" in page_title.lower():
                        print("   ✅ Looks like a rental search page")
                        
                        # Look for listing indicators
                        listing_indicators = [
                            'div[data-testid="feed-item"]',
                            '.feeditem',
                            '.feed_item',
                            '[data-item-id]',
                            'div[data-testid*="item"]'
                        ]
                        
                        found_listings = False
                        for selector in listing_indicators:
                            elements = soup.select(selector)
                            if elements:
                                print(f"   🎯 Found {len(elements)} elements with: {selector}")
                                found_listings = True
                                
                                # Save this response for further analysis
                                filename = f"working_yad2_response_{i+1}.html"
                                with open(filename, 'w', encoding='utf-8') as f:
                                    f.write(html_content)
                                print(f"   💾 Saved response to {filename}")
                                break
                        
                        if not found_listings:
                            print("   ❌ No listing elements found")
                    else:
                        print("   ❌ Not a rental search page")
                        
                    # Check for common elements that might indicate listing structure
                    common_checks = [
                        ('script', 'window.__INITIAL_STATE__'),
                        ('script', 'window.__NUXT__'),
                        ('div', 'data-testid'),
                        ('div', 'class*="feed"'),
                        ('div', 'class*="item"')
                    ]
                    
                    for tag, attr_check in common_checks:
                        if 'window.' in attr_check:
                            scripts = soup.find_all('script')
                            for script in scripts:
                                if script.string and attr_check in script.string:
                                    print(f"   🔍 Found {attr_check} in script tag")
                                    break
                        elif 'data-testid' in attr_check:
                            elements = soup.find_all('div', attrs={'data-testid': True})
                            if elements:
                                testids = [elem.get('data-testid') for elem in elements[:5]]
                                print(f"   🔍 Found data-testid elements: {testids}")
                        elif 'class*=' in attr_check:
                            class_pattern = attr_check.split('*=')[1].strip('"')
                            elements = soup.find_all('div', class_=lambda x: x and class_pattern in ' '.join(x).lower())
                            if elements:
                                print(f"   🔍 Found {len(elements)} divs with class containing '{class_pattern}'")
                
                else:
                    print(f"   ❌ Firecrawl failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Add delay between requests
        import time
        time.sleep(2)

if __name__ == "__main__":
    test_yad2_urls()
