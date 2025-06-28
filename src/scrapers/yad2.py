"""
Yad2 property listing scraper implementation

This scraper extracts rental property listings from Yad2.co.il
using requests and BeautifulSoup for HTML parsing.
"""

import logging
import time
import random
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode, urlparse, parse_qs
import re

import requests
from bs4 import BeautifulSoup, Tag

from .base import BaseScraper, ScrapedListing

logger = logging.getLogger(__name__)

class Yad2Scraper(BaseScraper):
    """Yad2.co.il property listing scraper"""
    
    BASE_URL = "https://www.yad2.co.il"
    SEARCH_BASE = "https://www.yad2.co.il/realestate/rent"
    
    def __init__(self):
        super().__init__("Yad2")
        self.session = requests.Session()
        
        # Set realistic headers to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def construct_search_url(self, profile_config: Dict[str, Any]) -> str:
        """
        Construct Yad2 search URL from user profile configuration
        
        Args:
            profile_config: User profile with search criteria
                Expected keys: price, rooms, location_criteria, property_type
            
        Returns:
            Complete Yad2 search URL
        """
        params = {}
        
        # Price range
        if 'price' in profile_config:
            price_range = profile_config['price']
            if 'min' in price_range and price_range['min']:
                params['priceMin'] = str(price_range['min'])
            if 'max' in price_range and price_range['max']:
                params['priceMax'] = str(price_range['max'])
        
        # Room range
        if 'rooms' in profile_config:
            room_range = profile_config['rooms']
            if 'min' in room_range and room_range['min']:
                params['rooms'] = f"{room_range['min']}-"
            if 'max' in room_range and room_range['max']:
                if 'rooms' in params:
                    params['rooms'] = f"{room_range['min']}-{room_range['max']}"
                else:
                    params['rooms'] = f"-{room_range['max']}"
        
        # Location (city)
        if 'location_criteria' in profile_config:
            location = profile_config['location_criteria']
            if 'city' in location and location['city']:
                # Yad2 uses numeric city codes, we'll need to map common cities
                city_code = self._get_city_code(location['city'])
                if city_code:
                    params['city'] = city_code
        
        # Property type
        if 'property_type' in profile_config and profile_config['property_type']:
            # Yad2 property type mapping
            property_types = []
            for prop_type in profile_config['property_type']:
                if prop_type in ['דירה', 'apartment']:
                    property_types.append('1')  # Apartment
                elif prop_type in ['סטודיו', 'studio']:
                    property_types.append('4')  # Studio
            if property_types:
                params['propertyGroup'] = ','.join(property_types)
        
        # Build final URL
        if params:
            url = f"{self.SEARCH_BASE}?{urlencode(params)}"
        else:
            url = self.SEARCH_BASE
        
        self.logger.info("Constructed Yad2 search URL: %s", url)
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
    
    def scrape_listings(self, search_url: str, max_listings: int = 50) -> List[ScrapedListing]:
        """
        Scrape property listings from Yad2 search results
        
        Args:
            search_url: Yad2 search URL to scrape
            max_listings: Maximum number of listings to return
            
        Returns:
            List of scraped listings
        """
        listings = []
        
        try:
            self.logger.info("Scraping Yad2 listings from: %s", search_url)
            
            # Add random delay to appear more human-like
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing containers (Yad2 structure may change)
            listing_containers = self._find_listing_containers(soup)
            
            self.logger.info("Found %d listing containers", len(listing_containers))
            
            for i, container in enumerate(listing_containers[:max_listings]):
                try:
                    listing = self.parse_listing_details(container)
                    if listing and self.validate_listing(listing):
                        listings.append(listing)
                        self.logger.debug("Parsed listing %d: %s", i+1, listing.listing_id)
                    else:
                        self.logger.debug("Skipped invalid listing %d", i+1)
                        
                except Exception as e:
                    self.logger.warning("Error parsing listing %d: %s", i+1, str(e))
                    continue
            
            self.logger.info("Successfully scraped %d valid listings", len(listings))
            
        except requests.RequestException as e:
            self.logger.error("HTTP error scraping Yad2: %s", str(e))
        except Exception as e:
            self.logger.error("Unexpected error scraping Yad2: %s", str(e))
        
        return listings
    
    def _find_listing_containers(self, soup: BeautifulSoup) -> List[Tag]:
        """
        Find listing container elements in the page
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of listing container elements
        """
        # Try multiple selectors as Yad2's structure may vary
        selectors = [
            'div[data-testid="feed-item"]',  # Common Yad2 listing container
            '.feeditem',
            '.feed_item',
            '[data-item-id]',
            '.feed-list-item',
            '.result-item',
        ]
        
        for selector in selectors:
            containers = soup.select(selector)
            if containers:
                self.logger.debug("Found listings using selector: %s", selector)
                return containers
        
        # Fallback: look for divs that might contain listings
        self.logger.warning("No listings found with known selectors, trying fallback")
        return soup.find_all('div', class_=re.compile(r'(feed|item|listing)', re.I))[:20]
    
    def parse_listing_details(self, listing_element: Tag) -> Optional[ScrapedListing]:
        """
        Parse individual listing details from HTML element
        
        Args:
            listing_element: BeautifulSoup Tag containing listing data
            
        Returns:
            Parsed listing data or None if parsing failed
        """
        try:
            # Extract listing ID
            listing_id = self._extract_listing_id(listing_element)
            if not listing_id:
                return None
            
            # Extract title
            title = self._extract_title(listing_element)
            
            # Extract price
            price = self._extract_price(listing_element)
            
            # Extract rooms
            rooms = self._extract_rooms(listing_element)
            
            # Extract location
            location = self._extract_location(listing_element)
            
            # Extract URL
            url = self._extract_url(listing_element)
            
            # Extract image URL
            image_url = self._extract_image_url(listing_element)
            
            # Extract description
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
                    'source': 'Yad2',
                    'scraped_at': time.time(),
                    'html_snippet': str(listing_element)[:500]  # First 500 chars for debugging
                }
            )
            
            return listing
            
        except Exception as e:
            self.logger.warning("Error parsing listing element: %s", str(e))
            return None
    
    def _extract_listing_id(self, element: Tag) -> Optional[str]:
        """Extract listing ID from element"""
        # Try various attributes that might contain the ID
        for attr in ['data-item-id', 'data-listing-id', 'data-id']:
            if element.has_attr(attr):
                return element[attr]
        
        # Try to extract from URL
        link = element.find('a', href=True)
        if link:
            href = link['href']
            # Look for patterns like /item/12345 or id=12345
            id_match = re.search(r'(?:item/|id=)(\d+)', href)
            if id_match:
                return f"yad2_{id_match.group(1)}"
        
        # Generate ID from element content as fallback
        content_hash = hash(str(element)[:200])
        return f"yad2_generated_{abs(content_hash)}"
    
    def _extract_title(self, element: Tag) -> str:
        """Extract listing title"""
        # Try various selectors for title
        selectors = [
            '[data-testid="title"]',
            '.title',
            '.item-title',
            'h2', 'h3', 'h4',
            '.heading'
        ]
        
        for selector in selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                return self.clean_text(title_elem.get_text())
        
        return "לא צוין כותרת"  # "No title specified"
    
    def _extract_price(self, element: Tag) -> Optional[int]:
        """Extract and normalize price"""
        # Try various selectors for price
        selectors = [
            '[data-testid="price"]',
            '.price',
            '.item-price',
            '[class*="price"]'
        ]
        
        for selector in selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text()
                return self.normalize_price(price_text)
        
        # Look for price patterns in text
        text = element.get_text()
        price_pattern = r'(\d{1,3}(?:,\d{3})*)\s*₪'
        price_match = re.search(price_pattern, text)
        if price_match:
            return self.normalize_price(price_match.group(1))
        
        return None
    
    def _extract_rooms(self, element: Tag) -> Optional[float]:
        """Extract room count"""
        # Try various selectors for rooms
        selectors = [
            '[data-testid="rooms"]',
            '.rooms',
            '.item-rooms',
            '[class*="room"]'
        ]
        
        for selector in selectors:
            rooms_elem = element.select_one(selector)
            if rooms_elem:
                rooms_text = rooms_elem.get_text()
                return self.normalize_rooms(rooms_text)
        
        # Look for room patterns in text
        text = element.get_text()
        room_patterns = [
            r'(\d+(?:\.\d+)?)\s*חדרים?',
            r'(\d+(?:\.\d+)?)\s*חד',
            r'(\d+(?:\.\d+)?)\s*rooms?'
        ]
        
        for pattern in room_patterns:
            room_match = re.search(pattern, text, re.IGNORECASE)
            if room_match:
                return self.normalize_rooms(room_match.group(1))
        
        return None
    
    def _extract_location(self, element: Tag) -> str:
        """Extract location information"""
        # Try various selectors for location
        selectors = [
            '[data-testid="location"]',
            '.location',
            '.item-location',
            '.address',
            '[class*="location"]'
        ]
        
        for selector in selectors:
            loc_elem = element.select_one(selector)
            if loc_elem:
                return self.clean_text(loc_elem.get_text())
        
        return ""
    
    def _extract_url(self, element: Tag) -> str:
        """Extract listing URL"""
        link = element.find('a', href=True)
        if link:
            href = link['href']
            return self.make_absolute_url(href, self.BASE_URL)
        
        return ""
    
    def _extract_image_url(self, element: Tag) -> Optional[str]:
        """Extract image URL"""
        # Try to find image in listing
        img = element.find('img', src=True)
        if img:
            src = img['src']
            # Skip placeholder/loading images
            if 'placeholder' not in src.lower() and 'loading' not in src.lower():
                return self.make_absolute_url(src, self.BASE_URL)
        
        return None
    
    def _extract_description(self, element: Tag) -> str:
        """Extract listing description"""
        # Try various selectors for description
        selectors = [
            '[data-testid="description"]',
            '.description',
            '.item-description',
            '.summary'
        ]
        
        for selector in selectors:
            desc_elem = element.select_one(selector)
            if desc_elem:
                return self.clean_text(desc_elem.get_text())[:500]  # Limit to 500 chars
        
        return ""
