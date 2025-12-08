"""
Model categorization system with benchmark-based rankings
Maps models to their category (fast or powerful) and provider
"""

from typing import Optional, List
from dataclasses import dataclass
from app.models.benchmarks import get_model_benchmarks


ModelCategory = str  # 'fast' | 'powerful'


@dataclass
class ModelMetadata:
    """Model metadata"""
    provider: str
    model: str
    category: ModelCategory
    ranking: Optional[int] = None  # Ranking within category (1 = best)
    benchmark_score: Optional[float] = None  # Overall benchmark score


# Model categorization mapping
MODEL_CATEGORIZATION: dict[str, ModelMetadata] = {
    # Groq Models (Free Tier - No Credits Required)
    # All Groq models are free tier with rate limits - no credits needed
    'llama-3.1-8b-instant': ModelMetadata('groq', 'llama-3.1-8b-instant', 'fast'),
    'mixtral-8x7b-32768': ModelMetadata('groq', 'mixtral-8x7b-32768', 'fast'),
    'gemma-7b-it': ModelMetadata('groq', 'gemma-7b-it', 'fast'),
    'llama-3.3-70b-versatile': ModelMetadata('groq', 'llama-3.3-70b-versatile', 'powerful'),
    'llama-3.1-70b-versatile': ModelMetadata('groq', 'llama-3.1-70b-versatile', 'powerful'),
    'llama-3.1-405b-reasoning': ModelMetadata('groq', 'llama-3.1-405b-reasoning', 'powerful'),

    # GitHub Models API (Free for GitHub Pro/Education - No Credits Required)
    # All models are free with GitHub Pro account or GitHub Education Pack
    'openai/gpt-3.5-turbo': ModelMetadata('github-copilot', 'openai/gpt-3.5-turbo', 'fast'),
    'openai/gpt-4-turbo': ModelMetadata('github-copilot', 'openai/gpt-4-turbo', 'powerful'),
    'openai/gpt-4o': ModelMetadata('github-copilot', 'openai/gpt-4o', 'powerful'),
    'anthropic/claude-3-haiku': ModelMetadata('github-copilot', 'anthropic/claude-3-haiku', 'fast'),
    'anthropic/claude-3-sonnet': ModelMetadata('github-copilot', 'anthropic/claude-3-sonnet', 'powerful'),
    'anthropic/claude-3-opus': ModelMetadata('github-copilot', 'anthropic/claude-3-opus', 'powerful'),

    # DeepSeek (Pay-as-You-Go API - No Free Tier)
    # Note: DeepSeek API requires pay-as-you-go pricing. Free tier only available for chat interface, not API.
    'deepseek-chat': ModelMetadata('deepseek', 'deepseek-chat', 'fast'),
    'deepseek-coder': ModelMetadata('deepseek', 'deepseek-coder', 'fast'),

    # OpenRouter (Free Tier - Requires Credits in Balance)
    # Note: OpenRouter requires account credits ($10+ recommended) even for free models
    # Free models (credits not consumed, but account must have credits):
    'meta-llama/llama-3.1-8b-instruct': ModelMetadata('openrouter', 'meta-llama/llama-3.1-8b-instruct', 'fast'),
    'microsoft/phi-3-mini-4k-instruct': ModelMetadata('openrouter', 'microsoft/phi-3-mini-4k-instruct', 'fast'),
    'google/gemini-flash-1.5': ModelMetadata('openrouter', 'google/gemini-flash-1.5', 'fast'),
    'deepseek/deepseek-chat:free': ModelMetadata('openrouter', 'deepseek/deepseek-chat:free', 'fast'),

    # Google Gemini (Free Tier - No Credits Required)
    # All Gemini models are free with rate limits - no credits needed
    'gemini-2.0-flash-exp': ModelMetadata('gemini', 'gemini-2.0-flash-exp', 'fast'),
    'gemini-1.5-flash': ModelMetadata('gemini', 'gemini-1.5-flash', 'fast'),
    'gemini-1.5-pro': ModelMetadata('gemini', 'gemini-1.5-pro', 'powerful'),
    'gemini-1.5-pro-latest': ModelMetadata('gemini', 'gemini-1.5-pro-latest', 'powerful'),

    # Mistral
    'mistral-tiny': ModelMetadata('mistral', 'mistral-tiny', 'fast'),
    'mistral-7b-instruct': ModelMetadata('mistral', 'mistral-7b-instruct', 'fast'),
    'mistral-small': ModelMetadata('mistral', 'mistral-small', 'powerful'),
    'mistral-medium': ModelMetadata('mistral', 'mistral-medium', 'powerful'),
    'mistral-large-latest': ModelMetadata('mistral', 'mistral-large-latest', 'powerful'),

    # Codestral
    'codestral-latest': ModelMetadata('codestral', 'codestral-latest', 'fast'),
    'codestral-mamba-latest': ModelMetadata('codestral', 'codestral-mamba-latest', 'fast'),
}


def get_model_metadata(model_id: str) -> Optional[ModelMetadata]:
    """Get model metadata by model ID"""
    return MODEL_CATEGORIZATION.get(model_id)


def get_models_by_provider(provider: str) -> List[ModelMetadata]:
    """Get all models for a specific provider"""
    return [m for m in MODEL_CATEGORIZATION.values() if m.provider == provider]


def get_models_by_category(category: ModelCategory) -> List[ModelMetadata]:
    """Get all models in a specific category, sorted by ranking"""
    models = [m for m in MODEL_CATEGORIZATION.values() if m.category == category]

    # Enhance with benchmark data
    enhanced = []
    for model in models:
        benchmarks = get_model_benchmarks(model.provider, model.model)
        enhanced.append(ModelMetadata(
            provider=model.provider,
            model=model.model,
            category=model.category,
            ranking=benchmarks.ranking if benchmarks else None,
            benchmark_score=benchmarks.mmlu if benchmarks else None,
        ))

    # Sort by ranking (lower is better)
    return sorted(enhanced, key=lambda m: m.ranking or 999)


def get_category_fallback_order(category: ModelCategory) -> List[ModelMetadata]:
    """Get fallback order for a category based on benchmarks"""
    return get_models_by_category(category)


def is_model_categorized(model_id: str) -> bool:
    """Check if a model is categorized"""
    return model_id in MODEL_CATEGORIZATION

