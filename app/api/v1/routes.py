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
    ComponentHealth,
    ProviderStatus,
    RateLimitRemaining,
    ModelRateLimit,
)
from app.api.middleware import verify_api_key
from app.config import GatewayConfig
from app.config.manager import get_config_manager
from app.storage.database import get_db
from app.storage.models import ProviderState
from app.core.litellm_client import LiteLLMClient
from app.core.portkey_client import PortkeyClient
from app.models.benchmark_selector import BenchmarkSelector
from app.models.task_classifier import get_detailed_classification
from app.monitoring.tracker import UsageTracker
from app.config.pricing import calculate_cost
from app.utils.logger import Logger
from app.utils.exceptions import (
    LumniError,
    ProviderError,
    RateLimitError,
    ValidationError,
    AuthenticationError,
    ConfigurationError,
)
from app.utils.error_context import ErrorContext, create_error_context
from fastapi import Request

router = APIRouter()
logger = Logger("APIRoutes")


def get_request_id(request: Request) -> str:
    """Get request ID from request state"""
    return getattr(request.state, "request_id", "unknown")


# Dependency to get config (thread-safe singleton)
from app.config.manager import get_config_manager

def get_gateway_config() -> GatewayConfig:
    """Get gateway config with thread-safe caching"""
    return get_config_manager().load()


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


# Dependency to get provider health checker
def get_provider_health_checker(config: GatewayConfig = Depends(get_gateway_config)) -> ProviderHealthChecker:
    return ProviderHealthChecker(health_check_ttl=config.fallback.health_check_interval // 1000)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint with component status (no auth required)"""
    from datetime import datetime
    import time
    from app.storage.database import check_database_connection
    from app.config.manager import get_config_manager
    from app.core.cache import Cache
    
    components = {}
    overall_status = "healthy"
    
    # Check database connection
    db_start = time.time()
    db_healthy, db_error = check_database_connection()
    db_time = (time.time() - db_start) * 1000
    components["database"] = ComponentHealth(
        name="database",
        status="healthy" if db_healthy else "unhealthy",
        message="Database connection successful" if db_healthy else (db_error or "Database connection failed"),
        response_time_ms=round(db_time, 2)
    )
    if not db_healthy:
        overall_status = "unhealthy"
    
    # Check cache if configured
    try:
        from app.config.manager import get_config_manager
        config = get_config_manager().load()
        if config.cache.type == "redis" and config.cache.connection_string:
            cache_start = time.time()
            try:
                cache = Cache(config.cache.connection_string)
                await cache.connect()
                # Test cache operation
                await cache.set("__health_check__", "test", ttl=1)
                await cache.get("__health_check__")
                cache_healthy = True
                cache_message = "Redis cache connection successful"
            except Exception as e:
                cache_healthy = False
                cache_message = f"Redis cache connection failed: {str(e)}"
            finally:
                await cache.disconnect()
            cache_time = (time.time() - cache_start) * 1000
            components["cache"] = ComponentHealth(
                name="cache",
                status="healthy" if cache_healthy else "degraded",  # Cache is optional
                message=cache_message,
                response_time_ms=round(cache_time, 2)
            )
            if not cache_healthy:
                overall_status = "degraded" if overall_status == "healthy" else overall_status
    except Exception as e:
        components["cache"] = ComponentHealth(
            name="cache",
            status="degraded",
            message=f"Cache health check skipped: {str(e)}"
        )
        overall_status = "degraded" if overall_status == "healthy" else overall_status
    
    # Check configuration
    config_start = time.time()
    try:
        from app.config.manager import get_config_manager
        config = get_config_manager().load()
        config_healthy = True
        config_message = "Configuration loaded successfully"
    except Exception as e:
        config_healthy = False
        config_message = f"Configuration load failed: {str(e)}"
        overall_status = "unhealthy"
    config_time = (time.time() - config_start) * 1000
    components["configuration"] = ComponentHealth(
        name="configuration",
        status="healthy" if config_healthy else "unhealthy",
        message=config_message,
        response_time_ms=round(config_time, 2)
    )
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now().isoformat(),
        components=components,
        version="2.0.0"
    )


@router.get("/health/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness probe - checks if service is ready to accept traffic"""
    from datetime import datetime
    from app.storage.database import check_database_connection
    from app.config.manager import get_config_manager
    
    # Readiness checks: database must be available
    db_ready, _ = check_database_connection()
    
    try:
        config = get_config_manager().load()
        config_ready = True
    except Exception:
        config_ready = False
    
    ready = db_ready and config_ready
    
    return HealthResponse(
        status="healthy" if ready else "unhealthy",
        timestamp=datetime.now().isoformat(),
        version="2.0.0"
    )


@router.get("/health/live", response_model=HealthResponse)
async def liveness_check():
    """Liveness probe - checks if service is alive"""
    from datetime import datetime
    
    # Liveness is simple - just check if the service responds
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="2.0.0"
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    request: Request,
    chat_request: ChatRequest = Body(..., embed=False),
    api_key: str = Depends(verify_api_key),
    config: GatewayConfig = Depends(get_gateway_config),
    litellm_client: LiteLLMClient = Depends(get_litellm_client),
    portkey_client: PortkeyClient = Depends(get_portkey_client),
    benchmark_selector: BenchmarkSelector = Depends(get_benchmark_selector),
    usage_tracker: UsageTracker = Depends(get_usage_tracker),
    db: Session = Depends(get_db)
):
    """Chat completion endpoint with rate limiting"""
    import asyncio
    request_id = get_request_id(request)
    
    # Rate limiting is handled by decorator if slowapi is available
    # The limiter middleware will automatically apply limits
    
    # Apply request timeout from config (timeout is handled at LiteLLM client level)
    request_timeout = config.server.request_timeout
    
    try:
        # Classify task if auto mode
        if chat_request.task_type == 'auto' or not chat_request.task_type:
            classification = get_detailed_classification(chat_request)
            logger.info(f"Task classified as {classification.task_type} with confidence {classification.confidence:.2f}")

        # Select model
        selection = await benchmark_selector.select_model(chat_request)
        logger.info(f"Selected model: {selection.model} from {selection.provider} - {selection.reason}")
        
        # Check provider health before use
        from app.core.provider_health_checker import ProviderHealthChecker
        health_checker = ProviderHealthChecker()
        provider_healthy = await health_checker.check_provider_health(
            selection.provider,
            litellm_client,
            force_check=False
        )
        
        if not provider_healthy:
            logger.warn(f"Provider {selection.provider} is unhealthy, but proceeding with request")
            # In a full implementation, you might want to select a different provider here

        # Execute via LiteLLM with Portkey tracking
        # Get proxy URL from environment or config
        # Note: config.litellm.proxy is a dict with enabled/rotationInterval flags
        # The actual proxy URL should come from environment variables (HTTP_PROXY, HTTPS_PROXY)
        # or be configured elsewhere. For now, we don't pass proxy to litellm_client
        # as it will use environment variables automatically if set.
        proxy = None  # Proxy is handled via environment variables in litellm_client
        
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

    except (ProviderError, RateLimitError, ValidationError) as e:
        # Known errors - log with context and re-raise as HTTPException
        error_context = create_error_context(
            error_type=e.code,
            message=e.message,
            request_id=request_id,
            provider=getattr(e, 'provider', None),
            model=getattr(e, 'model', None),
            original_exception=e,
            **e.details
        )
        logger.error(
            f"Chat request failed: {e.code} - {e.message}",
            meta=error_context.to_dict()
        )
        
        # For provider errors, check if all providers failed and provide graceful degradation
        if isinstance(e, ProviderError):
            # Get provider status to provide helpful error message
            try:
                from app.storage.repositories import ProviderStateRepository
                provider_states = db.query(ProviderState).filter(
                    ProviderState.provider.in_(list(config.providers.keys()))
                ).all()
                available_providers = [p.provider for p in provider_states if p.available and p.healthy]
                
                if not available_providers:
                    # All providers failed - graceful degradation
                    raise HTTPException(
                        status_code=503,
                        detail={
                            "error": "All providers are currently unavailable. Please try again later.",
                            "code": "ALL_PROVIDERS_UNAVAILABLE",
                            "request_id": request_id,
                            "provider_status": {
                                "total_providers": len(config.providers),
                                "available_providers": 0,
                                "suggestion": "Please retry after a few moments. The service will automatically retry when providers become available."
                            },
                            "retry_after": 60  # Suggest retry after 60 seconds
                        },
                        headers={"Retry-After": "60"}
                    )
            except Exception:
                pass  # Fall through to original error handling
        
        raise HTTPException(
            status_code=400 if isinstance(e, (ValidationError, RateLimitError)) else 502,
            detail={
                "error": e.message,
                "code": e.code,
                "request_id": request_id
            }
        ) from e
    except Exception as e:
        # Unknown errors - log full details but return generic message to client
        error_context = create_error_context(
            error_type="INTERNAL_ERROR",
            message=f"Unexpected error: {str(e)}",
            request_id=request_id,
            original_exception=e
        )
        logger.error(
            f"Unexpected error in chat request: {str(e)}",
            meta=error_context.to_dict(),
            exc_info=True  # Include full stack trace
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An internal error occurred while processing your request",
                "code": "INTERNAL_ERROR",
                "request_id": request_id
            }
        ) from e


@router.get("/providers/status", response_model=ProvidersStatusResponse)
async def get_providers_status(
    request: Request,
    api_key: str = Depends(verify_api_key),
    config: GatewayConfig = Depends(get_gateway_config),
    usage_tracker: UsageTracker = Depends(get_usage_tracker),
    db: Session = Depends(get_db)
):
    """Get provider statuses (cached for 30 seconds)"""
    from app.storage.repositories import ProviderStateRepository, ModelRateLimitsRepository
    from app.storage.models import ProviderState
    from app.config.rate_limits import get_provider_rate_limit
    from datetime import datetime, timedelta
    
    # Check cache if available
    cache_key = "provider_status:all"
    cache = getattr(request.app.state, 'cache', None)
    
    if cache:
        try:
            cached_result = await cache.get_json(cache_key)
            if cached_result:
                logger.debug("Returning cached provider status")
                return ProvidersStatusResponse(**cached_result)
        except Exception as e:
            logger.warn(f"Cache read failed: {str(e)}")
    
    providers = []
    
    # Get all enabled provider names
    enabled_providers = [
        name for name, provider_config in config.providers.items()
        if provider_config.enabled
    ]
    
    if not enabled_providers:
        return ProvidersStatusResponse(providers=[])
    
    # Batch query all provider states at once (fix N+1 query problem)
    provider_states = {
        state.provider: state
        for state in db.query(ProviderState).filter(
            ProviderState.provider.in_(enabled_providers)
        ).all()
    }
    
    # Get all stored rate limits at once
    stored_rate_limits = ModelRateLimitsRepository.get_all(db)
    all_model_rate_limits = {}
    for stored in stored_rate_limits:
        if stored.provider not in all_model_rate_limits:
            all_model_rate_limits[stored.provider] = {}
        all_model_rate_limits[stored.provider][stored.model or "default"] = ModelRateLimit(
            perMinute=stored.per_minute,
            perDay=stored.per_day
        )
    
    # Get all configured providers
    for provider_name, provider_config in config.providers.items():
        if not provider_config.enabled:
            continue
        
        # Get provider state from batch query result
        state = provider_states.get(provider_name)
        
        # Get rate limit config
        rate_limit_config = get_provider_rate_limit(provider_name)
        
        # Get stored rate limits from batch query result
        model_rate_limits = all_model_rate_limits.get(provider_name, {})
        
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
    
    response = ProvidersStatusResponse(providers=providers)
    
    # Cache the result for 30 seconds
    if cache:
        try:
            await cache.set_json(cache_key, response.model_dump(), ttl=30)
        except Exception as e:
            logger.warn(f"Cache write failed: {str(e)}")
    
    return response


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

