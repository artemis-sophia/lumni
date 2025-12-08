"""
FastAPI Application Entry Point
Main application with middleware setup and startup/shutdown handlers
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api.v1.routes import router
from app.config import load_config
from app.storage.database import init_db, engine
from app.utils.logger import Logger
from app.utils.exceptions import LumniError
from app.core.cache import Cache

logger = Logger("Main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Starting Lumni API Gateway...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handlers
@app.exception_handler(LumniError)
async def lumni_exception_handler(request: Request, exc: LumniError):
    """Handle custom exceptions"""
    return JSONResponse(
        status_code=400 if exc.code in ["VALIDATION_ERROR", "AUTHENTICATION_ERROR"] else 500,
        content={
            "error": exc.message,
            "code": exc.code,
            "details": exc.details
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

