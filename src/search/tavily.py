"""
Tavily Search Integration for RealtyScanner
Enhanced web search capabilities using Tavily API
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    TavilyClient = None

logger = logging.getLogger(__name__)

class TavilySearcher:
    """Tavily API integration for enhanced web search"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily searcher
        
        Args:
            api_key: Tavily API key (if None, reads from environment)
        """
        if not TAVILY_AVAILABLE:
            raise ImportError("Tavily Python client not available. Install with: pip install tavily-python")
        
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "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")
        if not self.api_key:
            raise ValueError("Tavily API key is required")
        
        self.client = TavilyClient(api_key=self.api_key)
        
    async def search_real_estate(self, query: str, location: str = "", max_results: int = 10, today_only: bool = True) -> List[Dict[str, Any]]:
        """
        Search for real estate information using Tavily
        
        Args:
            query: Search query
            location: Location filter
            max_results: Maximum number of results
            today_only: Filter for today's listings only
            
        Returns:
            List of search results
        """
        try:
            # Construct enhanced query for real estate with strict date filter
            current_date = datetime.now().strftime("%Y-%m-%d")
            today_str = datetime.now().strftime("%B %d, %Y")  # June 28, 2025
            today_hebrew = datetime.now().strftime("%d/%m/%Y")  # Hebrew date format
            
            enhanced_query = f"{query} דירה apartment rental השכרה {location}".strip()
            
            if today_only:
                # More aggressive today-only filtering
                enhanced_query += f' "posted today" "פורסם היום" "{current_date}" "{today_str}" "{today_hebrew}" new listing fresh TODAY'
            
            # Use Tavily's search method with broader search first
            response = self.client.search(
                query=enhanced_query,
                search_depth="advanced",
                max_results=max_results * 3,  # Get more results to filter more strictly
                include_domains=[
                    "yad2.co.il",
                    "madlan.co.il", 
                    "onmap.co.il",
                    "facebook.com",
                    "homeless.co.il",
                    "ad-dor.com"
                ]
            )
            
            results = []
            current_date = datetime.now().date()
            
            for result in response.get("results", []):
                # More strict filtering by date if today_only is enabled
                if today_only:
                    is_today_listing = False
                    
                    # Check published_date first (most reliable)
                    published_date = result.get("published_date")
                    if published_date:
                        try:
                            # Parse published date
                            pub_date = datetime.fromisoformat(published_date.replace('Z', '+00:00')).date()
                            is_today_listing = (pub_date == current_date)
                        except (ValueError, TypeError):
                            pass
                    
                    # If no published_date or not today, check content more strictly
                    if not is_today_listing:
                        content = result.get("content", "").lower()
                        title = result.get("title", "").lower()
                        
                        # Look for strong "today" indicators
                        strong_today_indicators = [
                            "posted today", "פורסם היום", "עודכן היום", "נוסף היום",
                            current_date.strftime("%d/%m/%Y"),
                            current_date.strftime("%Y-%m-%d"),
                            current_date.strftime("%d.%m.%Y"),
                            current_date.strftime("%d-%m-%Y"),
                            "today", "היום"
                        ]
                        
                        # Check if any strong today indicators are present
                        has_strong_today_indicator = any(indicator in content or indicator in title for indicator in strong_today_indicators)
                        
                        # Additional checks for freshness
                        fresh_indicators = ["new listing", "מודעה חדשה", "חדש", "fresh", "just posted"]
                        has_fresh_indicator = any(indicator in content or indicator in title for indicator in fresh_indicators)
                        
                        # Skip if no strong indicators of being posted today
                        if not (has_strong_today_indicator or has_fresh_indicator):
                            continue
                        
                        # Additional filter: check for old date patterns that would indicate it's NOT today
                        old_date_patterns = [
                            "yesterday", "אתמול", "days ago", "יום", "week", "שבוע", 
                            "month", "חודש", "עודכן ב"
                        ]
                        has_old_date_pattern = any(pattern in content for pattern in old_date_patterns)
                        if has_old_date_pattern:
                            continue
                
                processed_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0),
                    "published_date": result.get("published_date"),
                    "source": "tavily",
                    "scraped_at": datetime.now().isoformat()
                }
                
                # Additional relevance filtering - only include results with good relevance scores
                if processed_result["score"] < 0.3:  # Filter low relevance results
                    continue
                
                # Check if the content actually looks like a real estate listing
                content_lower = processed_result["content"].lower()
                title_lower = processed_result["title"].lower()
                
                # Real estate keywords that should be present
                real_estate_keywords = [
                    "apartment", "דירה", "rooms", "חדרים", "rent", "שכירות", 
                    "₪", "nis", "שח", "bedroom", "bathroom", "balcony", "מרפסת",
                    "floor", "קומה", "m²", "מטר", "price", "מחיר"
                ]
                
                # Check if it contains real estate content
                has_real_estate_content = any(keyword in content_lower or keyword in title_lower for keyword in real_estate_keywords)
                if not has_real_estate_content:
                    continue
                    
                results.append(processed_result)
                
                # Stop if we have enough results
                if len(results) >= max_results:
                    break
            
            logger.info("Tavily search completed: %d results for '%s'", len(results), enhanced_query)
            return results
            
        except Exception as e:
            logger.error("Tavily search error: %s", str(e))
            return []
    
    async def search_market_trends(self, location: str, property_type: str = "apartment") -> Dict[str, Any]:
        """
        Search for real estate market trends and prices
        
        Args:
            location: Location to analyze
            property_type: Type of property
            
        Returns:
            Market analysis data
        """
        try:
            query = f"{location} {property_type} rental prices market trends 2025"
            
            # Use Tavily's search method
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_domains=[
                    "madlan.co.il",
                    "yad2.co.il", 
                    "bankhapoalim.co.il",
                    "cbs.gov.il"
                ]
            )
            
            # Extract market insights
            market_data = {
                "location": location,
                "property_type": property_type,
                "answer": response.get("answer", ""),
                "trends": [],
                "price_indicators": [],
                "sources": [],
                "analyzed_at": datetime.now().isoformat()
            }
            
            for result in response.get("results", []):
                market_data["sources"].append({
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "relevance_score": result.get("score", 0)
                })
            
            logger.info("Market trends analysis completed for %s", location)
            return market_data
            
        except Exception as e:
            logger.error("Market trends search error: %s", str(e))
            return {}
    
    async def verify_listing_legitimacy(self, listing_url: str, title: str) -> Dict[str, Any]:
        """
        Verify if a property listing is legitimate using web search
        
        Args:
            listing_url: URL of the listing
            title: Title of the listing
            
        Returns:
            Legitimacy analysis
        """
        try:
            # Search for similar listings or scam reports
            query = f'"{title}" scam fraud fake listing site:{listing_url.split("/")[2]}'
            
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=5
            )
            
            # Analyze results for red flags
            red_flags = []
            positive_indicators = []
            
            for result in response.get("results", []):
                content = result.get("content", "").lower()
                if any(flag in content for flag in ["scam", "fraud", "fake", "suspicious"]):
                    red_flags.append(result.get("title"))
                if any(indicator in content for indicator in ["verified", "legitimate", "trusted"]):
                    positive_indicators.append(result.get("title"))
            
            legitimacy_score = max(0, 100 - len(red_flags) * 30 + len(positive_indicators) * 20)
            
            return {
                "listing_url": listing_url,
                "legitimacy_score": legitimacy_score,
                "red_flags": red_flags,
                "positive_indicators": positive_indicators,
                "recommendation": "proceed" if legitimacy_score > 70 else "caution" if legitimacy_score > 40 else "avoid",
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Legitimacy verification error: %s", str(e))
            return {"error": str(e)}
    
    async def search_neighborhood_info(self, neighborhood: str, city: str) -> Dict[str, Any]:
        """
        Get comprehensive neighborhood information
        
        Args:
            neighborhood: Neighborhood name
            city: City name
            
        Returns:
            Neighborhood analysis
        """
        try:
            query = f"{neighborhood} {city} neighborhood safety amenities transportation schools reviews"
            
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=8
            )
            
            return {
                "neighborhood": neighborhood,
                "city": city,
                "summary": response.get("answer", ""),
                "key_info": response.get("results", []),
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Neighborhood info search error: %s", str(e))
            return {}

# Module-level instance
_tavily_searcher = None

def get_tavily_searcher() -> TavilySearcher:
    """Get global Tavily searcher instance"""
    global _tavily_searcher
    if _tavily_searcher is None:
        _tavily_searcher = TavilySearcher()
    return _tavily_searcher
