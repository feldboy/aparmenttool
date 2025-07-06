"""
Anthropic Provider
Implementation for Anthropic Claude models
"""

import asyncio
import logging
from typing import Dict, Any
import anthropic

from .base_provider import BaseAIProvider
from ..models import AgentConfig, AIProvider

logger = logging.getLogger(__name__)

class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude provider implementation"""
    
    def _initialize_client(self):
        """Initialize Anthropic client"""
        try:
            self.client = anthropic.AsyncAnthropic(
                api_key=self.api_key,
                timeout=self.timeout
            )
            logger.info(f"Anthropic client initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise
    
    async def _make_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Make request to Anthropic API"""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system="אתה מומחה בניתוח נכסים. אנא חלץ מידע מטקסטים על נכסים בפורמט JSON מובנה בלבד.",
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nאנא החזר JSON תקני בלבד, בלי הסברים נוספים."
                    }
                ]
            )
            
            # Extract response data
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            # Parse JSON response
            parsed_data = self._parse_json_response(content)
            
            return {
                "content": content,
                "parsed_data": parsed_data,
                "confidence": parsed_data.get("confidence", 0.8),
                "tokens_used": tokens_used,
                "metadata": {
                    "model": response.model,
                    "stop_reason": response.stop_reason,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
            
        except anthropic.RateLimitError as e:
            logger.warning(f"Anthropic rate limit exceeded: {e}")
            raise
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error with Anthropic: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """Test Anthropic connection"""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return True
        except Exception as e:
            logger.error(f"Anthropic connection test failed: {e}")
            return False
