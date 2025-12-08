"""
Circuit Breaker Pattern
Prevents cascading failures by opening circuit after threshold failures
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any, Optional
from dataclasses import dataclass, field
import asyncio
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


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics"""
    failures: int = 0
    successes: int = 0
    last_failure_time: Optional[datetime] = None
    state: CircuitState = CircuitState.CLOSED
    opened_at: Optional[datetime] = None


class CircuitBreaker:
    """Circuit breaker implementation"""

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.stats = CircuitBreakerStats()
        self.logger = Logger(f"CircuitBreaker:{name}")
        self._lock = asyncio.Lock()

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection"""
        async with self._lock:
            # Check if circuit should transition
            await self._check_state_transition()

            # If circuit is open, reject immediately
            if self.stats.state == CircuitState.OPEN:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service unavailable."
                )

        # Execute function
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            await self._record_success()
            return result
        except self.config.expected_exception as e:
            await self._record_failure()
            raise

    async def _check_state_transition(self):
        """Check and update circuit breaker state"""
        now = datetime.now()

        # Transition from OPEN to HALF_OPEN after timeout
        if (
            self.stats.state == CircuitState.OPEN
            and self.stats.opened_at
            and (now - self.stats.opened_at).total_seconds() >= self.config.timeout
        ):
            self.stats.state = CircuitState.HALF_OPEN
            self.stats.successes = 0
            self.logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN")

    async def _record_success(self):
        """Record successful call"""
        async with self._lock:
            if self.stats.state == CircuitState.HALF_OPEN:
                self.stats.successes += 1
                if self.stats.successes >= self.config.success_threshold:
                    self.stats.state = CircuitState.CLOSED
                    self.stats.failures = 0
                    self.stats.successes = 0
                    self.logger.info(f"Circuit breaker '{self.name}' CLOSED (recovered)")
            elif self.stats.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.stats.failures = 0

    async def _record_failure(self):
        """Record failed call"""
        async with self._lock:
            self.stats.failures += 1
            self.stats.last_failure_time = datetime.now()

            if self.stats.state == CircuitState.HALF_OPEN:
                # Any failure in half-open goes back to open
                self.stats.state = CircuitState.OPEN
                self.stats.opened_at = datetime.now()
                self.stats.successes = 0
                self.logger.warn(f"Circuit breaker '{self.name}' OPEN (failed in half-open)")
            elif (
                self.stats.state == CircuitState.CLOSED
                and self.stats.failures >= self.config.failure_threshold
            ):
                self.stats.state = CircuitState.OPEN
                self.stats.opened_at = datetime.now()
                self.logger.error(
                    f"Circuit breaker '{self.name}' OPEN "
                    f"({self.stats.failures} failures >= {self.config.failure_threshold})"
                )

    def get_state(self) -> CircuitState:
        """Get current circuit breaker state"""
        return self.stats.state

    def is_open(self) -> bool:
        """Check if circuit is open"""
        return self.stats.state == CircuitState.OPEN


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass

