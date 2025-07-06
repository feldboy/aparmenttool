"""
AI Agent Manager
Central manager for all AI providers and property analysis
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables with override
load_dotenv(override=True)

from .models import (
    AIProvider, AgentConfig, AnalysisRequest, PropertyAnalysis, 
    AIResponse, AgentPerformance
)
from .providers.openai_provider import OpenAIProvider
from .providers.google_provider import GoogleProvider
from .providers.anthropic_provider import AnthropicProvider
from .providers.deepseek_provider import DeepSeekProvider

logger = logging.getLogger(__name__)

class AIAgentManager:
    """Central manager for all AI agents"""
    
    def __init__(self):
        self.providers: Dict[AIProvider, Any] = {}
        self.performance_metrics: Dict[AIProvider, AgentPerformance] = {}
        self.enabled_providers: List[AIProvider] = []
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available AI providers"""
        try:
            # OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key and openai_key not in ["your_openai_api_key_here", "your-openai-key-here", "sk-your-openai-key-here"]:
                config = AgentConfig(
                    provider=AIProvider.OPENAI,
                    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                    api_key=openai_key,
                    temperature=float(os.getenv("AI_AGENT_TEMPERATURE", "0.7")),
                    max_tokens=int(os.getenv("AI_AGENT_MAX_TOKENS", "1000")),
                    timeout=int(os.getenv("AI_AGENT_TIMEOUT", "30")),
                    max_retries=int(os.getenv("AI_AGENT_MAX_RETRIES", "3"))
                )
                self.providers[AIProvider.OPENAI] = OpenAIProvider(config)
                self.performance_metrics[AIProvider.OPENAI] = AgentPerformance(
                    provider=AIProvider.OPENAI,
                    model=config.model
                )
                self.enabled_providers.append(AIProvider.OPENAI)
                logger.info("OpenAI provider initialized")
            
            # Google
            google_key = os.getenv("GOOGLE_API_KEY")
            if google_key and google_key not in ["your_google_api_key_here", "your-google-ai-key-here"]:
                config = AgentConfig(
                    provider=AIProvider.GOOGLE,
                    model=os.getenv("GOOGLE_MODEL", "gemini-pro"),
                    api_key=google_key,
                    temperature=float(os.getenv("AI_AGENT_TEMPERATURE", "0.7")),
                    max_tokens=int(os.getenv("AI_AGENT_MAX_TOKENS", "1000")),
                    timeout=int(os.getenv("AI_AGENT_TIMEOUT", "30")),
                    max_retries=int(os.getenv("AI_AGENT_MAX_RETRIES", "3"))
                )
                self.providers[AIProvider.GOOGLE] = GoogleProvider(config)
                self.performance_metrics[AIProvider.GOOGLE] = AgentPerformance(
                    provider=AIProvider.GOOGLE,
                    model=config.model
                )
                self.enabled_providers.append(AIProvider.GOOGLE)
                logger.info("Google provider initialized")
            
            # Anthropic
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key and anthropic_key not in ["your_anthropic_api_key_here", "your-anthropic-key-here", "sk-ant-your-anthropic-key-here"]:
                config = AgentConfig(
                    provider=AIProvider.ANTHROPIC,
                    model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                    api_key=anthropic_key,
                    temperature=float(os.getenv("AI_AGENT_TEMPERATURE", "0.7")),
                    max_tokens=int(os.getenv("AI_AGENT_MAX_TOKENS", "1000")),
                    timeout=int(os.getenv("AI_AGENT_TIMEOUT", "30")),
                    max_retries=int(os.getenv("AI_AGENT_MAX_RETRIES", "3"))
                )
                self.providers[AIProvider.ANTHROPIC] = AnthropicProvider(config)
                self.performance_metrics[AIProvider.ANTHROPIC] = AgentPerformance(
                    provider=AIProvider.ANTHROPIC,
                    model=config.model
                )
                self.enabled_providers.append(AIProvider.ANTHROPIC)
                logger.info("Anthropic provider initialized")
            
            # DeepSeek
            deepseek_key = os.getenv("DEEPSEEK_API_KEY")
            logger.debug(f"DeepSeek key check: {repr(deepseek_key)}")
            if deepseek_key and deepseek_key not in ["your_deepseek_api_key_here", "your-deepseek-key-here"]:
                try:
                    config = AgentConfig(
                        provider=AIProvider.DEEPSEEK,
                        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                        api_key=deepseek_key,
                        temperature=float(os.getenv("AI_AGENT_TEMPERATURE", "0.7")),
                        max_tokens=int(os.getenv("AI_AGENT_MAX_TOKENS", "1000")),
                        timeout=int(os.getenv("AI_AGENT_TIMEOUT", "30")),
                        max_retries=int(os.getenv("AI_AGENT_MAX_RETRIES", "3"))
                    )
                    self.providers[AIProvider.DEEPSEEK] = DeepSeekProvider(config)
                    self.performance_metrics[AIProvider.DEEPSEEK] = AgentPerformance(
                        provider=AIProvider.DEEPSEEK,
                        model=config.model
                    )
                    self.enabled_providers.append(AIProvider.DEEPSEEK)
                    logger.info("DeepSeek provider initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize DeepSeek provider: {e}")
            else:
                logger.debug(f"DeepSeek not initialized - key validation failed")
            
            logger.info(f"AI Agent Manager initialized with {len(self.enabled_providers)} providers: {[p.value for p in self.enabled_providers]}")
            
        except Exception as e:
            logger.error(f"Error initializing AI providers: {e}")
    
    async def analyze_property_single(self, request: AnalysisRequest, provider: AIProvider) -> PropertyAnalysis:
        """Analyze property with a single AI provider"""
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} is not available")
        
        try:
            # Get AI response
            ai_response = await self.providers[provider].analyze_property(request)
            
            # Update performance metrics
            success = ai_response.confidence > 0.0
            self.performance_metrics[provider].update_metrics(ai_response, success)
            
            # Create property analysis
            analysis = self._create_property_analysis(request, [ai_response])
            
            logger.info(f"Property analysis completed with {provider.value}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing property with {provider.value}: {e}")
            # Create failed response
            failed_response = AIResponse(
                provider=provider,
                content=f"Error: {str(e)}",
                confidence=0.0,
                processing_time=0.0,
                tokens_used=0,
                model_used="unknown",
                timestamp=datetime.utcnow(),
                metadata={"error": str(e)}
            )
            return self._create_property_analysis(request, [failed_response])
    
    async def analyze_property_multi(self, request: AnalysisRequest, providers: Optional[List[AIProvider]] = None) -> PropertyAnalysis:
        """Analyze property with multiple AI providers and create consensus"""
        if providers is None:
            providers = self.enabled_providers
        
        if not providers:
            raise ValueError("No AI providers available")
        
        # Run analysis with all providers concurrently
        tasks = []
        for provider in providers:
            if provider in self.providers:
                task = self.providers[provider].analyze_property(request)
                tasks.append(task)
        
        # Wait for all responses
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful responses
        valid_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(f"Provider {providers[i].value} failed: {response}")
                # Create error response
                error_response = AIResponse(
                    provider=providers[i],
                    content=f"Error: {str(response)}",
                    confidence=0.0,
                    processing_time=0.0,
                    tokens_used=0,
                    model_used="unknown",
                    timestamp=datetime.utcnow(),
                    metadata={"error": str(response)}
                )
                valid_responses.append(error_response)
            else:
                valid_responses.append(response)
                # Update performance metrics
                success = response.confidence > 0.0
                self.performance_metrics[providers[i]].update_metrics(response, success)
        
        # Create consensus analysis
        analysis = self._create_property_analysis(request, valid_responses)
        
        logger.info(f"Multi-provider analysis completed with {len(valid_responses)} responses")
        return analysis
    
    def _create_property_analysis(self, request: AnalysisRequest, responses: List[AIResponse]) -> PropertyAnalysis:
        """Create property analysis from AI responses"""
        analysis = PropertyAnalysis(
            property_id=request.property_id,
            original_text=request.raw_text,
            ai_responses=responses,
            analysis_timestamp=datetime.utcnow()
        )
        
        # Extract consensus data from responses
        valid_responses = [r for r in responses if r.confidence > 0.0]
        
        if not valid_responses:
            analysis.consensus_score = 0.0
            return analysis
        
        # Calculate consensus score
        analysis.consensus_score = sum(r.confidence for r in valid_responses) / len(valid_responses)
        
        # Try to parse and merge data from successful responses
        try:
            merged_data = self._merge_analysis_data(valid_responses)
            
            # Update analysis with merged data
            analysis.location = merged_data.get("location", {}).get("address")
            analysis.neighborhood = merged_data.get("location", {}).get("neighborhood")
            analysis.city = merged_data.get("location", {}).get("city")
            analysis.property_type = merged_data.get("property_details", {}).get("property_type")
            analysis.rooms = merged_data.get("property_details", {}).get("rooms")
            analysis.bedrooms = merged_data.get("property_details", {}).get("bedrooms")
            analysis.bathrooms = merged_data.get("property_details", {}).get("bathrooms")
            analysis.size_sqm = merged_data.get("property_details", {}).get("size_sqm")
            analysis.floor = merged_data.get("property_details", {}).get("floor")
            analysis.total_floors = merged_data.get("property_details", {}).get("total_floors")
            analysis.price = merged_data.get("financial", {}).get("price")
            analysis.currency = merged_data.get("financial", {}).get("currency")
            analysis.price_per_sqm = merged_data.get("financial", {}).get("price_per_sqm")
            analysis.features = merged_data.get("features", [])
            analysis.amenities = merged_data.get("amenities", [])
            analysis.condition = merged_data.get("condition")
            analysis.quality_score = merged_data.get("quality_score")
            
        except Exception as e:
            logger.error(f"Error merging analysis data: {e}")
        
        return analysis
    
    def _merge_analysis_data(self, responses: List[AIResponse]) -> Dict[str, Any]:
        """Merge analysis data from multiple responses"""
        merged = defaultdict(dict)
        
        for response in responses:
            try:
                # Check if response has parsed_data
                if hasattr(response, 'parsed_data') and response.parsed_data:
                    data = response.parsed_data
                else:
                    # Skip if no parsed data available
                    logger.warning(f"No parsed data available for {response.provider.value}")
                    continue
                
                # Merge data with confidence weighting
                weight = response.confidence
                
                for key, value in data.items():
                    if key not in merged:
                        merged[key] = value
                    elif isinstance(value, dict) and isinstance(merged[key], dict):
                        merged[key].update(value)
                    elif isinstance(value, list) and isinstance(merged[key], list):
                        merged[key].extend(value)
                    # For conflicting values, prefer higher confidence
                    elif weight > 0.8:  # High confidence threshold
                        merged[key] = value
                        
            except Exception as e:
                logger.warning(f"Error parsing response data: {e}")
                continue
        
        return dict(merged)
    
    async def test_providers(self) -> Dict[AIProvider, bool]:
        """Test all providers connectivity"""
        results = {}
        
        for provider_type, provider in self.providers.items():
            try:
                if hasattr(provider, 'test_connection'):
                    results[provider_type] = await provider.test_connection()
                else:
                    results[provider_type] = True
            except Exception as e:
                logger.error(f"Error testing {provider_type.value}: {e}")
                results[provider_type] = False
        
        return results
    
    def get_performance_metrics(self) -> Dict[AIProvider, AgentPerformance]:
        """Get performance metrics for all providers"""
        return self.performance_metrics.copy()
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about all providers"""
        return {
            "enabled_providers": [p.value for p in self.enabled_providers],
            "total_providers": len(self.providers),
            "provider_details": {
                provider.value: self.providers[provider].get_provider_info()
                for provider in self.enabled_providers
            }
        }
    
    async def close(self):
        """Close all providers"""
        for provider in self.providers.values():
            if hasattr(provider, 'close'):
                await provider.close()
