"""
Integration tests for rate limiting
"""

import pytest
from app.monitoring.tracker import UsageTracker
from app.storage.models import UsageMetrics
from datetime import datetime


def test_usage_tracker_records_requests(db_session):
    """Test that usage tracker records requests"""
    tracker = UsageTracker()
    
    import asyncio
    
    async def test():
        await tracker.record_request(
            provider="test-provider",
            tokens=100,
            success=True,
            rate_limit_hit=False,
            model="test-model",
            db=db_session
        )
    
    asyncio.run(test())
    
    # Check database
    metrics = db_session.query(UsageMetrics).filter(
        UsageMetrics.provider == "test-provider"
    ).all()
    
    assert len(metrics) > 0
    assert metrics[0].tokens == 100
    assert metrics[0].errors == 0


def test_usage_tracker_records_errors(db_session):
    """Test that usage tracker records errors"""
    tracker = UsageTracker()
    
    import asyncio
    
    async def test():
        await tracker.record_request(
            provider="test-provider",
            tokens=0,
            success=False,
            rate_limit_hit=False,
            model="test-model",
            db=db_session
        )
    
    asyncio.run(test())
    
    # Check database
    metrics = db_session.query(UsageMetrics).filter(
        UsageMetrics.provider == "test-provider",
        UsageMetrics.errors > 0
    ).all()
    
    assert len(metrics) > 0
    assert metrics[0].errors == 1


def test_usage_tracker_records_rate_limit_hits(db_session):
    """Test that usage tracker records rate limit hits"""
    tracker = UsageTracker()
    
    import asyncio
    
    async def test():
        await tracker.record_request(
            provider="test-provider",
            tokens=50,
            success=True,
            rate_limit_hit=True,
            model="test-model",
            db=db_session
        )
    
    asyncio.run(test())
    
    # Check database
    metrics = db_session.query(UsageMetrics).filter(
        UsageMetrics.provider == "test-provider",
        UsageMetrics.rate_limit_hits > 0
    ).all()
    
    assert len(metrics) > 0
    assert metrics[0].rate_limit_hits == 1


def test_usage_tracker_get_stats(db_session):
    """Test getting usage statistics"""
    tracker = UsageTracker()
    
    import asyncio
    
    async def test():
        # Record some requests
        await tracker.record_request(
            provider="test-provider",
            tokens=100,
            success=True,
            db=db_session
        )
        await tracker.record_request(
            provider="test-provider",
            tokens=200,
            success=True,
            db=db_session
        )
    
    asyncio.run(test())
    
    # Get stats
    stats = tracker.get_provider_stats("test-provider", time_window=3600000, db=db_session)
    
    assert stats["requests"] >= 2
    assert stats["tokens"] >= 300
    assert stats["errors"] == 0

