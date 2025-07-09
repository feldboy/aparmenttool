#!/usr/bin/env python3
"""
Quick test to verify Firecrawl API key is working
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_firecrawl_api():
    """Test Firecrawl API connectivity"""
    print("🔥 Testing Firecrawl API...")
    
    # Load environment
    load_dotenv(".env.scraping")
    
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("❌ No Firecrawl API key found")
        return False
    
    print(f"API Key: {api_key[:10]}...")
    
    try:
        # Test with a simple scrape request instead of test endpoint
        payload = {
            "url": "https://httpbin.org/get",
            "pageOptions": {
                "waitFor": 1000,
                "includeHtml": True
            }
        }
        
        response = requests.post(
            "https://api.firecrawl.dev/v0/scrape",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Firecrawl API key is valid!")
                print(f"   Scrape successful: {len(result.get('data', {}).get('html', ''))} chars")
                return True
            else:
                print(f"❌ API error: {result.get('error', 'Unknown error')}")
                return False
        elif response.status_code == 401:
            print("❌ Invalid API key - check your Firecrawl API key")
            return False
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_simple_scrape():
    """Test a simple scrape with Firecrawl"""
    print("\n🕷️  Testing Yad2 scrape...")
    
    load_dotenv(".env.scraping")
    api_key = os.getenv("FIRECRAWL_API_KEY")
    
    if not api_key:
        print("❌ No API key available")
        return False
    
    try:
        # Test scraping Yad2 homepage to see if we can bypass ShieldSquare
        payload = {
            "url": "https://www.yad2.co.il/realestate/rent",
            "pageOptions": {
                "waitFor": 5000,
                "includeHtml": True,
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            }
        }
        
        print("   Testing Yad2 scrape (this may take 30-60 seconds)...")
        
        response = requests.post(
            "https://api.firecrawl.dev/v0/scrape",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=90
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                html = result.get('data', {}).get('html', '')
                print(f"✅ Yad2 scrape successful!")
                print(f"   Content length: {len(html)} chars")
                
                # Check if we got actual content or ShieldSquare protection
                if "validate.perfdrive.com" in html or "ShieldSquare" in html:
                    print("⚠️  ShieldSquare protection detected - may need proxy/better config")
                    return False
                elif "דירות להשכרה" in html or "apartments" in html.lower():
                    print("🎉 Successfully bypassed protection! Found apartment listings.")
                    return True
                else:
                    print("❓ Unclear if protection was bypassed - check content manually")
                    return True
            else:
                print(f"❌ Scrape failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during scrape: {e}")
        return False

def main():
    print("🚀 Firecrawl API Test")
    print("=" * 30)
    
    # Test API connectivity
    if test_firecrawl_api():
        # Test simple scrape
        test_simple_scrape()
    
    print("\n" + "=" * 30)
    print("Test complete!")

if __name__ == "__main__":
    main()
