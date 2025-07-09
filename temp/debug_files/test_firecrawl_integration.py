#!/usr/bin/env python3
"""
Test script to verify Firecrawl integration for Yad2 scraping
Tests the Firecrawl API configuration and scraping functionality
"""

import os
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env.scraping"""
    env_file = Path(__file__).parent / ".env.scraping"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        logger.info("Loaded environment from .env.scraping")
    else:
        logger.warning(".env.scraping file not found")

def test_firecrawl_api():
    """Test basic Firecrawl API connectivity"""
    try:
        import requests
        
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            logger.error("FIRECRAWL_API_KEY not found in environment")
            return False
        
        logger.info(f"Testing Firecrawl API with key: {api_key[:10]}...")
        
        # Test with a simple URL first
        test_url = "https://httpbin.org/html"
        
        firecrawl_url = "https://api.firecrawl.dev/v0/scrape"
        payload = {
            "url": test_url,
            "pageOptions": {
                "waitFor": 2000,
                "includeHtml": True,
                "includeRawHtml": False,
                "onlyMainContent": False
            }
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(firecrawl_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                logger.info("✅ Firecrawl API is working correctly")
                return True
            else:
                logger.error(f"❌ Firecrawl API returned success=false: {result}")
                return False
        else:
            logger.error(f"❌ Firecrawl API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing Firecrawl API: {e}")
        return False

def test_yad2_scraping():
    """Test Yad2 scraping with Firecrawl"""
    try:
        from scrapers.firecrawl_yad2 import FirecrawlYad2Scraper
        
        # Test URL - a simple Yad2 search
        test_url = "https://www.yad2.co.il/realestate/rent?city=5000&rooms=2-3&priceMin=3000&priceMax=8000"
        
        scraper = FirecrawlYad2Scraper()
        
        logger.info(f"Testing Yad2 scraping with URL: {test_url}")
        
        # Test the scraping
        listings = scraper.scrape_listings(test_url, max_listings=5)
        
        if listings:
            logger.info(f"✅ Successfully scraped {len(listings)} listings from Yad2")
            
            # Display first listing details
            if len(listings) > 0:
                first_listing = listings[0]
                logger.info("Sample listing:")
                logger.info(f"  ID: {first_listing.listing_id}")
                logger.info(f"  Title: {first_listing.title}")
                logger.info(f"  Price: {first_listing.price}")
                logger.info(f"  Rooms: {first_listing.rooms}")
                logger.info(f"  Location: {first_listing.location}")
                logger.info(f"  URL: {first_listing.url}")
            
            return True
        else:
            logger.warning("⚠️ No listings were scraped - this could indicate protection is still active")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("Make sure all dependencies are installed")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing Yad2 scraping: {e}")
        return False

def test_firecrawl_direct():
    """Test Firecrawl with a direct Yad2 URL to check content retrieval"""
    try:
        import requests
        
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            logger.error("FIRECRAWL_API_KEY not found")
            return False
        
        # Test with Yad2 main page first
        yad2_url = "https://www.yad2.co.il/realestate/rent?city=5000"
        
        logger.info(f"Testing direct Firecrawl scraping of: {yad2_url}")
        
        firecrawl_url = "https://api.firecrawl.dev/v0/scrape"
        payload = {
            "url": yad2_url,
            "pageOptions": {
                "waitFor": 5000,
                "includeHtml": True,
                "includeRawHtml": True,
                "onlyMainContent": False,
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            }
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(firecrawl_url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                data = result.get("data", {})
                html_content = data.get("html", "")
                
                # Save HTML for debugging
                debug_file = Path(__file__).parent / "firecrawl_yad2_response.html"
                with open(debug_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                
                logger.info(f"✅ Successfully retrieved HTML content ({len(html_content)} characters)")
                logger.info(f"Debug HTML saved to: {debug_file}")
                
                # Check for key indicators
                if "יד2" in html_content or "yad2" in html_content.lower():
                    logger.info("✅ HTML content appears to be from Yad2")
                    
                    # Check for listings
                    if "נדל״ן" in html_content or "דירה" in html_content:
                        logger.info("✅ HTML content contains real estate listings")
                        return True
                    else:
                        logger.warning("⚠️ No real estate content detected in HTML")
                        return False
                else:
                    logger.warning("⚠️ HTML content doesn't appear to be from Yad2")
                    return False
                    
            else:
                logger.error(f"❌ Firecrawl returned success=false: {result}")
                return False
        else:
            logger.error(f"❌ Firecrawl API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in direct Firecrawl test: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting Firecrawl integration tests...")
    
    # Load environment
    load_environment()
    
    # Test 1: Basic API connectivity
    logger.info("\n📡 Test 1: Firecrawl API connectivity")
    api_test = test_firecrawl_api()
    
    # Test 2: Direct Yad2 content retrieval
    logger.info("\n🌐 Test 2: Direct Yad2 content retrieval")
    direct_test = test_firecrawl_direct()
    
    # Test 3: Full scraping integration
    logger.info("\n🏠 Test 3: Full Yad2 scraping integration")
    scraping_test = test_yad2_scraping()
    
    # Summary
    logger.info("\n📊 Test Results Summary:")
    logger.info(f"  API Connectivity: {'✅ PASS' if api_test else '❌ FAIL'}")
    logger.info(f"  Content Retrieval: {'✅ PASS' if direct_test else '❌ FAIL'}")
    logger.info(f"  Scraping Integration: {'✅ PASS' if scraping_test else '❌ FAIL'}")
    
    if all([api_test, direct_test, scraping_test]):
        logger.info("\n🎉 All tests passed! Firecrawl integration is working correctly.")
        return True
    else:
        logger.error("\n❌ Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
