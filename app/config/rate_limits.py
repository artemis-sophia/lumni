"""
Rate Limit Configuration System
Comprehensive rate limit configuration for all providers and models.
"""

from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    provider: str
    model: Optional[str] = None  # If None, applies to all models for provider
    requests_per_minute: int = 0
    requests_per_day: int = 0
    tokens_per_minute: Optional[int] = None
    tokens_per_day: Optional[int] = None
    input_tokens_per_minute: Optional[int] = None
    output_tokens_per_minute: Optional[int] = None
    notes: Optional[str] = None


# Rate limit configurations for all providers
RATE_LIMIT_CONFIGS: List[RateLimitConfig] = [
    # GitHub Models API
    RateLimitConfig(
        'github-copilot',
        requests_per_minute=60,
        requests_per_day=5000,
        notes='Pro account limits. Actual limits may vary by account tier.'
    ),

    # Groq - Free Tier (default)
    RateLimitConfig(
        'groq',
        requests_per_minute=30,
        requests_per_day=1000,
        notes='Free tier limits. Paid tiers have higher limits.'
    ),
    RateLimitConfig(
        'groq',
        model='llama-3.1-8b-instant',
        requests_per_minute=30,
        requests_per_day=1000,
        notes='Fast model, higher throughput possible.'
    ),
    RateLimitConfig(
        'groq',
        model='llama-3.1-405b-reasoning',
        requests_per_minute=10,
        requests_per_day=500,
        notes='Large model, lower rate limits.'
    ),

    # DeepSeek - No official rate limits
    RateLimitConfig(
        'deepseek',
        requests_per_minute=999999,
        requests_per_day=999999,
        notes='No official rate limits. May experience throttling during high traffic.'
    ),

    # OpenRouter
    RateLimitConfig(
        'openrouter',
        requests_per_minute=100,
        requests_per_day=5000,
        notes='Limits vary by account tier and underlying model provider.'
    ),

    # Google Gemini - Tier 1 (Pro Account)
    RateLimitConfig(
        'gemini',
        model='gemini-2.0-flash-exp',
        requests_per_minute=2000,
        requests_per_day=999999,
        tokens_per_minute=4000000,
        notes='Tier 1 pro account limits.'
    ),
    RateLimitConfig(
        'gemini',
        model='gemini-2.0-flash-lite',
        requests_per_minute=4000,
        requests_per_day=999999,
        tokens_per_minute=4000000,
        notes='Tier 1 pro account limits.'
    ),
    RateLimitConfig(
        'gemini',
        model='gemini-1.5-flash',
        requests_per_minute=2000,
        requests_per_day=999999,
        tokens_per_minute=4000000,
        notes='Tier 1 pro account limits.'
    ),
    RateLimitConfig(
        'gemini',
        model='gemini-1.5-pro',
        requests_per_minute=1000,
        requests_per_day=999999,
        tokens_per_minute=4000000,
        notes='Tier 1 pro account limits.'
    ),

    # Mistral AI
    RateLimitConfig(
        'mistral',
        requests_per_minute=50,
        requests_per_day=2000,
        notes='Limits vary by account tier.'
    ),
    RateLimitConfig(
        'mistral',
        model='mistral-tiny',
        requests_per_minute=100,
        requests_per_day=5000,
    ),
    RateLimitConfig(
        'mistral',
        model='mistral-large-latest',
        requests_per_minute=20,
        requests_per_day=1000,
    ),

    # Codestral
    RateLimitConfig(
        'codestral',
        requests_per_minute=50,
        requests_per_day=2000,
        notes='Same rate limit structure as Mistral AI.'
    ),
]

# Module-level tracking for dynamic rate limit state
# Key format: "provider:model" or "provider" for provider-level
_rate_limit_state: Dict[str, Dict] = {}


def get_provider_rate_limit(provider: str) -> Optional[RateLimitConfig]:
    """Get rate limit configuration for a provider"""
    for config in RATE_LIMIT_CONFIGS:
        if config.provider == provider and config.model is None:
            return config
    return None


def get_model_rate_limit(provider: str, model: str) -> Optional[RateLimitConfig]:
    """Get rate limit configuration for a specific model"""
    # First try to find model-specific config
    for config in RATE_LIMIT_CONFIGS:
        if config.provider == provider and config.model == model:
            return config

    # Fall back to provider default
    return get_provider_rate_limit(provider)


def get_provider_rate_limits(provider: str) -> List[RateLimitConfig]:
    """Get all rate limit configurations for a provider"""
    return [c for c in RATE_LIMIT_CONFIGS if c.provider == provider]


def update_rate_limit_from_headers(
    provider: str,
    model: Optional[str],
    headers: dict
) -> Optional[dict]:
    """Update rate limit configuration dynamically from API response headers"""
    updates = {}
    
    # Create key for tracking state
    state_key = f"{provider}:{model}" if model else provider
    
    # Initialize state if not exists
    if state_key not in _rate_limit_state:
        _rate_limit_state[state_key] = {}

    # Parse common rate limit headers
    if 'x-ratelimit-limit-requests' in headers:
        updates['requests_per_minute'] = int(headers['x-ratelimit-limit-requests'])

    if 'x-ratelimit-remaining-requests' in headers:
        # Store remaining for tracking
        remaining = int(headers['x-ratelimit-remaining-requests'])
        _rate_limit_state[state_key]['remaining_requests'] = remaining
        updates['remaining_requests'] = remaining

    if 'x-ratelimit-reset-requests' in headers:
        # Store reset time for tracking
        reset_timestamp = int(headers['x-ratelimit-reset-requests'])
        _rate_limit_state[state_key]['reset_timestamp'] = reset_timestamp
        _rate_limit_state[state_key]['reset_time'] = datetime.fromtimestamp(reset_timestamp)
        updates['reset_timestamp'] = reset_timestamp

    if 'retry-after' in headers:
        # Store retry-after for backoff calculation
        retry_after = int(headers['retry-after'])
        _rate_limit_state[state_key]['retry_after'] = retry_after
        _rate_limit_state[state_key]['retry_after_until'] = datetime.now().timestamp() + retry_after
        updates['retry_after'] = retry_after

    return updates if updates else None


def get_rate_limit_state(provider: str, model: Optional[str] = None) -> Optional[Dict]:
    """Get current rate limit state for a provider/model"""
    state_key = f"{provider}:{model}" if model else provider
    return _rate_limit_state.get(state_key)

