---
name: Python Migration Implementation
overview: Complete migration of Anna's Gift from TypeScript/Node.js to Python, leveraging LiteLLM and Portkey AI natively while preserving all unique features (VPN rotation, academic task classification, benchmark-based selection).
todos:
  - id: setup-project
    content: Create Python project structure with app/, tests/, alembic/ directories and configuration files (pyproject.toml, requirements.txt, Dockerfile)
    status: pending
  - id: config-management
    content: Implement app/config.py with Pydantic Settings for type-safe configuration loading with environment variable substitution
    status: pending
    dependencies:
      - setup-project
  - id: pydantic-schemas
    content: Create app/api/v1/schemas.py with Pydantic models for all request/response types (ChatRequest, ChatResponse, ProviderStatus, etc.)
    status: pending
    dependencies:
      - setup-project
  - id: database-setup
    content: Set up SQLAlchemy in app/storage/database.py, create ORM models in app/storage/models.py, and initialize Alembic for migrations
    status: pending
    dependencies:
      - config-management
  - id: litellm-integration
    content: Create app/core/litellm_client.py wrapping litellm.completion() with proxy support and error handling
    status: pending
    dependencies:
      - config-management
      - pydantic-schemas
  - id: portkey-integration
    content: Create app/core/portkey_client.py integrating Portkey SDK for observability and request tracking
    status: pending
    dependencies:
      - config-management
  - id: vpn-manager
    content: Create app/core/vpn_manager.py with rotation logic and proxy configuration integration for LiteLLM
    status: pending
    dependencies:
      - database-setup
  - id: task-classifier
    content: Migrate task classification logic to app/models/task_classifier.py with complexity analysis and factor calculation
    status: pending
    dependencies:
      - pydantic-schemas
  - id: benchmark-data
    content: Create app/models/benchmarks.py and app/models/categorization.py with benchmark scores and model categories
    status: pending
  - id: benchmark-selector
    content: Create app/models/benchmark_selector.py with optimization scoring algorithm integrating LiteLLM model selection
    status: pending
    dependencies:
      - task-classifier
      - benchmark-data
      - litellm-integration
  - id: pricing-rate-limits
    content: Create app/config/pricing.py and app/config/rate_limits.py with pricing data and rate limit configurations
    status: pending
    dependencies:
      - config-management
  - id: fastapi-app
    content: Create app/main.py with FastAPI application, middleware setup, and startup/shutdown event handlers
    status: pending
    dependencies:
      - config-management
      - database-setup
  - id: auth-middleware
    content: Create app/api/middleware.py with unified API key authentication as FastAPI dependency
    status: pending
    dependencies:
      - fastapi-app
      - config-management
  - id: api-routes
    content: Create app/api/v1/routes.py with all API endpoints (health, chat, providers, usage, models, vpn) integrating all components
    status: pending
    dependencies:
      - fastapi-app
      - auth-middleware
      - litellm-integration
      - portkey-integration
      - benchmark-selector
      - vpn-manager
  - id: usage-tracker
    content: Create app/monitoring/tracker.py with usage tracking logic and database persistence
    status: pending
    dependencies:
      - database-setup
  - id: storage-repositories
    content: Create app/storage/repositories.py with data access methods for all entities (usage metrics, VPN endpoints, etc.)
    status: pending
    dependencies:
      - database-setup
  - id: test-infrastructure
    content: Set up pytest in tests/conftest.py with fixtures for test database, mock clients, and FastAPI test client
    status: pending
    dependencies:
      - fastapi-app
      - database-setup
  - id: unit-tests
    content: Create unit tests for task classifier, benchmark selector, VPN manager, usage tracker, and config modules
    status: pending
    dependencies:
      - test-infrastructure
  - id: integration-tests
    content: Create integration tests for API endpoints, LiteLLM integration, Portkey integration, and end-to-end request flow
    status: pending
    dependencies:
      - test-infrastructure
      - api-routes
  - id: documentation
    content: Update README.md, create QUICKSTART.md and SETUP.md for Python, document API endpoints, and create migration guide
    status: pending
    dependencies:
      - api-routes
  - id: docker-deployment
    content: Finalize Dockerfile and create docker-compose.yml with app, PostgreSQL, and Redis services
    status: pending
    dependencies:
      - fastapi-app
      - database-setup
---

# Python Migration Implementation Plan

## Overview

Migrate the entire Anna's Gift codebase from TypeScript/Node.js to Python, using FastAPI, LiteLLM (native), Portkey AI, and modern Python tooling. The migration will preserve all unique features while improving maintainability and leveraging native AI/ML ecosystem.

## Technology Stack

- **FastAPI** - Modern async web framework (replaces Express)
- **LiteLLM** - Native Python provider abstraction
- **Portkey AI** - Python SDK for observability
- **SQLAlchemy** - ORM for database (PostgreSQL)
- **Pydantic** - Type validation and settings
- **Redis** - Caching (via redis-py)
- **Alembic** - Database migrations
- **pytest** - Testing framework
- **uvicorn** - ASGI server

## Project Structure

```
anna's-gift/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry
│   ├── config.py                  # Configuration management
│   ├── dependencies.py            # Dependency injection
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py          # API route handlers
│   │   │   └── schemas.py         # Pydantic request/response models
│   │   └── middleware.py          # Auth, logging middleware
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── litellm_client.py      # LiteLLM integration
│   │   ├── portkey_client.py      # Portkey integration
│   │   └── vpn_manager.py          # VPN rotation
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task_classifier.py     # Academic task classification
│   │   ├── benchmark_selector.py  # Benchmark-based selection
│   │   ├── categorization.py     # Model categorization
│   │   └── benchmarks.py          # Benchmark data
│   │
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── tracker.py             # Usage tracking
│   │   └── alerts.py              # Alert management
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py            # SQLAlchemy setup
│   │   ├── models.py              # Database models
│   │   └── repositories.py        # Data access layer
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── pricing.py             # Pricing configuration
│   │   └── rate_limits.py         # Rate limit configuration
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py              # Logging setup
│
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # pytest fixtures
│   ├── test_api/
│   ├── test_models/
│   ├── test_core/
│   └── test_integration/
│
├── litellm_config.yaml            # LiteLLM configuration
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Development dependencies
├── pyproject.toml                 # Project metadata
├── .env.example                   # Environment variables template
├── Dockerfile                     # Container configuration
├── docker-compose.yml             # Local development setup
└── README.md                      # Updated documentation
```

## Implementation Phases

### Phase 1: Project Foundation (Week 1)

#### 1.1 Setup Python Project Structure

- Create `app/` directory with package structure
- Set up `pyproject.toml` with project metadata
- Create `requirements.txt` with core dependencies
- Create `requirements-dev.txt` for development tools
- Set up `.env.example` with all environment variables
- Create `Dockerfile` and `docker-compose.yml`

**Files to create:**

- `pyproject.toml` - Project configuration
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies
- `.env.example` - Environment template
- `Dockerfile` - Container definition
- `docker-compose.yml` - Local development stack

#### 1.2 Configuration Management

- Create `app/config.py` using Pydantic Settings
- Migrate configuration schema from `config.example.json`
- Support environment variable substitution
- Load LiteLLM and Portkey configurations

**Key file:** `app/config.py`

- Use Pydantic BaseSettings for type-safe config
- Support JSON config file with env var substitution
- Include all sections: server, auth, litellm, portkey, academic, vpn, storage, cache

#### 1.3 Type Definitions (Pydantic Models)

- Create `app/api/v1/schemas.py` with request/response models
- Migrate TypeScript interfaces to Pydantic models:
  - `ChatRequest` → `ChatRequestSchema`
  - `ChatResponse` → `ChatResponseSchema`
  - `ProviderStatus` → `ProviderStatusSchema`
  - `ModelInfo` → `ModelInfoSchema`
  - `UsageMetrics` → `UsageMetricsSchema`

**Key file:** `app/api/v1/schemas.py`

- All request/response models as Pydantic schemas
- Validation rules matching TypeScript types
- Optional fields properly handled

### Phase 2: Core Infrastructure (Week 1-2)

#### 2.1 Database Setup

- Create `app/storage/database.py` with SQLAlchemy setup
- Define database models in `app/storage/models.py`:
  - `UsageMetrics` table
  - `VPNEndpoints` table
  - `TaskClassifications` table
  - `ModelSelections` table
- Set up Alembic for migrations
- Create initial migration

**Key files:**

- `app/storage/database.py` - SQLAlchemy engine, session management
- `app/storage/models.py` - SQLAlchemy ORM models
- `alembic/env.py` - Migration environment
- `alembic/versions/001_initial_schema.py` - Initial schema

#### 2.2 LiteLLM Integration

- Create `app/core/litellm_client.py`
- Initialize LiteLLM with `litellm_config.yaml`
- Implement chat completion wrapper
- Handle proxy configuration for VPN
- Integrate with model selection

**Key file:** `app/core/litellm_client.py`

- Class `LiteLLMClient` wrapping litellm.completion()
- Method `chat()` accepting request and returning response
- Proxy support via `extra_headers` or HTTP client configuration
- Error handling and transformation

#### 2.3 Portkey Integration

- Create `app/core/portkey_client.py`
- Initialize Portkey SDK
- Wrap LiteLLM calls with Portkey tracking
- Implement cost analytics retrieval
- Set up observability hooks

**Key file:** `app/core/portkey_client.py`

- Class `PortkeyClient` wrapping Portkey SDK
- Method `track_completion()` for request tracking
- Integration with LiteLLM client
- Cost and metrics retrieval methods

#### 2.4 VPN Manager

- Create `app/core/vpn_manager.py`
- Migrate VPN rotation logic from TypeScript
- Integrate with LiteLLM proxy configuration
- Implement endpoint testing and rotation
- Store endpoints in database

**Key file:** `app/core/vpn_manager.py`

- Class `VPNManager` with rotation logic
- Method `get_proxy_config()` returning proxy URL
- Integration with LiteLLM client for proxy injection
- Database persistence for endpoints

### Phase 3: Unique Features (Week 2)

#### 3.1 Academic Task Classifier

- Create `app/models/task_classifier.py`
- Migrate classification logic from `src/models/task-classifier.ts`
- Implement complexity analysis
- Implement factor calculation
- Return task type (fast/powerful) with confidence

**Key file:** `app/models/task_classifier.py`

- Function `classify_task(request: ChatRequest) -> TaskClassification`
- Functions: `analyze_complexity()`, `calculate_factors()`, `calculate_scores()`
- Match TypeScript logic exactly

#### 3.2 Benchmark Data and Categorization

- Create `app/models/benchmarks.py` with benchmark data
- Create `app/models/categorization.py` with model categories
- Migrate benchmark scores (MMLU, HellaSwag, GSM8K, HumanEval)
- Implement fallback ordering based on benchmarks

**Key files:**

- `app/models/benchmarks.py` - Benchmark data dictionaries
- `app/models/categorization.py` - Model category mappings
- Functions: `get_model_benchmarks()`, `get_category_fallback_order()`

#### 3.3 Benchmark-Based Model Selector

- Create `app/models/benchmark_selector.py`
- Migrate selection logic from `src/models/selector.ts`
- Implement optimization scoring algorithm
- Integrate with LiteLLM model list
- Consider rate limits, cost, benchmarks

**Key file:** `app/models/benchmark_selector.py`

- Class `BenchmarkSelector` with method `select_model()`
- Optimization scoring with weights (benchmark ranking 30%, score 20%, rate limits 20%, etc.)
- Integration with LiteLLM to get available models
- Fallback ordering based on benchmarks

#### 3.4 Pricing and Rate Limits

- Create `app/config/pricing.py` with pricing data
- Create `app/config/rate_limits.py` with rate limit configs
- Migrate pricing calculations
- Migrate rate limit tracking

**Key files:**

- `app/config/pricing.py` - Pricing data and `calculate_cost()` function
- `app/config/rate_limits.py` - Rate limit configs and accessors

### Phase 4: API Layer (Week 2-3)

#### 4.1 FastAPI Application Setup

- Create `app/main.py` with FastAPI app
- Set up middleware (CORS, logging, error handling)
- Configure dependency injection
- Set up startup/shutdown events

**Key file:** `app/main.py`

- FastAPI app instance
- Middleware setup
- Router registration
- Startup: database init, LiteLLM init, Portkey init
- Shutdown: cleanup

#### 4.2 Authentication Middleware

- Create `app/api/middleware.py`
- Implement unified API key authentication
- Create dependency for route protection
- Match TypeScript auth behavior

**Key file:** `app/api/middleware.py`

- Function `verify_api_key()` as FastAPI dependency
- Extract Bearer token from Authorization header
- Validate against config unified API key

#### 4.3 API Routes

- Create `app/api/v1/routes.py`
- Implement all endpoints:
  - `GET /health` - Health check
  - `POST /api/v1/chat` - Chat completion
  - `GET /api/v1/providers/status` - Provider statuses
  - `GET /api/v1/usage` - Usage statistics
  - `GET /api/v1/models` - List all models
  - `GET /api/v1/models/{provider}` - List provider models
  - `GET /api/v1/models/{provider}/{model}/status` - Model status
  - `GET /api/v1/vpn/status` - VPN status
  - `POST /api/v1/vpn/rotate` - Manual VPN rotation

**Key file:** `app/api/v1/routes.py`

- All route handlers as async functions
- Request validation via Pydantic schemas
- Response formatting
- Error handling

#### 4.4 Request Flow Integration

- Integrate task classifier into chat endpoint
- Integrate benchmark selector
- Integrate LiteLLM client
- Integrate Portkey tracking
- Integrate VPN proxy
- Track usage metrics

**Flow in `POST /api/v1/chat`:**

1. Authenticate request
2. Classify task (if auto mode)
3. Select model via benchmark selector
4. Get VPN proxy config (if enabled)
5. Execute via LiteLLM with Portkey tracking
6. Calculate cost
7. Track usage
8. Return enhanced response

### Phase 5: Monitoring and Storage (Week 3)

#### 5.1 Usage Tracker

- Create `app/monitoring/tracker.py`
- Migrate tracking logic from `src/monitoring/tracker.ts`
- Record requests, tokens, errors, rate limit hits
- Store in database via repositories
- Implement statistics retrieval

**Key file:** `app/monitoring/tracker.py`

- Class `UsageTracker` with methods:
  - `record_request()` - Store usage metrics
  - `get_stats()` - Retrieve statistics
  - `get_model_stats()` - Model-specific stats

#### 5.2 Storage Repositories

- Create `app/storage/repositories.py`
- Implement data access methods:
  - Usage metrics CRUD
  - VPN endpoints CRUD
  - Task classifications storage
  - Model selections storage

**Key file:** `app/storage/repositories.py`

- Repository classes for each entity
- SQLAlchemy query methods
- Transaction management

#### 5.3 Health Checking

- Implement provider health checks
- Periodic health monitoring
- Automatic recovery detection
- Status endpoint implementation

**Implementation:**

- Background task for health checks
- Store health status in memory/cache
- Expose via `/api/v1/providers/status`

### Phase 6: Testing (Week 3-4)

#### 6.1 Test Infrastructure

- Set up `pytest` configuration
- Create `tests/conftest.py` with fixtures:
  - Test database setup
  - Mock LiteLLM client
  - Mock Portkey client
  - Test FastAPI client

#### 6.2 Unit Tests

- Test task classifier
- Test benchmark selector
- Test VPN manager
- Test usage tracker
- Test pricing/rate limit configs

#### 6.3 Integration Tests

- Test API endpoints
- Test LiteLLM integration
- Test Portkey integration
- Test end-to-end request flow

#### 6.4 Test Coverage

- Aim for 80%+ coverage
- Cover all critical paths
- Test error scenarios

### Phase 7: Documentation and Deployment (Week 4)

#### 7.1 Update Documentation

- Update `README.md` for Python setup
- Create `QUICKSTART.md` for Python
- Update `SETUP.md` with Python instructions
- Document API endpoints
- Create migration guide from TypeScript

#### 7.2 Docker and Deployment

- Finalize `Dockerfile`
- Create `docker-compose.yml` with:
  - Python app
  - PostgreSQL
  - Redis
- Create deployment documentation
- Set up environment variable documentation

## Key Implementation Details

### Configuration Loading

- Use Pydantic Settings for type-safe config
- Support JSON config file with env var substitution (like TypeScript version)
- Load `litellm_config.yaml` for LiteLLM
- Environment variables via `.env` file

### Database Models

```python
# app/storage/models.py structure:
- UsageMetrics: provider, model, timestamp, requests, tokens, errors, rate_limit_hits, cost
- VPNEndpoints: id, host, port, country, provider, active, last_used
- TaskClassifications: request_id, task_type, confidence, factors (JSON), timestamp
- ModelSelections: request_id, task_type, selected_provider, selected_model, reason, benchmark_score, timestamp
```

### LiteLLM Integration Pattern

```python
# app/core/litellm_client.py pattern:
from litellm import completion

class LiteLLMClient:
    async def chat(self, request: ChatRequest, proxy: Optional[str] = None):
        # Configure proxy if provided
        # Call litellm.completion()
        # Transform response
        # Return ChatResponse
```

### Portkey Integration Pattern

```python
# app/core/portkey_client.py pattern:
from portkey import Portkey

class PortkeyClient:
    async def track_completion(self, request, completion_fn):
        # Start tracking
        # Execute completion
        # Record metrics
        # Return response with trace_id
```

### Request Flow

1. FastAPI receives request
2. Auth middleware validates API key
3. Task classifier analyzes request (if auto)
4. Benchmark selector chooses model
5. VPN manager provides proxy (if enabled)
6. Portkey wraps LiteLLM call
7. LiteLLM executes with proxy
8. Usage tracker records metrics
9. Response enhanced with cost, classification, etc.
10. Return to client

## Dependencies

### Core Dependencies (requirements.txt)

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
litellm>=1.50.0
portkey-ai>=1.0.0
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.0
redis>=5.0.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
httpx>=0.25.0
pyyaml>=6.0.0
```

### Development Dependencies (requirements-dev.txt)

```
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
httpx>=0.25.0  # For test client
black>=23.11.0
ruff>=0.1.6
mypy>=1.7.0
```

## Migration Checklist

- [ ] Phase 1: Project foundation (structure, config, types)
- [ ] Phase 2: Core infrastructure (database, LiteLLM, Portkey, VPN)
- [ ] Phase 3: Unique features (classifier, benchmarks, selector)
- [ ] Phase 4: API layer (FastAPI, routes, integration)
- [ ] Phase 5: Monitoring and storage (tracker, repositories)
- [ ] Phase 6: Testing (unit, integration, coverage)
- [ ] Phase 7: Documentation and deployment

## Success Criteria

1. All TypeScript features replicated in Python
2. API endpoints match (with improvements allowed)
3. LiteLLM integration working natively
4. Portkey observability functional
5. VPN rotation working
6. Academic features preserved
7. 80%+ test coverage
8. Documentation complete
9. Docker deployment working
10. Performance equal or better than TypeScript version

## Timeline

- **Week 1:** Phases 1-2 (Foundation + Core Infrastructure)
- **Week 2:** Phases 3-4 (Unique Features + API Layer)
- **Week 3:** Phases 5-6 (Monitoring + Testing)
- **Week 4:** Phase 7 (Documentation + Deployment)

**Total Estimated Time:** 4 weeks