# Rate Limits Documentation

This document provides comprehensive rate limit information for all supported AI model providers, sourced from official documentation and community findings.

## Overview

Rate limits are enforced to ensure fair usage and system stability. Each provider has different rate limit structures, which may include:
- **RPM**: Requests Per Minute
- **TPM**: Tokens Per Minute
- **RPD**: Requests Per Day
- **TPD**: Tokens Per Day
- **ITPM**: Input Tokens Per Minute
- **OTPM**: Output Tokens Per Minute

## Provider Rate Limits

### GitHub Models API

**Status**: Pro Account Available

**Rate Limits** (as of 2024):
- Official documentation indicates rate limits are based on GitHub account tier
- Pro accounts have higher limits than free accounts
- Specific limits are not publicly documented but are generally generous for pro accounts
- Rate limits may vary by model

**Workarounds**:
- Use classic Personal Access Tokens (not fine-grained tokens)
- Ensure token has `repo` scope minimum
- Monitor rate limit headers in API responses

**Sources**:
- GitHub Models API Documentation
- Community testing and verification

### Groq

**Status**: Free Tier Available, Paid Tiers Available

**Free Tier Rate Limits**:
- **RPM**: ~30 requests per minute (varies by model)
- **TPM**: Varies by model
- **Daily Limits**: Limited requests per day

**Paid Tier Rate Limits**:
- **RPM**: Significantly higher (exact limits depend on tier)
- **TPM**: Higher token limits
- **Priority**: Higher priority processing

**Per-Model Differences**:
- Smaller models (8B) have higher rate limits
- Larger models (70B, 405B) have lower rate limits
- Instant models optimized for speed have highest limits

**Sources**:
- Groq API Documentation
- Community benchmarks and testing

### DeepSeek

**Status**: No Strict Rate Limits (Pay-as-You-Go API)

**Rate Limits**:
- **Official**: No explicit rate limits enforced for API access
- **Soft Limits**: May experience throttling during high traffic periods
- **Connection Timeout**: Requests not completed within 30 minutes will be closed
- **Best Practice**: Monitor response times and implement exponential backoff if needed

**Notes**:
- **API Access**: Requires pay-as-you-go pricing (not free tier)
- **Free Tier**: Only available for chat interface (chat.deepseek.com), not API access
- **Pricing**: Competitive pay-as-you-go pricing with off-peak discounts (up to 75% off)
- **Suitable for**: High-volume usage with proper error handling

**API Pricing** (as of 2025):
- Input tokens: ~$0.028 per 1M tokens (cache hit), ~$0.28 per 1M tokens (cache miss)
- Output tokens: ~$0.42 per 1M tokens

**Sources**:
- [DeepSeek API Documentation](https://api-docs.deepseek.com/quick_start/rate_limit/)
- [DeepSeek Pricing](https://api-docs.deepseek.com/quick_start/pricing/)

### OpenRouter

**Status**: Free Models Available (Requires Credits in Balance)

**Rate Limits for Free Models**:
- **Without purchased credits** (< $10):
  - 50 requests per day
  - 20 requests per minute
- **With $10+ credits in account**:
  - 1,000 requests per day
  - 20 requests per minute

**Important Notes**:
- ⚠️ **Free models require credits in account balance** (even though credits are not consumed)
- Minimum recommended: $10 in credits for 1,000 requests/day limit
- Free models include: `meta-llama/llama-3.1-8b-instruct`, `microsoft/phi-3-mini-4k-instruct`, `google/gemini-flash-1.5`, `deepseek/deepseek-chat:free`
- Credits are NOT consumed when using free models, but account must have credits

**Pricing Structure**:
- Pay-per-use model for paid models
- Pricing varies by underlying model provider
- Transparent pricing with cost per token
- Free models: $0 cost (but require credits in balance)

**Sources**:
- [OpenRouter API Documentation](https://openrouter.ai/docs/api-reference/limits)
- [OpenRouter Rate Limits Guide](https://openrouter.zendesk.com/hc/en-us/articles/39501163636379-OpenRouter-Rate-Limits-What-You-Need-to-Know)

### Google Gemini

**Status**: Pro Account Available (Tier 1)

**Tier 1 Rate Limits** (Pro Account):
- **Gemini 2.0 Flash**: 
  - RPM: 2,000
  - TPM: 4,000,000
- **Gemini 2.0 Flash Lite**:
  - RPM: 4,000
  - TPM: 4,000,000
- **Gemini 1.5 Flash**:
  - RPM: 2,000
  - TPM: 4,000,000
- **Gemini 1.5 Pro**:
  - RPM: 1,000
  - TPM: 4,000,000

**Higher Tiers**:
- Limits increase with higher usage tiers
- Specific limits available in Google Cloud Console

**Sources**:
- Google AI Studio Documentation
- Google Cloud Console rate limit information

### Mistral AI

**Status**: Free Tier Available, Paid Tiers Available

**Rate Limits**:
- Varies by account tier and model
- Free tier has lower limits
- Paid tiers offer higher limits
- Limits are enforced per API key

**Per-Model Limits**:
- Smaller models (Tiny, 7B) have higher limits
- Larger models (Medium, Large) have lower limits
- Codestral models have separate limits

**Sources**:
- Mistral AI API Documentation
- Account dashboard rate limit information

### Codestral (Mistral)

**Status**: Part of Mistral AI

**Rate Limits**:
- Same rate limit structure as Mistral AI
- Limits shared with Mistral account
- May have model-specific adjustments

**Sources**:
- Mistral AI API Documentation (Codestral section)

## Rate Limit Management Strategies

### 1. Request Queuing
Implement queuing systems to manage request flow and prevent exceeding limits.

### 2. Exponential Backoff
When encountering 429 errors, implement exponential backoff with retry logic.

### 3. Rate Limit Header Monitoring
Monitor rate limit headers in API responses:
- `x-ratelimit-limit-requests`
- `x-ratelimit-remaining-requests`
- `x-ratelimit-reset-requests`
- `retry-after`

### 4. Client-Side Rate Limiting
Implement token bucket or sliding window algorithms to stay within limits.

### 5. Multi-Provider Distribution
Distribute requests across multiple providers to avoid hitting limits on a single provider.

### 6. Priority-Based Routing
Route critical requests to providers with higher limits or better availability.

## Implementation Notes

### Per-Model Rate Limits
Some providers enforce different rate limits per model. The system tracks:
- Provider-level rate limits (default)
- Model-level rate limits (when available)
- Dynamic rate limit updates from API headers

### Rate Limit Tracking
The system maintains:
- Current rate limit status per provider
- Current rate limit status per model
- Historical rate limit hit data
- Automatic recovery after rate limit windows

### Fallback Behavior
When rate limits are hit:
1. Provider is marked as unavailable
2. System automatically falls back to next available provider
3. Rate limit status is tracked for recovery
4. Automatic retry after rate limit window expires

## References

- [OpenAI Rate Limits Guide](https://platform.openai.com/docs/guides/rate-limits)
- [Anthropic Rate Limits Documentation](https://docs.anthropic.com/en/api/rate-limits)
- [Google AI Studio Documentation](https://ai.google.dev/docs)
- [Groq API Documentation](https://console.groq.com/docs)
- [DeepSeek API Documentation](https://api-docs.deepseek.com)
- [Mistral AI Documentation](https://docs.mistral.ai)
- [OpenRouter Documentation](https://openrouter.ai/docs)

## Last Updated

2024-12-07 - Initial documentation based on research from official sources and community findings.

