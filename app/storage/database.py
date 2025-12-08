"""
SQLAlchemy database setup and session management
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from pathlib import Path
import os

Base = declarative_base()

# Database URL from environment or config
# Use absolute path for SQLite to ensure cross-platform compatibility
default_db_path = Path("./data/gateway.db").resolve()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{default_db_path}"
)

# Check if using SQLite in production (not recommended)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"
if IS_PRODUCTION and DATABASE_URL.startswith("sqlite"):
    import warnings
    warnings.warn(
        "WARNING: SQLite is not recommended for production. "
        "Please use PostgreSQL or another production-grade database. "
        "Set DATABASE_URL to a PostgreSQL connection string for production.",
        UserWarning
    )

# Create engine with connection pooling for production
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
        pool_pre_ping=True  # Verify connections before using
    )
else:
    # PostgreSQL or other databases - use connection pooling
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600  # Recycle connections after 1 hour
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def check_database_connection() -> bool:
    """Check if database connection is healthy"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

