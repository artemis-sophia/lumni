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
from app.config.manager import get_config_manager
from app.storage.database import init_db, engine, check_database_connection
from app.utils.logger import Logger
from app.utils.exceptions import LumniError, ConfigurationError
from app.core.cache import Cache

logger = Logger("Main")

# Initialize OpenTelemetry
try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    
    # Initialize tracing
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    
    # Add console exporter for development (can be replaced with OTLP exporter for production)
    span_processor = BatchSpanProcessor(ConsoleSpanExporter())
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    FastAPIInstrumentor = FastAPIInstrumentor
    logger.info("OpenTelemetry instrumentation available")
except ImportError:
    logger.warn("OpenTelemetry not available - install opentelemetry packages")
    FastAPIInstrumentor = None
    trace = None
    tracer = None
    generate_latest = None
    CONTENT_TYPE_LATEST = None


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
    
    # Initialize OpenTelemetry instrumentation
    if FastAPIInstrumentor:
        try:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("OpenTelemetry FastAPI instrumentation initialized")
        except Exception as e:
            logger.warn(f"Failed to initialize OpenTelemetry: {e}")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Verify database connection
    db_healthy, db_error = check_database_connection()
    if not db_healthy:
        logger.warn(f"Database connection check failed: {db_error}, but continuing startup")
    else:
        logger.info("Database connection verified")
    
    # Load configuration
    config = get_config_manager().load()
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


# Create FastAPI app with request size limits
# Limit request body to 10MB to prevent DoS attacks
app = FastAPI(
    title="Lumni API Gateway",
    description="Unified Student API Gateway with smart fallback and limit monitoring",
    version="2.0.0",
    lifespan=lifespan,
    # Request body size limit: 10MB
    # This is enforced at the ASGI level
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

# Request Body Size Limit Middleware
MAX_REQUEST_BODY_SIZE = 10 * 1024 * 1024  # 10MB

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request body size"""
    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > MAX_REQUEST_BODY_SIZE:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": f"Request body too large. Maximum size is {MAX_REQUEST_BODY_SIZE / 1024 / 1024}MB",
                            "code": "PAYLOAD_TOO_LARGE",
                            "max_size_mb": MAX_REQUEST_BODY_SIZE / 1024 / 1024
                        }
                    )
            except ValueError:
                pass  # Invalid content-length, let it through to be handled by FastAPI
        
        response = await call_next(request)
        return response


# Request ID Middleware with OpenTelemetry trace correlation
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID and trace correlation to all requests"""
    async def dispatch(self, request: Request, call_next):
        # Generate or get request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        # Add trace context if available
        if trace:
            span = trace.get_current_span()
            if span:
                span.set_attribute("http.request_id", request_id)
                # Set trace ID in response headers
                trace_id = format(span.get_span_context().trace_id, '032x')
                request.state.trace_id = trace_id
        
        # Set request ID in context variable for logger
        from app.utils.logger import _request_id_context
        _request_id_context.set(request_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        if trace and hasattr(request.state, 'trace_id'):
            response.headers["X-Trace-ID"] = request.state.trace_id
        
        # Clear request ID from context after request
        _request_id_context.set(None)
        return response


app.add_middleware(RequestSizeLimitMiddleware)
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

# Add Prometheus metrics endpoint
if generate_latest:
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint"""
        from starlette.responses import Response
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    logger.info("Prometheus metrics endpoint available at /metrics")


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
    from app.config.manager import get_config_manager
    config = get_config_manager().load()
    uvicorn.run(
        "app.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=True
    )

