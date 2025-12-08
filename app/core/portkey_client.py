"""
Portkey AI Integration
Integrates Portkey SDK for observability and request tracking
"""

from typing import Optional, Dict, Any, Callable, Awaitable
from app.utils.logger import Logger

# Make Portkey optional
try:
    from portkey import Portkey
    PORTKEY_AVAILABLE = True
except ImportError:
    PORTKEY_AVAILABLE = False
    Portkey = None


class PortkeyClient:
    """Portkey AI client wrapper"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        environment: str = "development",
        virtual_key: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.logger = Logger("PortkeyClient")
        self.api_key = api_key
        self.environment = environment
        self.virtual_key = virtual_key
        self.config = config or {}
        self.enabled = bool(api_key)

        if self.enabled:
            if not PORTKEY_AVAILABLE:
                self.logger.warn("Portkey SDK not installed. Install with: pip install portkey-ai")
                self.enabled = False
            else:
                try:
                    # Initialize Portkey
                    self.portkey = Portkey(
                        api_key=api_key,
                        environment=environment,
                        virtual_key=virtual_key,
                        **self.config
                    )
                    self.logger.info("Portkey client initialized")
                except Exception as e:
                    self.logger.error(f"Failed to initialize Portkey: {str(e)}")
                    self.enabled = False
        else:
            self.logger.info("Portkey is disabled (no API key provided)")

    async def track_completion(
        self,
        request: Any,
        completion_fn: Callable[[], Awaitable[Any]]
    ) -> Any:
        """Track a completion request with Portkey"""
        if not self.enabled:
            return await completion_fn()

        # Execute completion function once
        response = await completion_fn()
        
        # Attempt Portkey tracking (non-blocking, failures don't affect response)
        # Portkey tracking is typically done via callbacks in LiteLLM
        # For direct tracking, we wrap the completion
        try:
            # Log to Portkey (if needed for custom tracking)
            # Portkey is usually integrated via LiteLLM callbacks
            # If tracking fails, we still return the successful response
            pass  # Portkey tracking happens via LiteLLM callbacks
        except Exception as e:
            error_context = create_error_context(
                error_type="PORTKEY_TRACKING_ERROR",
                message=f"Portkey tracking failed: {str(e)}",
                original_exception=e
            )
            self.logger.error(
                f"Portkey tracking failed: {str(e)}",
                meta=error_context.to_dict()
            )
            # Don't retry completion - just log the tracking failure
        
        return response

    def get_cost_analytics(self, time_range: Optional[str] = None) -> Dict[str, Any]:
        """Get cost analytics from Portkey"""
        if not self.enabled:
            return {}

        try:
            # Portkey SDK methods for analytics
            # This would need to be implemented based on Portkey SDK API
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get cost analytics: {str(e)}")
            return {}

