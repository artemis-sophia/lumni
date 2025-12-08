"""
Benchmark-Based Model Selector
Optimization scoring algorithm integrating LiteLLM model selection
"""

from typing import Optional, List, Dict, Any
from app.api.v1.schemas import ChatRequest
from app.models.task_classifier import get_recommended_category
from app.models.categorization import get_models_by_category, get_category_fallback_order
from app.models.benchmarks import get_model_benchmarks, get_fallback_order
from app.config.pricing import get_model_pricing, calculate_cost
from app.config.rate_limits import get_model_rate_limit
from app.core.litellm_client import LiteLLMClient
from app.utils.logger import Logger


class ModelSelectionResult:
    """Model selection result"""
    def __init__(self, provider: str, model: str, reason: str):
        self.provider = provider
        self.model = model
        self.reason = reason


class BenchmarkSelector:
    """Benchmark-based model selector"""

    def __init__(self, litellm_client: LiteLLMClient):
        self.litellm_client = litellm_client
        self.logger = Logger("BenchmarkSelector")

    async def select_model(self, request: ChatRequest) -> ModelSelectionResult:
        """Select the best model for a given request"""
        # If provider and model are explicitly specified, use them
        if request.provider and request.model:
            # Validate OpenRouter only uses free models (requires credits in balance)
            if request.provider == "openrouter":
                free_models = [
                    "meta-llama/llama-3.1-8b-instruct",
                    "microsoft/phi-3-mini-4k-instruct",
                    "google/gemini-flash-1.5",
                    "deepseek/deepseek-chat:free",
                    "openrouter/meta-llama/llama-3.1-8b-instruct",
                    "openrouter/microsoft/phi-3-mini-4k-instruct",
                    "openrouter/google/gemini-flash-1.5",
                    "openrouter/deepseek/deepseek-chat:free"
                ]
                model_check = request.model.replace("openrouter/", "")
                allowed_patterns = [
                    "llama-3.1-8b-instruct",
                    "phi-3-mini-4k-instruct",
                    "gemini-flash-1.5",
                    "deepseek-chat:free"
                ]
                if not any(pattern in model_check for pattern in allowed_patterns):
                    raise ValueError(
                        f"OpenRouter can only use free models (requires credits in balance). "
                        f"Allowed: meta-llama/llama-3.1-8b-instruct, microsoft/phi-3-mini-4k-instruct, "
                        f"google/gemini-flash-1.5, deepseek/deepseek-chat:free. Got: {request.model}"
                    )
            
            # Format model name with provider prefix for LiteLLM
            model_name = f"{request.provider}/{request.model}" if "/" not in request.model else request.model
            return ModelSelectionResult(
                provider=request.provider,
                model=model_name,
                reason=f"Explicitly specified provider {request.provider} and model {request.model}"
            )

        # If only model is specified, find a provider that supports it
        if request.model:
            return await self._find_provider_for_model(request.model)

        # If only provider is specified, use default model for that provider
        if request.provider:
            models = await self._get_provider_models(request.provider)
            if models:
                return ModelSelectionResult(
                    provider=request.provider,
                    model=models[0],
                    reason=f"Using default model for provider {request.provider}"
                )
            raise ValueError(f"No models available for provider {request.provider}")

        # Auto-select based on task type
        task_type = request.task_type or get_recommended_category(request)
        return await self._select_model_by_task_type(task_type)

    async def _find_provider_for_model(self, model: str) -> ModelSelectionResult:
        """Find a provider that supports the given model"""
        # Try to find model in categorization
        from app.models.categorization import MODEL_CATEGORIZATION
        for model_id, metadata in MODEL_CATEGORIZATION.items():
            if model_id == model or metadata.model == model:
                return ModelSelectionResult(
                    provider=metadata.provider,
                    model=model,
                    reason=f"Found provider {metadata.provider} that supports model {model}"
                )

        # Fallback: try to use model directly with LiteLLM
        return ModelSelectionResult(
            provider="unknown",
            model=model,
            reason=f"Using model {model} directly (provider auto-detected by LiteLLM)"
        )

    async def _get_provider_models(self, provider: str) -> List[str]:
        """Get available models for a provider"""
        # This would query LiteLLM or use categorization
        from app.models.categorization import get_models_by_provider
        models = get_models_by_provider(provider)
        return [m.model for m in models]

    async def _select_model_by_task_type(self, task_type: str) -> ModelSelectionResult:
        """Select model based on task type using benchmark optimization"""
        # Get models in category
        category_models = get_models_by_category(task_type)
        if not category_models:
            # Fallback to benchmark-based order
            fallback_order = get_fallback_order(task_type)
            if fallback_order:
                first = fallback_order[0]
                return ModelSelectionResult(
                    provider=first['provider'],
                    model=first['model'],
                    reason=f"Selected {task_type} model based on benchmark fallback order"
                )
            raise ValueError(f"No models available for task type {task_type}")

        # Score and rank models
        scored_models = []
        for model_meta in category_models:
            score = await self._calculate_optimization_score(
                model_meta.provider,
                model_meta.model,
                task_type
            )
            scored_models.append((score, model_meta))

        # Sort by score (higher is better)
        scored_models.sort(key=lambda x: x[0], reverse=True)

        if scored_models:
            best_score, best_model = scored_models[0]
            # Format model name with provider prefix for LiteLLM
            model_name = f"{best_model.provider}/{best_model.model}" if "/" not in best_model.model else best_model.model
            return ModelSelectionResult(
                provider=best_model.provider,
                model=model_name,
                reason=f"Selected {task_type} model with optimization score {best_score:.2f}"
            )

        raise ValueError(f"No models available for task type {task_type}")

    async def _calculate_optimization_score(
        self,
        provider: str,
        model: str,
        task_type: str
    ) -> float:
        """Calculate optimization score for a model"""
        # Get benchmark data
        benchmarks = get_model_benchmarks(provider, model)
        
        # Get pricing
        pricing = get_model_pricing(provider, model)
        
        # Get rate limits
        rate_limit = get_model_rate_limit(provider, model)

        # Calculate weighted score
        # Weights from config (default values)
        weights = {
            'benchmark_ranking': 0.3,
            'benchmark_score': 0.2,
            'rate_limit_availability': 0.2,
            'provider_priority': 0.1,
            'recent_usage': 0.1,
            'cost_efficiency': 0.1,
        }

        score = 0.0

        # Benchmark ranking (lower is better, so invert)
        if benchmarks:
            ranking_score = 1.0 / (benchmarks.ranking or 10)
            score += ranking_score * weights['benchmark_ranking']

            # Benchmark score (MMLU, normalized to 0-1)
            if benchmarks.mmlu:
                mmlu_score = benchmarks.mmlu / 100.0
                score += mmlu_score * weights['benchmark_score']

        # Rate limit availability
        if rate_limit:
            # Higher rate limits = better availability
            rpm_score = min(rate_limit.requests_per_minute / 1000.0, 1.0)
            score += rpm_score * weights['rate_limit_availability']

        # Cost efficiency (lower cost = higher score)
        if pricing:
            avg_cost = (pricing.input_cost_per_million + pricing.output_cost_per_million) / 2
            # Invert cost (lower cost = higher score)
            cost_score = 1.0 / (avg_cost + 1.0)  # +1 to avoid division by zero
            score += cost_score * weights['cost_efficiency']

        # Provider priority (would come from config, default to 0.5)
        provider_priority = 0.5
        score += provider_priority * weights['provider_priority']

        # Recent usage (would come from usage tracker, default to 0.5)
        recent_usage = 0.5
        score += recent_usage * weights['recent_usage']

        return score

    async def get_all_models(self) -> List[Dict[str, Any]]:
        """Get all available models"""
        from app.models.categorization import MODEL_CATEGORIZATION
        models = []
        for model_id, metadata in MODEL_CATEGORIZATION.items():
            benchmarks = get_model_benchmarks(metadata.provider, metadata.model)
            rate_limit = get_model_rate_limit(metadata.provider, metadata.model)
            
            models.append({
                'provider': metadata.provider,
                'model': metadata.model,
                'category': metadata.category,
                'rate_limits': {
                    'per_minute': rate_limit.requests_per_minute if rate_limit else 0,
                    'per_day': rate_limit.requests_per_day if rate_limit else 0,
                } if rate_limit else None,
                'available': True,
            })
        return models

    async def get_models_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """Get models for a specific provider"""
        all_models = await self.get_all_models()
        return [m for m in all_models if m['provider'] == provider]

