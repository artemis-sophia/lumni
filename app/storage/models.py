"""
SQLAlchemy ORM models for database tables
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from app.storage.database import Base


class UsageMetrics(Base):
    """Usage metrics table"""
    __tablename__ = "usage_metrics"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False, index=True)
    model = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)
    requests = Column(Integer, nullable=False, default=0)
    tokens = Column(Integer, nullable=False, default=0)
    errors = Column(Integer, nullable=False, default=0)
    rate_limit_hits = Column(Integer, nullable=False, default=0)


class ModelRateLimits(Base):
    """Model rate limits table"""
    __tablename__ = "model_rate_limits"

    provider = Column(String, primary_key=True)
    model = Column(String, primary_key=True)
    per_minute = Column(Integer, nullable=False)
    per_day = Column(Integer, nullable=False)
    remaining_per_minute = Column(Integer, nullable=False)
    remaining_per_day = Column(Integer, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class ProviderState(Base):
    """Provider state table"""
    __tablename__ = "provider_state"

    provider = Column(String, primary_key=True)
    healthy = Column(Boolean, nullable=False, default=True)
    available = Column(Boolean, nullable=False, default=True)
    error_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    last_used = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class TaskClassifications(Base):
    """Task classifications table"""
    __tablename__ = "task_classifications"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, nullable=True, index=True)
    task_type = Column(String, nullable=False)  # fast, powerful
    confidence = Column(Integer, nullable=False)  # 0-100
    factors = Column(JSON, nullable=True)  # Store factors as JSON
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)


class ModelSelections(Base):
    """Model selections table"""
    __tablename__ = "model_selections"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, nullable=True, index=True)
    task_type = Column(String, nullable=False)  # fast, powerful
    selected_provider = Column(String, nullable=False)
    selected_model = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    benchmark_score = Column(Integer, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)

