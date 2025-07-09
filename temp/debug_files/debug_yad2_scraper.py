#!/usr/bin/env python3
"""
Debug script for Yad2 scraper to identify and fix current issues
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_different_user_agents():
    """Test different user agents to find one that works"""
    print("🔍 Testing different user agents...")
    
    user_agents = [
        # Desktop browsers
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        
        # Mobile browsers (often bypass protection)
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    ]
    
    test_urls = [
        "https://www.yad2.co.il/realestate/rent",
        "https://www.yad2.co.il/realestate/rent?city=5000&priceMax=8000",
        "https://www.yad2.co.il",
    ]
    
    results = []
    
    for i, ua in enumerate(user_agents):
        print(f"\\n🧪 Testing User Agent {i+1}: {'Mobile' if 'Mobile' in ua or 'iPhone' in ua else 'Desktop'}")
        
        for url in test_urls:
            try:
                headers = {
                    'User-Agent': ua,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                print(f"  📡 Testing: {url}")
                response = requests.get(url, headers=headers, timeout=15)
                
                # Check for ShieldSquare protection
                shieldsquare_detected = any(indicator in response.text.lower() for indicator in [
                    'validate.perfdrive.com', 'shieldsquare', 'bot management',
                    'human verification', 'security check', 'captcha', 'blocked'
                ])
                
                # Check for actual content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for signs of real Yad2 content
                yad2_indicators = [
                    'data-testid="feed-item"',
                    'class="feeditem"',
                    'realestate',
                    'listing',
                    'דירות להשכרה',
                ]
                
                content_found = any(indicator in response.text for indicator in yad2_indicators)
                
                status = "✅ SUCCESS" if not shieldsquare_detected and content_found else (
                    "🛡️ BLOCKED" if shieldsquare_detected else "⚠️ NO_CONTENT"
                )
                
                print(f"    {status} - Status: {response.status_code}, Length: {len(response.content)}")
                
                results.append({
                    'user_agent': ua,
                    'url': url,
                    'status_code': response.status_code,
                    'content_length': len(response.content),
                    'shieldsquare_detected': shieldsquare_detected,
                    'content_found': content_found,
                    'success': not shieldsquare_detected and content_found
                })
                
                # Save successful responses
                if not shieldsquare_detected and content_found:
                    filename = f"successful_response_{i+1}_{len(results)}.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"    💾 Saved response to {filename}")
                
                time.sleep(2)  # Be polite
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                results.append({
                    'user_agent': ua,
                    'url': url,
                    'error': str(e),
                    'success': False
                })
    
    # Summary
    print("\\n📊 SUMMARY:")
    successful = [r for r in results if r.get('success', False)]
    print(f"✅ Successful requests: {len(successful)}/{len(results)}")
    
    if successful:
        print("\\n🎯 Working configurations:")
        for result in successful:
            ua_type = 'Mobile' if 'Mobile' in result['user_agent'] or 'iPhone' in result['user_agent'] else 'Desktop'
            print(f"  - {ua_type}: {result['url']}")
    
    return results

def test_firecrawl_integration():
    """Test Firecrawl API integration"""
    print("\\n🔥 Testing Firecrawl integration...")
    
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("❌ No Firecrawl API key found in environment")
        return False
    
    try:
        # Test with a simple Yad2 URL
        test_url = "https://www.yad2.co.il/realestate/rent"
        
        firecrawl_url = "https://api.firecrawl.dev/v0/scrape"
        payload = {
            "url": test_url,
            "pageOptions": {
                "waitFor": 5000,
                "screenshot": False,
                "includeHtml": True,
                "includeRawHtml": True,
                "onlyMainContent": False
            }
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        print(f"📡 Testing Firecrawl with: {test_url}")
        response = requests.post(firecrawl_url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                data = result.get("data", {})
                html_content = data.get("html", "")
                markdown_content = data.get("markdown", "")
                
                print(f"✅ Firecrawl successful!")
                print(f"📄 HTML length: {len(html_content)}")
                print(f"📝 Markdown length: {len(markdown_content)}")
                
                # Save response for analysis
                with open("firecrawl_response.json", 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                if html_content:
                    with open("firecrawl_response.html", 'w', encoding='utf-8') as f:
                        f.write(html_content)
                
                if markdown_content:
                    with open("firecrawl_response.md", 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                
                print("💾 Saved Firecrawl responses to files")
                
                # Check for ShieldSquare protection
                shieldsquare_detected = any(indicator in html_content.lower() for indicator in [
                    'validate.perfdrive.com', 'shieldsquare', 'bot management'
                ])
                
                if shieldsquare_detected:
                    print("🛡️ ShieldSquare protection still detected in Firecrawl response")
                else:
                    print("✅ No ShieldSquare protection detected in Firecrawl response")
                
                return True
            else:
                print(f"❌ Firecrawl failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Firecrawl API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Firecrawl: {str(e)}")
        return False

def analyze_current_yad2_structure():
    """Analyze the current HTML structure of Yad2 pages"""
    print("\\n🔍 Analyzing current Yad2 HTML structure...")
    
    # Look for any saved successful responses
    response_files = [f for f in os.listdir('.') if f.startswith('successful_response') and f.endswith('.html')]
    
    if not response_files:
        print("❌ No successful response files found. Run user agent test first.")
        return
    
    for file in response_files[:2]:  # Analyze first 2 files
        print(f"\\n📄 Analyzing {file}...")
        
        try:
            with open(file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for listing containers with various selectors
            selectors_to_try = [
                'div[data-testid="feed-item"]',
                '.feeditem',
                '.feed_item',
                '[data-item-id]',
                '.feed-list-item',
                '.result-item',
                '[class*="listing"]',
                '[class*="item"]',
                '[data-testid*="item"]',
                '[id*="item"]',
            ]
            
            print("🔍 Looking for listing containers...")
            for selector in selectors_to_try:
                elements = soup.select(selector)
                if elements:
                    print(f"  ✅ Found {len(elements)} elements with selector: {selector}")
                    
                    # Analyze first element
                    if elements:
                        first_elem = elements[0]
                        print(f"    📋 First element classes: {first_elem.get('class', [])}")
                        print(f"    📋 First element attributes: {list(first_elem.attrs.keys())}")
                        
                        # Look for price, title, location in this element
                        price_elem = first_elem.find(text=re.compile(r'\\d+.*₪'))
                        if price_elem:
                            print(f"    💰 Found price pattern: {price_elem.strip()}")
                        
                        # Save sample element for detailed analysis
                        with open(f"sample_element_{len(elements)}.html", 'w', encoding='utf-8') as f:
                            f.write(str(first_elem))
                else:
                    print(f"  ❌ No elements found with selector: {selector}")
            
            # Look for specific Yad2 patterns
            print("\\n🏠 Looking for Yad2-specific patterns...")
            
            # Check for modern React/JS patterns
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and ('feed' in script.string.lower() or 'listing' in script.string.lower()):
                    print("  📜 Found potential listing data in JavaScript")
                    # Look for JSON data
                    import re
                    json_pattern = r'\\{[^{}]*"(id|price|title|rooms)"[^{}]*\\}'
                    matches = re.findall(json_pattern, script.string)
                    if matches:
                        print(f"    🎯 Found {len(matches)} JSON-like structures")
            
            # Check for data attributes
            elements_with_data = soup.find_all(attrs={"data-testid": True})
            if elements_with_data:
                print(f"  📊 Found {len(elements_with_data)} elements with data-testid")
                testids = set(elem.get('data-testid') for elem in elements_with_data)
                print(f"    🏷️ Unique testids: {sorted(testids)}")
                
        except Exception as e:
            print(f"❌ Error analyzing {file}: {str(e)}")

def main():
    """Run all debugging tests"""
    print("🔧 Yad2 Scraper Debug Tool")
    print("=" * 50)
    
    # Test 1: User agents
    ua_results = test_different_user_agents()
    
    # Test 2: Firecrawl
    firecrawl_working = test_firecrawl_integration()
    
    # Test 3: HTML structure analysis
    analyze_current_yad2_structure()
    
    # Final recommendations
    print("\\n🎯 RECOMMENDATIONS:")
    successful_ua = [r for r in ua_results if r.get('success', False)]
    
    if successful_ua:
        print("✅ Use mobile user agents - they bypass ShieldSquare protection")
        mobile_ua = next((r for r in successful_ua if 'Mobile' in r['user_agent'] or 'iPhone' in r['user_agent']), None)
        if mobile_ua:
            print(f"💡 Recommended UA: {mobile_ua['user_agent'][:80]}...")
    
    if firecrawl_working:
        print("✅ Firecrawl is working as a backup option")
    else:
        print("❌ Firecrawl needs configuration - run setup_advanced_scraping.py")
    
    print("\\n🔄 Next steps:")
    print("1. Update Yad2Scraper to use mobile user agent")
    print("2. Fix URL construction for current Yad2 API")
    print("3. Update HTML parsing selectors")
    print("4. Test with real scraping")

if __name__ == "__main__":
    main()
