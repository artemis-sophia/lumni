# Model Benchmarks and Categorization

This document provides benchmark scores and rationale for categorizing models as "fast" or "powerful" based on academic benchmarks and performance metrics.

## Benchmark Overview

Models are evaluated across multiple dimensions:
- **Reasoning**: MMLU, HellaSwag, GSM8K, HumanEval
- **Speed**: Tokens per second, latency
- **Code Generation**: Code-specific benchmarks
- **Token Efficiency**: Performance per token cost

## Categorization Criteria

### Fast Models
**Characteristics**:
- High throughput (tokens per second)
- Low latency
- Cost-effective for token-intensive operations
- Suitable for: Simple Q&A, code completion, text generation, batch processing

**Benchmark Thresholds**:
- Latency: < 100ms per token
- Throughput: > 50 tokens/second
- Cost: < $1.00 per million tokens (blended)

### Powerful Models
**Characteristics**:
- High reasoning capability
- Better performance on complex tasks
- Suitable for: Complex reasoning, critical analysis, code review, strategic planning

**Benchmark Thresholds**:
- MMLU Score: > 70
- Reasoning: Strong performance on GSM8K, HumanEval
- Cost: May be higher, but justified for complex tasks

## Benchmark Scores

### GitHub Models API Models

#### openai/gpt-4o
- **Category**: Powerful
- **MMLU**: ~88
- **HellaSwag**: ~95
- **GSM8K**: ~95
- **HumanEval**: ~90
- **Latency**: Moderate
- **Ranking**: 1 (Powerful)

#### openai/gpt-4-turbo
- **Category**: Powerful
- **MMLU**: ~87
- **HellaSwag**: ~94
- **GSM8K**: ~94
- **HumanEval**: ~88
- **Latency**: Moderate
- **Ranking**: 2 (Powerful)

#### openai/gpt-3.5-turbo
- **Category**: Fast
- **MMLU**: ~70
- **HellaSwag**: ~85
- **GSM8K**: ~80
- **HumanEval**: ~75
- **Latency**: Fast
- **Ranking**: 1 (Fast)

#### anthropic/claude-3-opus
- **Category**: Powerful
- **MMLU**: ~87
- **HellaSwag**: ~95
- **GSM8K**: ~96
- **HumanEval**: ~84
- **Latency**: Moderate
- **Ranking**: 1 (Powerful) - Highest reasoning

#### anthropic/claude-3-sonnet
- **Category**: Powerful
- **MMLU**: ~82
- **HellaSwag**: ~93
- **GSM8K**: ~92
- **HumanEval**: ~81
- **Latency**: Moderate
- **Ranking**: 3 (Powerful)

#### anthropic/claude-3-haiku
- **Category**: Fast
- **MMLU**: ~75
- **HellaSwag**: ~88
- **GSM8K**: ~85
- **HumanEval**: ~73
- **Latency**: Fast
- **Ranking**: 2 (Fast)

### Groq Models

#### llama-3.1-8b-instant
- **Category**: Fast
- **MMLU**: ~68
- **HellaSwag**: ~82
- **GSM8K**: ~75
- **HumanEval**: ~65
- **Latency**: Very Fast (>100 tokens/sec)
- **Ranking**: 1 (Fast) - Fastest throughput

#### llama-3.3-70b-versatile
- **Category**: Powerful
- **MMLU**: ~82
- **HellaSwag**: ~92
- **GSM8K**: ~90
- **HumanEval**: ~78
- **Latency**: Fast
- **Ranking**: 2 (Powerful)

#### llama-3.1-70b-versatile
- **Category**: Powerful
- **MMLU**: ~80
- **HellaSwag**: ~91
- **GSM8K**: ~88
- **HumanEval**: ~76
- **Latency**: Fast
- **Ranking**: 3 (Powerful)

#### llama-3.1-405b-reasoning
- **Category**: Powerful
- **MMLU**: ~85
- **HellaSwag**: ~94
- **GSM8K**: ~95
- **HumanEval**: ~82
- **Latency**: Moderate
- **Ranking**: 1 (Powerful) - Best reasoning

#### mixtral-8x7b-32768
- **Category**: Fast
- **MMLU**: ~70
- **HellaSwag**: ~86
- **GSM8K**: ~82
- **HumanEval**: ~70
- **Latency**: Very Fast
- **Ranking**: 2 (Fast)

### DeepSeek Models

#### deepseek-chat
- **Category**: Fast
- **MMLU**: ~73
- **HellaSwag**: ~87
- **GSM8K**: ~83
- **HumanEval**: ~72
- **Latency**: Fast
- **Ranking**: 3 (Fast)

#### deepseek-coder
- **Category**: Fast
- **MMLU**: ~70
- **HellaSwag**: ~85
- **GSM8K**: ~80
- **HumanEval**: ~78 (Code-focused)
- **Latency**: Fast
- **Ranking**: 4 (Fast) - Code-optimized

#### deepseek-reasoner (R1)
- **Category**: Powerful
- **MMLU**: ~83
- **HellaSwag**: ~93
- **GSM8K**: ~94
- **HumanEval**: ~80
- **Latency**: Moderate
- **Ranking**: 4 (Powerful) - Strong reasoning

### Google Gemini Models

#### gemini-2.0-flash-exp
- **Category**: Fast
- **MMLU**: ~72
- **HellaSwag**: ~88
- **GSM8K**: ~84
- **HumanEval**: ~74
- **Latency**: Fast
- **Ranking**: 5 (Fast)

#### gemini-1.5-flash
- **Category**: Fast
- **MMLU**: ~74
- **HellaSwag**: ~89
- **GSM8K**: ~86
- **HumanEval**: ~75
- **Latency**: Fast
- **Ranking**: 6 (Fast)

#### gemini-1.5-pro
- **Category**: Powerful
- **MMLU**: ~84
- **HellaSwag**: ~93
- **GSM8K**: ~93
- **HumanEval**: ~79
- **Latency**: Moderate
- **Ranking**: 5 (Powerful)

### Mistral AI Models

#### mistral-tiny
- **Category**: Fast
- **MMLU**: ~65
- **HellaSwag**: ~80
- **GSM8K**: ~70
- **HumanEval**: ~60
- **Latency**: Very Fast
- **Ranking**: 7 (Fast)

#### mistral-7b-instruct
- **Category**: Fast
- **MMLU**: ~68
- **HellaSwag**: ~83
- **GSM8K**: ~78
- **HumanEval**: ~68
- **Latency**: Fast
- **Ranking**: 8 (Fast)

#### mistral-small
- **Category**: Powerful
- **MMLU**: ~78
- **HellaSwag**: ~90
- **GSM8K**: ~87
- **HumanEval**: ~75
- **Latency**: Moderate
- **Ranking**: 6 (Powerful)

#### mistral-medium
- **Category**: Powerful
- **MMLU**: ~81
- **HellaSwag**: ~92
- **GSM8K**: ~90
- **HumanEval**: ~77
- **Latency**: Moderate
- **Ranking**: 7 (Powerful)

#### mistral-large-latest
- **Category**: Powerful
- **MMLU**: ~83
- **HellaSwag**: ~93
- **GSM8K**: ~91
- **HumanEval**: ~78
- **Latency**: Moderate
- **Ranking**: 8 (Powerful)

### Codestral Models

#### codestral-latest
- **Category**: Fast
- **MMLU**: ~70
- **HellaSwag**: ~85
- **GSM8K**: ~78
- **HumanEval**: ~76 (Code-focused)
- **Latency**: Fast
- **Ranking**: 9 (Fast) - Code-optimized

#### codestral-mamba-latest
- **Category**: Fast
- **MMLU**: ~68
- **HellaSwag**: ~83
- **GSM8K**: ~75
- **HumanEval**: ~74 (Code-focused)
- **Latency**: Very Fast
- **Ranking**: 10 (Fast) - Mamba architecture

### OpenRouter Models

OpenRouter provides access to models from multiple providers. Benchmark scores match the underlying provider models (see above).

## Ranking Summary

### Fast Models (Ranked by Speed + Cost Efficiency)
1. llama-3.1-8b-instant (Groq) - Fastest
2. mixtral-8x7b-32768 (Groq)
3. anthropic/claude-3-haiku (GitHub/OpenRouter)
4. openai/gpt-3.5-turbo (GitHub/OpenRouter)
5. gemini-2.0-flash-exp (Gemini)
6. gemini-1.5-flash (Gemini)
7. mistral-tiny (Mistral)
8. mistral-7b-instruct (Mistral)
9. deepseek-chat (DeepSeek)
10. codestral-latest (Codestral)

### Powerful Models (Ranked by Reasoning Capability)
1. anthropic/claude-3-opus (GitHub/OpenRouter) - Best reasoning
2. llama-3.1-405b-reasoning (Groq) - Best reasoning
3. openai/gpt-4o (GitHub/OpenRouter)
4. deepseek-reasoner (DeepSeek)
5. gemini-1.5-pro (Gemini)
6. openai/gpt-4-turbo (GitHub/OpenRouter)
7. anthropic/claude-3-sonnet (GitHub/OpenRouter)
8. llama-3.3-70b-versatile (Groq)
9. llama-3.1-70b-versatile (Groq)
10. mistral-large-latest (Mistral)

## Fallback Ordering

### Fast Category Fallback Order
Based on speed, cost, and availability:
1. llama-3.1-8b-instant (Groq) - Highest priority
2. mixtral-8x7b-32768 (Groq)
3. anthropic/claude-3-haiku
4. openai/gpt-3.5-turbo
5. gemini-2.0-flash-exp
6. gemini-1.5-flash
7. mistral-tiny
8. mistral-7b-instruct
9. deepseek-chat
10. codestral-latest

### Powerful Category Fallback Order
Based on reasoning capability and availability:
1. anthropic/claude-3-opus - Highest priority
2. llama-3.1-405b-reasoning (Groq)
3. openai/gpt-4o
4. deepseek-reasoner
5. gemini-1.5-pro
6. openai/gpt-4-turbo
7. anthropic/claude-3-sonnet
8. llama-3.3-70b-versatile (Groq)
9. llama-3.1-70b-versatile (Groq)
10. mistral-large-latest

## Benchmark Sources

- **MMLU**: Massive Multitask Language Understanding
- **HellaSwag**: Commonsense reasoning
- **GSM8K**: Grade school math problems
- **HumanEval**: Code generation benchmark
- **Latency**: Measured tokens per second

## Notes

- Benchmark scores are approximate and may vary by implementation
- Rankings consider both performance and cost efficiency
- Fallback ordering optimizes for availability and performance
- Code-focused models (codestral, deepseek-coder) excel on HumanEval
- Reasoning models (claude-3-opus, llama-3.1-405b) excel on GSM8K

## Last Updated

2024-12-07 - Initial benchmark documentation based on published results and community testing.

