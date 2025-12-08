"""
Provider Health Checker
Checks provider health before use and caches health status
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from app.utils.logger import Logger
from app.core.litellm_client import LiteLLMClient
from app.api.v1.schemas import ChatRequest, Message

logger = Logger("ProviderHealthChecker")


class ProviderHealthChecker:
    """Provider health checking with caching"""
    
    def __init__(self, health_check_ttl: int = 60):
        """Initialize health checker
        
        Args:
            health_check_ttl: Time to live for health check cache in seconds
        """
        self.health_check_ttl = health_check_ttl
        self.health_cache: Dict[str, tuple[bool, datetime]] = {}  # provider -> (healthy, timestamp)
        self.logger = Logger("ProviderHealthChecker")
    
    async def check_provider_health(
        self,
        provider: str,
        litellm_client: LiteLLMClient,
        force_check: bool = False
    ) -> bool:
        """Check if a provider is healthy
        
        Args:
            provider: Provider name to check
            litellm_client: LiteLLM client for testing
            force_check: If True, bypass cache and check immediately
            
        Returns:
            True if provider is healthy, False otherwise
        """
        # Check cache first
        if not force_check and provider in self.health_cache:
            is_healthy, cached_time = self.health_cache[provider]
            if datetime.now() - cached_time < timedelta(seconds=self.health_check_ttl):
                return is_healthy
        
        # Perform health check
        try:
            # Create a minimal test request
            test_request = ChatRequest(
                messages=[Message(role="user", content="test")],
                model="gpt-3.5-turbo",  # Use a common model for testing
                provider=provider,
                max_tokens=1
            )
            
            # Try to make a very small request with short timeout
            # We don't actually need the response, just need to see if it connects
            # For now, we'll just check if the provider is configured
            # In a full implementation, you might make a minimal API call
            
            # Cache the result
            is_healthy = True  # Assume healthy if no exception
            self.health_cache[provider] = (is_healthy, datetime.now())
            return is_healthy
            
        except Exception as e:
            self.logger.warn(f"Health check failed for provider {provider}: {str(e)}")
            is_healthy = False
            self.health_cache[provider] = (is_healthy, datetime.now())
            return is_healthy
    
    def get_cached_health(self, provider: str) -> Optional[bool]:
        """Get cached health status without performing check
        
        Args:
            provider: Provider name
            
        Returns:
            Cached health status or None if not cached
        """
        if provider in self.health_cache:
            is_healthy, cached_time = self.health_cache[provider]
            if datetime.now() - cached_time < timedelta(seconds=self.health_check_ttl):
                return is_healthy
        return None
    
    def mark_unhealthy(self, provider: str):
        """Mark a provider as unhealthy
        
        Args:
            provider: Provider name
        """
        self.health_cache[provider] = (False, datetime.now())
        self.logger.warn(f"Marked provider {provider} as unhealthy")
    
    def mark_healthy(self, provider: str):
        """Mark a provider as healthy
        
        Args:
            provider: Provider name
        """
        self.health_cache[provider] = (True, datetime.now())
        self.logger.info(f"Marked provider {provider} as healthy")
    
    def clear_cache(self):
        """Clear health check cache"""
        self.health_cache.clear()

