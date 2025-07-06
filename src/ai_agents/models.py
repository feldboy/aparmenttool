"""
AI Agents Models
Data models for AI agent responses and configurations
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

class AIProvider(str, Enum):
    """AI Provider types"""
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"

@dataclass
class AIResponse:
    """AI Agent response model"""
    provider: AIProvider
    content: str
    confidence: float  # 0.0 to 1.0
    processing_time: float  # in seconds
    tokens_used: int
    model_used: str
    timestamp: datetime
    metadata: Dict[str, Any]
    parsed_data: Optional[Dict[str, Any]] = None  # Parsed structured data
    
    def __post_init__(self):
        """Post-initialization validation"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if self.processing_time < 0:
            raise ValueError("Processing time cannot be negative")

@dataclass
class PropertyAnalysis:
    """Property analysis result from AI agents"""
    property_id: str
    original_text: str
    
    # Location analysis
    location: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    
    # Property details
    property_type: Optional[str] = None
    rooms: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    size_sqm: Optional[float] = None
    floor: Optional[int] = None
    total_floors: Optional[int] = None
    
    # Financial information
    price: Optional[float] = None
    currency: Optional[str] = None
    price_per_sqm: Optional[float] = None
    
    # Features and amenities
    features: List[str] = None
    amenities: List[str] = None
    
    # Condition and quality
    condition: Optional[str] = None
    quality_score: Optional[float] = None  # 0.0 to 10.0
    
    # AI analysis metadata
    ai_responses: List[AIResponse] = None
    consensus_score: Optional[float] = None  # Agreement between AI agents
    analysis_timestamp: datetime = None
    
    def __post_init__(self):
        """Post-initialization setup"""
        if self.features is None:
            self.features = []
        if self.amenities is None:
            self.amenities = []
        if self.ai_responses is None:
            self.ai_responses = []
        if self.analysis_timestamp is None:
            self.analysis_timestamp = datetime.utcnow()

@dataclass
class AnalysisRequest:
    """Request for property analysis"""
    property_id: str
    raw_text: str
    source_url: Optional[str] = None
    source_platform: Optional[str] = None
    images: List[str] = None
    priority: int = 1  # 1 (high) to 5 (low)
    
    def __post_init__(self):
        """Post-initialization setup"""
        if self.images is None:
            self.images = []
        if not 1 <= self.priority <= 5:
            raise ValueError("Priority must be between 1 and 5")

@dataclass
class AgentConfig:
    """Configuration for AI agent"""
    provider: AIProvider
    model: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 30
    max_retries: int = 3
    
    def __post_init__(self):
        """Validate configuration"""
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        if self.max_tokens <= 0:
            raise ValueError("Max tokens must be positive")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")

@dataclass
class AgentPerformance:
    """Performance metrics for AI agent"""
    provider: AIProvider
    model: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    average_confidence: float = 0.0
    total_tokens_used: int = 0
    last_used: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate percentage"""
        return 100.0 - self.success_rate
    
    def update_metrics(self, response: AIResponse, success: bool):
        """Update performance metrics"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
            # Update averages
            if self.successful_requests == 1:
                self.average_response_time = response.processing_time
                self.average_confidence = response.confidence
            else:
                # Running average
                n = self.successful_requests
                self.average_response_time = ((n - 1) * self.average_response_time + response.processing_time) / n
                self.average_confidence = ((n - 1) * self.average_confidence + response.confidence) / n
        else:
            self.failed_requests += 1
        
        self.total_tokens_used += response.tokens_used
        self.last_used = datetime.utcnow()
