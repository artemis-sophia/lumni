"""
API Routes
All API endpoints integrating all components
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Optional
from sqlalchemy.orm import Session

from app.api.v1.schemas import (
    ChatRequest,
    ChatResponse,
    ProvidersStatusResponse,
    UsageResponse,
    ModelsResponse,
    ProviderModelsResponse,
    ModelStatusResponse,
    HealthResponse,
    ProviderStatus,
    RateLimitRemaining,
    ModelRateLimit,
)
from app.api.middleware import verify_api_key
from app.config import GatewayConfig, load_config
from app.storage.database import get_db
from app.core.litellm_client import LiteLLMClient
from app.core.portkey_client import PortkeyClient
from app.models.benchmark_selector import BenchmarkSelector
from app.models.task_classifier import get_detailed_classification
from app.monitoring.tracker import UsageTracker
from app.config.pricing import calculate_cost
from app.utils.logger import Logger

router = APIRouter()
logger = Logger("APIRoutes")


# Dependency to get config (cached)
_config_cache: Optional[GatewayConfig] = None

def get_gateway_config() -> GatewayConfig:
    global _config_cache
    if _config_cache is None:
        _config_cache = load_config()
    return _config_cache


# Dependency to get LiteLLM client
def get_litellm_client(config: GatewayConfig = Depends(get_gateway_config)) -> LiteLLMClient:
    return LiteLLMClient(config.litellm.config_path)


# Dependency to get Portkey client
def get_portkey_client(config: GatewayConfig = Depends(get_gateway_config)) -> PortkeyClient:
    return PortkeyClient(
        api_key=config.portkey.api_key,
        environment=config.portkey.environment,
        virtual_key=config.portkey.virtual_key,
        config=config.portkey.config
    )


# Dependency to get benchmark selector
def get_benchmark_selector(
    litellm_client: LiteLLMClient = Depends(get_litellm_client)
) -> BenchmarkSelector:
    from app.models.benchmark_selector import BenchmarkSelector
    return BenchmarkSelector(litellm_client)


# Dependency to get usage tracker
def get_usage_tracker(config: GatewayConfig = Depends(get_gateway_config)) -> UsageTracker:
    return UsageTracker(config.monitoring.alert_threshold)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint (no auth required)"""
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    chat_request: ChatRequest = Body(..., embed=False),
    api_key: str = Depends(verify_api_key),
    config: GatewayConfig = Depends(get_gateway_config),
    litellm_client: LiteLLMClient = Depends(get_litellm_client),
    portkey_client: PortkeyClient = Depends(get_portkey_client),
    benchmark_selector: BenchmarkSelector = Depends(get_benchmark_selector),
    usage_tracker: UsageTracker = Depends(get_usage_tracker),
    db: Session = Depends(get_db)
):
    """Chat completion endpoint"""
    try:
        
        # Classify task if auto mode
        if chat_request.task_type == 'auto' or not chat_request.task_type:
            classification = get_detailed_classification(chat_request)
            logger.info(f"Task classified as {classification.task_type} with confidence {classification.confidence:.2f}")

        # Select model
        selection = await benchmark_selector.select_model(chat_request)
        logger.info(f"Selected model: {selection.model} from {selection.provider} - {selection.reason}")

        # Execute via LiteLLM with Portkey tracking
        async def completion_fn():
            # Create a new request with selected model
            selected_request = ChatRequest(
                model=selection.model,
                provider=selection.provider,
                messages=chat_request.messages,
                temperature=chat_request.temperature,
                max_tokens=chat_request.max_tokens,
                stream=chat_request.stream
            )
            return await litellm_client.chat(selected_request, proxy=proxy)

        response = await portkey_client.track_completion(chat_request, completion_fn)

        # Calculate cost
        cost = calculate_cost(
            response.provider,
            response.model,
            response.usage.prompt_tokens,
            response.usage.completion_tokens
        )

        # Track usage
        await usage_tracker.record_request(
            provider=response.provider,
            tokens=response.usage.total_tokens,
            success=True,
            rate_limit_hit=False,
            model=response.model,
            db=db
        )

        # Enhance response with cost
        response.cost = {
            "input": response.usage.prompt_tokens / 1_000_000,
            "output": response.usage.completion_tokens / 1_000_000,
            "total": cost,
            "currency": "USD"
        }

        return response

    except Exception as e:
        logger.error(f"Chat request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers/status", response_model=ProvidersStatusResponse)
async def get_providers_status(
    api_key: str = Depends(verify_api_key),
    config: GatewayConfig = Depends(get_gateway_config),
    usage_tracker: UsageTracker = Depends(get_usage_tracker),
    db: Session = Depends(get_db)
):
    """Get provider statuses"""
    from app.storage.repositories import ProviderStateRepository, ModelRateLimitsRepository
    from app.config.rate_limits import get_provider_rate_limit
    from datetime import datetime, timedelta
    
    providers = []
    
    # Get all configured providers
    for provider_name, provider_config in config.providers.items():
        if not provider_config.enabled:
            continue
        
        # Get provider state from database
        state = ProviderStateRepository.get(db, provider_name)
        
        # Get rate limit config
        rate_limit_config = get_provider_rate_limit(provider_name)
        
        # Get stored rate limits from database
        stored_rate_limits = ModelRateLimitsRepository.get_all(db)
        model_rate_limits = {}
        for stored in stored_rate_limits:
            if stored.provider == provider_name:
                model_rate_limits[stored.model or "default"] = ModelRateLimit(
                    perMinute=stored.per_minute,
                    perDay=stored.per_day
                )
        
        # Get usage stats for last hour
        stats = usage_tracker.get_provider_stats(provider_name, time_window=3600000, db=db)
        
        # Calculate rate limit remaining (simplified - would need actual tracking)
        # Use configured rate limits as remaining (in real implementation, would track actual remaining)
        per_minute = rate_limit_config.requests_per_minute if rate_limit_config else provider_config.rate_limit.requests_per_minute
        per_day = rate_limit_config.requests_per_day if rate_limit_config else provider_config.rate_limit.requests_per_day
        
        # Determine health status
        healthy = state.healthy if state else True
        available = state.available if state else True
        
        # If we have recent errors, mark as potentially unhealthy
        if stats and stats.get("requests", 0) > 0:
            error_rate = stats.get("errors", 0) / stats.get("requests", 1)
            if error_rate > 0.5:
                healthy = False
        
        provider_status = ProviderStatus(
            name=provider_name,
            healthy=healthy,
            available=available,
            rate_limit_remaining=RateLimitRemaining(
                perMinute=per_minute,
                perDay=per_day
            ),
            model_rate_limits=model_rate_limits if model_rate_limits else None,
            last_used=state.last_used if state else None,
            error_count=state.error_count if state else 0,
            success_count=state.success_count if state else 0
        )
        
        providers.append(provider_status)
    
    return ProvidersStatusResponse(providers=providers)


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    window: int = Query(3600000, description="Time window in milliseconds"),
    api_key: str = Depends(verify_api_key),
    usage_tracker: UsageTracker = Depends(get_usage_tracker),
    db: Session = Depends(get_db)
):
    """Get usage statistics"""
    stats = usage_tracker.get_all_stats(time_window=window, db=db)
    return UsageResponse(
        stats={k: v for k, v in stats.items()},
        time_window=window
    )


@router.get("/models", response_model=ModelsResponse)
async def get_models(
    api_key: str = Depends(verify_api_key),
    benchmark_selector: BenchmarkSelector = Depends(get_benchmark_selector)
):
    """List all available models"""
    models = await benchmark_selector.get_all_models()
    return ModelsResponse(models=models)


@router.get("/models/{provider}", response_model=ProviderModelsResponse)
async def get_provider_models(
    provider: str,
    api_key: str = Depends(verify_api_key),
    benchmark_selector: BenchmarkSelector = Depends(get_benchmark_selector)
):
    """List models for a specific provider"""
    models = await benchmark_selector.get_models_by_provider(provider)
    if not models:
        raise HTTPException(
            status_code=404,
            detail=f"Provider {provider} not found or has no available models"
        )
    return ProviderModelsResponse(provider=provider, models=models)


@router.get("/models/{provider}/{model}/status", response_model=ModelStatusResponse)
async def get_model_status(
    provider: str,
    model: str,
    window: int = Query(3600000, description="Time window in milliseconds"),
    api_key: str = Depends(verify_api_key),
    usage_tracker: UsageTracker = Depends(get_usage_tracker),
    db: Session = Depends(get_db)
):
    """Get usage and rate limits for a specific model"""
    from app.config.rate_limits import get_model_rate_limit

    # Get rate limits
    rate_limit = get_model_rate_limit(provider, model)
    if not rate_limit:
        raise HTTPException(
            status_code=404,
            detail=f"Rate limits not found for model {model} on provider {provider}"
        )

    # Get usage stats
    stats = usage_tracker.get_model_stats(provider, model, time_window=window, db=db)

    return ModelStatusResponse(
        provider=provider,
        model=model,
        rate_limits={
            "per_minute": rate_limit.requests_per_minute,
            "per_day": rate_limit.requests_per_day
        },
        stored_rate_limits=None,
        usage=stats,
        provider_status={
            "healthy": True,
            "available": True,
            "last_used": None
        }
    )

