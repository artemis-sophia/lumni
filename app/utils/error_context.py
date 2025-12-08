"""
Error Context Utilities
Provides structured error context for better error handling and logging
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class ErrorContext:
    """Structured error context for consistent error handling"""
    error_type: str
    message: str
    request_id: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    original_exception: Optional[Exception] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error context to dictionary for logging"""
        result = {
            "error_type": self.error_type,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }
        
        if self.request_id:
            result["request_id"] = self.request_id
        if self.provider:
            result["provider"] = self.provider
        if self.model:
            result["model"] = self.model
        if self.original_exception:
            result["original_exception_type"] = type(self.original_exception).__name__
            result["original_exception_message"] = str(self.original_exception)
        
        return result
    
    def add_detail(self, key: str, value: Any):
        """Add a detail to the error context"""
        self.details[key] = value


def create_error_context(
    error_type: str,
    message: str,
    request_id: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    original_exception: Optional[Exception] = None,
    **kwargs
) -> ErrorContext:
    """Create an ErrorContext with common parameters"""
    return ErrorContext(
        error_type=error_type,
        message=message,
        request_id=request_id,
        provider=provider,
        model=model,
        original_exception=original_exception,
        details=kwargs
    )

