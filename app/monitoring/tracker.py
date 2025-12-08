"""
Usage Tracker
Uses OpenTelemetry for metrics and observability while maintaining API compatibility
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from app.storage.models import UsageMetrics
from app.storage.database import get_db
from app.utils.logger import Logger

logger = Logger("UsageTracker")

# Initialize OpenTelemetry metrics
_resource = Resource.create({"service.name": "lumni-gateway"})
# Use in-memory metrics (Prometheus exporter will be handled separately)
_meter_provider = MeterProvider(resource=_resource)
metrics.set_meter_provider(_meter_provider)

_meter = metrics.get_meter(__name__)

# Create metrics
_request_counter = _meter.create_counter(
    "lumni_requests_total",
    description="Total number of requests",
    unit="1"
)

_token_counter = _meter.create_counter(
    "lumni_tokens_total",
    description="Total number of tokens processed",
    unit="1"
)

_error_counter = _meter.create_counter(
    "lumni_errors_total",
    description="Total number of errors",
    unit="1"
)

_rate_limit_counter = _meter.create_counter(
    "lumni_rate_limit_hits_total",
    description="Total number of rate limit hits",
    unit="1"
)

_request_duration = _meter.create_histogram(
    "lumni_request_duration_seconds",
    description="Request duration in seconds",
    unit="s"
)


class UsageTracker:
    """Usage tracking and statistics using OpenTelemetry"""

    def __init__(self, alert_threshold: float = 0.8):
        self.alert_threshold = alert_threshold
        self.logger = Logger("UsageTracker")

    async def record_request(
        self,
        provider: str,
        tokens: int,
        success: bool,
        rate_limit_hit: bool = False,
        model: Optional[str] = None,
        db: Optional[Session] = None
    ):
        """Record a request using OpenTelemetry metrics"""
        # Record OpenTelemetry metrics
        labels = {
            "provider": provider,
            "model": model or "unknown",
            "success": str(success).lower()
        }
        
        _request_counter.add(1, labels)
        _token_counter.add(tokens, labels)
        
        if not success:
            _error_counter.add(1, labels)
        
        if rate_limit_hit:
            _rate_limit_counter.add(1, labels)

        # Persist to database for historical analysis
        metric = UsageMetrics(
            provider=provider,
            model=model,
            timestamp=datetime.now(),
            requests=1,
            tokens=tokens,
            errors=0 if success else 1,
            rate_limit_hits=1 if rate_limit_hit else 0
        )

        # Persist to database
        if db:
            try:
                db.add(metric)
                db.commit()
            except Exception as e:
                db.rollback()
                self.logger.error(f"Failed to persist usage metric: {str(e)}")
                raise
        else:
            # Use dependency injection if available - run in executor for async safety
            import asyncio
            from app.storage.transaction import get_db_transaction
            
            def sync_db_operation():
                with get_db_transaction() as transaction_db:
                    transaction_db.add(metric)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, sync_db_operation)

        # Check for alerts (use same db session if available)
        await self.check_alerts(provider, db=db if db else None)

    async def check_alerts(self, provider: str, db: Optional[Session] = None):
        """Check for rate limit alerts"""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        if db:
            recent_metrics = db.query(UsageMetrics).filter(
                UsageMetrics.provider == provider,
                UsageMetrics.timestamp >= one_hour_ago
            ).all()
        else:
            # Query database directly if no session provided - run in executor for async safety
            import asyncio
            from app.storage.database import SessionLocal
            
            def sync_query():
                db_session = SessionLocal()
                try:
                    return db_session.query(UsageMetrics).filter(
                        UsageMetrics.provider == provider,
                        UsageMetrics.timestamp >= one_hour_ago
                    ).all()
                finally:
                    db_session.close()
            
            loop = asyncio.get_event_loop()
            recent_metrics = await loop.run_in_executor(None, sync_query)

        total_requests = sum(m.requests for m in recent_metrics)
        rate_limit_hits = sum(m.rate_limit_hits for m in recent_metrics)

        if total_requests > 0:
            hit_rate = rate_limit_hits / total_requests
            if hit_rate >= self.alert_threshold:
                self.logger.warn(
                    f"⚠️ Alert: {provider} rate limit hit rate is {hit_rate * 100:.1f}%"
                )

    def get_provider_stats(
        self,
        provider: str,
        time_window: int = 3600000,
        db: Optional[Session] = None
    ) -> Dict:
        """Get statistics for a provider"""
        window_start = datetime.now() - timedelta(milliseconds=time_window)

        if db:
            recent_metrics = db.query(UsageMetrics).filter(
                UsageMetrics.provider == provider,
                UsageMetrics.timestamp >= window_start
            ).all()
        else:
            # Query database directly if no session provided - run in executor for async safety
            import asyncio
            from app.storage.database import SessionLocal
            
            def sync_query():
                db_session = SessionLocal()
                try:
                    return db_session.query(UsageMetrics).filter(
                        UsageMetrics.provider == provider,
                        UsageMetrics.timestamp >= window_start
                    ).all()
                finally:
                    db_session.close()
            
            loop = asyncio.get_event_loop()
            recent_metrics = await loop.run_in_executor(None, sync_query)

        return {
            'requests': sum(m.requests for m in recent_metrics),
            'tokens': sum(m.tokens for m in recent_metrics),
            'errors': sum(m.errors for m in recent_metrics),
            'rate_limit_hits': sum(m.rate_limit_hits for m in recent_metrics),
            'time_window': time_window,
        }

    def get_model_stats(
        self,
        provider: str,
        model: str,
        time_window: int = 3600000,
        db: Optional[Session] = None
    ) -> Dict:
        """Get statistics for a specific model"""
        window_start = datetime.now() - timedelta(milliseconds=time_window)

        if db:
            recent_metrics = db.query(UsageMetrics).filter(
                UsageMetrics.provider == provider,
                UsageMetrics.model == model,
                UsageMetrics.timestamp >= window_start
            ).all()
        else:
            # Query database directly if no session provided - run in executor for async safety
            import asyncio
            from app.storage.database import SessionLocal
            
            def sync_query():
                db_session = SessionLocal()
                try:
                    return db_session.query(UsageMetrics).filter(
                        UsageMetrics.provider == provider,
                        UsageMetrics.model == model,
                        UsageMetrics.timestamp >= window_start
                    ).all()
                finally:
                    db_session.close()
            
            loop = asyncio.get_event_loop()
            recent_metrics = await loop.run_in_executor(None, sync_query)

        return {
            'requests': sum(m.requests for m in recent_metrics),
            'tokens': sum(m.tokens for m in recent_metrics),
            'errors': sum(m.errors for m in recent_metrics),
            'rate_limit_hits': sum(m.rate_limit_hits for m in recent_metrics),
            'time_window': time_window,
        }

    def get_all_stats(
        self,
        time_window: int = 3600000,
        db: Optional[Session] = None
    ) -> Dict[str, Dict]:
        """Get statistics for all providers"""
        # Get unique providers from database
        if db:
            providers = db.query(UsageMetrics.provider).distinct().all()
            providers = [p[0] for p in providers]
        else:
            # Query database directly if no session provided - run in executor for async safety
            import asyncio
            from app.storage.database import SessionLocal
            
            def sync_query():
                db_session = SessionLocal()
                try:
                    providers = db_session.query(UsageMetrics.provider).distinct().all()
                    return [p[0] for p in providers]
                finally:
                    db_session.close()
            
            loop = asyncio.get_event_loop()
            providers = await loop.run_in_executor(None, sync_query)

        stats = {}
        for provider in providers:
            stats[provider] = self.get_provider_stats(provider, time_window, db)

        return stats
