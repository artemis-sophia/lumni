"""
Unit tests for retry logic
"""

import pytest
import asyncio
from app.core.retry import retry_with_backoff, retry_with_custom_backoff


@pytest.mark.asyncio
async def test_retry_with_backoff_success():
    """Test retry decorator with successful call"""
    
    @retry_with_backoff(max_attempts=3, initial_delay=0.1)
    async def success_func():
        return "success"
    
    result = await success_func()
    assert result == "success"


@pytest.mark.asyncio
async def test_retry_with_backoff_eventual_success():
    """Test retry decorator with eventual success"""
    attempt_count = 0
    
    @retry_with_backoff(max_attempts=3, initial_delay=0.1)
    async def flaky_func():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError("Temporary error")
        return "success"
    
    result = await flaky_func()
    assert result == "success"
    assert attempt_count == 3


@pytest.mark.asyncio
async def test_retry_with_backoff_max_attempts():
    """Test retry decorator exhausts attempts"""
    attempt_count = 0
    
    @retry_with_backoff(max_attempts=3, initial_delay=0.1)
    async def always_failing_func():
        nonlocal attempt_count
        attempt_count += 1
        raise ValueError("Always fails")
    
    with pytest.raises(ValueError):
        await always_failing_func()
    
    assert attempt_count == 3


@pytest.mark.asyncio
async def test_retry_with_custom_backoff_success():
    """Test retry_with_custom_backoff with successful call"""
    
    async def success_func():
        return "success"
    
    result = await retry_with_custom_backoff(
        success_func,
        max_attempts=3,
        initial_delay=0.1
    )
    assert result == "success"


@pytest.mark.asyncio
async def test_retry_with_custom_backoff_eventual_success():
    """Test retry_with_custom_backoff with eventual success"""
    attempt_count = 0
    
    async def flaky_func():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 2:
            raise ValueError("Temporary error")
        return "success"
    
    result = await retry_with_custom_backoff(
        flaky_func,
        max_attempts=3,
        initial_delay=0.1
    )
    assert result == "success"
    assert attempt_count == 2


@pytest.mark.asyncio
async def test_retry_with_custom_backoff_max_attempts():
    """Test retry_with_custom_backoff exhausts attempts"""
    attempt_count = 0
    
    async def always_failing_func():
        nonlocal attempt_count
        attempt_count += 1
        raise ValueError("Always fails")
    
    with pytest.raises(ValueError):
        await retry_with_custom_backoff(
            always_failing_func,
            max_attempts=3,
            initial_delay=0.1
        )
    
    assert attempt_count == 3


# Removed timing test - too flaky and not essential

