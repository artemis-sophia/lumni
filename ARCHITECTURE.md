# Architecture Overview

## System Components

### 1. API Gateway (`src/gateway/server.ts`)
The main Express server that handles incoming requests and routes them through the provider system.

**Responsibilities:**
- HTTP request handling
- Authentication via unified API key
- Request routing to fallback manager
- Usage tracking integration
- Health monitoring endpoints

### 2. Provider Abstraction (`src/providers/`)
Abstract base class and concrete implementations for each AI provider.

**Base Provider (`base.ts`):**
- Common interface for all providers
- Rate limit tracking
- Error handling
- Status management

**Provider Implementations:**
- `github-copilot.ts` - GitHub Copilot API
- `groq.ts` - Groq API
- `deepseek.ts` - DeepSeek API
- `together-ai.ts` - Together AI API
- `fireworks-ai.ts` - Fireworks AI API

### 3. Fallback Manager (`src/fallback/manager.ts`)
Intelligent provider switching system.

**Features:**
- Priority-based fallback
- Round-robin distribution
- Least-used provider selection
- Automatic retry with exponential backoff
- Health-aware routing

**Strategies:**
1. **Priority**: Always try providers in configured priority order
2. **Round-Robin**: Distribute requests evenly across providers
3. **Least-Used**: Prefer providers with fewer total requests

### 4. Health Checker (`src/fallback/health-checker.ts`)
Periodic health monitoring for all providers.

**Features:**
- Configurable check interval
- Automatic recovery detection
- Provider availability tracking

### 5. Usage Tracker (`app/monitoring/tracker.py`)
Real-time usage monitoring and alerting.

**Features:**
- Request counting
- Token usage tracking
- Error rate monitoring
- Rate limit hit detection
- Alert threshold configuration

### 6. Storage Layer (`app/storage/`)
Persistent state management using SQLite.

**Stored Data:**
- Usage metrics (historical)
- Provider state snapshots
- Task classifications
- Model selections

### 7. Authentication (`app/api/middleware.py`)
Unified API key authentication middleware.

**Features:**
- Bearer token validation
- Single key for all providers
- Request logging

## Request Flow

```
Client Request
    ↓
Express Server
    ↓
Auth Middleware (validate unified API key)
    ↓
Gateway Handler
    ↓
Fallback Manager
    ↓
Provider Selection (based on strategy)
    ↓
Provider.chat()
    ↓
Success? → Usage Tracker → Response
    ↓
Failure? → Next Provider (fallback)
    ↓
All Failed? → Error Response
```

## Fallback Flow

```
Primary Provider (Priority 1)
    ↓ (fails)
Secondary Provider (Priority 2)
    ↓ (fails)
Tertiary Provider (Priority 3)
    ↓ (fails)
...
    ↓
All Providers Exhausted → Error
```

## Rate Limit Handling

1. **Request arrives** → Check provider availability
2. **Provider selected** → Check rate limit status
3. **If limit available** → Process request
4. **If limit exceeded** → Mark provider unavailable, try next
5. **Periodic reset** → Cron job resets limits based on time windows


## Data Persistence

### SQLite Database Schema

**usage_metrics:**
- provider, timestamp, requests, tokens, errors, rate_limit_hits

**provider_state:**
- provider, healthy, available, error_count, success_count, last_used

## Configuration

Configuration is loaded from `config.json` with environment variable substitution.

**Key Sections:**
- `server`: Port and host configuration
- `auth`: Unified API key settings
- `providers`: Provider-specific configs with priorities
- `fallback`: Fallback strategy and retry settings
- `monitoring`: Usage tracking and alerting
- `storage`: Database configuration

## Error Handling

1. **Provider Errors**: Caught and logged, triggers fallback
2. **Rate Limit Errors**: Provider marked unavailable, immediate fallback
3. **Network Errors**: Retry with exponential backoff
4. **Configuration Errors**: Fail fast with clear error messages

## Monitoring & Observability

- **Logging**: Winston-based structured logging
- **Metrics**: Usage statistics via REST API
- **Health Checks**: Provider status endpoints
- **Alerts**: Configurable threshold-based alerts

## Extensibility

### Adding a New Provider

1. Create new provider class extending `BaseProvider`
2. Implement `chat()` and `getAvailableModels()` methods
3. Add to `createProvider()` factory function
4. Add configuration to `config.json`

### Custom Fallback Strategies

Extend `FallbackManager` and add new strategy logic in `getProviderOrder()`.

### Custom Storage Backends

Implement storage interface and swap in `GatewayServer` constructor.

