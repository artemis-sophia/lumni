"""
Logging utility using loguru with rotation and sanitization
Wraps loguru to maintain existing API compatibility
"""

import re
import sys
from pathlib import Path
from typing import Any, Optional
from contextvars import ContextVar
from loguru import logger as loguru_logger

# Context variable for request ID (set by middleware)
# This is exported so middleware can set it
_request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


# Remove default handler
loguru_logger.remove()


# Initialize log directory
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)


def _sanitize_log_message(message: str) -> str:
    """Sanitize log message to redact sensitive information"""
    # Redact API keys (common patterns)
    patterns = [
        (r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?', r'api_key="***REDACTED***"'),
        (r'token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?', r'token="***REDACTED***"'),
        (r'password["\']?\s*[:=]\s*["\']?([^"\']+)["\']?', r'password="***REDACTED***"'),
        (r'secret["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?', r'secret="***REDACTED***"'),
        (r'authorization["\']?\s*[:=]\s*["\']?bearer\s+([a-zA-Z0-9_-]{20,})["\']?', r'authorization="Bearer ***REDACTED***"'),
    ]
    
    sanitized = message
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    
    return sanitized


def _sanitize_filter(record):
    """Loguru filter to sanitize log messages"""
    # Sanitize the message
    if isinstance(record["message"], str):
        record["message"] = _sanitize_log_message(record["message"])
    return True


# Configure console handler (INFO level)
loguru_logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss} [{name}] {level}: {message}",
    level="INFO",
    filter=_sanitize_filter,
    colorize=True
)

# Configure error log file (ERROR level, 10MB rotation, 5 backups)
loguru_logger.add(
    "logs/error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} [{name}] {level}: {message}",
    level="ERROR",
    rotation="10 MB",
    retention=5,
    filter=_sanitize_filter,
    compression=None
)

# Configure combined log file (INFO level, 50MB rotation, 5 backups)
loguru_logger.add(
    "logs/combined.log",
    format="{time:YYYY-MM-DD HH:mm:ss} [{name}] {level}: {message}",
    level="INFO",
    rotation="50 MB",
    retention=5,
    filter=_sanitize_filter,
    compression=None
)


class Logger:
    """Logger wrapper for consistent logging across the application
    Maintains API compatibility with previous logging implementation
    Supports OpenTelemetry trace correlation
    """

    def __init__(self, context: str):
        self.context = context
        # Use patch to set the name in the record
        self.logger = loguru_logger.patch(lambda record: record.update(name=context))
        
        # Try to get OpenTelemetry tracer for correlation
        try:
            from opentelemetry import trace
            self._tracer = trace.get_tracer(__name__)
        except ImportError:
            self._tracer = None

    def _format_message_with_meta(self, message: str, meta: Optional[Any] = None) -> str:
        """Format message with meta parameter, trace correlation, and request ID"""
        sanitized_msg = _sanitize_log_message(message)
        
        # Get request ID from context
        request_id = _request_id_context.get()
        request_id_info = f" [request_id={request_id}]" if request_id else ""
        
        # Add trace correlation if available
        trace_info = ""
        if self._tracer:
            try:
                from opentelemetry import trace
                span = trace.get_current_span()
                if span and span.get_span_context().trace_id:
                    trace_id = format(span.get_span_context().trace_id, '032x')
                    span_id = format(span.get_span_context().span_id, '016x')
                    trace_info = f" [trace_id={trace_id[:16]}... span_id={span_id[:8]}...]"
            except Exception:
                pass  # Ignore trace errors
        
        if meta:
            if isinstance(meta, dict):
                # Ensure request_id is in meta if not already present
                if 'request_id' not in meta and request_id:
                    meta = {**meta, 'request_id': request_id}
                # Sanitize dict values
                sanitized_meta = {
                    k: _sanitize_log_message(str(v)) if isinstance(v, str) else v
                    for k, v in meta.items()
                }
                # Format as string for compatibility with old API
                meta_str = " " + str(sanitized_meta)
            else:
                meta_str = " " + _sanitize_log_message(str(meta))
            return sanitized_msg + request_id_info + trace_info + meta_str
        
        return sanitized_msg + request_id_info + trace_info

    def info(self, message: str, meta: Optional[Any] = None):
        """Log info message with sanitization"""
        formatted_msg = self._format_message_with_meta(message, meta)
        self.logger.info(formatted_msg)

    def warn(self, message: str, meta: Optional[Any] = None):
        """Log warning message with sanitization"""
        formatted_msg = self._format_message_with_meta(message, meta)
        self.logger.warning(formatted_msg)

    def error(self, message: str, meta: Optional[Any] = None):
        """Log error message with sanitization"""
        formatted_msg = self._format_message_with_meta(message, meta)
        # Loguru automatically includes exception info if exception is in context
        # For compatibility, we log the message (exc_info is handled by loguru automatically)
        self.logger.error(formatted_msg)

    def debug(self, message: str, meta: Optional[Any] = None):
        """Log debug message with sanitization"""
        formatted_msg = self._format_message_with_meta(message, meta)
        self.logger.debug(formatted_msg)
