# Setup Guide - Lumni API Gateway

This guide will help you set up the unified API gateway for teaching AI engineering with student API packages.

## Prerequisites

### Python Version (Recommended)

- Python 3.11+
- pip
- API keys for at least one student provider (see below)
- Basic understanding of REST APIs

### TypeScript Version (Legacy)

- Node.js 18+ and npm
- API keys for at least one student provider (see below)
- Basic understanding of REST APIs

## Step 1: Installation

### Python Version

```bash
# Clone or navigate to the project directory
cd "lumni"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development (with tests)
pip install -r requirements-dev.txt

# Initialize database
python3 -m alembic upgrade head
```

### TypeScript Version

```bash
# Clone or navigate to the project directory
cd "lumni"

# Install dependencies
npm install

# Build the project
npm run build
```

## Step 2: Configuration

### 2.1 Create Configuration File

```bash
# Copy the example configuration
cp config.example.json config.json
```

### 2.2 Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env
```

### 2.3 Configure Your API Keys

Edit `.env` and add your API keys. You need at least one provider configured:

**Minimum Setup (Free Tier):**
- `GROQ_API_KEY` - Get free at https://console.groq.com
- `DEEPSEEK_API_KEY` - Get API key at https://platform.deepseek.com (pay-as-you-go pricing)
- `MISTRAL_API_KEY` - Get free at https://console.mistral.ai
- `OPENROUTER_API_KEY` - Get free at https://openrouter.ai

**Recommended Setup (Student Programs):**
- `GITHUB_TOKEN` - Free via GitHub Education Pack
- `GROQ_API_KEY` - Free tier (600 RPM)
- `DEEPSEEK_API_KEY` - Pay-as-you-go API (competitive pricing)
- `MISTRAL_API_KEY` - Free tier or student plan
- `CODESTRAL_API_KEY` - Optional, automatically falls back to `MISTRAL_API_KEY` if not set (uses same Mistral API endpoint)
- `OPENROUTER_API_KEY` - Free tier models available
- `TOGETHER_API_KEY` - Apply for research credits
- `FIREWORKS_API_KEY` - Apply for student program

**Note on Codestral API Key:**
Codestral uses the same API endpoint as Mistral (`https://api.mistral.ai/v1`), so you can use the same API key. If `CODESTRAL_API_KEY` is not set in your `.env` file, the system will automatically use `MISTRAL_API_KEY` as a fallback. This reduces configuration complexity - you only need to set `MISTRAL_API_KEY` to use both providers.

### 2.4 Configure Unified API Key

Edit `config.json` and set your unified API key:

```json
{
  "auth": {
    "unifiedApiKey": "your-secure-unified-key-here"
  }
}
```

Or set it in `.env`:
```
UNIFIED_API_KEY=your-secure-unified-key-here
```

### 2.5 Initialize Database (Python Only)

For Python version, initialize the database:

```bash
python3 -m alembic upgrade head
```

This creates the necessary database tables for usage tracking, VPN endpoints, and provider state.

### 2.6 Running Tests (Python)

For Python version, you can run tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_models/test_task_classifier.py

# Run tests in verbose mode
pytest -v
```

## Step 3: Configure Providers

Edit `config.json` to enable/disable providers and set priorities:

```json
{
  "providers": {
    "groq": {
      "enabled": true,
      "priority": 1,
      "rateLimit": {
        "requestsPerMinute": 600,
        "requestsPerDay": 10000
      }
    },
    "deepseek": {
      "enabled": true,
      "priority": 2,
      "rateLimit": {
        "requestsPerMinute": 30,
        "requestsPerDay": 1000
      }
    }
  }
}
```

**Priority System:**
- Lower number = higher priority
- Provider with priority 1 is tried first
- Falls back to priority 2, then 3, etc.

### Available Models by Provider

**Mistral AI:**
- `mistral-tiny` - Fast, cost-effective model (default, free tier)
- `mistral-small` - Balanced performance
- `mistral-medium` - High performance (requires paid tier)
- `mistral-large-latest` - Latest large model
- `mistral-7b-instruct` - 7B instruction-tuned model

**Codestral:**
- `codestral-latest` - Latest code model (default)
- `codestral-mamba-latest` - Mamba architecture variant

**OpenRouter:**
OpenRouter provides access to many models from different providers:
- `meta-llama/llama-3-8b-instruct` - Meta Llama 3 8B (default, free tier)
- `meta-llama/llama-3-70b-instruct` - Meta Llama 3 70B
- `openai/gpt-4` - OpenAI GPT-4
- `openai/gpt-4-turbo` - OpenAI GPT-4 Turbo
- `openai/gpt-3.5-turbo` - OpenAI GPT-3.5 Turbo
- `anthropic/claude-3-opus` - Anthropic Claude 3 Opus
- `anthropic/claude-3-sonnet` - Anthropic Claude 3 Sonnet
- `anthropic/claude-3-haiku` - Anthropic Claude 3 Haiku
- `google/gemini-pro` - Google Gemini Pro
- `mistralai/mistral-medium` - Mistral Medium

**Groq:**
- `llama-3-8b-8192` - Llama 3 8B (default, lower cost)
- `llama-3-70b-8192` - Llama 3 70B
- `mixtral-8x7b-32768` - Mixtral 8x7B

**DeepSeek:**
- `deepseek-chat` - Chat model (default)
- `deepseek-coder` - Code model

## Step 4: Start the Gateway

### Python Version

```bash
# Development mode (with auto-reload)
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload

# Production mode
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 3000

# Or use the main module directly
python3 -m app.main
```

The gateway will start on `http://localhost:3000` (or your configured port).

### TypeScript Version

```bash
# Development mode (with auto-reload)
npm run dev

# Production mode
npm start
```

The gateway will start on `http://localhost:3000` (or your configured port).

## Step 5: Test the Gateway

### Health Check
```bash
curl http://localhost:3000/health
```

### Make a Chat Request
```bash
curl -X POST http://localhost:3000/api/v1/chat \
  -H "Authorization: Bearer your-unified-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-tiny",
    "messages": [
      {"role": "user", "content": "Hello! How are you?"}
    ]
  }'
```

**Note:** Default models are set to free/low-cost tiers for testing. You can specify any model explicitly in the request.

### Check Provider Status
```bash
curl -H "Authorization: Bearer your-unified-api-key" \
  http://localhost:3000/api/v1/providers/status
```

### View Usage Statistics
```bash
curl -H "Authorization: Bearer your-unified-api-key" \
  http://localhost:3000/api/v1/usage
```

## Advanced Configuration

### VPN Rotation (Optional)

If you have VPN endpoints configured:

1. Add VPN endpoints to the database or configure in `config.json`
2. Enable VPN rotation:
```json
{
  "vpn": {
    "enabled": true,
    "rotationInterval": 3600000
  }
}
```

### Fallback Strategy

Choose from three strategies:

1. **priority** (default): Always try providers in priority order
2. **round-robin**: Rotate through providers evenly
3. **least-used**: Prefer providers with fewer requests

```json
{
  "fallback": {
    "strategy": "priority"
  }
}
```

### Monitoring Alerts

Configure alert thresholds:

```json
{
  "monitoring": {
    "alertThreshold": 0.8,
    "trackUsage": true
  }
}
```

When 80% of requests hit rate limits, you'll get alerts.

## Getting Student API Keys

### Free Tier Providers

1. **Groq**: https://console.groq.com - Free tier with 600 RPM
2. **DeepSeek**: https://platform.deepseek.com - Pay-as-you-go API (competitive pricing)
3. **Mistral AI**: https://console.mistral.ai - Free tier available
4. **Codestral**: Uses Mistral API - Automatically falls back to `MISTRAL_API_KEY` if `CODESTRAL_API_KEY` is not set
5. **OpenRouter**: https://openrouter.ai - Free tier models available
6. **HuggingFace**: https://huggingface.co - Free inference API

### Student Credit Programs

1. **GitHub Education Pack**: https://education.github.com
   - Free GitHub Copilot
   - $100 Azure credits
   - Other student benefits

2. **Together AI Research Credits**: https://together.ai
   - Apply for research credits ($200-600)
   - Mention you're doing research/education

3. **Fireworks AI Student Program**: https://fireworks.ai
   - Apply for student program
   - Get $500 in credits

4. **AWS Educate**: https://aws.amazon.com/education/awseducate
   - $25-300 in AWS credits
   - Access to Bedrock

5. **Google Cloud for Education**: https://cloud.google.com/edu
   - $300 in free credits
   - Access to Vertex AI

## Troubleshooting

### Gateway won't start
- Check that port 3000 is available
- Verify `config.json` exists and is valid JSON
- Check logs in `logs/combined.log`

### Providers failing
- Verify API keys are correct in `.env`
- Check provider status: `GET /api/v1/providers/status`
- Review rate limits in provider configuration

### Rate limit issues
- Enable more providers for better fallback
- Adjust rate limits in `config.json` to match actual limits
- Consider enabling VPN rotation

## Next Steps

- Integrate the gateway into your teaching materials
- Set up monitoring dashboards
- Configure VPN endpoints for extended usage
- Add custom providers as needed

## Support

For issues or questions, check the logs in `logs/` directory or review the main README.md.

