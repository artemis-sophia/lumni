"""
SQLAlchemy database setup and session management
"""

from sqlalchemy import create_engine
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

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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

