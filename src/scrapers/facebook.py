"""
Facebook Groups scraper for property listings

This module implements Facebook group scraping using Playwright to extract
property posts from specified Facebook groups with user authentication.
"""

import logging
import re
import asyncio
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pathlib import Path

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from .base import BaseScraper, ScrapedListing

logger = logging.getLogger(__name__)

class FacebookScraper(BaseScraper):
    """Facebook Groups scraper for property listings"""
    
    def __init__(self, cookies_file: Optional[str] = None, headless: bool = True):
        super().__init__("Facebook")
        self.cookies_file = cookies_file
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        
    async def initialize_browser(self) -> bool:
        """
        Initialize browser with session cookies
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            # Create context with realistic user agent
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Load cookies if available
            if self.cookies_file and Path(self.cookies_file).exists():
                try:
                    with open(self.cookies_file, 'r') as f:
                        cookies = json.load(f)
                    await self.context.add_cookies(cookies)
                    self.logger.info("Loaded %d cookies from %s", len(cookies), self.cookies_file)
                except Exception as e:
                    self.logger.warning("Failed to load cookies: %s", e)
            
            return True
            
        except Exception as e:
            self.logger.error("Failed to initialize browser: %s", e)
            return False
    
    async def close_browser(self):
        """Close browser and cleanup resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    def construct_search_url(self, profile_config: Dict[str, Any]) -> str:
        """
        Construct Facebook group URL from profile configuration
        
        Args:
            profile_config: User profile with facebook_group_ids
            
        Returns:
            Facebook group URL (returns first group if multiple)
        """
        facebook_groups = profile_config.get("scan_targets", {}).get("facebook_group_ids", [])
        
        if not facebook_groups:
            raise ValueError("No Facebook group IDs specified in profile")
        
        # Return URL for first group (we'll handle multiple groups in scrape_listings)
        group_id = facebook_groups[0]
        return f"https://www.facebook.com/groups/{group_id}"
    
    async def scrape_listings(self, search_url: str, max_listings: int = 50) -> List[ScrapedListing]:
        """
        Scrape property listings from Facebook group
        
        Args:
            search_url: Facebook group URL
            max_listings: Maximum number of listings to return
            
        Returns:
            List of scraped listings
        """
        if not self.context:
            raise RuntimeError("Browser not initialized. Call initialize_browser() first.")
        
        listings = []
        
        try:
            page = await self.context.new_page()
            
            # Navigate to Facebook group
            self.logger.info("Navigating to %s", search_url)
            await page.goto(search_url, wait_until='networkidle')
            
            # Wait for page to load and check if login is required
            await page.wait_for_timeout(3000)
            
            # Check for login requirement
            if await self._check_login_required(page):
                self.logger.error("Login required or session expired")
                return listings
            
            # Scroll and collect posts
            post_count = 0
            last_height = 0
            
            while post_count < max_listings:
                # Scroll down to load more posts
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(2000)
                
                # Check if we've loaded more content
                new_height = await page.evaluate('document.body.scrollHeight')
                if new_height == last_height:
                    self.logger.info("No more content to load")
                    break
                last_height = new_height
                
                # Extract posts from current view
                posts = await self._extract_posts_from_page(page)
                
                for post in posts:
                    if post and self.validate_listing(post):
                        # Check if we already have this post
                        if not any(existing.listing_id == post.listing_id for existing in listings):
                            listings.append(post)
                            post_count += 1
                            
                            if post_count >= max_listings:
                                break
                
                self.logger.info("Collected %d posts so far", len(listings))
            
            await page.close()
            
        except Exception as e:
            self.logger.error("Error scraping Facebook listings: %s", e)
        
        self.logger.info("Scraped %d listings from Facebook", len(listings))
        return listings[:max_listings]
    
    async def _check_login_required(self, page: Page) -> bool:
        """Check if login is required"""
        try:
            # Look for login-related elements
            login_selectors = [
                '[data-testid="royal_login_form"]',
                '#email',
                'input[name="email"]',
                'text="Log In"',
                'text="Sign Up"'
            ]
            
            for selector in login_selectors:
                if await page.locator(selector).count() > 0:
                    return True
            
            return False
            
        except Exception:
            return True
    
    async def _extract_posts_from_page(self, page: Page) -> List[Optional[ScrapedListing]]:
        """Extract posts from current page view"""
        posts = []
        
        try:
            # Find post containers (Facebook uses various selectors)
            post_selectors = [
                '[data-pagelet="FeedUnit_0"]',
                '[data-testid="fbfeed_story"]',
                '[role="article"]',
                'div[data-testid="story-subtitle"] ~ div'
            ]
            
            post_elements = []
            for selector in post_selectors:
                elements = await page.locator(selector).all()
                if elements:
                    post_elements = elements
                    break
            
            for element in post_elements:
                try:
                    post = await self._parse_post_element(element)
                    if post:
                        posts.append(post)
                except Exception as e:
                    self.logger.debug("Failed to parse post element: %s", e)
                    continue
            
        except Exception as e:
            self.logger.error("Error extracting posts: %s", e)
        
        return posts
    
    async def _parse_post_element(self, element) -> Optional[ScrapedListing]:
        """Parse individual Facebook post element"""
        try:
            # Extract post text
            text_content = ""
            text_selectors = [
                '[data-testid="post_message"]',
                '[data-ad-preview="message"]',
                'div[data-testid="story-subtitle"] + div',
                'span[dir="auto"]'
            ]
            
            for selector in text_selectors:
                text_elem = element.locator(selector).first
                if await text_elem.count() > 0:
                    text_content = await text_elem.inner_text()
                    break
            
            if not text_content or len(text_content.strip()) < 10:
                return None
            
            # Filter for property-related posts
            if not self._is_property_post(text_content):
                return None
            
            # Extract post URL/ID
            post_url = ""
            try:
                link_elem = element.locator('a[href*="/groups/"]').first
                if await link_elem.count() > 0:
                    post_url = await link_elem.get_attribute('href')
                    if post_url and not post_url.startswith('http'):
                        post_url = f"https://www.facebook.com{post_url}"
            except Exception:
                pass
            
            # Generate unique ID from content
            import hashlib
            post_id = hashlib.md5(text_content.encode()).hexdigest()[:12]
            
            # Extract price and rooms using regex
            price = self._extract_price_from_text(text_content)
            rooms = self._extract_rooms_from_text(text_content)
            location = self._extract_location_from_text(text_content)
            
            # Extract images
            image_url = None
            try:
                img_elem = element.locator('img').first
                if await img_elem.count() > 0:
                    image_url = await img_elem.get_attribute('src')
            except Exception:
                pass
            
            return ScrapedListing(
                listing_id=f"fb_{post_id}",
                title=text_content[:100] + "..." if len(text_content) > 100 else text_content,
                price=price,
                rooms=rooms,
                location=location,
                url=post_url,
                image_url=image_url,
                description=text_content,
                posted_date=datetime.now(timezone.utc),
                raw_data={"source": "facebook", "full_text": text_content}
            )
            
        except Exception as e:
            self.logger.debug("Failed to parse post: %s", e)
            return None
    
    def _is_property_post(self, text: str) -> bool:
        """Check if post is property-related"""
        property_keywords = [
            # Hebrew keywords
            'דירה', 'דירות', 'דיור', 'להשכרה', 'למכירה', 'לשכירות',
            'חדרים', 'חדר', 'מטר', 'קומה', 'בניין', 'משכנתא',
            'שכירות', 'מכירה', 'נדלן', 'רוצה דירה', 'מחפש דירה',
            # English keywords
            'apartment', 'flat', 'rent', 'sale', 'bedroom', 'room',
            'sqm', 'floor', 'building', 'property', 'real estate',
            'for rent', 'for sale', 'looking for', 'seeking',
            # Common abbreviations
            'חד', 'ש"ח', 'ש״ח', 'NIS', '₪'
        ]
        
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in property_keywords)
    
    def _extract_price_from_text(self, text: str) -> Optional[int]:
        """Extract price from Facebook post text"""
        # Look for price patterns in Hebrew and English
        price_patterns = [
            r'(\d{1,2}[,\.]?\d{3,4})\s*(?:ש״ח|ש"ח|שקל|₪|NIS)',  # Hebrew currency
            r'(\d{1,2}[,\.]?\d{3,4})\s*(?:per month|monthly|לחודש)',  # Monthly rent
            r'(\d{1,2}[,\.]?\d{3,4})\s*(?:total|סה״כ|סה"כ)',  # Total price
            r'(?:price|מחיר).*?(\d{1,2}[,\.]?\d{3,4})',  # Price: X
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    price_str = matches[0].replace(',', '').replace('.', '')
                    price = int(price_str)
                    # Reasonable price range (500-50000 NIS)
                    if 500 <= price <= 50000:
                        return price
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _extract_rooms_from_text(self, text: str) -> Optional[float]:
        """Extract room count from Facebook post text"""
        room_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:חדרים|חדר|rooms?|bedroom)',
            r'(\d+(?:\.\d+)?)\s*(?:br|bed)',
            r'(?:חדרים|rooms?).*?(\d+(?:\.\d+)?)'
        ]
        
        for pattern in room_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    rooms = float(matches[0])
                    if 0.5 <= rooms <= 10:  # Reasonable room range
                        return rooms
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _extract_location_from_text(self, text: str) -> str:
        """Extract location from Facebook post text"""
        # Common Israeli cities and areas
        locations = [
            'תל אביב', 'תל-אביב', 'tel aviv', 'jerusalem', 'ירושלים',
            'חיפה', 'haifa', 'בת ים', 'bat yam', 'רמת גן', 'ramat gan',
            'פתח תקווה', 'petah tikva', 'ראשון לציון', 'rishon lezion',
            'אשדוד', 'ashdod', 'נתניה', 'netanya', 'חולון', 'holon',
            'בני ברק', 'bnei brak', 'רמת השרון', 'ramat hasharon',
            'הרצליה', 'herzliya', 'כפר סבא', 'kfar saba', 'רעננה', 'raanana'
        ]
        
        text_lower = text.lower()
        for location in locations:
            if location.lower() in text_lower:
                return location
        
        return "Unknown"
    
    def parse_listing_details(self, listing_element: Any) -> Optional[ScrapedListing]:
        """
        Parse individual listing details (async version handled in _parse_post_element)
        
        This method is required by the base class but the actual parsing
        is done in the async _parse_post_element method.
        """
        # This method is not used in the async implementation
        # The actual parsing is done in _parse_post_element
        return None

# Synchronous wrapper for easier integration
class FacebookScraperSync:
    """Synchronous wrapper for FacebookScraper"""
    
    def __init__(self, cookies_file: Optional[str] = None, headless: bool = True):
        self.scraper = FacebookScraper(cookies_file, headless)
    
    def scrape_listings(self, search_url: str, max_listings: int = 50) -> List[ScrapedListing]:
        """Synchronous wrapper for scraping listings"""
        return asyncio.run(self._scrape_async(search_url, max_listings))
    
    async def _scrape_async(self, search_url: str, max_listings: int) -> List[ScrapedListing]:
        """Internal async method"""
        try:
            await self.scraper.initialize_browser()
            return await self.scraper.scrape_listings(search_url, max_listings)
        finally:
            await self.scraper.close_browser()
    
    def construct_search_url(self, profile_config: Dict[str, Any]) -> str:
        """Construct search URL from profile"""
        return self.scraper.construct_search_url(profile_config)
