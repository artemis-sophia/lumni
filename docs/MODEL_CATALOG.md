# Model Catalog with Pricing

Complete catalog of all available models across providers with accurate pricing information (cost per million tokens).

## Pricing Structure

Pricing is typically quoted as:
- **Input Tokens**: Cost per million input tokens
- **Output Tokens**: Cost per million output tokens
- **Blended**: Average cost when input/output pricing is the same

## GitHub Models API

**Provider**: GitHub Models API (models.github.ai)  
**Account Type**: Pro Account Available

### Available Models

| Model | Input ($/1M) | Output ($/1M) | Category | Notes |
|-------|-------------|---------------|----------|-------|
| openai/gpt-4o | ~$2.50 | ~$10.00 | Powerful | Latest GPT-4 model |
| openai/gpt-4-turbo | ~$10.00 | ~$30.00 | Powerful | High performance |
| openai/gpt-3.5-turbo | ~$0.50 | ~$1.50 | Fast | Cost-effective |
| anthropic/claude-3-opus | ~$15.00 | ~$75.00 | Powerful | Highest capability |
| anthropic/claude-3-sonnet | ~$3.00 | ~$15.00 | Powerful | Balanced performance |
| anthropic/claude-3-haiku | ~$0.80 | ~$4.00 | Fast | Fast and efficient |

**Note**: Pricing through GitHub Models API may differ from direct provider pricing. Check GitHub documentation for current rates.

## Groq

**Provider**: Groq  
**Account Type**: Free Tier + Paid Tiers

### Available Models

| Model | Input ($/1M) | Output ($/1M) | Category | Speed |
|-------|-------------|---------------|----------|-------|
| llama-3.1-8b-instant | Free (tier limits) | Free (tier limits) | Fast | Very Fast |
| llama-3.3-70b-versatile | Free (tier limits) | Free (tier limits) | Powerful | Fast |
| llama-3.1-70b-versatile | Free (tier limits) | Free (tier limits) | Powerful | Fast |
| llama-3.1-405b-reasoning | Free (tier limits) | Free (tier limits) | Powerful | Moderate |
| mixtral-8x7b-32768 | Free (tier limits) | Free (tier limits) | Fast | Very Fast |
| gemma-7b-it | Free (tier limits) | Free (tier limits) | Fast | Very Fast |

**Note**: Groq offers free tier with rate limits. Paid tiers may have different pricing.

## DeepSeek

**Provider**: DeepSeek  
**Account Type**: Pay-per-use

### Available Models

| Model | Input ($/1M) | Output ($/1M) | Category | Notes |
|-------|-------------|---------------|----------|-------|
| deepseek-chat | $0.27 | $1.10 | Fast | V3 model |
| deepseek-coder | $0.27 | $1.10 | Fast | Code-optimized |
| deepseek-reasoner (R1) | $0.55 | $2.19 | Powerful | Reasoning-focused |

**Off-Peak Pricing**: DeepSeek offers up to 75% discount during off-peak hours. Check current off-peak schedule.

## OpenRouter

**Provider**: OpenRouter  
**Account Type**: Free Tier + Paid Tiers

### Available Models

OpenRouter provides access to multiple models from different providers. Pricing varies by underlying model.

| Model | Input ($/1M) | Output ($/1M) | Category | Provider |
|-------|-------------|---------------|----------|----------|
| meta-llama/llama-3-8b-instruct | ~$0.05 | ~$0.15 | Fast | Meta |
| meta-llama/llama-3-70b-instruct | ~$0.59 | ~$0.79 | Powerful | Meta |
| mistralai/mistral-7b-instruct | ~$0.20 | ~$0.60 | Fast | Mistral |
| anthropic/claude-3-haiku | ~$0.80 | ~$4.00 | Fast | Anthropic |
| openai/gpt-3.5-turbo | ~$0.50 | ~$1.50 | Fast | OpenAI |
| google/gemini-pro | ~$0.10 | ~$0.40 | Fast | Google |
| openai/gpt-4 | ~$30.00 | ~$60.00 | Powerful | OpenAI |
| openai/gpt-4-turbo | ~$10.00 | ~$30.00 | Powerful | OpenAI |
| anthropic/claude-3-sonnet | ~$3.00 | ~$15.00 | Powerful | Anthropic |
| anthropic/claude-3-opus | ~$15.00 | ~$75.00 | Powerful | Anthropic |
| mistralai/mistral-medium | ~$2.00 | ~$6.00 | Powerful | Mistral |

**Note**: OpenRouter adds a small markup to underlying provider pricing. Check OpenRouter pricing page for current rates.

## Google Gemini

**Provider**: Google AI (Gemini)  
**Account Type**: Pro Account Available (Tier 1)

### Available Models

| Model | Input ($/1M) | Output ($/1M) | Category | Notes |
|-------|-------------|---------------|----------|-------|
| gemini-2.0-flash-exp | $0.10 | $0.40 | Fast | Experimental |
| gemini-1.5-flash | $0.07 | $0.30 | Fast | Production-ready |
| gemini-1.5-pro | $1.25 | $5.00 | Powerful | High capability |
| gemini-1.5-pro-latest | $1.25 | $5.00 | Powerful | Latest version |

**Free Tier**: Limited requests per day. Pro account has higher limits.

## Mistral AI

**Provider**: Mistral AI  
**Account Type**: Free Tier + Paid Tiers

### Available Models

| Model | Input ($/1M) | Output ($/1M) | Category | Notes |
|-------|-------------|---------------|----------|-------|
| mistral-tiny | ~$0.20 | ~$0.60 | Fast | Smallest model |
| mistral-7b-instruct | ~$0.20 | ~$0.60 | Fast | 7B parameter model |
| mistral-small | ~$2.00 | ~$6.00 | Powerful | Balanced |
| mistral-medium | ~$2.00 | ~$6.00 | Powerful | High performance |
| mistral-large-latest | ~$2.00 | ~$6.00 | Powerful | Latest large model |

## Codestral (Mistral)

**Provider**: Mistral AI (Codestral)  
**Account Type**: Same as Mistral AI

### Available Models

| Model | Input ($/1M) | Output ($/1M) | Category | Notes |
|-------|-------------|---------------|----------|-------|
| codestral-latest | ~$0.20 | ~$0.60 | Fast | Code generation |
| codestral-mamba-latest | ~$0.20 | ~$0.60 | Fast | Mamba architecture |

## Cost Optimization Strategies

### 1. Model Selection by Task Type
- **Fast Models**: Use for token-intensive, low-complexity tasks
- **Powerful Models**: Use only for complex reasoning or critical tasks

### 2. Off-Peak Pricing
- DeepSeek offers 75% discount during off-peak hours
- Schedule non-critical tasks during off-peak periods

### 3. Free Tier Utilization
- Groq free tier for development and testing
- Gemini free tier for low-volume usage

### 4. Token Optimization
- Minimize prompt size where possible
- Set appropriate `max_tokens` to avoid unnecessary generation
- Use streaming for long responses to reduce wait time

### 5. Caching
- Cache responses for repeated queries
- Use embeddings for semantic similarity instead of full generation

### 6. Batch Processing
- Group similar requests when possible
- Use batch APIs where available

## Cost Tracking

The system tracks:
- Cost per request (input + output tokens)
- Cost per provider
- Cost per model
- Daily/monthly cost summaries
- Cost optimization recommendations

## Pricing Updates

Pricing information is subject to change. This document should be updated regularly based on:
- Official provider pricing pages
- API documentation updates
- Community reports of pricing changes

## References

- [OpenAI Pricing](https://openai.com/api/pricing/)
- [Anthropic Pricing](https://www.anthropic.com/pricing)
- [Google AI Pricing](https://ai.google.dev/pricing)
- [Groq Pricing](https://console.groq.com/pricing)
- [DeepSeek Pricing](https://www.deepseek.com/pricing)
- [Mistral Pricing](https://mistral.ai/pricing/)
- [OpenRouter Pricing](https://openrouter.ai/models)

## Last Updated

2024-12-07 - Initial catalog based on research from official pricing pages and community sources.

