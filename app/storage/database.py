"""
SQLAlchemy database setup and session management
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DatabaseError
from typing import Generator, Tuple, Optional
from pathlib import Path
import os
from app.utils.logger import Logger

logger = Logger("Database")

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
    # SQLite connection pooling (limited but still useful)
    # SQLite has a single writer, so pool_size should be small
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,  # Small pool for SQLite (single writer limitation)
        max_overflow=10,  # Allow some overflow for read operations
        pool_recycle=3600  # Recycle connections after 1 hour
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


def check_database_connection() -> Tuple[bool, Optional[str]]:
    """Check if database connection is healthy
    
    Returns:
        Tuple of (is_healthy: bool, error_message: Optional[str])
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except OperationalError as e:
        error_msg = f"Database operational error: {str(e)}"
        logger.error(error_msg, meta={"error_type": "OperationalError", "error_code": getattr(e, 'orig', {}).get('code', 'unknown')})
        return False, error_msg
    except DatabaseError as e:
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg, meta={"error_type": "DatabaseError"})
        return False, error_msg
    except SQLAlchemyError as e:
        error_msg = f"SQLAlchemy error: {str(e)}"
        logger.error(error_msg, meta={"error_type": "SQLAlchemyError"})
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected database error: {type(e).__name__}: {str(e)}"
        logger.error(error_msg, meta={"error_type": type(e).__name__})
        return False, error_msg


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

