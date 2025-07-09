#!/usr/bin/env python3
"""
Test different strategies to bypass Yad2 ShieldSquare protection

This script tests multiple approaches to access Yad2 real estate listings
while avoiding ShieldSquare anti-bot protection.
"""

import requests
import time
import random
import os
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Yad2BypassTester:
    """Main class for testing different Yad2 bypass strategies"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'successful_strategies': [],
            'failed_strategies': [],
            'saved_files': []
        }
        
        # Create output directory
        self.output_dir = 'yad2_bypass_results'
        os.makedirs(self.output_dir, exist_ok=True)


    def test_strategy_1_different_user_agents(self):
        """Test with different user agents and headers"""
        strategy_name = "Different User Agents"
        logger.info(f"=== Strategy 1: {strategy_name} ===")
        
        user_agents = [
            # Mobile user agents (often less blocked)
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 14; Mobile; rv:109.0) Gecko/118.0 Firefox/118.0',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            
            # Older browser versions
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            
            # Real browser headers from automation tools
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/120.0.0.0 Safari/537.36',
        ]
        
        base_url = "https://www.yad2.co.il/realestate/rent"
        
        for i, ua in enumerate(user_agents):
            logger.info(f"Trying User Agent {i+1}: {ua[:50]}...")
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': ua,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            try:
                # Add delay to appear human-like
                time.sleep(random.uniform(2, 5))
                
                response = session.get(base_url, timeout=15)
                logger.info(f"Status: {response.status_code}, Length: {len(response.content)}")
                
                # Check for ShieldSquare
                if 'shieldsquare' in response.text.lower() or 'captcha' in response.text.lower():
                    logger.warning("❌ ShieldSquare detected")
                    continue
                else:
                    logger.info("✅ No ShieldSquare detected")
                    
                    # Look for listings
                    content_check = self._check_apartment_content(response.text)
                    
                    if content_check['has_content']:
                        logger.info("✅ Found Hebrew apartment content")
                        
                        # Save this successful response
                        filename = f'{self.output_dir}/successful_ua_response_{i+1}.html'
                        self._save_response(response.text, filename)
                        
                        self.results['successful_strategies'].append({
                            'strategy': strategy_name,
                            'user_agent': ua,
                            'file': filename,
                            'content_stats': content_check
                        })
                        
                        return response.text
                    else:
                        logger.warning("❌ No apartment content found")
                        
            except requests.RequestException as e:
                logger.error(f"❌ Request Error: {e}")
            except Exception as e:
                logger.error(f"❌ Unexpected Error: {e}")
        
        self.results['failed_strategies'].append(strategy_name)
        return None


    def _check_apartment_content(self, html_content):
        """Check if the HTML content contains apartment listings"""
        # Check for Hebrew text indicating apartments
        hebrew_indicators = ['דירות', 'להשכרה', 'חדרים', 'ש"ח', '₪']
        found_indicators = [indicator for indicator in hebrew_indicators if indicator in html_content]
        
        # Parse content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Count price elements
        price_elements = soup.find_all(string=lambda text: text and '₪' in text)
        
        # Count room elements
        room_elements = soup.find_all(string=lambda text: text and ('חדר' in text or 'חד' in text))
        
        return {
            'has_content': len(found_indicators) > 0,
            'found_indicators': found_indicators,
            'price_count': len(price_elements),
            'room_count': len(room_elements)
        }
    
    def _save_response(self, content, filename):
        """Save response content to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            self.results['saved_files'].append(filename)
            logger.info("Saved response to %s", filename)
        except Exception as e:
            logger.error("Failed to save file %s: %s", filename, e)


def test_strategy_2_simple_search():
    """Test with very simple search URL"""
    print("\n=== Strategy 2: Simple Search URLs ===")
    
    # Try different simple URLs
    urls = [
        "https://www.yad2.co.il/realestate/rent",
        "https://www.yad2.co.il/realestate/rent?city=5000",  # Tel Aviv
        "https://www.yad2.co.il/realestate/rent?priceMin=3000",
        "https://m.yad2.co.il/realestate/rent",  # Mobile version
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'he-IL,he;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    })
    
    for url in urls:
        print(f"\nTrying URL: {url}")
        
        try:
            time.sleep(random.uniform(2, 4))
            response = session.get(url, timeout=15)
            print(f"Status: {response.status_code}, Length: {len(response.content)}")
            
            if 'shieldsquare' in response.text.lower():
                print("❌ ShieldSquare detected")
            else:
                print("✅ No ShieldSquare detected")
                
                # Look for apartment listings content
                if 'דירות' in response.text or 'להשכרה' in response.text:
                    print("✅ Found apartment content")
                    
                    # Parse and look for listing containers
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Try different selectors
                    selectors = [
                        'div[data-testid="feed-item"]',
                        '.feeditem',
                        '.feed_item', 
                        '[data-item-id]',
                        '.feed-list-item',
                        '.result-item',
                        'div[class*="feed"]',
                        'div[class*="item"]',
                        'div[class*="listing"]',
                    ]
                    
                    for selector in selectors:
                        containers = soup.select(selector)
                        if containers:
                            print(f"✅ Found {len(containers)} containers with selector: {selector}")
                            
                            # Save this successful response
                            with open('successful_simple_search.html', 'w', encoding='utf-8') as f:
                                f.write(response.text)
                            print("Saved response to successful_simple_search.html")
                            return response.text
                    
                    print("❌ No listing containers found with known selectors")
                else:
                    print("❌ No apartment content found")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None


def test_strategy_3_api_endpoints():
    """Test potential API endpoints"""
    print("\n=== Strategy 3: API Endpoints ===")
    
    # Common API patterns for real estate sites
    api_urls = [
        "https://www.yad2.co.il/api/pre-load/getFeed/realestate/rent",
        "https://www.yad2.co.il/api/search/realestate/rent",
        "https://api.yad2.co.il/search/realestate/rent",
        "https://www.yad2.co.il/api/feed/realestate/rent",
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.yad2.co.il/',
        'X-Requested-With': 'XMLHttpRequest',
    })
    
    for url in api_urls:
        print(f"\nTrying API URL: {url}")
        
        try:
            time.sleep(random.uniform(1, 3))
            response = session.get(url, timeout=15)
            print(f"Status: {response.status_code}, Length: {len(response.content)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Got JSON response with {len(data)} items")
                    
                    # Save successful API response
                    with open('successful_api_response.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print("Saved response to successful_api_response.json")
                    return data
                except:
                    print("❌ Response is not valid JSON")
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None


def analyze_page_structure(html_content):
    """Analyze the structure of a successful page"""
    print("\n=== Analyzing Page Structure ===")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for common patterns
    print("Looking for potential listing containers...")
    
    # Find all divs with classes that might contain listings
    all_divs = soup.find_all('div')
    interesting_divs = []
    
    for div in all_divs:
        if div.get('class'):
            class_str = ' '.join(div['class']).lower()
            if any(keyword in class_str for keyword in ['feed', 'item', 'listing', 'card', 'result']):
                interesting_divs.append((div, class_str))
    
    print(f"Found {len(interesting_divs)} interesting divs")
    
    for i, (div, class_str) in enumerate(interesting_divs[:10]):  # Show first 10
        print(f"{i+1}. Class: {class_str}")
        print(f"   Content preview: {div.get_text()[:100]}...")
    
    # Look for price patterns
    price_patterns = soup.find_all(text=lambda text: text and '₪' in text)
    print(f"\nFound {len(price_patterns)} elements with ₪ symbol")
    
    # Look for room patterns
    room_patterns = soup.find_all(text=lambda text: text and ('חדר' in text or 'חד' in text))
    print(f"Found {len(room_patterns)} elements with room indicators")


if __name__ == "__main__":
    print("Testing different strategies to bypass Yad2 ShieldSquare protection...\n")
    
    # Try each strategy
    success_content = None
    
    # Strategy 1: Different user agents
    success_content = test_strategy_1_different_user_agents()
    
    if not success_content:
        # Strategy 2: Simple URLs
        success_content = test_strategy_2_simple_search()
    
    if not success_content:
        # Strategy 3: API endpoints
        api_data = test_strategy_3_api_endpoints()
        if api_data:
            print("✅ Found working API endpoint!")
    
    if success_content:
        analyze_page_structure(success_content)
        print("\n✅ Success! Found a working approach.")
    else:
        print("\n❌ All strategies failed. ShieldSquare protection is very strong.")
