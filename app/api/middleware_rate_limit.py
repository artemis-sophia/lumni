"""
Rate Limiting Middleware
Implements rate limiting for API endpoints using slowapi
"""

try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from fastapi import Request, HTTPException
    import os
    import hashlib

    # Initialize rate limiter
    # Use Redis if available, otherwise use in-memory storage
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            limiter = Limiter(
                key_func=get_remote_address,
                storage_uri=redis_url,
                default_limits=["1000/hour", "100/minute"]
            )
        except Exception:
            # Fallback to in-memory if Redis connection fails
            limiter = Limiter(
                key_func=get_remote_address,
                default_limits=["1000/hour", "100/minute"]
            )
    else:
        # In-memory rate limiting (per-process)
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=["1000/hour", "100/minute"]
        )


    def get_api_key_from_request(request: Request) -> str:
        """Extract API key from request for rate limiting"""
        # Try to get API key from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        # Fallback to IP address
        return get_remote_address(request)


    # Custom rate limit key function that uses API key if available
    def rate_limit_key_func(request: Request) -> str:
        """Rate limit key function - uses API key if available, otherwise IP
        
        Uses SHA-256 hash of API key to prevent exposure while allowing per-key rate limiting.
        """
        api_key = get_api_key_from_request(request)
        if api_key and api_key != get_remote_address(request):
            # Use SHA-256 hash of API key for rate limiting (allows per-key limits without exposure)
            api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]  # First 16 chars of hash
            return f"api_key:{api_key_hash}"
        return get_remote_address(request)


    # Update limiter to use custom key function
    limiter.key_func = rate_limit_key_func


    def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        """Custom handler for rate limit exceeded"""
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "code": "RATE_LIMIT_EXCEEDED",
                "retry_after": exc.retry_after
            }
        )
except ImportError:
    # slowapi not installed, create dummy limiter
    limiter = None
    
    def rate_limit_exceeded_handler(request, exc):
        pass
