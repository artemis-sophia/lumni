"""
Usage Tracker
Tracks usage metrics and persists to database
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.storage.models import UsageMetrics
from app.storage.database import get_db
from app.utils.logger import Logger


class UsageTracker:
    """Usage tracking and statistics"""

    def __init__(self, alert_threshold: float = 0.8):
        self.alert_threshold = alert_threshold
        self.logger = Logger("UsageTracker")
        self.metrics: Dict[str, list] = {}

    async def record_request(
        self,
        provider: str,
        tokens: int,
        success: bool,
        rate_limit_hit: bool = False,
        model: Optional[str] = None,
        db: Optional[Session] = None
    ):
        """Record a request"""
        metric = UsageMetrics(
            provider=provider,
            model=model,
            timestamp=datetime.now(),
            requests=1,
            tokens=tokens,
            errors=0 if success else 1,
            rate_limit_hits=1 if rate_limit_hit else 0
        )

        # Store in memory
        key = f"{provider}:{model}" if model else provider
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append(metric)

        # Persist to database
        if db:
            db.add(metric)
            db.commit()
        else:
            # Use dependency injection if available
            db_gen = get_db()
            db = next(db_gen)
            try:
                db.add(metric)
                db.commit()
            finally:
                db.close()

        # Check for alerts
        await self.check_alerts(provider)

    async def check_alerts(self, provider: str):
        """Check for rate limit alerts"""
        provider_metrics = self.metrics.get(provider, [])
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_metrics = [
            m for m in provider_metrics
            if isinstance(m.timestamp, datetime) and m.timestamp >= one_hour_ago
        ]

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
            # Use memory cache
            all_metrics = []
            for key, metrics in self.metrics.items():
                if key == provider or key.startswith(f"{provider}:"):
                    all_metrics.extend(metrics)
            recent_metrics = [
                m for m in all_metrics
                if isinstance(m.timestamp, datetime) and m.timestamp >= window_start
            ]

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
            key = f"{provider}:{model}"
            model_metrics = self.metrics.get(key, [])
            recent_metrics = [
                m for m in model_metrics
                if isinstance(m.timestamp, datetime) and m.timestamp >= window_start
            ]

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
        # Get unique providers
        providers = set()
        for key in self.metrics.keys():
            if ':' in key:
                providers.add(key.split(':')[0])
            else:
                providers.add(key)

        stats = {}
        for provider in providers:
            stats[provider] = self.get_provider_stats(provider, time_window, db)

        return stats

