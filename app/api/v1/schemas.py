"""
Pydantic schemas for API request/response types
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator


class Message(BaseModel):
    """Chat message"""
    role: Literal["system", "user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., min_length=1, max_length=100000, description="Message content (max 100KB)")
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate message content is not empty"""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


class ChatRequest(BaseModel):
    """Chat completion request"""
    model: Optional[str] = None
    provider: Optional[str] = None
    task_type: Optional[str] = Field(None, alias="task_type")  # fast, powerful, auto
    messages: List[Message] = Field(..., min_length=1, max_length=100, description="Message list (max 100 messages)")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperature (0.0-2.0)")
    max_tokens: Optional[int] = Field(None, ge=1, le=1000000, alias="max_tokens", description="Max tokens (1-1,000,000)")
    stream: Optional[bool] = False

    @field_validator('messages')
    @classmethod
    def validate_messages(cls, v: List[Message]) -> List[Message]:
        """Validate message list"""
        if not v or len(v) == 0:
            raise ValueError("At least one message is required")
        if len(v) > 100:
            raise ValueError("Maximum 100 messages allowed")
        return v
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: Optional[float]) -> Optional[float]:
        """Validate temperature range"""
        if v is not None and (v < 0.0 or v > 2.0):
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v
    
    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v: Optional[int]) -> Optional[int]:
        """Validate max_tokens range"""
        if v is not None and (v < 1 or v > 1000000):
            raise ValueError("max_tokens must be between 1 and 1,000,000")
        return v

    class Config:
        populate_by_name = True


class Choice(BaseModel):
    """Chat response choice"""
    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    """Token usage information"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class CostInfo(BaseModel):
    """Cost information"""
    input: float
    output: float
    total: float
    currency: str = "USD"


class ChatResponse(BaseModel):
    """Chat completion response"""
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Usage
    provider: str
    cost: Optional[CostInfo] = None


class RateLimitRemaining(BaseModel):
    """Rate limit remaining"""
    per_minute: int = Field(..., alias="perMinute")
    per_day: int = Field(..., alias="perDay")

    class Config:
        populate_by_name = True


class ModelRateLimit(BaseModel):
    """Model-specific rate limit"""
    per_minute: int = Field(..., alias="perMinute")
    per_day: int = Field(..., alias="perDay")

    class Config:
        populate_by_name = True


class ProviderStatus(BaseModel):
    """Provider status information"""
    name: str
    healthy: bool
    available: bool
    rate_limit_remaining: RateLimitRemaining = Field(..., alias="rateLimitRemaining")
    model_rate_limits: Optional[Dict[str, ModelRateLimit]] = Field(
        None, alias="modelRateLimits"
    )
    last_used: Optional[datetime] = Field(None, alias="lastUsed")
    error_count: int = Field(0, alias="errorCount")
    success_count: int = Field(0, alias="successCount")

    class Config:
        populate_by_name = True


class ProvidersStatusResponse(BaseModel):
    """Response for provider status endpoint"""
    providers: List[ProviderStatus]


class ModelInfo(BaseModel):
    """Model information"""
    provider: str
    model: str
    category: str  # fast, powerful
    rate_limits: Optional[ModelRateLimit] = Field(None, alias="rateLimits")
    available: Optional[bool] = True

    class Config:
        populate_by_name = True


class ModelsResponse(BaseModel):
    """Response for models endpoint"""
    models: List[ModelInfo]


class ProviderModelsResponse(BaseModel):
    """Response for provider models endpoint"""
    provider: str
    models: List[ModelInfo]


class UsageStats(BaseModel):
    """Usage statistics"""
    requests: int
    tokens: int
    errors: int
    rate_limit_hits: int = Field(..., alias="rateLimitHits")
    time_window: int = Field(..., alias="timeWindow")

    class Config:
        populate_by_name = True


class UsageResponse(BaseModel):
    """Response for usage endpoint"""
    stats: Dict[str, UsageStats]
    time_window: int = Field(..., alias="timeWindow")

    class Config:
        populate_by_name = True


class ModelStatusResponse(BaseModel):
    """Response for model status endpoint"""
    provider: str
    model: str
    rate_limits: ModelRateLimit = Field(..., alias="rateLimits")
    stored_rate_limits: Optional[Dict[str, Any]] = Field(None, alias="storedRateLimits")
    usage: UsageStats
    provider_status: Dict[str, Any] = Field(..., alias="providerStatus")

    class Config:
        populate_by_name = True


class ComponentHealth(BaseModel):
    """Component health status"""
    name: str
    status: str  # healthy, unhealthy, degraded
    message: Optional[str] = None
    response_time_ms: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str  # healthy, unhealthy, degraded
    timestamp: str
    components: Optional[Dict[str, ComponentHealth]] = None
    version: str = "2.0.0"

