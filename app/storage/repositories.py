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
from app.utils.exceptions import DatabaseError
from app.utils.error_context import create_error_context
from sqlalchemy.exc import OperationalError, DisconnectionError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)
from functools import wraps

# Retry decorator for database operations
retry_db_operation = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    reraise=True
)


class UsageMetricsRepository:
    """Repository for usage metrics"""

    @staticmethod
    @retry_db_operation
    def save(db: Session, metric: UsageMetrics) -> UsageMetrics:
        """Save usage metric with transaction rollback on error"""
        try:
            db.add(metric)
            db.commit()
            db.refresh(metric)
            return metric
        except Exception as e:
            db.rollback()
            error_context = create_error_context(
                error_type="DATABASE_ERROR",
                message=f"Failed to save usage metric: {str(e)}",
                original_exception=e,
                operation="save_usage_metric"
            )
            raise DatabaseError(
                f"Failed to save usage metric: {str(e)}",
                error_context.to_dict()
            ) from e

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
    @retry_db_operation
    def save(db: Session, rate_limit: ModelRateLimits) -> ModelRateLimits:
        """Save model rate limit with transaction rollback on error"""
        try:
            db.merge(rate_limit)
            db.commit()
            db.refresh(rate_limit)
            return rate_limit
        except Exception as e:
            db.rollback()
            error_context = create_error_context(
                error_type="DATABASE_ERROR",
                message=f"Failed to save model rate limit: {str(e)}",
                original_exception=e,
                operation="save_model_rate_limit"
            )
            raise DatabaseError(
                f"Failed to save model rate limit: {str(e)}",
                error_context.to_dict()
            ) from e

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
    @retry_db_operation
    def save(db: Session, state: ProviderState) -> ProviderState:
        """Save provider state with transaction rollback on error"""
        try:
            db.merge(state)
            db.commit()
            db.refresh(state)
            return state
        except Exception as e:
            db.rollback()
            error_context = create_error_context(
                error_type="DATABASE_ERROR",
                message=f"Failed to save provider state: {str(e)}",
                original_exception=e,
                operation="save_provider_state"
            )
            raise DatabaseError(
                f"Failed to save provider state: {str(e)}",
                error_context.to_dict()
            ) from e

    @staticmethod
    def get(db: Session, provider: str) -> Optional[ProviderState]:
        """Get provider state"""
        return db.query(ProviderState).filter(ProviderState.provider == provider).first()


class TaskClassificationsRepository:
    """Repository for task classifications"""

    @staticmethod
    @retry_db_operation
    def save(db: Session, classification: TaskClassifications) -> TaskClassifications:
        """Save task classification with transaction rollback on error"""
        try:
            db.add(classification)
            db.commit()
            db.refresh(classification)
            return classification
        except Exception as e:
            db.rollback()
            error_context = create_error_context(
                error_type="DATABASE_ERROR",
                message=f"Failed to save task classification: {str(e)}",
                original_exception=e,
                operation="save_task_classification"
            )
            raise DatabaseError(
                f"Failed to save task classification: {str(e)}",
                error_context.to_dict()
            ) from e


class ModelSelectionsRepository:
    """Repository for model selections"""

    @staticmethod
    @retry_db_operation
    def save(db: Session, selection: ModelSelections) -> ModelSelections:
        """Save model selection with transaction rollback on error"""
        try:
            db.add(selection)
            db.commit()
            db.refresh(selection)
            return selection
        except Exception as e:
            db.rollback()
            error_context = create_error_context(
                error_type="DATABASE_ERROR",
                message=f"Failed to save model selection: {str(e)}",
                original_exception=e,
                operation="save_model_selection"
            )
            raise DatabaseError(
                f"Failed to save model selection: {str(e)}",
                error_context.to_dict()
            ) from e

