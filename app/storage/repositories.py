"""
Storage Repositories
Data access layer for all entities
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.storage.models import (
    UsageMetrics,
    ModelRateLimits,
    ProviderState,
    TaskClassifications,
    ModelSelections
)


class UsageMetricsRepository:
    """Repository for usage metrics"""

    @staticmethod
    def save(db: Session, metric: UsageMetrics) -> UsageMetrics:
        """Save usage metric"""
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric

    @staticmethod
    def get_by_provider(
        db: Session,
        provider: str,
        since: Optional[datetime] = None
    ) -> List[UsageMetrics]:
        """Get metrics for a provider"""
        query = db.query(UsageMetrics).filter(UsageMetrics.provider == provider)
        if since:
            query = query.filter(UsageMetrics.timestamp >= since)
        return query.all()

    @staticmethod
    def get_by_model(
        db: Session,
        provider: str,
        model: str,
        since: Optional[datetime] = None
    ) -> List[UsageMetrics]:
        """Get metrics for a model"""
        query = db.query(UsageMetrics).filter(
            and_(
                UsageMetrics.provider == provider,
                UsageMetrics.model == model
            )
        )
        if since:
            query = query.filter(UsageMetrics.timestamp >= since)
        return query.all()


class ModelRateLimitsRepository:
    """Repository for model rate limits"""

    @staticmethod
    def save(db: Session, rate_limit: ModelRateLimits) -> ModelRateLimits:
        """Save model rate limit"""
        db.merge(rate_limit)
        db.commit()
        db.refresh(rate_limit)
        return rate_limit

    @staticmethod
    def get(db: Session, provider: str, model: str) -> Optional[ModelRateLimits]:
        """Get rate limit for a model"""
        return db.query(ModelRateLimits).filter(
            and_(
                ModelRateLimits.provider == provider,
                ModelRateLimits.model == model
            )
        ).first()

    @staticmethod
    def get_all(db: Session) -> List[ModelRateLimits]:
        """Get all rate limits"""
        return db.query(ModelRateLimits).all()


class ProviderStateRepository:
    """Repository for provider state"""

    @staticmethod
    def save(db: Session, state: ProviderState) -> ProviderState:
        """Save provider state"""
        db.merge(state)
        db.commit()
        db.refresh(state)
        return state

    @staticmethod
    def get(db: Session, provider: str) -> Optional[ProviderState]:
        """Get provider state"""
        return db.query(ProviderState).filter(ProviderState.provider == provider).first()


class TaskClassificationsRepository:
    """Repository for task classifications"""

    @staticmethod
    def save(db: Session, classification: TaskClassifications) -> TaskClassifications:
        """Save task classification"""
        db.add(classification)
        db.commit()
        db.refresh(classification)
        return classification


class ModelSelectionsRepository:
    """Repository for model selections"""

    @staticmethod
    def save(db: Session, selection: ModelSelections) -> ModelSelections:
        """Save model selection"""
        db.add(selection)
        db.commit()
        db.refresh(selection)
        return selection

