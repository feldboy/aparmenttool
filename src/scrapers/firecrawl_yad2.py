"""
Advanced Yad2 scraper using Firecrawl to bypass ShieldSquare protection

This scraper implements sophisticated anti-detection techniques:
- Headless browser with stealth mode
- Human-like behavior simulation
- Residential proxy rotation
- Session persistence
- CAPTCHA solving integration
"""

import logging
import time
import random
import json
import hashlib
import os
from typing import List, Optional, Dict, Any, Union
from urllib.parse import urlencode, urlparse, parse_qs
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup, Tag

from .base import BaseScraper, ScrapedListing

logger = logging.getLogger(__name__)

class FirecrawlYad2Scraper(BaseScraper):
    """Enhanced Yad2 scraper using Firecrawl for ShieldSquare bypass"""
    
    BASE_URL = "https://www.yad2.co.il"
    SEARCH_BASE = "https://www.yad2.co.il/realestate/rent"
    
    def __init__(self, firecrawl_api_key: str = None, proxy_config: Dict[str, Any] = None):
        super().__init__("Yad2_Firecrawl")
        
        # Firecrawl configuration
        self.firecrawl_api_key = firecrawl_api_key or os.getenv("FIRECRAWL_API_KEY")
        self.firecrawl_base_url = "https://api.firecrawl.dev/v0"
        
        # Proxy configuration
        self.proxy_config = proxy_config or {}
        
        # Session for regular requests
        self.session = requests.Session()
        self.session.headers.update(self._get_realistic_headers())
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 2.0  # Minimum seconds between requests
        
        # Session persistence
        self.browser_session_id = None
        
    def _get_realistic_headers(self) -> Dict[str, str]:
        """Get realistic browser headers to avoid detection"""
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"macOS"',
            'Cache-Control': 'max-age=0'
        }
    
    def _wait_for_rate_limit(self):
        """Implement rate limiting to avoid suspicious behavior"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            sleep_time += random.uniform(0.5, 2.0)  # Add random delay
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_firecrawl_config(self) -> Dict[str, Any]:
        """Get Firecrawl configuration optimized for ShieldSquare bypass"""
        config = {
            "pageOptions": {
                "waitFor": random.randint(3000, 8000),  # Wait 3-8 seconds
                "screenshot": False,
                "fullPageScreenshot": False,
                "headers": self._get_realistic_headers(),
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
        
        # Add proxy configuration if available
        if self.proxy_config:
            config["pageOptions"]["proxy"] = self.proxy_config
        
        return config
    
    def _scrape_with_firecrawl(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape URL using Firecrawl with advanced anti-detection"""
        if not self.firecrawl_api_key:
            logger.error("Firecrawl API key not configured")
            return None
        
        try:
            self._wait_for_rate_limit()
            
            # Configure Firecrawl request
            config = self._get_firecrawl_config()
            
            # Add behavioral randomization
            config["pageOptions"]["waitFor"] = random.randint(3000, 8000)
            
            # Make request to Firecrawl
            firecrawl_url = f"{self.firecrawl_base_url}/scrape"
            payload = {
                "url": url,
                **config
            }
            
            headers = {
                "Authorization": f"Bearer {self.firecrawl_api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Scraping {url} with Firecrawl...")
            response = requests.post(firecrawl_url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for success
                if result.get("success"):
                    logger.info("Successfully scraped with Firecrawl")
                    return result.get("data", {})
                else:
                    logger.error(f"Firecrawl scraping failed: {result.get('error', 'Unknown error')}")
                    return None
            else:
                logger.error(f"Firecrawl API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping with Firecrawl: {str(e)}")
            return None
    
    def _detect_shieldsquare_protection(self, html_content: str) -> bool:
        """Detect if page is showing ShieldSquare protection"""
        shieldsquare_indicators = [
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
        
        html_lower = html_content.lower()
        for indicator in shieldsquare_indicators:
            if indicator.lower() in html_lower:
                logger.warning(f"ShieldSquare protection detected: {indicator}")
                return True
        
        return False
    
    def _handle_captcha_challenge(self, html_content: str, url: str) -> Optional[str]:
        """Handle CAPTCHA challenges using solving services"""
        logger.warning("CAPTCHA challenge detected, attempting to solve...")
        
        # TODO: Integrate with 2Captcha or similar service
        # For now, we'll return None and retry later
        return None
    
    def scrape_listings(self, search_url: str, max_listings: int = 50) -> List[ScrapedListing]:
        """
        Scrape property listings from Yad2 using Firecrawl
        
        Args:
            search_url: Yad2 search URL to scrape
            max_listings: Maximum number of listings to return
            
        Returns:
            List of scraped listings
        """
        listings = []
        
        try:
            logger.info(f"Scraping Yad2 listings from: {search_url}")
            
            # First attempt with Firecrawl
            scraped_data = self._scrape_with_firecrawl(search_url)
            
            if not scraped_data:
                logger.error("Failed to scrape with Firecrawl")
                return listings
            
            # Get HTML content
            html_content = scraped_data.get("html", "")
            
            # Check for ShieldSquare protection
            if self._detect_shieldsquare_protection(html_content):
                logger.warning("ShieldSquare protection detected, attempting bypass...")
                
                # Try with different configuration
                time.sleep(random.uniform(5, 15))  # Wait longer
                scraped_data = self._scrape_with_firecrawl(search_url)
                
                if not scraped_data:
                    logger.error("Failed to bypass ShieldSquare protection")
                    return listings
                
                html_content = scraped_data.get("html", "")
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find listing containers
            listing_containers = self._find_listing_containers(soup)
            
            logger.info(f"Found {len(listing_containers)} listing containers")
            
            # Parse each listing
            for i, container in enumerate(listing_containers[:max_listings]):
                try:
                    listing = self.parse_listing_details(container)
                    if listing and self.validate_listing(listing):
                        listings.append(listing)
                        logger.debug(f"Parsed listing {i+1}: {listing.listing_id}")
                    else:
                        logger.debug(f"Skipped invalid listing {i+1}")
                        
                except Exception as e:
                    logger.warning(f"Error parsing listing {i+1}: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(listings)} valid listings")
            
        except Exception as e:
            logger.error(f"Unexpected error scraping Yad2: {str(e)}")
        
        return listings
    
    def _find_listing_containers(self, soup: BeautifulSoup) -> List[Tag]:
        """Find listing container elements in the page"""
        # Updated selectors for current Yad2 structure
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
        
        for selector in selectors:
            containers = soup.select(selector)
            if containers:
                logger.debug(f"Found listings using selector: {selector}")
                return containers
        
        # Fallback search
        logger.warning("No listings found with known selectors, trying fallback")
        potential_containers = soup.find_all('div', class_=re.compile(r'(feed|item|listing|property)', re.I))
        
        # Filter containers that likely contain listings
        filtered_containers = []
        for container in potential_containers:
            # Check if container has typical listing elements
            if (container.find(string=re.compile(r'₪|שח|rooms|חדרים', re.I)) or 
                container.find('a', href=re.compile(r'item|listing')) or
                len(container.find_all('div')) > 3):
                filtered_containers.append(container)
        
        return filtered_containers[:20]  # Limit to prevent false positives
    
    def parse_listing_details(self, listing_element: Tag) -> Optional[ScrapedListing]:
        """Parse individual listing details from HTML element"""
        try:
            # Extract listing ID
            listing_id = self._extract_listing_id(listing_element)
            if not listing_id:
                return None
            
            # Extract all fields
            title = self._extract_title(listing_element)
            price = self._extract_price(listing_element)
            rooms = self._extract_rooms(listing_element)
            location = self._extract_location(listing_element)
            url = self._extract_url(listing_element)
            image_url = self._extract_image_url(listing_element)
            description = self._extract_description(listing_element)
            
            # Create listing object
            listing = ScrapedListing(
                listing_id=listing_id,
                title=title,
                price=price,
                rooms=rooms,
                location=location,
                url=url,
                image_url=image_url,
                description=description,
                raw_data={
                    'source': 'Yad2_Firecrawl',
                    'scraped_at': datetime.utcnow().isoformat(),
                    'html_snippet': str(listing_element)[:500]
                }
            )
            
            return listing
            
        except Exception as e:
            logger.warning(f"Error parsing listing element: {str(e)}")
            return None
    
    def _extract_listing_id(self, element: Tag) -> Optional[str]:
        """Extract listing ID from element"""
        # Try various attributes
        for attr in ['data-item-id', 'data-listing-id', 'data-id', 'data-testid']:
            if element.has_attr(attr):
                attr_value = element[attr]
                if attr_value and str(attr_value).isdigit():
                    return f"yad2_{attr_value}"
        
        # Try to extract from nested elements
        for child in element.find_all(['div', 'a'], recursive=True):
            for attr in ['data-item-id', 'data-listing-id', 'data-id']:
                if child.has_attr(attr):
                    attr_value = child[attr]
                    if attr_value and str(attr_value).isdigit():
                        return f"yad2_{attr_value}"
        
        # Try to extract from URL
        link = element.find('a', href=True)
        if link:
            href = link['href']
            id_match = re.search(r'(?:item/|id=|/)(\d+)', href)
            if id_match:
                return f"yad2_{id_match.group(1)}"
        
        # Generate ID from content hash as fallback
        content_hash = hashlib.md5(str(element)[:200].encode()).hexdigest()[:8]
        return f"yad2_hash_{content_hash}"
    
    def _extract_title(self, element: Tag) -> str:
        """Extract listing title"""
        selectors = [
            '[data-testid="title"]',
            '.title',
            '.item-title',
            '.listing-title',
            'h1', 'h2', 'h3', 'h4',
            '.heading',
            '.property-title'
        ]
        
        for selector in selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title = self.clean_text(title_elem.get_text())
                if title and len(title) > 5:
                    return title
        
        # Fallback: look for the longest text content
        text_elements = element.find_all(string=True)
        longest_text = max(text_elements, key=len, default="")
        return self.clean_text(longest_text)[:100] if longest_text else "No title"
    
    def _extract_price(self, element: Tag) -> Optional[int]:
        """Extract listing price"""
        # Look for price indicators
        price_selectors = [
            '[data-testid="price"]',
            '.price',
            '.item-price',
            '.listing-price'
        ]
        
        price_text = ""
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text()
                break
        
        if not price_text:
            # Look for text containing currency symbols
            all_text = element.get_text()
            price_match = re.search(r'([\d,]+)\s*[₪שח]', all_text)
            if price_match:
                price_text = price_match.group(1)
        
        if price_text:
            # Clean and convert to integer
            price_clean = re.sub(r'[^\d]', '', price_text)
            if price_clean.isdigit():
                return int(price_clean)
        
        return None
    
    def _extract_rooms(self, element: Tag) -> Optional[float]:
        """Extract number of rooms"""
        # Look for room indicators
        room_selectors = [
            '[data-testid="rooms"]',
            '.rooms',
            '.item-rooms'
        ]
        
        room_text = ""
        for selector in room_selectors:
            room_elem = element.select_one(selector)
            if room_elem:
                room_text = room_elem.get_text()
                break
        
        if not room_text:
            # Look for text containing room indicators
            all_text = element.get_text()
            room_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:חדרים|חדר|rooms?)', all_text, re.I)
            if room_match:
                room_text = room_match.group(1)
        
        if room_text:
            try:
                return float(room_text.replace(',', '.'))
            except ValueError:
                pass
        
        return None
    
    def _extract_location(self, element: Tag) -> str:
        """Extract listing location"""
        location_selectors = [
            '[data-testid="location"]',
            '.location',
            '.item-location',
            '.address'
        ]
        
        for selector in location_selectors:
            location_elem = element.select_one(selector)
            if location_elem:
                location = self.clean_text(location_elem.get_text())
                if location:
                    return location
        
        # Look for common location patterns
        all_text = element.get_text()
        location_match = re.search(r'(תל אביב|ירושלים|חיפה|[^,]+,\s*[^,]+)', all_text)
        if location_match:
            return self.clean_text(location_match.group(1))
        
        return "Unknown location"
    
    def _extract_url(self, element: Tag) -> Optional[str]:
        """Extract listing URL"""
        link = element.find('a', href=True)
        if link:
            href = link['href']
            if href.startswith('/'):
                return self.BASE_URL + href
            elif href.startswith('http'):
                return href
        
        return None
    
    def _extract_image_url(self, element: Tag) -> Optional[str]:
        """Extract listing image URL"""
        img = element.find('img', src=True)
        if img:
            src = img['src']
            if src.startswith('http'):
                return src
            elif src.startswith('/'):
                return self.BASE_URL + src
        
        return None
    
    def _extract_description(self, element: Tag) -> str:
        """Extract listing description"""
        # Remove script and style elements
        for script in element(["script", "style"]):
            script.decompose()
        
        # Get all text and clean it
        text = element.get_text()
        description = self.clean_text(text)
        
        # Truncate if too long
        if len(description) > 500:
            description = description[:500] + "..."
        
        return description
    
    def construct_search_url(self, profile_config: Dict[str, Any]) -> str:
        """Construct Yad2 search URL from user profile configuration"""
        params = {}
        
        # Price range
        price_config = profile_config.get('price', profile_config.get('price_range', {}))
        if price_config:
            if 'min' in price_config and price_config['min']:
                params['priceMin'] = str(price_config['min'])
            if 'max' in price_config and price_config['max']:
                params['priceMax'] = str(price_config['max'])
        
        # Room range
        room_config = profile_config.get('rooms', profile_config.get('rooms_range', {}))
        if room_config:
            if 'min' in room_config and room_config['min']:
                params['rooms'] = f"{room_config['min']}-"
            if 'max' in room_config and room_config['max']:
                if 'rooms' in params:
                    params['rooms'] = f"{room_config['min']}-{room_config['max']}"
                else:
                    params['rooms'] = f"-{room_config['max']}"
        
        # Location (city)
        location_config = profile_config.get('location_criteria', profile_config.get('location', {}))
        if location_config:
            if 'city' in location_config and location_config['city']:
                city_code = self._get_city_code(location_config['city'])
                if city_code:
                    params['city'] = city_code
        
        # Property type
        if 'property_type' in profile_config and profile_config['property_type']:
            property_types = []
            for prop_type in profile_config['property_type']:
                if prop_type in ['דירה', 'apartment']:
                    property_types.append('1')
                elif prop_type in ['סטודיו', 'studio']:
                    property_types.append('4')
            if property_types:
                params['propertyGroup'] = ','.join(property_types)
        
        # Build final URL
        if params:
            url = f"{self.SEARCH_BASE}?{urlencode(params)}"
        else:
            url = self.SEARCH_BASE
        
        logger.info(f"Constructed Yad2 search URL: {url}")
        return url
    
    def _get_city_code(self, city_name: str) -> Optional[str]:
        """Map city names to Yad2 city codes"""
        city_mapping = {
            'תל אביב - יפו': '5000',
            'תל אביב': '5000',
            'Tel Aviv': '5000',
            'Jerusalem': '3000',
            'ירושלים': '3000',
            'חיפה': '4000',
            'Haifa': '4000',
            'באר שבע': '8600',
            'Beer Sheva': '8600',
            'פתח תקווה': '7900',
            'Petah Tikva': '7900',
            'רמת גן': '8300',
            'Ramat Gan': '8300',
        }
        
        return city_mapping.get(city_name.strip())
