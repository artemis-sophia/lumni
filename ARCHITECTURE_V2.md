# Architecture V2: LiteLLM + Portkey AI Integration

## Executive Summary

This architecture redesign leverages **LiteLLM** for provider abstraction and routing, and **Portkey AI** for observability and monitoring, while preserving Lumni's unique features: academic task classification and student optimization.

## Technology Stack

### Core Infrastructure
- **LiteLLM** - Unified LLM API gateway (provider abstraction, fallback, rate limiting)
- **Portkey AI** - Observability, monitoring, prompt management, A/B testing
- **FastAPI** - API server layer
- **Python** - Type safety with Pydantic

### Unique Features Layer
- **Academic Task Classifier** - Research-backed task categorization (custom)
- **Benchmark-Based Selector** - Model selection using MMLU, HellaSwag, etc. (custom)
- **Student Optimizer** - Free tier optimization (custom)

### Supporting Infrastructure
- **PostgreSQL** - Primary database (replaces SQLite for production)
- **Redis** - Caching and rate limit tracking
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization (optional)
- **Docker** - Containerization
- **Kubernetes** - Orchestration (optional, for scale)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Client Applications                       │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Express API Gateway Layer                    │
│  - Authentication (Unified API Key)                      │
│  - Request Validation                                    │
│  - Response Formatting                                   │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Lumni Intelligence Layer                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Academic Task Classifier                         │   │
│  │  - Fast vs Powerful Detection                   │   │
│  │  - Complexity Analysis                           │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Benchmark-Based Model Selector                 │   │
│  │  - MMLU/HellaSwag/GSM8K Scoring                 │   │
│  │  - Cost-Aware Optimization                      │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    LiteLLM Core                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Provider Abstraction                           │   │
│  │  - 100+ Provider Support                        │   │
│  │  - Unified API Interface                       │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Fallback Manager                                │   │
│  │  - Automatic Retry                               │   │
│  │  - Exponential Backoff                           │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Rate Limit Management                          │   │
│  │  - Per-Provider Tracking                        │   │
│  │  - Automatic Throttling                          │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Caching Layer                                  │   │
│  │  - Response Caching                             │   │
│  │  - Cost Optimization                            │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Portkey AI Observability                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Request Tracking                               │   │
│  │  - Latency Monitoring                           │   │
│  │  - Error Tracking                               │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Cost Analytics                                 │   │
│  │  - Per-Model Costs                              │   │
│  │  - Usage Trends                                 │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Prompt Management                              │   │
│  │  - Versioning                                   │   │
│  │  - A/B Testing                                  │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Dashboard & Alerts                             │   │
│  │  - Real-time Metrics                            │   │
│  │  - Threshold Alerts                             │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              AI Provider APIs                            │
│  - OpenAI, Anthropic, Groq, DeepSeek, etc.              │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### 1. FastAPI Gateway Layer

**Purpose:** Entry point, authentication, request/response handling

**Responsibilities:**
- Unified API key authentication
- Request validation and sanitization
- Response formatting
- Error handling
- Request logging

**Key Files:**
- `app/main.py` - FastAPI application
- `app/api/v1/routes.py` - API routes
- `app/api/middleware.py` - Authentication middleware

**Changes:**
- Simplified - delegates to LiteLLM for provider logic
- Focuses on API contract and authentication

---

### 2. Lumni Intelligence Layer

**Purpose:** Unique features that differentiate Lumni

#### 2.1 Academic Task Classifier

**Purpose:** Automatically classify tasks as "fast" or "powerful" based on research

**Integration:**
- Runs BEFORE LiteLLM routing
- Injects `model` parameter into LiteLLM request
- Uses LiteLLM's model selection as fallback

**Key Files:**
- `app/models/task_classifier.py` - Classification logic
- `app/models/benchmark_selector.py` - Model selection with benchmarks

**Flow:**
```
Request → Task Classifier → Category (fast/powerful) → Model Selector → LiteLLM
```

#### 2.2 Benchmark-Based Model Selector

**Purpose:** Select optimal model using benchmark scores

**Integration:**
- Wraps LiteLLM's model selection
- Uses benchmark data (MMLU, HellaSwag, etc.)
- Considers cost, rate limits, availability

**Key Files:**
- `app/models/benchmark_selector.py` - Selection logic
- `app/models/benchmarks.py` - Benchmark data
- `app/models/categorization.py` - Model categories

**Flow:**
```
Task Category → Benchmark Lookup → Model Ranking → LiteLLM Request
```

---

### 3. LiteLLM Core

**Purpose:** Provider abstraction, routing, fallback, rate limiting

**Responsibilities:**
- Unified API for 100+ providers
- Automatic fallback and retry
- Rate limit management
- Response caching
- Cost tracking

**Configuration:**
- `litellm_config.yaml` - Provider configurations
- Environment variables for API keys

**Key Features Used:**
- `litellm.completion()` - Main API call
- `litellm.router` - Intelligent routing
- `litellm.cache` - Response caching
- `litellm.fallbacks` - Automatic fallback

**Integration Points:**
- Model selection from Lumni layer
- Portkey observability hooks

---

### 4. Portkey AI Observability

**Purpose:** Monitoring, analytics, prompt management

**Responsibilities:**
- Request/response tracking
- Latency monitoring
- Error tracking
- Cost analytics
- Prompt versioning
- A/B testing

**Integration:**
- Portkey SDK wraps LiteLLM calls
- Automatic instrumentation
- Dashboard for visualization

**Key Features Used:**
- Request tracking
- Cost analytics
- Prompt management
- A/B testing framework

---

## Request Flow (Detailed)

```
1. Client Request
   ↓
2. Express Gateway
   - Authenticate (unified API key)
   - Validate request
   ↓
3. Academic Task Classifier
   - Analyze request content
   - Classify as "fast" or "powerful"
   - Calculate confidence score
   ↓
4. Benchmark-Based Model Selector
   - Get task category
   - Lookup benchmark scores
   - Rank models by optimization score
   - Select best model
   ↓
5. Portkey SDK (instrumentation)
   - Start request tracking
   - Log metadata
   ↓
7. LiteLLM Router
   - Route to selected model/provider
   - Apply rate limiting
   - Check cache
   - Execute request
   ↓
6. Provider API
   - Execute LLM request
   ↓
7. LiteLLM Response Processing
   - Parse response
   - Update rate limits
   - Cache if applicable
   ↓
10. Portkey SDK (completion)
    - Track latency
    - Record costs
    - Update analytics
    ↓
11. Lumni Enhancement
    - Add cost breakdown
    - Add classification metadata
    - Add benchmark info
    ↓
12. Express Response
    - Format response
    - Return to client
```

## Data Flow

### Request Metadata
```typescript
{
  // Original request
  messages: Message[],
  model?: string,
  provider?: string,
  
  // Lumni enhancements
  taskType?: 'fast' | 'powerful' | 'auto',
  classification?: {
    taskType: 'fast' | 'powerful',
    confidence: number,
    factors: {...}
  },
  
  // Model selection
  selectedModel?: {
    provider: string,
    model: string,
    reason: string,
    benchmarkScore?: number
  },
  
  // Portkey
  portkeyTraceId?: string
}
```

### Response Metadata
```typescript
{
  // LiteLLM response
  id: string,
  choices: Choice[],
  usage: Usage,
  model: string,
  
  // Lumni enhancements
  cost: {
    input: number,
    output: number,
    total: number,
    currency: 'USD'
  },
  classification: {
    taskType: 'fast' | 'powerful',
    confidence: number
  },
  benchmark: {
    model: string,
    mmlu?: number,
    hellaswag?: number,
    gsm8k?: number
  },
  
  // Portkey
  portkeyTraceId: string,
  latency: number
}
```

## Configuration Structure

### LiteLLM Configuration (`litellm_config.yaml`)
```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
  
  - model_name: groq-llama-3-70b
    litellm_params:
      model: groq/llama-3-70b-8192
      api_key: os.environ/GROQ_API_KEY
  
  - model_name: deepseek-chat
    litellm_params:
      model: deepseek/deepseek-chat
      api_key: os.environ/DEEPSEEK_API_KEY

router_settings:
  num_retries: 3
  timeout: 60
  fallbacks:
    - gpt-4o
    - groq-llama-3-70b
    - deepseek-chat

litellm_settings:
  success_callback: ["portkey"]
  failure_callback: ["portkey"]
  cache: true
```

### Portkey Configuration
```typescript
{
  apiKey: process.env.PORTKEY_API_KEY,
  environment: process.env.NODE_ENV || 'development',
  virtualKey: process.env.PORTKEY_VIRTUAL_KEY, // Optional
  config: {
    cache: {
      mode: 'semantic',
      ttl: 3600
    },
    retry: {
      attempts: 3,
      onStatusCodes: [429, 500, 502, 503]
    }
  }
}
```

### Lumni Configuration (`config.json`)
```json
{
  "server": {
    "port": 3000,
    "host": "0.0.0.0"
  },
  "auth": {
    "unifiedApiKey": "${UNIFIED_API_KEY}"
  },
  "litellm": {
    "configPath": "./litellm_config.yaml",
    "proxy": {
      "enabled": true,
      "rotationInterval": 3600000
    }
  },
  "portkey": {
    "enabled": true,
    "apiKey": "${PORTKEY_API_KEY}",
    "environment": "development"
  },
  "academic": {
    "taskClassification": {
      "enabled": true,
      "autoDetect": true
    },
    "benchmarkSelection": {
      "enabled": true,
      "weights": {
        "benchmarkRanking": 0.3,
        "benchmarkScore": 0.2,
        "rateLimitAvailability": 0.2,
        "providerPriority": 0.1,
        "recentUsage": 0.1,
        "costEfficiency": 0.1
      }
    }
  },
  "storage": {
    "type": "postgresql",
    "connectionString": "${DATABASE_URL}"
  },
  "cache": {
    "type": "redis",
    "connectionString": "${REDIS_URL}",
    "ttl": 3600
  }
}
```

## Database Schema

### PostgreSQL Tables

#### `usage_metrics`
```sql
CREATE TABLE usage_metrics (
  id SERIAL PRIMARY KEY,
  provider VARCHAR(50) NOT NULL,
  model VARCHAR(100) NOT NULL,
  timestamp TIMESTAMP DEFAULT NOW(),
  requests INTEGER DEFAULT 0,
  tokens INTEGER DEFAULT 0,
  errors INTEGER DEFAULT 0,
  rate_limit_hits INTEGER DEFAULT 0,
  cost_usd DECIMAL(10, 6) DEFAULT 0,
  latency_ms INTEGER,
  INDEX idx_provider_model (provider, model),
  INDEX idx_timestamp (timestamp)
);
```

#### `task_classifications`
```sql
CREATE TABLE task_classifications (
  id SERIAL PRIMARY KEY,
  request_id VARCHAR(255) UNIQUE,
  task_type VARCHAR(20) NOT NULL,
  confidence DECIMAL(3, 2),
  factors JSONB,
  timestamp TIMESTAMP DEFAULT NOW(),
  INDEX idx_task_type (task_type),
  INDEX idx_timestamp (timestamp)
);
```

#### `model_selections`
```sql
CREATE TABLE model_selections (
  id SERIAL PRIMARY KEY,
  request_id VARCHAR(255),
  task_type VARCHAR(20),
  selected_provider VARCHAR(50),
  selected_model VARCHAR(100),
  reason TEXT,
  benchmark_score DECIMAL(5, 2),
  timestamp TIMESTAMP DEFAULT NOW(),
  INDEX idx_request_id (request_id),
  INDEX idx_timestamp (timestamp)
);
```

## Implementation Plan

### Phase 1: Core Integration (Week 1-2)

1. **Install Dependencies**
   ```bash
   npm install litellm @portkey-ai/portkey-js
   npm install pg redis ioredis
   npm install @types/pg
   ```

2. **Replace Provider Layer with LiteLLM**
   - Remove custom provider implementations
   - Integrate LiteLLM router
   - Configure providers via `litellm_config.yaml`

3. **Integrate Portkey SDK**
   - Wrap LiteLLM calls with Portkey
   - Configure observability
   - Set up dashboard access

4. **Update Gateway Server**
   - Simplify to use LiteLLM directly
   - Keep authentication and API contract
   - Remove custom fallback logic (use LiteLLM's)

### Phase 2: Unique Features Integration (Week 2-3)

1. **Academic Task Classifier Integration**
   - Run before LiteLLM routing
   - Inject model selection into LiteLLM request
   - Store classifications in database

2. **Benchmark-Based Selector Integration**
   - Wrap LiteLLM model selection
   - Use benchmark data for ranking
   - Integrate with LiteLLM router

### Phase 3: Infrastructure Upgrade (Week 3-4)

1. **Database Migration**
   - Migrate from SQLite to PostgreSQL
   - Update schema
   - Migrate existing data

2. **Redis Integration**
   - Set up Redis for caching
   - Integrate with LiteLLM cache
   - Rate limit tracking

3. **Monitoring Setup**
   - Configure Portkey dashboard
   - Set up Prometheus (optional)
   - Configure alerts

### Phase 4: Testing & Optimization (Week 4-5)

1. **Integration Testing**
   - Test LiteLLM integration
   - Test Portkey observability
   - Test unique features

2. **Performance Testing**
   - Load testing
   - Latency optimization
   - Cost optimization

3. **Documentation**
   - Update architecture docs
   - Update setup guides
   - Create migration guide

## Migration Strategy

### Step 1: Parallel Running
- Run old and new systems in parallel
- Route traffic gradually
- Compare results

### Step 2: Feature Parity
- Ensure all features work in new system
- Test edge cases
- Validate cost tracking

### Step 3: Cutover
- Switch all traffic to new system
- Monitor closely
- Keep old system as backup

## Benefits of New Architecture

### 1. Reduced Maintenance
- **Before:** Maintain 5+ custom provider implementations
- **After:** LiteLLM handles 100+ providers automatically

### 2. Better Observability
- **Before:** Custom logging and metrics
- **After:** Portkey provides enterprise-grade observability

### 3. Production Ready
- **Before:** Custom fallback, rate limiting
- **After:** Battle-tested LiteLLM infrastructure

### 4. Unique Features Preserved
- Academic classification (still unique)
- Benchmark-based selection (still unique)

### 5. Scalability
- **Before:** SQLite, limited scalability
- **After:** PostgreSQL + Redis, horizontal scaling

## Risks & Mitigations

### Risk 1: LiteLLM Learning Curve
**Mitigation:** Start with simple integration, gradually add features

### Risk 2: Portkey Cost
**Mitigation:** Use free tier initially, monitor usage

### Risk 3: Data Migration
**Mitigation:** Run parallel systems, migrate gradually

## Next Steps

1. Review and approve architecture
2. Set up development environment
3. Begin Phase 1 implementation
4. Create detailed implementation tickets

---

**Last Updated:** 2024-12-07  
**Status:** Architecture Design Complete - Ready for Implementation


