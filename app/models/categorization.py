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
    # Note: OpenAI direct models removed - all are pay-as-you-go (not free)
    # Use GitHub Models API for free OpenAI models (requires GitHub Pro account)

    # Groq Models (Free Tier - No Credits Required)
    # All Groq models are free tier with rate limits - no credits needed
    # Note: Several models have been decommissioned - only working models are included
    'llama-3.1-8b-instant': ModelMetadata('groq', 'llama-3.1-8b-instant', 'fast'),
    'llama-3.3-70b-versatile': ModelMetadata('groq', 'llama-3.3-70b-versatile', 'powerful'),
    # Llama 4 Models (Preview - Free Tier Available)
    'llama-4-maverick': ModelMetadata('groq', 'meta-llama/llama-4-maverick-17b-128e-instruct', 'powerful'),
    'llama-4-scout': ModelMetadata('groq', 'meta-llama/llama-4-scout-17b-16e-instruct', 'powerful'),

    # GitHub Models API (Free for GitHub Pro/Education - No Credits Required)
    # All models are free with GitHub Pro account or GitHub Education Pack
    # Note: Only models verified to exist in the GitHub Models API catalog are included
    # WARNING: GitHub Models API has compatibility issues with LiteLLM Router - use direct HTTP calls
    
    # GitHub Models - New naming convention (github/provider-model)
    # OpenAI Models via GitHub
    'github/openai-gpt-5': ModelMetadata('github-copilot', 'openai/gpt-5', 'powerful'),
    'github/openai-gpt-5-chat': ModelMetadata('github-copilot', 'openai/gpt-5-chat', 'powerful'),
    'github/openai-gpt-5-mini': ModelMetadata('github-copilot', 'openai/gpt-5-mini', 'fast'),
    'github/openai-gpt-5-nano': ModelMetadata('github-copilot', 'openai/gpt-5-nano', 'fast'),
    'github/openai-gpt-4.1': ModelMetadata('github-copilot', 'openai/gpt-4.1', 'powerful'),
    'github/openai-gpt-4.1-mini': ModelMetadata('github-copilot', 'openai/gpt-4.1-mini', 'fast'),
    'github/openai-gpt-4.1-nano': ModelMetadata('github-copilot', 'openai/gpt-4.1-nano', 'fast'),
    'github/openai-gpt-4o': ModelMetadata('github-copilot', 'openai/gpt-4o', 'powerful'),
    'github/openai-gpt-4o-mini': ModelMetadata('github-copilot', 'openai/gpt-4o-mini', 'fast'),
    'github/openai-o1': ModelMetadata('github-copilot', 'openai/o1', 'powerful'),
    'github/openai-o3': ModelMetadata('github-copilot', 'openai/o3', 'powerful'),
    'github/openai-o3-mini': ModelMetadata('github-copilot', 'openai/o3-mini', 'powerful'),
    'github/openai-o4-mini': ModelMetadata('github-copilot', 'openai/o4-mini', 'powerful'),
    
    # Meta Models via GitHub
    'github/meta-llama-3.3-70b': ModelMetadata('github-copilot', 'meta/llama-3.3-70b-instruct', 'powerful'),
    'github/meta-llama-3.2-11b-vision': ModelMetadata('github-copilot', 'meta/llama-3.2-11b-vision-instruct', 'powerful'),
    'github/meta-llama-3.2-90b-vision': ModelMetadata('github-copilot', 'meta/llama-3.2-90b-vision-instruct', 'powerful'),
    'github/meta-llama-4-maverick': ModelMetadata('github-copilot', 'meta/llama-4-maverick-17b-128e-instruct-fp8', 'powerful'),
    'github/meta-llama-4-scout': ModelMetadata('github-copilot', 'meta/llama-4-scout-17b-16e-instruct', 'powerful'),
    
    # Microsoft Models via GitHub
    'github/microsoft-phi-4': ModelMetadata('github-copilot', 'microsoft/phi-4', 'powerful'),
    'github/microsoft-phi-4-mini': ModelMetadata('github-copilot', 'microsoft/phi-4-mini-instruct', 'fast'),
    
    # xAI Models via GitHub
    'github/xai-grok-3': ModelMetadata('github-copilot', 'xai/grok-3', 'powerful'),
    'github/xai-grok-3-mini': ModelMetadata('github-copilot', 'xai/grok-3-mini', 'fast'),
    
    # Cohere Models via GitHub
    'github/cohere-command-a': ModelMetadata('github-copilot', 'cohere/cohere-command-a', 'powerful'),
    'github/cohere-command-r': ModelMetadata('github-copilot', 'cohere/cohere-command-r-08-2024', 'powerful'),
    'github/cohere-command-r-plus': ModelMetadata('github-copilot', 'cohere/cohere-command-r-plus-08-2024', 'powerful'),
    
    # DeepSeek Models via GitHub
    'github/deepseek-r1': ModelMetadata('github-copilot', 'deepseek/deepseek-r1', 'powerful'),
    'github/deepseek-r1-0528': ModelMetadata('github-copilot', 'deepseek/deepseek-r1-0528', 'powerful'),
    'github/deepseek-v3': ModelMetadata('github-copilot', 'deepseek/deepseek-v3-0324', 'powerful'),
    
    # Legacy naming convention (backward compatibility)
    # OpenAI Models via GitHub
    'openai/gpt-5': ModelMetadata('github-copilot', 'openai/gpt-5', 'powerful'),
    'openai/gpt-5-chat': ModelMetadata('github-copilot', 'openai/gpt-5-chat', 'powerful'),
    'openai/gpt-5-mini': ModelMetadata('github-copilot', 'openai/gpt-5-mini', 'fast'),
    'openai/gpt-5-nano': ModelMetadata('github-copilot', 'openai/gpt-5-nano', 'fast'),
    'openai/gpt-4.1': ModelMetadata('github-copilot', 'openai/gpt-4.1', 'powerful'),
    'openai/gpt-4.1-mini': ModelMetadata('github-copilot', 'openai/gpt-4.1-mini', 'fast'),
    'openai/gpt-4.1-nano': ModelMetadata('github-copilot', 'openai/gpt-4.1-nano', 'fast'),
    'openai/gpt-4o': ModelMetadata('github-copilot', 'openai/gpt-4o', 'powerful'),
    'openai/gpt-4o-mini': ModelMetadata('github-copilot', 'openai/gpt-4o-mini', 'fast'),
    'openai/o1': ModelMetadata('github-copilot', 'openai/o1', 'powerful'),
    'openai/o3': ModelMetadata('github-copilot', 'openai/o3', 'powerful'),
    'openai/o3-mini': ModelMetadata('github-copilot', 'openai/o3-mini', 'powerful'),
    'openai/o4-mini': ModelMetadata('github-copilot', 'openai/o4-mini', 'powerful'),
    
    # Meta Models via GitHub
    'meta/llama-3.3-70b-instruct': ModelMetadata('github-copilot', 'meta/llama-3.3-70b-instruct', 'powerful'),
    'meta/llama-3.2-11b-vision-instruct': ModelMetadata('github-copilot', 'meta/llama-3.2-11b-vision-instruct', 'powerful'),
    'meta/llama-3.2-90b-vision-instruct': ModelMetadata('github-copilot', 'meta/llama-3.2-90b-vision-instruct', 'powerful'),
    'meta/llama-4-maverick-17b-128e-instruct-fp8': ModelMetadata('github-copilot', 'meta/llama-4-maverick-17b-128e-instruct-fp8', 'powerful'),
    'meta/llama-4-scout-17b-16e-instruct': ModelMetadata('github-copilot', 'meta/llama-4-scout-17b-16e-instruct', 'powerful'),
    
    # Microsoft Models via GitHub
    'microsoft/phi-4': ModelMetadata('github-copilot', 'microsoft/phi-4', 'powerful'),
    'microsoft/phi-4-mini-instruct': ModelMetadata('github-copilot', 'microsoft/phi-4-mini-instruct', 'fast'),
    
    # xAI Models via GitHub
    'xai/grok-3': ModelMetadata('github-copilot', 'xai/grok-3', 'powerful'),
    'xai/grok-3-mini': ModelMetadata('github-copilot', 'xai/grok-3-mini', 'fast'),
    
    # Cohere Models via GitHub
    'cohere/cohere-command-a': ModelMetadata('github-copilot', 'cohere/cohere-command-a', 'powerful'),
    'cohere/cohere-command-r-08-2024': ModelMetadata('github-copilot', 'cohere/cohere-command-r-08-2024', 'powerful'),
    'cohere/cohere-command-r-plus-08-2024': ModelMetadata('github-copilot', 'cohere/cohere-command-r-plus-08-2024', 'powerful'),
    
    # DeepSeek Models via GitHub
    'deepseek/deepseek-r1': ModelMetadata('github-copilot', 'deepseek/deepseek-r1', 'powerful'),
    'deepseek/deepseek-r1-0528': ModelMetadata('github-copilot', 'deepseek/deepseek-r1-0528', 'powerful'),
    'deepseek/deepseek-v3-0324': ModelMetadata('github-copilot', 'deepseek/deepseek-v3-0324', 'powerful'),
    # Use OpenRouter for free DeepSeek models (deepseek/deepseek-chat:free)

    # OpenRouter (Free Tier - No Credits Required)
    # Note: OpenRouter free models work WITHOUT credits (50 requests/day limit)
    # With $10+ credits: 1,000 requests/day limit (increased, but not required)
    # Free models (credits not consumed when using free models):
    'meta-llama/llama-3.1-8b-instruct': ModelMetadata('openrouter', 'meta-llama/llama-3.1-8b-instruct', 'fast'),
    'meta-llama/llama-3.2-11b-instruct': ModelMetadata('openrouter', 'meta-llama/llama-3.2-11b-instruct', 'fast'),
    'meta-llama/llama-3.2-90b-instruct': ModelMetadata('openrouter', 'meta-llama/llama-3.2-90b-instruct', 'powerful'),
    'microsoft/phi-3-mini-4k-instruct': ModelMetadata('openrouter', 'microsoft/phi-3-mini-4k-instruct', 'fast'),
    'google/gemini-flash-1.5': ModelMetadata('openrouter', 'google/gemini-flash-1.5', 'fast'),
    'deepseek/deepseek-chat:free': ModelMetadata('openrouter', 'deepseek/deepseek-chat:free', 'fast'),
    'mistralai/mistral-small': ModelMetadata('openrouter', 'mistralai/mistral-small', 'powerful'),
    'qwen/qwen-2.5-7b-instruct': ModelMetadata('openrouter', 'qwen/qwen-2.5-7b-instruct', 'fast'),

    # Google Gemini (Free Tier - No Credits Required)
    # All Gemini models are free with rate limits - no credits needed
    # Note: Gemini 1.5 models were retired as of December 2025 - use Gemini 2.0/2.5 models instead
    # Direct API testing confirmed these models work (some may be rate-limited)
    
    # Gemini 2.5 Models (Latest Generation)
    'gemini-2.5-flash': ModelMetadata('gemini', 'gemini-2.5-flash', 'fast'),
    'gemini-flash-latest': ModelMetadata('gemini', 'gemini-flash-latest', 'fast'),
    
    # Gemini 2.0 Models (Current Generation)
    'gemini-2.0-flash-exp': ModelMetadata('gemini', 'gemini-2.0-flash-exp', 'fast'),
    'gemini-2.0-flash': ModelMetadata('gemini', 'gemini-2.0-flash', 'fast'),
    'gemini-2.0-flash-lite': ModelMetadata('gemini', 'gemini-2.0-flash-lite', 'fast'),
    
    # Gemini Pro Models (Powerful - may be rate-limited)
    'gemini-2.5-pro': ModelMetadata('gemini', 'gemini-2.5-pro', 'powerful'),
    'gemini-pro-latest': ModelMetadata('gemini', 'gemini-pro-latest', 'powerful'),
    # Note: gemini-2.0-pro and gemini-2.0-pro-exp do not exist (tested and confirmed)
    
    # Note: Gemini 1.5 models (flash, pro) are retired - migration to 2.0/2.5 recommended

    # Mistral
    'mistral-tiny': ModelMetadata('mistral', 'mistral-tiny', 'fast'),
    'mistral-7b-instruct': ModelMetadata('mistral', 'mistral-7b-instruct', 'fast'),
    'mistral-small-latest': ModelMetadata('mistral', 'mistral-small-latest', 'powerful'),
    'mistral-medium-latest': ModelMetadata('mistral', 'mistral-medium-latest', 'powerful'),
    'mistral-large-latest': ModelMetadata('mistral', 'mistral-large-latest', 'powerful'),
    'pixtral-12b': ModelMetadata('mistral', 'pixtral-12b', 'powerful'),

    # Codestral
    'codestral-latest': ModelMetadata('codestral', 'codestral-latest', 'fast'),
    # Note: codestral-mamba-latest does not exist - only codestral-latest is available
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

