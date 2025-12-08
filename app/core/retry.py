"""
Retry Logic with Exponential Backoff
Uses tenacity for robust retry handling
"""

from typing import Callable, TypeVar, Any
from functools import wraps
import asyncio
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)
from app.utils.logger import Logger

T = TypeVar('T')
logger = Logger("Retry")


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_on: tuple = (Exception,)
):
    """
    Decorator for retrying async functions with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        retry_on: Tuple of exception types to retry on
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(
                multiplier=initial_delay,
                max=max_delay,
                exp_base=exponential_base
            ),
            retry=retry_if_exception_type(retry_on),
            reraise=True
        )
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except RetryError as e:
                logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                raise e.last_attempt.exception() from e
            except Exception as e:
                logger.warn(f"Function {func.__name__} failed: {str(e)}, retrying...")
                raise
        
        return wrapper
    return decorator


async def retry_with_custom_backoff(
    func: Callable[..., Any],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    *args: Any,
    **kwargs: Any
) -> Any:
    """
    Retry a function with custom exponential backoff
    
    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        *args, **kwargs: Arguments to pass to func
    """
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_attempts - 1:
                delay = min(
                    initial_delay * (exponential_base ** attempt),
                    max_delay
                )
                logger.warn(
                    f"Attempt {attempt + 1}/{max_attempts} failed: {str(e)}. "
                    f"Retrying in {delay:.2f}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
                raise
    
    if last_exception:
        raise last_exception

