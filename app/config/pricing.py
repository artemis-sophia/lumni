"""
Pricing Configuration and Calculator
Complete model catalog with pricing information (cost per million tokens).
"""

from typing import Optional, List
from dataclasses import dataclass


@dataclass
class ModelPricing:
    """Model pricing information"""
    provider: str
    model: str
    input_cost_per_million: float  # Cost per million input tokens
    output_cost_per_million: float  # Cost per million output tokens
    notes: Optional[str] = None


# Pricing configurations for all models
MODEL_PRICING: List[ModelPricing] = [
    # GitHub Models API (Free with GitHub Pro account)
    # OpenAI Models
    ModelPricing('github-copilot', 'openai/gpt-4o', 0.00, 0.00, 'Free with GitHub Pro account'),
    ModelPricing('github-copilot', 'openai/gpt-4-turbo', 0.00, 0.00, 'Free with GitHub Pro account'),
    ModelPricing('github-copilot', 'openai/gpt-3.5-turbo', 0.00, 0.00, 'Free with GitHub Pro account'),
    ModelPricing('github-copilot', 'openai/o1', 0.00, 0.00, 'Free with GitHub Pro account'),
    # Cohere Models
    ModelPricing('github-copilot', 'cohere/cohere-command-a', 0.00, 0.00, 'Free with GitHub Pro account'),
    ModelPricing('github-copilot', 'cohere/cohere-command-r-08-2024', 0.00, 0.00, 'Free with GitHub Pro account'),
    ModelPricing('github-copilot', 'cohere/cohere-command-r-plus-08-2024', 0.00, 0.00, 'Free with GitHub Pro account'),
    # DeepSeek Models
    ModelPricing('github-copilot', 'deepseek/deepseek-r1', 0.00, 0.00, 'Free with GitHub Pro account'),
    ModelPricing('github-copilot', 'deepseek/deepseek-r1-0528', 0.00, 0.00, 'Free with GitHub Pro account'),
    ModelPricing('github-copilot', 'deepseek/deepseek-v3-0324', 0.00, 0.00, 'Free with GitHub Pro account'),
    # Meta Vision Models
    ModelPricing('github-copilot', 'meta/llama-3.2-11b-vision-instruct', 0.00, 0.00, 'Free with GitHub Pro account'),
    ModelPricing('github-copilot', 'meta/llama-3.2-90b-vision-instruct', 0.00, 0.00, 'Free with GitHub Pro account'),

    # Groq (Free tier, no direct pricing)
    ModelPricing('groq', 'llama-3.1-8b-instant', 0.00, 0.00, 'Free tier available'),
    ModelPricing('groq', 'llama-3.3-70b-versatile', 0.00, 0.00, 'Free tier available'),
    ModelPricing('groq', 'meta-llama/llama-4-maverick-17b-128e-instruct', 0.00, 0.00, 'Free tier available - Preview model'),
    ModelPricing('groq', 'meta-llama/llama-4-scout-17b-16e-instruct', 0.00, 0.00, 'Free tier available - Preview model'),

    # DeepSeek
    ModelPricing('deepseek', 'deepseek-chat', 0.27, 1.10, 'V3 model. Off-peak pricing available (75% discount)'),
    ModelPricing('deepseek', 'deepseek-coder', 0.27, 1.10, 'Code-optimized. Off-peak pricing available'),
    ModelPricing('deepseek', 'deepseek-reasoner', 0.55, 2.19, 'R1 reasoning model. Off-peak pricing available'),

    # OpenRouter
    ModelPricing('openrouter', 'meta-llama/llama-3-8b-instruct', 0.05, 0.15),
    ModelPricing('openrouter', 'meta-llama/llama-3-70b-instruct', 0.59, 0.79),
    ModelPricing('openrouter', 'mistralai/mistral-7b-instruct', 0.20, 0.60),
    ModelPricing('openrouter', 'anthropic/claude-3-haiku', 0.80, 4.00),
    ModelPricing('openrouter', 'openai/gpt-3.5-turbo', 0.50, 1.50),
    ModelPricing('openrouter', 'google/gemini-pro', 0.10, 0.40),
    ModelPricing('openrouter', 'openai/gpt-4', 30.00, 60.00),
    ModelPricing('openrouter', 'openai/gpt-4-turbo', 10.00, 30.00),
    ModelPricing('openrouter', 'anthropic/claude-3-sonnet', 3.00, 15.00),
    ModelPricing('openrouter', 'anthropic/claude-3-opus', 15.00, 75.00),
    ModelPricing('openrouter', 'mistralai/mistral-medium', 2.00, 6.00),

    # Google Gemini
    # Flash Models
    ModelPricing('gemini', 'gemini-2.0-flash-exp', 0.10, 0.40, 'Experimental model'),
    ModelPricing('gemini', 'gemini-2.0-flash', 0.10, 0.40),
    ModelPricing('gemini', 'gemini-2.0-flash-lite', 0.10, 0.40),
    ModelPricing('gemini', 'gemini-2.5-flash', 0.10, 0.40),
    ModelPricing('gemini', 'gemini-flash-latest', 0.10, 0.40),
    # Pro Models
    ModelPricing('gemini', 'gemini-2.5-pro', 1.25, 5.00, 'Latest generation Pro model'),
    ModelPricing('gemini', 'gemini-pro-latest', 1.25, 5.00, 'Latest Pro model alias'),
    # Note: gemini-2.0-pro and gemini-2.0-pro-exp do not exist (tested and confirmed)
    # Retired models (kept for reference)
    ModelPricing('gemini', 'gemini-1.5-flash', 0.07, 0.30, 'Retired December 2025'),
    ModelPricing('gemini', 'gemini-1.5-pro', 1.25, 5.00, 'Retired December 2025'),
    ModelPricing('gemini', 'gemini-1.5-pro-latest', 1.25, 5.00, 'Retired December 2025'),

    # Mistral AI
    ModelPricing('mistral', 'mistral-tiny', 0.20, 0.60),
    ModelPricing('mistral', 'mistral-7b-instruct', 0.20, 0.60),
    ModelPricing('mistral', 'mistral-small', 2.00, 6.00),
    ModelPricing('mistral', 'mistral-medium', 2.00, 6.00),
    ModelPricing('mistral', 'mistral-large-latest', 2.00, 6.00),

    # Codestral
    ModelPricing('codestral', 'codestral-latest', 0.20, 0.60, 'Code generation model'),
    ModelPricing('codestral', 'codestral-mamba-latest', 0.20, 0.60, 'Mamba architecture variant'),
]


def calculate_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    """Calculate cost for a request"""
    pricing = get_model_pricing(provider, model)
    if not pricing:
        return 0.0  # Unknown pricing, assume free

    input_cost = (input_tokens / 1_000_000) * pricing.input_cost_per_million
    output_cost = (output_tokens / 1_000_000) * pricing.output_cost_per_million

    return input_cost + output_cost


def get_model_pricing(provider: str, model: str) -> Optional[ModelPricing]:
    """Get pricing for a specific model"""
    for pricing in MODEL_PRICING:
        if pricing.provider == provider and pricing.model == model:
            return pricing
    return None


def get_provider_pricing(provider: str) -> List[ModelPricing]:
    """Get all pricing for a provider"""
    return [p for p in MODEL_PRICING if p.provider == provider]


def get_cheapest_model(
    category: str,
    providers: Optional[List[str]] = None
) -> Optional[ModelPricing]:
    """Get cheapest model in a category"""
    filtered = MODEL_PRICING
    if providers:
        filtered = [p for p in filtered if p.provider in providers]

    if not filtered:
        return None

    # Calculate average cost (input + output) / 2
    return min(
        filtered,
        key=lambda p: (p.input_cost_per_million + p.output_cost_per_million) / 2
    )


def estimate_cost(
    provider: str,
    model: str,
    estimated_input_tokens: int,
    estimated_output_tokens: int
) -> float:
    """Estimate cost for a request based on average token usage"""
    return calculate_cost(provider, model, estimated_input_tokens, estimated_output_tokens)

