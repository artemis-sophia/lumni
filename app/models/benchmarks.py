"""
Benchmark Data and Rankings
Benchmark scores for models to support categorization and fallback ordering.
"""

from typing import Optional, List
from dataclasses import dataclass


@dataclass
class BenchmarkScores:
    """Benchmark scores for a model"""
    model: str
    provider: str
    mmlu: Optional[float] = None  # Massive Multitask Language Understanding (0-100)
    hellaswag: Optional[float] = None  # Commonsense reasoning (0-100)
    gsm8k: Optional[float] = None  # Grade school math (0-100)
    human_eval: Optional[float] = None  # Code generation (0-100)
    latency: Optional[float] = None  # Tokens per second (higher is better)
    category: str = 'fast'  # fast, powerful
    ranking: int = 1  # Ranking within category (1 = best)


# Benchmark scores for all models
BENCHMARK_SCORES: List[BenchmarkScores] = [
    # Fast Models (ranked by speed + cost efficiency)
    BenchmarkScores('llama-3.1-8b-instant', 'groq', 68, 82, 75, 65, 120, 'fast', 1),
    BenchmarkScores('mixtral-8x7b-32768', 'groq', 70, 86, 82, 70, 100, 'fast', 2),
    BenchmarkScores('anthropic/claude-3-haiku', 'github-copilot', 75, 88, 85, 73, 80, 'fast', 3),
    BenchmarkScores('openai/gpt-3.5-turbo', 'github-copilot', 70, 85, 80, 75, 70, 'fast', 4),
    BenchmarkScores('gemini-2.0-flash-exp', 'gemini', 72, 88, 84, 74, 75, 'fast', 5),
    BenchmarkScores('gemini-1.5-flash', 'gemini', 74, 89, 86, 75, 70, 'fast', 6),
    BenchmarkScores('mistral-tiny', 'mistral', 65, 80, 70, 60, 90, 'fast', 7),
    BenchmarkScores('mistral-7b-instruct', 'mistral', 68, 83, 78, 68, 85, 'fast', 8),
    BenchmarkScores('deepseek-chat', 'deepseek', 73, 87, 83, 72, 60, 'fast', 9),
    BenchmarkScores('codestral-latest', 'codestral', 70, 85, 78, 76, 65, 'fast', 10),

    # Powerful Models (ranked by reasoning capability)
    BenchmarkScores('anthropic/claude-3-opus', 'github-copilot', 87, 95, 96, 84, 30, 'powerful', 1),
    BenchmarkScores('llama-3.1-405b-reasoning', 'groq', 85, 94, 95, 82, 20, 'powerful', 2),
    BenchmarkScores('openai/gpt-4o', 'github-copilot', 88, 95, 95, 90, 35, 'powerful', 3),
    BenchmarkScores('deepseek-reasoner', 'deepseek', 83, 93, 94, 80, 25, 'powerful', 4),
    BenchmarkScores('gemini-1.5-pro', 'gemini', 84, 93, 93, 79, 30, 'powerful', 5),
    BenchmarkScores('openai/gpt-4-turbo', 'github-copilot', 87, 94, 94, 88, 32, 'powerful', 6),
    BenchmarkScores('anthropic/claude-3-sonnet', 'github-copilot', 82, 93, 92, 81, 28, 'powerful', 7),
    BenchmarkScores('llama-3.3-70b-versatile', 'groq', 82, 92, 90, 78, 40, 'powerful', 8),
    BenchmarkScores('llama-3.1-70b-versatile', 'groq', 80, 91, 88, 76, 38, 'powerful', 9),
    BenchmarkScores('mistral-large-latest', 'mistral', 83, 93, 91, 78, 35, 'powerful', 10),
]


def get_model_benchmarks(provider: str, model: str) -> Optional[BenchmarkScores]:
    """Get benchmark scores for a model"""
    for benchmark in BENCHMARK_SCORES:
        if benchmark.provider == provider and benchmark.model == model:
            return benchmark
    return None


def get_models_by_category(category: str) -> List[BenchmarkScores]:
    """Get all models in a category, sorted by ranking"""
    return sorted(
        [b for b in BENCHMARK_SCORES if b.category == category],
        key=lambda x: x.ranking
    )


def get_fallback_order(category: str) -> List[dict]:
    """Get fallback order for a category"""
    return [
        {'provider': b.provider, 'model': b.model}
        for b in get_models_by_category(category)
    ]


def compare_models(
    provider1: str,
    model1: str,
    provider2: str,
    model2: str
) -> int:
    """Compare two models by benchmark scores"""
    b1 = get_model_benchmarks(provider1, model1)
    b2 = get_model_benchmarks(provider2, model2)

    if not b1 and not b2:
        return 0
    if not b1:
        return 1
    if not b2:
        return -1

    # Compare by MMLU score (primary metric)
    if b1.mmlu and b2.mmlu:
        return int(b2.mmlu - b1.mmlu)  # Higher is better

    # Fall back to ranking
    return b1.ranking - b2.ranking

