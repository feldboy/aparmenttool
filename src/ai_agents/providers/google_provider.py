"""
Google AI Provider
Implementation for Google Gemini models
"""

import asyncio
import logging
from typing import Dict, Any
import google.generativeai as genai

from .base_provider import BaseAIProvider
from ..models import AgentConfig, AIProvider

logger = logging.getLogger(__name__)

class GoogleProvider(BaseAIProvider):
    """Google Gemini provider implementation"""
    
    def _initialize_client(self):
        """Initialize Google AI client"""
        try:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(
                model_name=self.model,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )
            logger.info(f"Google AI client initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Google AI client: {e}")
            raise
    
    async def _make_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Make request to Google AI API"""
        try:
            # Add JSON format instruction
            json_prompt = f"""
{prompt}

אנא החזר את התשובה בפורמט JSON תקני בלבד, בלי הסברים נוספים.
"""
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.client.generate_content, json_prompt
            )
            
            # Extract response data
            content = response.text
            tokens_used = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            
            # Parse JSON response
            parsed_data = self._parse_json_response(content)
            
            return {
                "content": content,
                "parsed_data": parsed_data,
                "confidence": parsed_data.get("confidence", 0.8),
                "tokens_used": tokens_used,
                "metadata": {
                    "model": self.model,
                    "finish_reason": response.candidates[0].finish_reason.name if response.candidates else None,
                    "safety_ratings": [
                        {
                            "category": rating.category.name,
                            "probability": rating.probability.name
                        }
                        for rating in response.candidates[0].safety_ratings
                    ] if response.candidates else []
                }
            }
            
        except Exception as e:
            logger.error(f"Google AI API error: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """Test Google AI connection"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.client.generate_content, "Hello"
            )
            return True
        except Exception as e:
            logger.error(f"Google AI connection test failed: {e}")
            return False
