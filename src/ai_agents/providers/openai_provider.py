"""
OpenAI Provider
Implementation for OpenAI GPT models
"""

import asyncio
import logging
from typing import Dict, Any
import openai

from .base_provider import BaseAIProvider
from ..models import AgentConfig, AIProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider implementation"""
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            self.client = openai.AsyncOpenAI(
                api_key=self.api_key,
                timeout=self.timeout
            )
            logger.info(f"OpenAI client initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    async def _make_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Make request to OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "אתה מומחה בניתוח נכסים. אנא חלץ מידע מטקסטים על נכסים בפורמט JSON מובנה."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Extract response data
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Parse JSON response
            parsed_data = self._parse_json_response(content)
            
            return {
                "content": content,
                "parsed_data": parsed_data,
                "confidence": parsed_data.get("confidence", 0.8),
                "tokens_used": tokens_used,
                "metadata": {
                    "model": response.model,
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            }
            
        except openai.RateLimitError as e:
            logger.warning(f"OpenAI rate limit exceeded: {e}")
            raise
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error with OpenAI: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """Test OpenAI connection"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False
