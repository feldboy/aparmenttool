"""
Base AI Provider
Abstract base class for all AI providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import logging
from datetime import datetime

from ..models import AIResponse, AgentConfig, AIProvider, AnalysisRequest

logger = logging.getLogger(__name__)

class BaseAIProvider(ABC):
    """Base class for all AI providers"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.provider_type = config.provider
        self.model = config.model
        self.api_key = config.api_key
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.timeout = config.timeout
        self.max_retries = config.max_retries
        
        # Initialize client
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the AI client"""
        pass
    
    @abstractmethod
    async def _make_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Make API request to the AI provider"""
        pass
    
    def _create_property_analysis_prompt(self, request: AnalysisRequest) -> str:
        """Create structured prompt for property analysis"""
        prompt = f"""
אנליזה מפורטת של נכס מבוססת על הטקסט הבא:

טקסט מקורי:
{request.raw_text}

אנא חלץ את המידע הבא בפורמט JSON:
{{
    "location": {{
        "address": "כתובת מדויקת",
        "neighborhood": "שכונה",
        "city": "עיר"
    }},
    "property_details": {{
        "property_type": "סוג הנכס (דירה/בית/סטודיו וכו')",
        "rooms": "מספר חדרים (מספר)",
        "bedrooms": "מספר חדרי שינה (מספר)",
        "bathrooms": "מספר חדרי רחצה (מספר)",
        "size_sqm": "גודל במ״ר (מספר)",
        "floor": "קומה (מספר)",
        "total_floors": "סך הכל קומות בבניין (מספר)"
    }},
    "financial": {{
        "price": "מחיר (מספר)",
        "currency": "מטבע (שקל/דולר/יורו)",
        "price_per_sqm": "מחיר למ״ר (מספר)"
    }},
    "features": [
        "רשימת תכונות ויתרונות"
    ],
    "amenities": [
        "רשימת שירותים וציוד"
    ],
    "condition": "מצב הנכס (חדש/משופץ/דרוש שיפוץ וכו')",
    "quality_score": "ציון איכות מ-1 עד 10",
    "summary": "סיכום קצר של הנכס",
    "confidence": "רמת ביטחון בניתוח מ-0 עד 1"
}}

חשוב: החזר רק JSON תקני, בלי הסברים נוספים.
"""
        return prompt
    
    async def analyze_property(self, request: AnalysisRequest) -> AIResponse:
        """Analyze property using the AI provider"""
        start_time = time.time()
        
        try:
            # Create prompt
            prompt = self._create_property_analysis_prompt(request)
            
            # Make API request with retries
            response_data = await self._make_request_with_retries(prompt)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create AI response
            ai_response = AIResponse(
                provider=self.provider_type,
                content=response_data.get('content', ''),
                confidence=response_data.get('confidence', 0.7),
                processing_time=processing_time,
                tokens_used=response_data.get('tokens_used', 0),
                model_used=self.model,
                timestamp=datetime.utcnow(),
                metadata=response_data.get('metadata', {}),
                parsed_data=response_data.get('parsed_data', {})
            )
            
            logger.info(f"Property analysis completed by {self.provider_type} in {processing_time:.2f}s")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error in property analysis with {self.provider_type}: {e}")
            # Return error response
            return AIResponse(
                provider=self.provider_type,
                content=f"Error: {str(e)}",
                confidence=0.0,
                processing_time=time.time() - start_time,
                tokens_used=0,
                model_used=self.model,
                timestamp=datetime.utcnow(),
                metadata={"error": str(e)}
            )
    
    async def _make_request_with_retries(self, prompt: str) -> Dict[str, Any]:
        """Make API request with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await self._make_request(prompt)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}), "
                                 f"retrying in {wait_time}s: {e}")
                    await self._wait(wait_time)
        
        # If all retries failed
        raise last_exception
    
    async def _wait(self, seconds: float):
        """Async wait helper"""
        import asyncio
        await asyncio.sleep(seconds)
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from AI model"""
        import json
        import re
        
        logger.debug("Attempting to parse JSON content: %s...", content[:200])
        
        # Clean the content - remove markdown code blocks
        cleaned_content = content.strip()
        if cleaned_content.startswith('```json'):
            cleaned_content = cleaned_content[7:]  # Remove ```json
        if cleaned_content.startswith('```'):
            cleaned_content = cleaned_content[3:]   # Remove ```
        if cleaned_content.endswith('```'):
            cleaned_content = cleaned_content[:-3]  # Remove trailing ```
        cleaned_content = cleaned_content.strip()
        
        # Try to extract JSON from response
        try:
            # First try direct JSON parsing on cleaned content
            result = json.loads(cleaned_content)
            logger.debug("Successfully parsed JSON directly")
            return result
        except json.JSONDecodeError as e:
            logger.debug("Direct JSON parsing failed: %s", e)
            # Try to find JSON block in response
            json_match = re.search(r'\{.*\}', cleaned_content, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    logger.debug("Successfully parsed JSON from extracted block")
                    return result
                except json.JSONDecodeError as e2:
                    logger.debug("JSON block parsing also failed: %s", e2)
        
        # If parsing fails, return structured error
        logger.warning("Failed to parse JSON, returning error structure")
        return {
            "error": "Failed to parse JSON response",
            "raw_content": content,
            "confidence": 0.0
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            "provider": self.provider_type.value,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "max_retries": self.max_retries
        }
