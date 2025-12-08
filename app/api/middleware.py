"""
Authentication Middleware
Unified API key authentication as FastAPI dependency
"""

import secrets
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
# Import from config.py directly to avoid circular import
from app.config import GatewayConfig

security = HTTPBearer()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security),
    config: Optional[GatewayConfig] = None
) -> str:
    """Verify API key from Authorization header using constant-time comparison"""
    if not config:
        from app.config.manager import get_config_manager
        config = get_config_manager().load()

    token = credentials.credentials

    # Use constant-time comparison to prevent timing attacks
    expected_key = config.auth.unified_api_key
    if not secrets.compare_digest(token, expected_key):
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Invalid API key",
                "code": "AUTHENTICATION_ERROR"
            }
        )

    return token


# Rate limiting can be added later with slowapi if needed
# For now, we rely on provider-level rate limiting
