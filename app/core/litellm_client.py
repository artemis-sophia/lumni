"""
LiteLLM Integration
Wraps litellm.completion() with proxy support and error handling
"""

import os
from typing import Optional, Dict, Any, List
import litellm
from litellm import completion
from app.api.v1.schemas import ChatRequest, ChatResponse, Message, Choice, Usage
from app.utils.logger import Logger
from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from app.utils.exceptions import ProviderError, RateLimitError


class LiteLLMClient:
    """LiteLLM client wrapper"""

    def __init__(self, config_path: str = "./litellm_config.yaml"):
        self.logger = Logger("LiteLLMClient")
        self.config_path = config_path
        
        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(
            "litellm",
            CircuitBreakerConfig(
                failure_threshold=5,
                timeout=60,
                expected_exception=Exception
            )
        )
        
        # Initialize LiteLLM
        if os.path.exists(config_path):
            litellm.config_path = config_path
            self.logger.info(f"Loaded LiteLLM config from {config_path}")
        else:
            self.logger.warn(f"LiteLLM config file not found: {config_path}")

    @retry_with_backoff(max_attempts=3, initial_delay=1.0, max_delay=60.0)
    async def chat(
        self,
        request: ChatRequest,
        proxy: Optional[str] = None
    ) -> ChatResponse:
        """Execute chat completion via LiteLLM with retry and circuit breaker"""
        try:
            # Use circuit breaker to protect against cascading failures
            return await self.circuit_breaker.call(self._execute_chat, request, proxy)
        except Exception as e:
            # Transform specific errors
            if "rate limit" in str(e).lower() or "429" in str(e):
                raise RateLimitError(
                    request.provider or "unknown",
                    request.model,
                    {"error": str(e)}
                )
            raise ProviderError(
                f"LiteLLM completion failed: {str(e)}",
                request.provider or "unknown",
                {"error": str(e), "model": request.model}
            )

    async def _execute_chat(
        self,
        request: ChatRequest,
        proxy: Optional[str] = None
    ) -> ChatResponse:
        """Internal chat execution method"""
        try:
            # Prepare messages
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]

            # Prepare completion parameters
            completion_params: Dict[str, Any] = {
                "model": request.model or litellm.default_model or "gpt-3.5-turbo",
                "messages": messages,
            }

            if request.temperature is not None:
                completion_params["temperature"] = request.temperature
            if request.max_tokens is not None:
                completion_params["max_tokens"] = request.max_tokens
            if request.stream:
                completion_params["stream"] = request.stream

            # Configure proxy if provided
            if proxy:
                # LiteLLM supports proxy via environment or extra_params
                # For HTTP proxies, we can set it in the request
                completion_params["extra_headers"] = {
                    "http_proxy": proxy,
                    "https_proxy": proxy,
                }
                # Also set environment variable for httpx
                os.environ["HTTP_PROXY"] = proxy
                os.environ["HTTPS_PROXY"] = proxy

            # Execute completion
            response = await litellm.acompletion(**completion_params)

            # Transform response to our schema
            return self._transform_response(response, request.provider or "unknown")

        except Exception as e:
            self.logger.error(f"LiteLLM completion failed: {str(e)}")
            raise

    def _transform_response(
        self,
        response: Any,
        provider: str
    ) -> ChatResponse:
        """Transform LiteLLM response to ChatResponse"""
        choices = [
            Choice(
                index=choice.index,
                message=Message(
                    role=choice.message.role,
                    content=choice.message.content
                ),
                finish_reason=choice.finish_reason or "stop"
            )
            for choice in response.choices
        ]

        usage = Usage(
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0
        )

        return ChatResponse(
            id=response.id,
            object=response.object,
            created=response.created,
            model=response.model,
            choices=choices,
            usage=usage,
            provider=provider
        )

    async def get_available_models(self) -> List[str]:
        """Get list of available models from LiteLLM"""
        try:
            # LiteLLM can list models from config
            # This is a simplified version - you may need to parse litellm_config.yaml
            models = []
            # In a real implementation, you'd parse the config file or use LiteLLM's model list
            return models
        except Exception as e:
            self.logger.error(f"Failed to get available models: {str(e)}")
            return []

