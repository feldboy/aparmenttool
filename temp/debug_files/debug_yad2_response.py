#!/usr/bin/env python3
"""
Debug script to inspect Yad2 response content
"""

import requests
import time
from bs4 import BeautifulSoup

def debug_yad2_response():
    """Debug what we're actually getting from Yad2"""
    print("🔍 Debugging Yad2 Response")
    print("=" * 30)
    
    # Test URL
    test_url = "https://www.yad2.co.il/realestate/rent?priceMin=4000&priceMax=8000&rooms=2.0-4.0&city=5000&propertyGroup=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print(f"📥 Fetching: {test_url}")
        response = requests.get(test_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Content Length: {len(response.content)} bytes")
        
        # Check for protection
        content = response.text
        protection_indicators = [
            "validate.perfdrive.com",
            "ShieldSquare",
            "Bot Management",
            "human verification",
            "security check",
            "Please wait while we verify",
            "Checking your browser",
            "blocked"
        ]
        
        protection_detected = False
        for indicator in protection_indicators:
            if indicator.lower() in content.lower():
                print(f"🚫 Protection detected: {indicator}")
                protection_detected = True
        
        if not protection_detected:
            print("✅ No protection detected")
        
        # Save response for inspection
        with open('debug_yad2_response.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("💾 Saved response to debug_yad2_response.html")
        
        # Parse and look for listing elements
        soup = BeautifulSoup(content, 'html.parser')
        
        # Check for various listing selectors
        selectors = [
            'div[data-testid="feed-item"]',
            '.feeditem',
            '.feed_item', 
            '[data-item-id]',
            '.feed-list-item',
            '.result-item',
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"🎯 Found {len(elements)} elements with selector: {selector}")
                # Save a sample element
                if elements:
                    print(f"📋 Sample element HTML (first 500 chars):")
                    print(str(elements[0])[:500])
                return
        
        # Check for any divs that might contain listings
        feed_divs = soup.find_all('div', class_=lambda x: x and ('feed' in x.lower() or 'item' in x.lower() or 'listing' in x.lower()))
        if feed_divs:
            print(f"🔍 Found {len(feed_divs)} potential listing divs")
            print(f"📋 Sample div classes: {[div.get('class') for div in feed_divs[:5]]}")
        
        # Look for any script tags that might contain data
        scripts = soup.find_all('script')
        data_scripts = [s for s in scripts if s.string and ('window.' in s.string or 'listings' in s.string.lower() or 'data' in s.string.lower())]
        if data_scripts:
            print(f"🔍 Found {len(data_scripts)} scripts that might contain data")
            for i, script in enumerate(data_scripts[:3]):
                script_content = script.string[:200] if script.string else "No content"
                print(f"   Script {i+1}: {script_content}...")
        
        # Check page title and meta
        title = soup.find('title')
        if title:
            print(f"📄 Page title: {title.get_text()}")
        
        # Count total divs for reference
        all_divs = soup.find_all('div')
        print(f"📊 Total divs in page: {len(all_divs)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_yad2_response()
