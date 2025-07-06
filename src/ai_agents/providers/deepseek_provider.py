"""
DeepSeek Provider
Implementation for DeepSeek models
"""

import asyncio
import logging
from typing import Dict, Any
import httpx
import json

from .base_provider import BaseAIProvider
from ..models import AgentConfig, AIProvider

logger = logging.getLogger(__name__)

class DeepSeekProvider(BaseAIProvider):
    """DeepSeek provider implementation"""
    
    def _initialize_client(self):
        """Initialize DeepSeek client"""
        try:
            self.api_url = "https://api.deepseek.com/v1/chat/completions"
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.client = httpx.AsyncClient(timeout=self.timeout)
            logger.info(f"DeepSeek client initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek client: {e}")
            raise
    
    async def _make_request(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Make request to DeepSeek API"""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "אתה מומחה בניתוח נכסים. אנא חלץ מידע מטקסטים על נכסים בפורמט JSON מובנה."
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nאנא החזר JSON תקני בלבד, בלי הסברים נוספים."
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False
            }
            
            response = await self.client.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"DeepSeek API returned status {response.status_code}: {response.text}")
            
            result = response.json()
            
            # Extract response data
            content = result["choices"][0]["message"]["content"]
            tokens_used = result["usage"]["total_tokens"]
            
            # Debug logging
            logger.debug(f"DeepSeek raw response: {content[:200]}...")
            
            # Parse JSON response
            parsed_data = self._parse_json_response(content)
            
            return {
                "content": content,
                "parsed_data": parsed_data,
                "confidence": parsed_data.get("confidence", 0.7),
                "tokens_used": tokens_used,
                "metadata": {
                    "model": result["model"],
                    "finish_reason": result["choices"][0]["finish_reason"],
                    "prompt_tokens": result["usage"]["prompt_tokens"],
                    "completion_tokens": result["usage"]["completion_tokens"]
                }
            }
            
        except httpx.TimeoutException as e:
            logger.error(f"DeepSeek API timeout: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"DeepSeek API HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error with DeepSeek: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """Test DeepSeek connection"""
        try:
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = await self.client.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"DeepSeek connection test failed: {e}")
            return False
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
