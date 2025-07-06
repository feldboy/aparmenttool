"""
Content analysis and filtering logic for property listings

This module provides:
1. Text normalization and cleaning
2. Keyword and location matching
3. Numeric filtering (price, rooms)
4. Duplicate detection hashing
5. Match scoring and ranking
6. AI-powered enhanced analysis
"""

import re
import hashlib
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from scrapers.base import ScrapedListing

logger = logging.getLogger(__name__)

# AI Agents integration
try:
    from ai_agents import AIAgentManager
    from ai_agents.models import AnalysisRequest, AIProvider
    AI_AGENTS_AVAILABLE = True
    logger.info("AI Agents integration enabled")
except ImportError:
    AI_AGENTS_AVAILABLE = False
    logger.warning("AI Agents not available - falling back to rule-based analysis")

logger = logging.getLogger(__name__)

class MatchConfidence(str, Enum):
    """Confidence levels for property matches"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NO_MATCH = "no_match"

@dataclass
class MatchResult:
    """Result of content analysis and filtering"""
    is_match: bool
    confidence: MatchConfidence
    score: float
    reasons: List[str]
    location_matches: List[str]
    price_match: bool
    rooms_match: bool
    keyword_matches: List[str]
    
    def __post_init__(self):
        if self.reasons is None:
            self.reasons = []
        if self.location_matches is None:
            self.location_matches = []
        if self.keyword_matches is None:
            self.keyword_matches = []

class ContentAnalyzer:
    """Content analysis and filtering engine"""
    
    def __init__(self):
        """Initialize the content analyzer"""
        self.logger = logging.getLogger(f"{__name__}.ContentAnalyzer")
        
        # Initialize AI Agent Manager
        if AI_AGENTS_AVAILABLE:
            self.ai_manager = AIAgentManager()
            self.use_ai_analysis = True
            self.logger.info("AI-powered content analysis enabled")
        else:
            self.ai_manager = None
            self.use_ai_analysis = False
            self.logger.warning("AI analysis not available - using rule-based analysis only")
        
        # Hebrew/English normalization mappings
        self.text_normalizations = {
            # Common Hebrew real estate terms
            'דירה': ['דירת', 'דירות', 'apartment', 'apt'],
            'חדרים': ['חדר', 'חד', 'rooms', 'room', 'חדרי'],
            'מטר': ['מ"ר', 'מטרים', 'sqm', 'm2'],
            'קומה': ['קומת', 'floor'],
            'מרפסת': ['מרפסות', 'balcony', 'terrace'],
            'חניה': ['חנייה', 'parking'],
            'מעלית': ['elevator', 'lift'],
            'משופץ': ['משופצת', 'renovated', 'refurbished'],
            'מרוהט': ['מרוהטת', 'furnished'],
            'מיזוג': ['מזגן', 'ac', 'air conditioning'],
        }
        
        # Common location aliases
        self.location_aliases = {
            'תל אביב': ['תל אביב - יפו', 'tel aviv', 'tlv'],
            'ירושלים': ['jerusalem', 'jlem'],
            'חיפה': ['haifa'],
            'דיזנגוף': ['dizengoff'],
            'רוטשילד': ['rothschild'],
            'אלנבי': ['allenby'],
            'שינקין': ['shenkin'],
            'פלורנטין': ['florentin'],
            'נווה צדק': ['neve tzedek'],
            'יפו העתיקה': ['old jaffa', 'jaffa'],
        }
        
        # Initialize Tavily for enhanced analysis
        try:
            from search.tavily import get_tavily_searcher
            self.tavily = get_tavily_searcher()
            self.use_tavily = True
            logger.info("Tavily integration enabled for enhanced content analysis")
        except ImportError:
            self.tavily = None
            self.use_tavily = False
            logger.warning("Tavily not available - using basic analysis only")

    def analyze_listing(self, listing: ScrapedListing, profile_criteria: Dict[str, Any]) -> MatchResult:
        """
        Analyze a listing against profile criteria
        
        Args:
            listing: Scraped listing to analyze
            profile_criteria: User profile search criteria
            
        Returns:
            MatchResult with analysis details
        """
        reasons = []
        location_matches = []
        keyword_matches = []
        score = 0.0
        
        # Normalize listing content
        normalized_text = self.normalize_text(listing.title + " " + listing.description + " " + listing.location)
        
        # 1. Price filtering
        price_match = self._check_price_match(listing.price, profile_criteria.get('price', {}), reasons)
        if price_match:
            score += 30.0
        
        # 2. Rooms filtering  
        rooms_match = self._check_rooms_match(listing.rooms, profile_criteria.get('rooms', {}), reasons)
        if rooms_match:
            score += 25.0
        
        # 3. Location matching
        location_score, loc_matches = self._check_location_match(
            normalized_text, listing.location, 
            profile_criteria.get('location_criteria', {}), reasons
        )
        location_matches.extend(loc_matches)
        score += location_score
        
        # 4. Property type matching
        type_score, type_keywords = self._check_property_type_match(
            normalized_text, profile_criteria.get('property_type', []), reasons
        )
        keyword_matches.extend(type_keywords)
        score += type_score
        
        # 5. Feature preferences (bonus points)
        feature_score, feature_keywords = self._check_feature_preferences(
            normalized_text, profile_criteria.get('preferred_features', []), reasons
        )
        keyword_matches.extend(feature_keywords)
        score += feature_score
        
        # Determine match status and confidence
        is_match = price_match and rooms_match and score >= 50.0
        confidence = self._calculate_confidence(score, price_match, rooms_match, len(location_matches))
        
        if is_match:
            reasons.append(f"Overall match score: {score:.1f}/100")
        
        result = MatchResult(
            is_match=is_match,
            confidence=confidence,
            score=score,
            reasons=reasons,
            location_matches=location_matches,
            price_match=price_match,
            rooms_match=rooms_match,
            keyword_matches=keyword_matches
        )
        
        self.logger.debug("Analyzed listing %s: match=%s, score=%.1f", 
                         listing.listing_id, is_match, score)
        
        return result
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize and clean text for analysis
        
        Args:
            text: Raw text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        normalized = text.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common punctuation but keep Hebrew characters
        normalized = re.sub(r'[^\w\s\u0590-\u05ff]', ' ', normalized)
        
        # Apply text normalizations
        for canonical, aliases in self.text_normalizations.items():
            for alias in aliases:
                normalized = normalized.replace(alias.lower(), canonical)
        
        return normalized
    
    def _check_price_match(self, listing_price: Optional[int], price_criteria: Dict[str, Any], reasons: List[str]) -> bool:
        """Check if listing price matches criteria"""
        if not listing_price or not price_criteria:
            reasons.append("Price not specified")
            return True  # Don't filter out if price is missing
        
        min_price = price_criteria.get('min', 0)
        max_price = price_criteria.get('max', float('inf'))
        
        if min_price <= listing_price <= max_price:
            reasons.append(f"Price {listing_price:,} ILS within range {min_price:,}-{max_price:,}")
            return True
        else:
            reasons.append(f"Price {listing_price:,} ILS outside range {min_price:,}-{max_price:,}")
            return False
    
    def _check_rooms_match(self, listing_rooms: Optional[float], rooms_criteria: Dict[str, Any], reasons: List[str]) -> bool:
        """Check if listing room count matches criteria"""
        if not listing_rooms or not rooms_criteria:
            reasons.append("Room count not specified")
            return True  # Don't filter out if rooms is missing
        
        min_rooms = rooms_criteria.get('min', 0)
        max_rooms = rooms_criteria.get('max', float('inf'))
        
        if min_rooms <= listing_rooms <= max_rooms:
            reasons.append(f"Rooms {listing_rooms} within range {min_rooms}-{max_rooms}")
            return True
        else:
            reasons.append(f"Rooms {listing_rooms} outside range {min_rooms}-{max_rooms}")
            return False
    
    def _check_location_match(self, normalized_text: str, location: str, location_criteria: Dict[str, Any], reasons: List[str]) -> Tuple[float, List[str]]:
        """Check location matching and return score + matches"""
        matches = []
        score = 0.0
        
        # Check city match
        city = location_criteria.get('city', '')
        if city and self._text_contains_location(normalized_text, city):
            matches.append(f"City: {city}")
            score += 20.0
        
        # Check neighborhood matches
        neighborhoods = location_criteria.get('neighborhoods', [])
        for neighborhood in neighborhoods:
            if self._text_contains_location(normalized_text, neighborhood):
                matches.append(f"Neighborhood: {neighborhood}")
                score += 15.0
        
        # Check street matches
        streets = location_criteria.get('streets', [])
        for street in streets:
            if self._text_contains_location(normalized_text, street):
                matches.append(f"Street: {street}")
                score += 10.0
        
        if matches:
            reasons.append(f"Location matches: {', '.join(matches)}")
        else:
            reasons.append("No specific location matches found")
        
        return score, matches
    
    def _text_contains_location(self, text: str, location: str) -> bool:
        """Check if text contains location (with aliases)"""
        location_lower = location.lower()
        
        # Direct match
        if location_lower in text:
            return True
        
        # Check aliases
        aliases = self.location_aliases.get(location, [])
        for alias in aliases:
            if alias.lower() in text:
                return True
        
        return False
    
    def _check_property_type_match(self, normalized_text: str, property_types: List[str], reasons: List[str]) -> Tuple[float, List[str]]:
        """Check property type matching"""
        matches = []
        score = 0.0
        
        for prop_type in property_types:
            prop_type_lower = prop_type.lower()
            if prop_type_lower in normalized_text:
                matches.append(prop_type)
                score += 10.0
        
        if matches:
            reasons.append(f"Property type matches: {', '.join(matches)}")
        
        return score, matches
    
    def _check_feature_preferences(self, normalized_text: str, preferred_features: List[str], reasons: List[str]) -> Tuple[float, List[str]]:
        """Check for preferred features (bonus scoring)"""
        matches = []
        score = 0.0
        
        # Common desirable features
        feature_keywords = {
            'מרפסת': ['balcony', 'terrace'],
            'חניה': ['parking'],
            'מעלית': ['elevator'],
            'מיזוג': ['ac', 'air conditioning'],
            'משופץ': ['renovated', 'refurbished'],
            'מרוהט': ['furnished'],
            'חדש': ['new'],
            'שקט': ['quiet'],
            'מרכזי': ['central'],
        }
        
        for feature, aliases in feature_keywords.items():
            if feature in normalized_text or any(alias in normalized_text for alias in aliases):
                matches.append(feature)
                score += 2.0  # Bonus points for features
        
        if matches:
            reasons.append(f"Desirable features: {', '.join(matches)}")
        
        return score, matches
    
    def _calculate_confidence(self, score: float, price_match: bool, rooms_match: bool, location_matches_count: int) -> MatchConfidence:
        """Calculate match confidence level"""
        if not price_match or not rooms_match:
            return MatchConfidence.NO_MATCH
        
        if score >= 80.0 and location_matches_count >= 2:
            return MatchConfidence.HIGH
        elif score >= 60.0 and location_matches_count >= 1:
            return MatchConfidence.MEDIUM
        elif score >= 50.0:
            return MatchConfidence.LOW
        else:
            return MatchConfidence.NO_MATCH
    
    def generate_content_hash(self, listing: ScrapedListing) -> str:
        """
        Generate content hash for duplicate detection
        Uses key fields that identify the same property
        """
        # Use key identifying fields
        hash_parts = [
            str(listing.price or 0),
            str(listing.rooms or 0),
            listing.location.strip().lower()[:50],  # First 50 chars of location
            listing.title.strip().lower()[:100],    # First 100 chars of title
        ]
        
        # Add normalized description snippet
        if listing.description:
            normalized_desc = self.normalize_text(listing.description)[:100]
            hash_parts.append(normalized_desc)
        
        content_string = "|".join(hash_parts)
        return hashlib.sha256(content_string.encode('utf-8')).hexdigest()
    
    def rank_matches(self, match_results: List[Tuple[ScrapedListing, MatchResult]]) -> List[Tuple[ScrapedListing, MatchResult]]:
        """
        Rank matched listings by relevance score
        
        Args:
            match_results: List of (listing, match_result) tuples
            
        Returns:
            Sorted list with highest scoring matches first
        """
        # Filter to only matches and sort by score (descending)
        matches_only = [(listing, result) for listing, result in match_results if result.is_match]
        
        # Sort by confidence first, then by score
        confidence_order = {
            MatchConfidence.HIGH: 3,
            MatchConfidence.MEDIUM: 2, 
            MatchConfidence.LOW: 1,
            MatchConfidence.NO_MATCH: 0
        }
        
        sorted_matches = sorted(
            matches_only,
            key=lambda x: (confidence_order[x[1].confidence], x[1].score),
            reverse=True
        )
        
        return sorted_matches

    async def analyze_with_web_context(self, listing: ScrapedListing, profile: Dict[str, Any]) -> MatchResult:
        """
        Enhanced analysis using Tavily web search for additional context
        
        Args:
            listing: Property listing to analyze
            profile: User search profile
            
        Returns:
            Enhanced match result with web context
        """
        # First run standard analysis
        basic_result = self.analyze_listing(listing, profile)
        
        # If Tavily is not available, return basic result
        if not self.use_tavily:
            return basic_result
        
        try:
            # Extract location for neighborhood search
            location_criteria = profile.get('location_criteria', {})
            city = location_criteria.get('city', '')
            
            # Enhanced checks using Tavily
            enhanced_reasons = list(basic_result.reasons)
            enhanced_score = basic_result.score
            
            # Check neighborhood information if available
            if city and listing.location:
                neighborhood_info = await self.tavily.search_neighborhood_info(
                    listing.location, city
                )
                if neighborhood_info.get('summary'):
                    enhanced_reasons.append(f"Neighborhood context: {neighborhood_info['summary'][:100]}...")
                    enhanced_score += 0.1  # Bonus for having neighborhood context
            
            # Verify listing legitimacy
            if listing.url:
                legitimacy_check = await self.tavily.verify_listing_legitimacy(
                    listing.url, listing.title or ""
                )
                legitimacy_score = legitimacy_check.get('legitimacy_score', 100)
                
                if legitimacy_score < 70:
                    enhanced_reasons.append(f"Legitimacy concern (score: {legitimacy_score})")
                    enhanced_score *= 0.8  # Reduce score for suspicious listings
                elif legitimacy_score > 90:
                    enhanced_reasons.append("High legitimacy confidence")
                    enhanced_score += 0.05
            
            # Market context search
            if listing.price and city:
                try:
                    market_trends = await self.tavily.search_market_trends(city, "apartment")
                    if market_trends.get('answer'):
                        enhanced_reasons.append(f"Market context available")
                        enhanced_score += 0.05
                except Exception as e:
                    logger.warning("Market trends search failed: %s", str(e))
            
            # Update confidence based on enhanced score
            enhanced_confidence = self._calculate_confidence(
                enhanced_score, 
                basic_result.price_match, 
                basic_result.rooms_match, 
                len(basic_result.location_matches)
            )
            
            return MatchResult(
                is_match=enhanced_score >= 0.5,
                confidence=enhanced_confidence,
                score=enhanced_score,
                reasons=enhanced_reasons,
                location_matches=basic_result.location_matches,
                price_match=basic_result.price_match,
                rooms_match=basic_result.rooms_match,
                keyword_matches=basic_result.keyword_matches
            )
            
        except Exception as e:
            logger.error("Enhanced analysis failed, using basic result: %s", str(e))
            return basic_result

    async def analyze_with_ai_agent(self, listing: ScrapedListing, profile: Dict[str, Any]) -> MatchResult:
        """
        Analyze listing using AI agent for advanced insights
        
        Args:
            listing: Property listing to analyze
            profile: User search profile
            
        Returns:
            MatchResult with AI-powered analysis details
        """
        if not AI_AGENTS_AVAILABLE:
            logger.warning("AI Agents not available - skipping AI analysis")
            return self.analyze_listing(listing, profile)  # Fallback to standard analysis
        
        try:
            # Prepare AI analysis request
            request = AnalysisRequest(
                listing_id=listing.listing_id,
                title=listing.title,
                description=listing.description,
                location=listing.location,
                price=listing.price,
                rooms=listing.rooms,
                url=listing.url,
                profile_criteria=profile,
                user_id="system",  # System-generated ID for internal requests
                agent_type=AIProvider.GPT_4,  # Use GPT-4 for analysis
                context="Analyze the property listing and provide match confidence and reasons."
            )
            
            # Send request to AI agent
            agent_response = await AIAgentManager.run_agent(request)
            
            # Parse AI response
            ai_confidence = MatchConfidence.LOW
            if agent_response and agent_response.get('confidence'):
                ai_confidence = MatchConfidence(agent_response['confidence'].lower())
            
            ai_reasons = agent_response.get('reasons', [])
            ai_score = agent_response.get('score', 0.0)
            
            return MatchResult(
                is_match=ai_score >= 0.5,
                confidence=ai_confidence,
                score=ai_score,
                reasons=ai_reasons,
                location_matches=[],  # AI analysis may not provide detailed matches
                price_match=True,     # Assume price match for AI analysis
                rooms_match=True,     # Assume rooms match for AI analysis
                keyword_matches=[]     # AI analysis may not provide keyword matches
            )
        
        except Exception as e:
            logger.error("AI analysis failed: %s", str(e))
            return self.analyze_listing(listing, profile)  # Fallback to standard analysis
    
    async def analyze_listing_with_ai(self, listing: ScrapedListing, profile_criteria: Dict[str, Any]) -> MatchResult:
        """
        Analyze a listing with AI-powered analysis
        
        Args:
            listing: Scraped listing to analyze
            profile_criteria: User profile search criteria
            
        Returns:
            MatchResult with enhanced AI analysis
        """
        if not self.use_ai_analysis:
            return self.analyze_listing(listing, profile_criteria)
        
        try:
            # Create analysis request
            request = AnalysisRequest(
                property_id=listing.id,
                raw_text=f"{listing.title}\n{listing.description}\n{listing.location}",
                source_url=listing.url,
                source_platform=listing.source.value,
                priority=1
            )
            
            # Run AI analysis with multiple providers
            analysis = await self.ai_manager.analyze_property_multi(request)
            
            # Combine AI analysis with rule-based analysis
            rule_based_result = self.analyze_listing(listing, profile_criteria)
            
            # Create enhanced match result
            return self._combine_ai_and_rule_results(analysis, rule_based_result, profile_criteria)
            
        except Exception as e:
            self.logger.error(f"AI analysis failed, falling back to rule-based: {e}")
            return self.analyze_listing(listing, profile_criteria)
    
    def _combine_ai_and_rule_results(self, ai_analysis, rule_result: MatchResult, profile_criteria: Dict[str, Any]) -> MatchResult:
        """Combine AI analysis with rule-based results"""
        try:
            # Start with rule-based score
            combined_score = rule_result.score
            reasons = rule_result.reasons.copy()
            
            # Add AI insights
            if ai_analysis.consensus_score and ai_analysis.consensus_score > 0.7:
                combined_score += 20.0  # Bonus for high AI confidence
                reasons.append(f"AI analysis confidence: {ai_analysis.consensus_score:.2f}")
            
            # Check AI-extracted location against criteria
            if ai_analysis.location or ai_analysis.city:
                ai_location = f"{ai_analysis.location or ''} {ai_analysis.city or ''}".strip()
                if self._location_matches_criteria(ai_location, profile_criteria.get('location_criteria', {})):
                    combined_score += 15.0
                    reasons.append(f"AI-extracted location match: {ai_location}")
            
            # Check AI-extracted price against criteria
            if ai_analysis.price:
                price_criteria = profile_criteria.get('price', {})
                if self._price_in_range(ai_analysis.price, price_criteria):
                    combined_score += 10.0
                    reasons.append(f"AI-extracted price match: {ai_analysis.price}")
            
            # Check AI-extracted rooms against criteria
            if ai_analysis.rooms:
                rooms_criteria = profile_criteria.get('rooms', {})
                if self._rooms_in_range(ai_analysis.rooms, rooms_criteria):
                    combined_score += 10.0
                    reasons.append(f"AI-extracted rooms match: {ai_analysis.rooms}")
            
            # Add AI features and amenities
            ai_features = (ai_analysis.features or []) + (ai_analysis.amenities or [])
            if ai_features:
                reasons.append(f"AI-detected features: {', '.join(ai_features[:3])}")
            
            # Determine final match confidence
            if combined_score >= 80:
                confidence = MatchConfidence.HIGH
            elif combined_score >= 60:
                confidence = MatchConfidence.MEDIUM
            elif combined_score >= 40:
                confidence = MatchConfidence.LOW
            else:
                confidence = MatchConfidence.NO_MATCH
            
            return MatchResult(
                is_match=combined_score >= 40,
                confidence=confidence,
                score=min(combined_score, 100.0),
                reasons=reasons,
                location_matches=rule_result.location_matches,
                price_match=rule_result.price_match or bool(ai_analysis.price),
                rooms_match=rule_result.rooms_match or bool(ai_analysis.rooms),
                keyword_matches=rule_result.keyword_matches
            )
            
        except Exception as e:
            self.logger.error(f"Error combining AI and rule results: {e}")
            return rule_result
    
    def _location_matches_criteria(self, location: str, criteria: Dict[str, Any]) -> bool:
        """Check if AI-extracted location matches criteria"""
        if not location or not criteria:
            return False
        
        location_lower = location.lower()
        for criterion in criteria.get('areas', []):
            if criterion.lower() in location_lower:
                return True
        return False
    
    def _price_in_range(self, price: float, criteria: Dict[str, Any]) -> bool:
        """Check if AI-extracted price is in range"""
        if not price or not criteria:
            return False
        
        min_price = criteria.get('min_price', 0)
        max_price = criteria.get('max_price', float('inf'))
        
        return min_price <= price <= max_price
    
    def _rooms_in_range(self, rooms: int, criteria: Dict[str, Any]) -> bool:
        """Check if AI-extracted rooms count is in range"""
        if not rooms or not criteria:
            return False
        
        min_rooms = criteria.get('min_rooms', 0)
        max_rooms = criteria.get('max_rooms', 10)
        
        return min_rooms <= rooms <= max_rooms
