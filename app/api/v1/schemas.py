"""
Pydantic schemas for API request/response types
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message"""
    role: str  # system, user, assistant
    content: str


class ChatRequest(BaseModel):
    """Chat completion request"""
    model: Optional[str] = None
    provider: Optional[str] = None
    task_type: Optional[str] = Field(None, alias="task_type")  # fast, powerful, auto
    messages: List[Message]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = Field(None, alias="max_tokens")
    stream: Optional[bool] = False

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


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str

