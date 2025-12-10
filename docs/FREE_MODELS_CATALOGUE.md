# Free Models Catalogue

**Complete catalogue of all models that can be used WITHOUT EXPENDING CREDITS (Rate-Limited Free Models)**

This document lists all models available through Lumni that require **zero credits** to use, including all rate-limited free tiers. Models are organized by provider with access requirements and rate limits.

**Key**: All models listed here are **rate-limited** but **do not expend credits** - they are completely free to use within their rate limits.

---

## Table of Contents

1. [Google Gemini](#google-gemini)
2. [GitHub Models API](#github-models-api)
3. [Groq](#groq)
5. [OpenRouter](#openrouter)
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
| `gemini-2.0-flash-thinking-exp` | Powerful | Moderate | Experimental with reasoning capabilities |

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
| `openai/gpt-5` | Powerful | Highest | Latest GPT-5 model |
| `openai/gpt-5-codex` | Powerful | Highest | Code-optimized GPT-5 |
| `openai/gpt-5.1` | Powerful | Highest | GPT-5.1 model |
| `openai/gpt-5.1-codex` | Powerful | Highest | Code-optimized GPT-5.1 |
| `openai/gpt-5.1-codex-mini` | Fast | High | Smaller code model |
| `openai/gpt-5.1-codex-max` | Powerful | Highest | Largest code model |
| `openai/gpt-4o` | Powerful | Highest | Latest GPT-4 model, best overall |
| `openai/gpt-4o-mini` | Fast | High | Cost-effective GPT-4 variant |
| `openai/gpt-4-turbo` | Powerful | Very High | High performance, fast responses |
| `openai/gpt-3.5-turbo` | Fast | High | Cost-effective, fast responses |
| `openai/o1` | Powerful | Highest | Reasoning-focused model |
| `meta/llama-3.3-70b-instruct` | Powerful | Very High | Llama 3.3 70B via GitHub |
| `meta/llama-3.2-11b-vision-instruct` | Powerful | Very High | Llama 3.2 11B Vision model |
| `meta/llama-3.2-90b-vision-instruct` | Powerful | Very High | Llama 3.2 90B Vision model |
| `meta/llama-4-maverick-17b-128e-instruct-fp8` | Powerful | Very High | Llama 4 Maverick via GitHub |
| `meta/llama-4-scout-17b-16e-instruct` | Powerful | Very High | Llama 4 Scout via GitHub |
| `microsoft/phi-4` | Powerful | Very High | Phi-4 via GitHub |
| `xai/grok-3` | Powerful | Very High | Grok 3 via GitHub |
| `cohere/cohere-command-a` | Powerful | Very High | Cohere Command A |
| `cohere/cohere-command-r-08-2024` | Powerful | Very High | Cohere Command R |
| `cohere/cohere-command-r-plus-08-2024` | Powerful | Very High | Cohere Command R+ |
| `deepseek/deepseek-r1` | Powerful | Very High | DeepSeek R1 reasoning model |
| `deepseek/deepseek-r1-0528` | Powerful | Very High | DeepSeek R1 (0528 version) |
| `deepseek/deepseek-v3-0324` | Powerful | Very High | DeepSeek V3 model |

**Note:** Anthropic (Claude) models are **NOT available** in GitHub Models API as of December 2025. Despite documentation references, catalog queries and API tests confirm no Anthropic models are accessible via GitHub Models API.

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
| `llama-3.3-70b-versatile` | Powerful | Fast | Large model, versatile capabilities |
| `llama-4-maverick-17b-128e-instruct` | Powerful | Fast | Llama 4 Maverick (Preview) - 17B model with 128 experts |
| `llama-4-scout-17b-16e-instruct` | Powerful | Fast | Llama 4 Scout (Preview) - 17B model with 16 experts |

**Note:** The following models were decommissioned or do not exist:
- `mixtral-8x7b-32768` - Decommissioned
- `gemma-7b-it` - Decommissioned
- `llama-3.1-70b-versatile` - Decommissioned
- `llama-3.1-405b-reasoning` - Does not exist
- `llama-3.2-11b-v0.1` - Does not exist
- `llama-3.2-90b-v0.1` - Does not exist

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


## OpenRouter

**Provider**: OpenRouter  
**Access**: Free tier with API key  
**Credits Required**: ❌ **NO** - Free models work without credits  
**Rate Limits**: 
  - Without credits: 50 requests/day, 20 requests/minute
  - With $10+ credits: 1,000 requests/day, 20 requests/minute (increased limit)

### Available Free Models

| Model | Category | Speed | Notes |
|-------|----------|-------|-------|
| `meta-llama/llama-3.1-8b-instruct` | Fast | Very Fast | General-purpose, fast responses |
| `microsoft/phi-3-mini-4k-instruct` | Fast | Very Fast | Compact model, efficient |
| `google/gemini-flash-1.5` | Fast | Very Fast | Fast, efficient model |
| `deepseek/deepseek-chat:free` | Fast | Fast | General-purpose with strong reasoning |
| `meta-llama/llama-3.2-11b-instruct` | Fast | Fast | Latest 11B model |
| `meta-llama/llama-3.2-90b-instruct` | Powerful | Fast | Large model, high capability |
| `mistralai/mistral-small` | Powerful | Fast | Balanced performance |
| `qwen/qwen-2.5-7b-instruct` | Fast | Fast | Efficient 7B model |

### Access Requirements

- **API Key**: Required (get from [OpenRouter](https://openrouter.ai))
- **Account**: Free OpenRouter account
- **Cost**: $0.00 - No credits needed (free models work without credits)
- **Rate Limits**: 
  - **Without credits**: 50 requests per day, 20 requests per minute
  - **With $10+ credits**: 1,000 requests per day, 20 requests per minute (increased limit)
- **Important**: Credits are **NOT consumed** when using free models. Adding $10+ credits only increases the daily limit from 50 to 1,000 requests/day.

### Usage Example

```bash
curl -X POST http://localhost:3000/api/v1/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openrouter",
    "model": "meta-llama/llama-3.1-8b-instruct",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## Summary

### Truly Free Models (No Credits Required)

| Provider | Models Count | Total Free Models |
|----------|-------------|-------------------|
| **Google Gemini** | 7 | 7 |
| **GitHub Models API** | 19 | 19 |
| **Groq** | 2 | 2 |
| **OpenRouter** | 8 | 8 |
| **Mistral AI** | 5 | 5 |
| **TOTAL** | **41** | **41** |

### Quick Reference

**Fast Models (No Credits)**:
- `gemini-1.5-flash` (Gemini)
- `gemini-2.0-flash-exp` (Gemini)
- `openai/gpt-3.5-turbo` (GitHub)
- `openai/gpt-4o-mini` (GitHub)
- `openai/gpt-5.1-codex-mini` (GitHub)
- `anthropic/claude-3-haiku` (GitHub)
- `anthropic/claude-4.5-haiku` (GitHub)
- `xai/grok-code-fast-1` (GitHub)
- `llama-3.1-8b-instant` (Groq)
- `llama-3.2-11b-v0.1` (Groq)
- `mixtral-8x7b-32768` (Groq)
- `gemma-7b-it` (Groq)

**Powerful Models (No Credits)**:
- `gemini-1.5-pro` (Gemini)
- `gemini-1.5-pro-latest` (Gemini)
- `gemini-2.0-flash-thinking-exp` (Gemini)
- `openai/gpt-5` (GitHub)
- `openai/gpt-5-codex` (GitHub)
- `openai/gpt-5.1` (GitHub)
- `openai/gpt-5.1-codex` (GitHub)
- `openai/gpt-5.1-codex-max` (GitHub)
- `openai/gpt-4o` (GitHub)
- `openai/gpt-4-turbo` (GitHub)
- `anthropic/claude-4.5-opus` (GitHub)
- `anthropic/claude-4.5-sonnet` (GitHub)
- `anthropic/claude-4-sonnet` (GitHub)
- `anthropic/claude-3-opus` (GitHub)
- `anthropic/claude-3-sonnet` (GitHub)
- `anthropic/claude-3.5-sonnet` (GitHub)
- `google/gemini-3-pro` (GitHub)
- `google/gemini-2.5-pro` (GitHub)
- `llama-3.3-70b-versatile` (Groq)
- `llama-3.1-70b-versatile` (Groq)
- `llama-3.2-90b-v0.1` (Groq)
- `llama-3.1-405b-reasoning` (Groq)

### Access Requirements Summary

| Provider | Account Type | API Key Required | Credits Required |
|----------|-------------|------------------|------------------|
| Google Gemini | Free Google Account | ✅ Yes | ❌ No |
| GitHub Models API | GitHub Pro/Education | ✅ Yes (Token) | ❌ No |
| Groq | Free Groq Account | ✅ Yes | ❌ No |
| OpenRouter | Free OpenRouter Account | ✅ Yes | ❌ No |
| Mistral AI | Free Mistral Account | ✅ Yes | ❌ No |

### Rate Limits Summary

| Provider | Requests/Minute | Requests/Day | Notes |
|----------|----------------|--------------|-------|
| Google Gemini | 15-60 (varies) | Varies | Depends on model |
| GitHub Models API | 60 | 5,000 | Pro account limits |
| Groq | 600 | 10,000 | Free tier limits |
| OpenRouter | 20 | 50 (or 1,000 with $10+ credits) | Free models work without credits |
| Mistral AI | Varies | Varies | Free tier with restrictive limits |

---

## Configuration Files

All free models are configured in:
- `litellm_config.yaml` - LiteLLM model configuration
- `app/models/categorization.py` - Model categorization and metadata
- `config.json` - Provider configuration

---

## Last Updated

2025-12-08 - Updated with additional free models: Gemini 2.0 thinking, Groq llama-3.2 variants, and GitHub gpt-4o-mini and claude-3.5-sonnet

---

## Notes

- **GitHub Models API**: Requires GitHub Pro subscription ($4/month) or free GitHub Education Pack for students
- **Google Gemini**: Completely free, no subscription needed (rate-limited)
- **Groq**: Completely free, no subscription needed (rate-limited: 600 RPM, 10K/day)
- **OpenRouter**: Free models work without credits (50 requests/day). $10+ credits increases limit to 1,000/day
- **Mistral AI**: Free tier available with restrictive rate limits

## Rate-Limited Free Models Summary

All models listed in this catalogue are **rate-limited** but **do not require credits**:
- Rate limits prevent abuse and ensure fair usage
- No credits are consumed when using these models
- Limits vary by provider and account type
- Free tiers are designed for development, testing, and moderate usage

