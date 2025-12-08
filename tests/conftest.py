"""
Pytest configuration and fixtures for testing
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.storage.database import Base, get_db
from app.main import app
from app.config import GatewayConfig, load_config
from app.core.litellm_client import LiteLLMClient
from app.core.portkey_client import PortkeyClient
from app.models.benchmark_selector import BenchmarkSelector
from app.monitoring.tracker import UsageTracker


# Test database URL (in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# Create test session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a test database session"""
    # Import all models to ensure they're registered with Base
    from app.storage.models import (
        UsageMetrics, ModelRateLimits,
        ProviderState, TaskClassifications, ModelSelections
    )
    
    # Ensure all models are imported and registered
    # Drop all tables first to ensure clean state
    try:
        Base.metadata.drop_all(bind=test_engine)
    except Exception:
        pass  # Ignore if tables don't exist
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        # Drop tables after test
        try:
            Base.metadata.drop_all(bind=test_engine)
        except Exception:
            pass


@pytest.fixture(scope="function")
def override_get_db(db_session: Session):
    """Override get_db dependency with test database"""
    def _get_db():
        try:
            yield db_session
        finally:
            pass
    return _get_db


@pytest.fixture(scope="function")
def test_client(override_get_db):
    """Create a test client for FastAPI"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for FastAPI"""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_config() -> GatewayConfig:
    """Create a test configuration"""
    # Load config and override with test values
    try:
        config = load_config()
    except FileNotFoundError:
        # Create minimal test config if config.json doesn't exist
        from app.config import (
            ServerConfig, AuthConfig, ProviderConfig, ProviderRateLimit,
            FallbackConfig, MonitoringConfig, StorageConfig,
            LiteLLMConfig, PortkeyConfig, AcademicConfig, CacheConfig, GatewayConfig
        )
        
        config = GatewayConfig(
            server=ServerConfig(port=3000, host="0.0.0.0"),
            auth=AuthConfig(unifiedApiKey="test-api-key"),
            providers={
                "test-provider": ProviderConfig(
                    enabled=True,
                    apiKey="test-key",
                    priority=1,
                    rateLimit=ProviderRateLimit(requestsPerMinute=100, requestsPerDay=10000)
                )
            },
            fallback=FallbackConfig(),
            monitoring=MonitoringConfig(),
            storage=StorageConfig(type="sqlite", path=":memory:"),
            litellm=LiteLLMConfig(),
            portkey=PortkeyConfig(),
            academic=AcademicConfig(
                taskClassification={},
                benchmarkSelection={}
            ),
            cache=CacheConfig()
        )
    
    return config


@pytest.fixture(scope="function")
def mock_litellm_client(test_config):
    """Create a mock LiteLLM client"""
    client = LiteLLMClient(test_config.litellm.config_path)
    return client


@pytest.fixture(scope="function")
def mock_portkey_client(test_config):
    """Create a mock Portkey client"""
    client = PortkeyClient(
        api_key=test_config.portkey.api_key,
        environment=test_config.portkey.environment,
        virtual_key=test_config.portkey.virtual_key,
        config=test_config.portkey.config
    )
    return client


@pytest.fixture(scope="function")
def mock_benchmark_selector(mock_litellm_client):
    """Create a mock benchmark selector"""
    return BenchmarkSelector(mock_litellm_client)


@pytest.fixture(scope="function")
def mock_usage_tracker(test_config):
    """Create a mock usage tracker"""
    return UsageTracker(test_config.monitoring.alert_threshold)


@pytest.fixture(scope="function")
def api_key():
    """Test API key"""
    return "test-unified-api-key-12345"


@pytest.fixture(scope="function")
def auth_headers(api_key):
    """Authorization headers for API requests"""
    return {"Authorization": f"Bearer {api_key}"}


# Event loop fixture for async tests
@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

