#!/usr/bin/env python3
"""
Debug script to analyze what Firecrawl is returning from Yad2
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

def debug_yad2_response():
    """Debug what Firecrawl returns from Yad2"""
    print("🔍 Debugging Yad2 Response")
    print("=" * 30)
    
    load_dotenv(".env.scraping")
    api_key = os.getenv("FIRECRAWL_API_KEY")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    # More sophisticated configuration to bypass ShieldSquare
    payload = {
        "url": "https://www.yad2.co.il/realestate/rent?priceMin=4000&priceMax=8000&city=5000",
        "pageOptions": {
            "waitFor": 8000,  # Wait 8 seconds
            "includeHtml": True,
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Cache-Control": "max-age=0",
                "Sec-CH-UA": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-CH-UA-Mobile": "?0",
                "Sec-CH-UA-Platform": '"macOS"'
            }
        }
    }
    
    print("🚀 Making request to Firecrawl...")
    print("   URL:", payload["url"])
    print("   Wait time:", payload["pageOptions"]["waitFor"], "ms")
    
    try:
        response = requests.post(
            "https://api.firecrawl.dev/v0/scrape",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=120  # 2 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                html = result.get("data", {}).get("html", "")
                markdown = result.get("data", {}).get("markdown", "")
                
                print(f"✅ Request successful!")
                print(f"   HTML length: {len(html)} chars")
                print(f"   Markdown length: {len(markdown)} chars")
                
                # Check for protection indicators
                protection_indicators = [
                    "validate.perfdrive.com",
                    "ShieldSquare",
                    "Bot Management",
                    "human verification",
                    "security check",
                    "Please wait while we verify",
                    "Checking your browser"
                ]
                
                found_protection = []
                for indicator in protection_indicators:
                    if indicator.lower() in html.lower():
                        found_protection.append(indicator)
                
                if found_protection:
                    print(f"⚠️  Protection detected: {', '.join(found_protection)}")
                    
                    # Save debug HTML
                    debug_file = Path("debug_yad2_response.html")
                    debug_file.write_text(html)
                    print(f"💾 Saved debug HTML to: {debug_file}")
                    
                else:
                    print("🎉 No protection detected!")
                    
                    # Check for actual content
                    content_indicators = [
                        "דירות להשכרה",
                        "apartments",
                        "feed-item",
                        "listing",
                        "property"
                    ]
                    
                    found_content = []
                    for indicator in content_indicators:
                        if indicator.lower() in html.lower():
                            found_content.append(indicator)
                    
                    if found_content:
                        print(f"✅ Content found: {', '.join(found_content)}")
                        
                        # Save successful HTML
                        success_file = Path("success_yad2_response.html")
                        success_file.write_text(html)
                        print(f"💾 Saved successful HTML to: {success_file}")
                    else:
                        print("❓ No clear content indicators found")
                
                # Show first 1000 chars
                print("\n📄 First 1000 characters of response:")
                print("-" * 50)
                print(html[:1000])
                print("-" * 50)
                
            else:
                print(f"❌ Request failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_yad2_response()
