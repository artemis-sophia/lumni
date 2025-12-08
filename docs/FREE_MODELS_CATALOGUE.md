# Free Models Catalogue

**Complete catalogue of all models that can be used WITHOUT EXPENDING CREDITS (Rate-Limited Free Models)**

This document lists all models available through Lumni that require **zero credits** to use, including all rate-limited free tiers. Models are organized by provider with access requirements and rate limits.

**Key**: All models listed here are **rate-limited** but **do not expend credits** - they are completely free to use within their rate limits.

---

## Table of Contents

1. [Google Gemini](#google-gemini)
2. [GitHub Models API](#github-models-api)
3. [Groq](#groq)
4. [DeepSeek (Rate-Limited Free Tier)](#deepseek-rate-limited-free-tier)
5. [OpenRouter (Requires Credits)](#openrouter-requires-credits)
6. [Summary](#summary)

---

## Google Gemini

**Provider**: Google AI (Gemini)  
**Access**: Free tier with API key  
**Credits Required**: ❌ **NO** - Completely free  
**Rate Limits**: Varies by model (typically 15-60 requests per minute)

### Available Free Models

| Model | Category | Speed | Notes |
|-------|----------|-------|-------|
| `gemini-1.5-flash` | Fast | Very Fast | Production-ready, optimized for speed |
| `gemini-1.5-pro` | Powerful | Moderate | High capability, best for complex tasks |
| `gemini-1.5-pro-latest` | Powerful | Moderate | Latest version of Pro model |
| `gemini-2.0-flash-exp` | Fast | Very Fast | Experimental, cutting-edge features |

### Access Requirements

- **API Key**: Required (get from [Google AI Studio](https://makersuite.google.com/app/apikey))
- **Account**: Free Google account
- **Cost**: $0.00 - No credits needed
- **Rate Limits**: 
  - Free tier: 15 requests per minute (RPM)
  - Some models may have daily limits

### Usage Example

```bash
curl -X POST http://localhost:3000/api/v1/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "gemini",
    "model": "gemini-1.5-flash",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## GitHub Models API

**Provider**: GitHub Models API (models.github.ai)  
**Access**: GitHub Pro account or GitHub Education Pack  
**Credits Required**: ❌ **NO** - Free with Pro account  
**Rate Limits**: 60 requests per minute, 5,000 requests per day

### Available Free Models

| Model | Category | Capability | Notes |
|-------|----------|------------|-------|
| `openai/gpt-4o` | Powerful | Highest | Latest GPT-4 model, best overall |
| `openai/gpt-4-turbo` | Powerful | Very High | High performance, fast responses |
| `openai/gpt-3.5-turbo` | Fast | High | Cost-effective, fast responses |
| `anthropic/claude-3-opus` | Powerful | Highest | Highest capability Claude model |
| `anthropic/claude-3-sonnet` | Powerful | Very High | Balanced performance |
| `anthropic/claude-3-haiku` | Fast | High | Fast and efficient |

### Access Requirements

- **GitHub Account**: Pro account or GitHub Education Pack required
- **API Token**: GitHub Personal Access Token with `models: read` permission
- **Cost**: $0.00 - No credits needed (included with Pro subscription)
- **Rate Limits**: 
  - 60 requests per minute
  - 5,000 requests per day
- **Setup**: 
  1. Get GitHub Pro (paid) or apply for GitHub Education Pack (free for students)
  2. Create Personal Access Token at https://github.com/settings/tokens
  3. Grant `models: read` permission

### Usage Example

```bash
curl -X POST http://localhost:3000/api/v1/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "github-copilot",
    "model": "openai/gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## Groq

**Provider**: Groq  
**Access**: Free tier with API key  
**Credits Required**: ❌ **NO** - Completely free  
**Rate Limits**: 600 requests per minute, 10,000 requests per day

### Available Free Models

| Model | Category | Speed | Notes |
|-------|----------|-------|-------|
| `llama-3.1-8b-instant` | Fast | Very Fast | Small, fast model for quick responses |
| `mixtral-8x7b-32768` | Fast | Very Fast | Mixture of experts, fast inference |
| `gemma-7b-it` | Fast | Very Fast | Google's Gemma model, instruction-tuned |
| `llama-3.3-70b-versatile` | Powerful | Fast | Large model, versatile capabilities |
| `llama-3.1-70b-versatile` | Powerful | Fast | High capability, good reasoning |
| `llama-3.1-405b-reasoning` | Powerful | Moderate | Largest model, best for reasoning |

### Access Requirements

- **API Key**: Required (get from [Groq Console](https://console.groq.com))
- **Account**: Free Groq account
- **Cost**: $0.00 - No credits needed
- **Rate Limits**: 
  - 600 requests per minute (RPM)
  - 10,000 requests per day

### Usage Example

```bash
curl -X POST http://localhost:3000/api/v1/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "groq",
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## DeepSeek (Rate-Limited Free Tier)

**Provider**: DeepSeek  
**Access**: Free tier with API key  
**Credits Required**: ❌ **NO** - Free tier available (rate-limited)  
**Rate Limits**: No official limits, but may experience throttling during high traffic

### Available Free Models

| Model | Category | Notes |
|-------|----------|-------|
| `deepseek-chat` | Fast | General-purpose chat model, V3 |
| `deepseek-coder` | Fast | Code-optimized model |

### Access Requirements

- **API Key**: Required (get from [DeepSeek Platform](https://platform.deepseek.com))
- **Account**: Free DeepSeek account
- **Cost**: $0.00 - Free tier available (rate-limited)
- **Rate Limits**: 
  - No official rate limits published
  - May experience throttling during high traffic
  - Free tier has usage limits (check DeepSeek documentation)

### Usage Example

```bash
curl -X POST http://localhost:3000/api/v1/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "deepseek",
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

**Note**: DeepSeek offers off-peak pricing discounts (up to 75% off) during certain hours, but the free tier is available with rate limits.

---

## OpenRouter (Requires Credits in Balance)

**Provider**: OpenRouter  
**Access**: Account with credits in balance (even for "free" models)  
**Credits Required**: ⚠️ **YES** - Requires account credits in balance even for free models  
**Status**: **NOT TRULY FREE** - Excluded from this catalogue (requires credits)

### Note on OpenRouter

While OpenRouter offers models labeled as "free", they still require:
- Account credits to be purchased (minimum $10 recommended)
- Credits are **NOT consumed** for free models, but account **must have credits in balance**
- Rate limits:
  - **Without credits**: 50 requests/day, 20 requests/minute
  - **With $10+ credits**: 1,000 requests/day, 20 requests/minute

**Free models available** (require credits in balance, but credits not consumed):
- `meta-llama/llama-3.1-8b-instruct` - Fast, general-purpose
- `microsoft/phi-3-mini-4k-instruct` - Fast, compact model
- `google/gemini-flash-1.5` - Fast, efficient model
- `deepseek/deepseek-chat:free` - General-purpose with strong reasoning

These are configured in the system but are **not included** in this free models catalogue as they require account credits in balance.

---

## Summary

### Truly Free Models (No Credits Required)

| Provider | Models Count | Total Free Models |
|----------|-------------|-------------------|
| **Google Gemini** | 4 | 4 |
| **GitHub Models API** | 6 | 6 |
| **Groq** | 6 | 6 |
| **DeepSeek** | 2 | 2 |
| **TOTAL** | **18** | **18** |

### Quick Reference

**Fast Models (No Credits)**:
- `gemini-1.5-flash` (Gemini)
- `gemini-2.0-flash-exp` (Gemini)
- `openai/gpt-3.5-turbo` (GitHub)
- `anthropic/claude-3-haiku` (GitHub)
- `llama-3.1-8b-instant` (Groq)
- `mixtral-8x7b-32768` (Groq)
- `gemma-7b-it` (Groq)
- `deepseek-chat` (DeepSeek)
- `deepseek-coder` (DeepSeek)

**Powerful Models (No Credits)**:
- `gemini-1.5-pro` (Gemini)
- `gemini-1.5-pro-latest` (Gemini)
- `openai/gpt-4o` (GitHub)
- `openai/gpt-4-turbo` (GitHub)
- `anthropic/claude-3-opus` (GitHub)
- `anthropic/claude-3-sonnet` (GitHub)
- `llama-3.3-70b-versatile` (Groq)
- `llama-3.1-70b-versatile` (Groq)
- `llama-3.1-405b-reasoning` (Groq)

### Access Requirements Summary

| Provider | Account Type | API Key Required | Credits Required |
|----------|-------------|------------------|------------------|
| Google Gemini | Free Google Account | ✅ Yes | ❌ No |
| GitHub Models API | GitHub Pro/Education | ✅ Yes (Token) | ❌ No |
| Groq | Free Groq Account | ✅ Yes | ❌ No |
| DeepSeek | Free DeepSeek Account | ✅ Yes | ❌ No (Rate-limited) |

### Rate Limits Summary

| Provider | Requests/Minute | Requests/Day | Notes |
|----------|----------------|--------------|-------|
| Google Gemini | 15-60 (varies) | Varies | Depends on model |
| GitHub Models API | 60 | 5,000 | Pro account limits |
| Groq | 600 | 10,000 | Free tier limits |
| DeepSeek | No official limit | No official limit | May throttle during high traffic |

---

## Configuration Files

All free models are configured in:
- `litellm_config.yaml` - LiteLLM model configuration
- `app/models/categorization.py` - Model categorization and metadata
- `config.json` - Provider configuration

---

## Last Updated

2025-12-07 - Complete catalogue of all free models (no credits required)

---

## Notes

- **GitHub Models API**: Requires GitHub Pro subscription ($4/month) or free GitHub Education Pack for students
- **Google Gemini**: Completely free, no subscription needed (rate-limited)
- **Groq**: Completely free, no subscription needed (rate-limited: 600 RPM, 10K/day)
- **DeepSeek**: Free tier available with rate limits (no official limits published, may throttle)
- **OpenRouter**: Not included as it requires account credits even for "free" models

## Rate-Limited Free Models Summary

All models listed in this catalogue are **rate-limited** but **do not require credits**:
- Rate limits prevent abuse and ensure fair usage
- No credits are consumed when using these models
- Limits vary by provider and account type
- Free tiers are designed for development, testing, and moderate usage

