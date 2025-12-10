"""
LiteLLM Integration
Wraps litellm.completion() with proxy support and error handling
"""

import os
import yaml
from contextvars import ContextVar
from typing import Optional, Dict, Any, List
import litellm
from litellm import completion
from app.api.v1.schemas import ChatRequest, ChatResponse, Message, Choice, Usage
from app.utils.logger import Logger
from app.core.retry import retry_with_backoff
from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from app.utils.exceptions import ProviderError, RateLimitError

# Default timeout for API calls (30 seconds)
DEFAULT_TIMEOUT = float(os.getenv("LLM_REQUEST_TIMEOUT", "30.0"))

# Context variables for thread-local proxy settings
_proxy_context: ContextVar[Optional[str]] = ContextVar('proxy', default=None)


class LiteLLMClient:
    """LiteLLM client wrapper"""

    def __init__(self, config_path: str = "./litellm_config.yaml", request_timeout: Optional[float] = None):
        self.logger = Logger("LiteLLMClient")
        self.config_path = config_path
        self.request_timeout = request_timeout or DEFAULT_TIMEOUT
        
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
        
        # Cache for config data to avoid repeated file reads
        self._config_cache: Optional[Dict[str, Any]] = None

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

    def _load_config(self) -> Dict[str, Any]:
        """Load and cache config file"""
        if self._config_cache is None:
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, "r") as f:
                        self._config_cache = yaml.safe_load(f) or {}
                except Exception as e:
                    self.logger.warn(f"Failed to load config file: {str(e)}")
                    self._config_cache = {}
            else:
                self._config_cache = {}
        return self._config_cache

    def _get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get model configuration from config file by model_name"""
        config = self._load_config()
        model_list = config.get("model_list", [])
        
        for model_config in model_list:
            if model_config.get("model_name") == model_name:
                return model_config.get("litellm_params", {})
        
        return None

    def _needs_explicit_config(self, model: Optional[str], provider: Optional[str]) -> bool:
        """Check if model needs explicit config loading (GitHub or Gemini models)"""
        if not model:
            return False
        
        # Check by model name prefix
        if model.startswith("github-") or model.startswith("gemini-"):
            return True
        
        # Check by provider
        if provider in ("github-copilot", "github", "gemini"):
            return True
        
        return False

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
            model_name = request.model or litellm.default_model or "gpt-3.5-turbo"
            completion_params: Dict[str, Any] = {
                "model": model_name,
                "messages": messages,
            }

            if request.temperature is not None:
                completion_params["temperature"] = request.temperature
            if request.max_tokens is not None:
                completion_params["max_tokens"] = request.max_tokens
            if request.stream:
                completion_params["stream"] = request.stream

            # For GitHub and Gemini models, explicitly load config to get api_base and api_key
            # This is necessary because LiteLLM may override api_base when model name matches
            # a known provider (e.g., "openai/gpt-5" routes to OpenAI instead of GitHub)
            if self._needs_explicit_config(model_name, request.provider):
                model_config = self._get_model_config(model_name)
                if model_config:
                    # Use the actual model ID from config (ensures gemini/ prefix for Gemini)
                    if "model" in model_config:
                        completion_params["model"] = model_config["model"]
                    
                    # Handle api_base for GitHub models (required to route to GitHub, not default provider)
                    if "api_base" in model_config:
                        completion_params["api_base"] = model_config["api_base"]
                        self.logger.debug(f"Using explicit api_base for {model_name}: {model_config['api_base']}")
                    
                    # Handle api_key from config
                    if "api_key" in model_config:
                        api_key_env = model_config["api_key"].replace("os.environ/", "")
                        api_key_value = os.getenv(api_key_env)
                        if api_key_value:
                            completion_params["api_key"] = api_key_value
                        else:
                            self.logger.warn(f"API key not found in environment: {api_key_env}")

            # Configure proxy if provided (using contextvars for thread-local storage)
            if proxy:
                # Set proxy in context variable for this request
                _proxy_context.set(proxy)
                # LiteLLM supports proxy via environment or extra_params
                # For HTTP proxies, we can set it in the request
                completion_params["extra_headers"] = {
                    "http_proxy": proxy,
                    "https_proxy": proxy,
                }
                # Note: We avoid setting os.environ to prevent global state pollution
                # LiteLLM/httpx will use the extra_headers for proxy configuration

            # Execute completion with timeout
            # LiteLLM uses httpx internally, set timeout via litellm settings
            # Note: LiteLLM timeout is set globally, not per-request
            # We set it here for this request context
            import asyncio
            original_timeout = getattr(litellm, 'request_timeout', None)
            try:
                litellm.request_timeout = self.request_timeout
                # Wrap in asyncio.wait_for for additional timeout protection
                response = await asyncio.wait_for(
                    litellm.acompletion(**completion_params),
                    timeout=self.request_timeout
                )
            except asyncio.TimeoutError:
                raise ProviderError(
                    f"Request timeout after {self.request_timeout} seconds",
                    request.provider or "unknown",
                    {"timeout": self.request_timeout, "model": request.model}
                )
            finally:
                if original_timeout is not None:
                    litellm.request_timeout = original_timeout

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

