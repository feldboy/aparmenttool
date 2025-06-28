"""
Base scraper interface and common utilities for property listing scrapers
"""

import logging
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

@dataclass
class ScrapedListing:
    """Raw scraped listing data"""
    listing_id: str
    title: str
    price: Optional[int] = None
    rooms: Optional[float] = None
    location: str = ""
    url: str = ""
    image_url: Optional[str] = None
    description: str = ""
    contact_info: Optional[str] = None
    features: List[str] = None
    posted_date: Optional[datetime] = None
    raw_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.raw_data is None:
            self.raw_data = {}
    
    def generate_content_hash(self) -> str:
        """Generate SHA256 hash of core content for duplicate detection"""
        # Use key fields that are unlikely to change for the same property
        content_parts = [
            str(self.price or 0),
            str(self.rooms or 0),
            self.location.strip().lower(),
            self.title.strip().lower()[:100],  # First 100 chars of title
        ]
        content_string = "|".join(content_parts)
        return hashlib.sha256(content_string.encode('utf-8')).hexdigest()

class BaseScraper(ABC):
    """Abstract base class for property listing scrapers"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.logger = logging.getLogger(f"scraper.{source_name.lower()}")
        
    @abstractmethod
    def construct_search_url(self, profile_config: Dict[str, Any]) -> str:
        """
        Construct search URL from user profile configuration
        
        Args:
            profile_config: User profile search criteria
            
        Returns:
            Complete search URL for the platform
        """
        pass
    
    @abstractmethod
    def scrape_listings(self, search_url: str, max_listings: int = 50) -> List[ScrapedListing]:
        """
        Scrape property listings from the given search URL
        
        Args:
            search_url: URL to scrape listings from
            max_listings: Maximum number of listings to return
            
        Returns:
            List of scraped listings
        """
        pass
    
    @abstractmethod
    def parse_listing_details(self, listing_element: Any) -> Optional[ScrapedListing]:
        """
        Parse individual listing details from HTML element
        
        Args:
            listing_element: HTML element containing listing data
            
        Returns:
            Parsed listing data or None if parsing failed
        """
        pass
    
    def validate_listing(self, listing: ScrapedListing) -> bool:
        """
        Validate that a scraped listing has required fields
        
        Args:
            listing: Scraped listing to validate
            
        Returns:
            True if listing is valid, False otherwise
        """
        if not listing.listing_id:
            self.logger.warning("Listing missing ID")
            return False
        
        if not listing.title:
            self.logger.warning("Listing %s missing title", listing.listing_id)
            return False
        
        if not listing.url:
            self.logger.warning("Listing %s missing URL", listing.listing_id)
            return False
        
        return True
    
    def normalize_price(self, price_text: str) -> Optional[int]:
        """
        Extract and normalize price from text
        
        Args:
            price_text: Raw price text
            
        Returns:
            Normalized price as integer or None if extraction failed
        """
        if not price_text:
            return None
        
        # Remove common currency symbols and text
        import re
        price_clean = re.sub(r'[^\d,]', '', price_text.replace('₪', '').replace('ILS', ''))
        price_clean = price_clean.replace(',', '')
        
        try:
            return int(price_clean)
        except ValueError:
            self.logger.warning("Could not parse price: %s", price_text)
            return None
    
    def normalize_rooms(self, rooms_text: str) -> Optional[float]:
        """
        Extract and normalize room count from text
        
        Args:
            rooms_text: Raw rooms text
            
        Returns:
            Normalized room count as float or None if extraction failed
        """
        if not rooms_text:
            return None
        
        import re
        # Look for patterns like "2", "2.5", "2 חדרים", etc.
        room_match = re.search(r'(\d+(?:\.\d+)?)', rooms_text)
        if room_match:
            try:
                return float(room_match.group(1))
            except ValueError:
                pass
        
        self.logger.warning("Could not parse rooms: %s", rooms_text)
        return None
    
    def make_absolute_url(self, url: str, base_url: str) -> str:
        """
        Convert relative URL to absolute URL
        
        Args:
            url: Potentially relative URL
            base_url: Base URL for the site
            
        Returns:
            Absolute URL
        """
        if not url:
            return ""
        
        return urljoin(base_url, url)
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        import re
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())
        # Remove common HTML entities
        cleaned = cleaned.replace('&nbsp;', ' ').replace('&amp;', '&')
        
        return cleaned
