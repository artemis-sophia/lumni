"""
Transaction Management Utilities
Provides context managers and dependencies for database transaction management
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.storage.database import SessionLocal
from app.utils.logger import Logger
from app.utils.exceptions import DatabaseError

logger = Logger("Transaction")


@contextmanager
def get_db_transaction() -> Generator[Session, None, None]:
    """Context manager for database transactions with automatic rollback on error
    
    Usage:
        with get_db_transaction() as db:
            # Perform database operations
            db.add(some_object)
            # Transaction commits automatically on success
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
        logger.debug("Transaction committed successfully")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Transaction rolled back due to error: {str(e)}")
        raise DatabaseError(f"Database transaction failed: {str(e)}", {"exception": str(e)}) from e
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction rolled back due to unexpected error: {str(e)}")
        raise DatabaseError(f"Unexpected error in transaction: {str(e)}", {"exception": str(e)}) from e
    finally:
        db.close()


def get_db_transaction_dependency() -> Generator[Session, None, None]:
    """FastAPI dependency for database transactions
    
    This ensures all database operations in a request are wrapped in a transaction.
    On success, commits automatically. On error, rolls back automatically.
    """
    return get_db_transaction()

