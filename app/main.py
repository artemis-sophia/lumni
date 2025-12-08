"""
FastAPI Application Entry Point
Main application with middleware setup and startup/shutdown handlers
"""

import os
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.v1.routes import router
from app.config import load_config
from app.storage.database import init_db, engine, check_database_connection
from app.utils.logger import Logger
from app.utils.exceptions import LumniError, ConfigurationError
from app.core.cache import Cache

logger = Logger("Main")


def validate_environment():
    """Validate required environment variables at startup"""
    missing_vars = []
    
    # Check if we're in production
    is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    if is_production:
        # In production, unified API key must be set
        if not os.getenv("UNIFIED_API_KEY") and not os.path.exists("config.json"):
            missing_vars.append("UNIFIED_API_KEY or config.json")
    
    if missing_vars:
        raise ConfigurationError(
            f"Missing required environment variables: {', '.join(missing_vars)}",
            {"missing_vars": missing_vars, "environment": "production" if is_production else "development"}
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Starting Lumni API Gateway...")
    
    # Validate environment variables
    try:
        validate_environment()
        logger.info("Environment validation passed")
    except ConfigurationError as e:
        logger.error(f"Environment validation failed: {e.message}")
        raise
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Verify database connection
    if not check_database_connection():
        logger.warn("Database connection check failed, but continuing startup")
    else:
        logger.info("Database connection verified")
    
    # Load configuration
    config = load_config()
    logger.info("Configuration loaded")
    
    # Initialize Redis cache if configured
    if config.cache.type == "redis" and config.cache.connection_string:
        cache = Cache(config.cache.connection_string)
        await cache.connect()
        app.state.cache = cache
        logger.info("Redis cache initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down gracefully...")
    
    # Cleanup cache
    if hasattr(app.state, 'cache'):
        await app.state.cache.disconnect()
        logger.info("Redis cache disconnected")


# Create FastAPI app
app = FastAPI(
    title="Lumni API Gateway",
    description="Unified Student API Gateway with smart fallback and limit monitoring",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware - configurable via environment variable
# In production, set CORS_ORIGINS to specific origins (comma-separated)
# Example: CORS_ORIGINS=https://example.com,https://app.example.com
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env:
    # Parse comma-separated origins
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
else:
    # Default to empty list in production (no CORS allowed)
    # For development, can be overridden with CORS_ORIGINS=*
    cors_origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request ID Middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests"""
    async def dispatch(self, request: Request, call_next):
        # Generate or get request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        # Add request ID to logger context
        # Note: This is a simple implementation. For production, consider using contextvars
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


app.add_middleware(RequestIDMiddleware)

# Rate Limiting Middleware
try:
    from app.api.middleware_rate_limit import limiter, rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    
    if limiter:
        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)
        app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
        logger.info("Rate limiting enabled")
    else:
        logger.warn("Rate limiting limiter not initialized - slowapi may not be installed")
except (ImportError, AttributeError) as e:
    logger.warn(f"Rate limiting not available: {e}")

# Error handlers
@app.exception_handler(LumniError)
async def lumni_exception_handler(request: Request, exc: LumniError):
    """Handle custom exceptions"""
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=400 if exc.code in ["VALIDATION_ERROR", "AUTHENTICATION_ERROR"] else 500,
        content={
            "error": exc.message,
            "code": exc.code,
            "details": exc.details,
            "request_id": request_id
        }
    )

# Include routers
app.include_router(router, prefix="/api/v1", tags=["v1"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Lumni API Gateway",
        "version": "2.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    config = load_config()
    uvicorn.run(
        "app.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=True
    )

