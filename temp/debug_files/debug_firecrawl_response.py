#!/usr/bin/env python3
"""
Debug Firecrawl response content
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

def debug_firecrawl_response():
    """Debug what Firecrawl returns for Yad2"""
    print("🔥 Debugging Firecrawl Response for Yad2")
    print("=" * 40)
    
    # Load environment
    load_dotenv(".env.scraping")
    
    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
    if not firecrawl_api_key:
        print("❌ FIRECRAWL_API_KEY not found in environment")
        return
    
    print(f"✅ Using Firecrawl API key: {firecrawl_api_key[:10]}...")
    
    # Test URL
    test_url = "https://www.yad2.co.il/realestate/rent?priceMin=4000&priceMax=8000&rooms=2.0-4.0&city=5000&propertyGroup=1"
    print(f"🔍 Test URL: {test_url}")
    
    try:
        # Configure Firecrawl request
        config = {
            "pageOptions": {
                "waitFor": 8000,  # Wait 8 seconds
                "screenshot": False,
                "fullPageScreenshot": False,
                "includeHtml": True,
                "includeRawHtml": True,
                "onlyMainContent": False
            },
            "crawlerOptions": {
                "maxDepth": 1,
                "limit": 1,
                "allowBackwardCrawling": False,
                "allowExternalContentLinks": False
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
        
        print("🚀 Making Firecrawl request...")
        print("   This may take 30-60 seconds...")
        
        response = requests.post(firecrawl_url, json=payload, headers=headers, timeout=120)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Save full response for inspection
            with open('firecrawl_full_response.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print("💾 Saved full response to firecrawl_full_response.json")
            
            # Check for success
            if result.get("success"):
                print("✅ Firecrawl request successful")
                
                data = result.get("data", {})
                html_content = data.get("html", "")
                markdown = data.get("markdown", "")
                
                print(f"📄 HTML content length: {len(html_content)} chars")
                print(f"📝 Markdown content length: {len(markdown)} chars")
                
                if html_content:
                    # Save HTML for inspection
                    with open('firecrawl_yad2_response.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print("💾 Saved HTML to firecrawl_yad2_response.html")
                    
                    # Check for protection
                    protection_indicators = [
                        "validate.perfdrive.com",
                        "ShieldSquare",
                        "Bot Management",
                        "human verification",
                        "security check",
                        "Please wait while we verify",
                        "Checking your browser",
                        "captcha",
                        "blocked",
                        "Access denied"
                    ]
                    
                    protection_detected = False
                    html_lower = html_content.lower()
                    for indicator in protection_indicators:
                        if indicator.lower() in html_lower:
                            print(f"🚫 Protection detected: {indicator}")
                            protection_detected = True
                    
                    if not protection_detected:
                        print("✅ No protection detected in Firecrawl response")
                        
                        # Parse and look for listing elements
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Check page title
                        title = soup.find('title')
                        if title:
                            print(f"📄 Page title: {title.get_text()}")
                        
                        # Check for various listing selectors
                        selectors = [
                            'div[data-testid="feed-item"]',
                            'div[data-testid="listing-item"]',
                            '.feeditem',
                            '.feed_item',
                            '[data-item-id]',
                            '.feed-list-item',
                            '.result-item',
                            '.item-wrapper',
                            '.listing-item',
                            '.property-item'
                        ]
                        
                        found_listings = False
                        for selector in selectors:
                            elements = soup.select(selector)
                            if elements:
                                print(f"🎯 Found {len(elements)} elements with selector: {selector}")
                                found_listings = True
                                # Save a sample element
                                if elements:
                                    print(f"📋 Sample element HTML (first 300 chars):")
                                    print(str(elements[0])[:300])
                                break
                        
                        if not found_listings:
                            print("❌ No listing elements found with known selectors")
                            
                            # Look for any divs that might contain listings
                            all_divs = soup.find_all('div')
                            print(f"📊 Total divs in page: {len(all_divs)}")
                            
                            # Look for divs with classes that might be listings
                            potential_divs = []
                            for div in all_divs:
                                classes = div.get('class', [])
                                if any('feed' in cls.lower() or 'item' in cls.lower() or 'listing' in cls.lower() 
                                      for cls in classes):
                                    potential_divs.append(div)
                            
                            if potential_divs:
                                print(f"🔍 Found {len(potential_divs)} potential listing divs")
                                print(f"📋 Sample classes: {[div.get('class') for div in potential_divs[:5]]}")
                
                if markdown:
                    # Save markdown for inspection
                    with open('firecrawl_yad2_markdown.txt', 'w', encoding='utf-8') as f:
                        f.write(markdown)
                    print("💾 Saved markdown to firecrawl_yad2_markdown.txt")
                    
                    # Look for listing patterns in markdown
                    lines = markdown.split('\n')
                    listing_keywords = ['₪', 'חדרים', 'rooms', 'מ"ר', 'sqm', 'דירה', 'apartment']
                    
                    potential_listings = 0
                    for line in lines:
                        if any(keyword in line.lower() for keyword in listing_keywords):
                            potential_listings += 1
                    
                    if potential_listings > 0:
                        print(f"📝 Found {potential_listings} potential listing lines in markdown")
                        
                        # Show sample lines
                        print("📋 Sample listing lines:")
                        count = 0
                        for line in lines:
                            if any(keyword in line.lower() for keyword in listing_keywords) and count < 3:
                                print(f"   {line.strip()}")
                                count += 1
            else:
                print(f"❌ Firecrawl request failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_firecrawl_response()
