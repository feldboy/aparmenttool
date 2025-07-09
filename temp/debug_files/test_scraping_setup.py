#!/usr/bin/env python3
"""
Test script to verify scraping setup
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scrapers.firecrawl_yad2 import FirecrawlYad2Scraper
from src.scrapers.config import ScrapingConfig
from dotenv import load_dotenv

def test_configuration():
    """Test the scraping configuration"""
    load_dotenv(".env.scraping")
    
    print("Testing scraping configuration...")
    
    # Test Firecrawl API
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    if firecrawl_key:
        print("✅ Firecrawl API key found")
    else:
        print("❌ Firecrawl API key not found")
    
    # Test proxy configuration
    proxy_endpoints = os.getenv("PROXY_ENDPOINTS")
    if proxy_endpoints:
        print("✅ Proxy configuration found")
    else:
        print("⚠️  No proxy configuration found")
    
    # Test CAPTCHA solver
    captcha_key = os.getenv("CAPTCHA_API_KEY")
    if captcha_key:
        print("✅ CAPTCHA solver API key found")
    else:
        print("⚠️  No CAPTCHA solver configured")
    
    # Test scraper initialization
    try:
        scraper = FirecrawlYad2Scraper()
        print("✅ Scraper initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing scraper: {e}")
    
    print("\nSetup verification complete!")

if __name__ == "__main__":
    test_configuration()
