"""
Circuit Breaker Pattern
Wraps circuitbreaker library to maintain existing API
"""

from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass
import asyncio
from circuitbreaker import CircuitBreaker as BaseCircuitBreaker
from app.utils.logger import Logger


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5  # Open circuit after N failures
    success_threshold: int = 2  # Close circuit after N successes (half-open)
    timeout: int = 60  # Seconds before trying half-open
    expected_exception: type = Exception


class CircuitBreaker:
    """Circuit breaker implementation using circuitbreaker library"""

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.logger = Logger(f"CircuitBreaker:{name}")
        
        # Initialize underlying circuit breaker
        # Note: circuitbreaker uses failure_threshold and recovery_timeout
        # success_threshold is handled internally by circuitbreaker
        self._breaker = BaseCircuitBreaker(
            failure_threshold=self.config.failure_threshold,
            recovery_timeout=self.config.timeout,
            expected_exception=self.config.expected_exception,
            name=name
        )

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection
        
        The circuit breaker library handles state checks internally.
        If the circuit is open, it will raise CircuitBreakerError automatically.
        """
        try:
            # Use circuitbreaker's async call method (handles state internally)
            if asyncio.iscoroutinefunction(func):
                return await self._breaker.call_async(func, *args, **kwargs)
            else:
                # For sync functions, run in executor
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None,
                    lambda: self._breaker.call(func, *args, **kwargs)
                )
        except Exception as e:
            # Re-raise the exception (circuitbreaker will track it)
            # If circuit is open, circuitbreaker will raise CircuitBreakerError
            raise

    def get_state(self) -> CircuitState:
        """Get current circuit breaker state"""
        # Map circuitbreaker states to our CircuitState enum
        if self._breaker.opened:
            return CircuitState.OPEN
        elif self._breaker.closed:
            return CircuitState.CLOSED
        else:
            # circuitbreaker doesn't explicitly expose half-open, but we can infer it
            # If not opened and not closed, it's likely in recovery (half-open)
            return CircuitState.HALF_OPEN

    def is_open(self) -> bool:
        """Check if circuit is open"""
        return self._breaker.opened


class CircuitBreakerOpenError(CircuitBreakerError):
    """Raised when circuit breaker is open"""
    pass
