#!/usr/bin/env python3
"""
Advanced Yad2 URL testing with different approaches
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_yad2_advanced():
    """Test Yad2 with more sophisticated approaches"""
    print("🎯 Advanced Yad2 Testing")
    print("=" * 30)
    
    # Load environment
    load_dotenv(".env.scraping")
    
    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
    if not firecrawl_api_key:
        print("❌ FIRECRAWL_API_KEY not found in environment")
        return
    
    # Try different strategies
    strategies = [
        {
            "name": "Strategy 1: Basic rental page with longer wait",
            "url": "https://www.yad2.co.il/realestate/rent",
            "config": {
                "pageOptions": {
                    "waitFor": 15000,  # Wait 15 seconds
                    "screenshot": False,
                    "includeHtml": True,
                    "onlyMainContent": False,
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                        "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
                        "Accept-Encoding": "gzip, deflate, br",
                        "DNT": "1",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1"
                    }
                }
            }
        },
        {
            "name": "Strategy 2: Tel Aviv specific with wait for selector", 
            "url": "https://www.yad2.co.il/realestate/rent",
            "config": {
                "pageOptions": {
                    "waitFor": "div[data-testid]",  # Wait for specific element
                    "screenshot": False,
                    "includeHtml": True,
                    "onlyMainContent": False
                }
            }
        },
        {
            "name": "Strategy 3: With actions to simulate user behavior",
            "url": "https://www.yad2.co.il/realestate/rent",
            "config": {
                "pageOptions": {
                    "waitFor": 10000,
                    "screenshot": False,
                    "includeHtml": True,
                    "onlyMainContent": False,
                    "actions": [
                        {"type": "wait", "milliseconds": 3000},
                        {"type": "scroll", "y": 500},
                        {"type": "wait", "milliseconds": 2000}
                    ]
                }
            }
        }
    ]
    
    for strategy in strategies:
        print(f"\n🔬 {strategy['name']}")
        print(f"URL: {strategy['url']}")
        
        try:
            # Make request to Firecrawl
            firecrawl_url = "https://api.firecrawl.dev/v0/scrape"
            payload = {
                "url": strategy['url'],
                **strategy['config']
            }
            
            headers = {
                "Authorization": f"Bearer {firecrawl_api_key}",
                "Content-Type": "application/json"
            }
            
            print("   🚀 Making request...")
            response = requests.post(firecrawl_url, json=payload, headers=headers, timeout=120)
            
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
                    print(f"   📄 Title: {page_title}")
                    
                    # Look for rental-specific content
                    rental_indicators = [
                        "השכרה",
                        "דירות להשכרה",
                        "rent",
                        "rental",
                        "apartment for rent"
                    ]
                    
                    is_rental_page = any(indicator in page_title for indicator in rental_indicators)
                    
                    if is_rental_page:
                        print("   ✅ Rental page detected!")
                    else:
                        # Check if content has rental indicators
                        page_text = soup.get_text()
                        rental_count = sum(1 for indicator in rental_indicators if indicator in page_text)
                        print(f"   📊 Rental indicators in content: {rental_count}")
                    
                    # Look for listing structures
                    potential_selectors = [
                        'div[data-testid*="feed"]',
                        'div[data-testid*="item"]',
                        'div[data-testid*="listing"]',
                        'div[class*="feed"]',
                        'div[class*="item"]',
                        'div[class*="listing"]',
                        'article',
                        '[data-item-id]'
                    ]
                    
                    found_structures = []
                    for selector in potential_selectors:
                        elements = soup.select(selector)
                        if elements:
                            found_structures.append(f"{selector}: {len(elements)} elements")
                    
                    if found_structures:
                        print("   🎯 Found potential listing structures:")
                        for structure in found_structures[:5]:  # Show first 5
                            print(f"      {structure}")
                    else:
                        print("   ❌ No potential listing structures found")
                    
                    # Check for JavaScript data
                    scripts = soup.find_all('script')
                    js_data_found = False
                    for script in scripts:
                        if script.string:
                            script_text = script.string
                            if any(keyword in script_text for keyword in ['__INITIAL_STATE__', '__NUXT__', 'window.DATA', 'listings', 'properties']):
                                print("   🔍 Found JavaScript data that might contain listings")
                                js_data_found = True
                                break
                    
                    if not js_data_found:
                        print("   ❌ No JavaScript data found")
                    
                    # Save response for the most promising strategy
                    if is_rental_page or found_structures:
                        filename = f"strategy_{strategy['name'].split()[1].replace(':', '')}_response.html"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        print(f"   💾 Saved response to {filename}")
                
                else:
                    print(f"   ❌ Firecrawl failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Wait between strategies
        time.sleep(5)

if __name__ == "__main__":
    test_yad2_advanced()
