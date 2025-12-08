"""
Logging utility using Python logging with rotation and sanitization
"""

import logging
import logging.handlers
import sys
import re
from pathlib import Path
from typing import Any, Optional


class Logger:
    """Logger wrapper for consistent logging across the application"""

    def __init__(self, context: str):
        self.logger = logging.getLogger(context)
        self.logger.setLevel(logging.INFO)

        # Avoid duplicate handlers
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_format = logging.Formatter(
                '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
            )
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)

            # File handlers with rotation
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)

            # Error log with rotation (10MB max, keep 5 backups)
            error_handler = logging.handlers.RotatingFileHandler(
                'logs/error.log',
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(console_format)
            self.logger.addHandler(error_handler)

            # Combined log with rotation (50MB max, keep 5 backups)
            combined_handler = logging.handlers.RotatingFileHandler(
                'logs/combined.log',
                maxBytes=50 * 1024 * 1024,  # 50MB
                backupCount=5
            )
            combined_handler.setLevel(logging.INFO)
            combined_handler.setFormatter(console_format)
            self.logger.addHandler(combined_handler)

    @staticmethod
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

    def info(self, message: str, meta: Optional[Any] = None):
        """Log info message with sanitization"""
        sanitized_msg = self._sanitize_log_message(message)
        if meta:
            # Sanitize meta if it's a string or dict
            if isinstance(meta, dict):
                sanitized_meta = {k: self._sanitize_log_message(str(v)) if isinstance(v, str) else v for k, v in meta.items()}
            else:
                sanitized_meta = self._sanitize_log_message(str(meta))
            self.logger.info(f"{sanitized_msg} {sanitized_meta}")
        else:
            self.logger.info(sanitized_msg)

    def warn(self, message: str, meta: Optional[Any] = None):
        """Log warning message with sanitization"""
        sanitized_msg = self._sanitize_log_message(message)
        if meta:
            if isinstance(meta, dict):
                sanitized_meta = {k: self._sanitize_log_message(str(v)) if isinstance(v, str) else v for k, v in meta.items()}
            else:
                sanitized_meta = self._sanitize_log_message(str(meta))
            self.logger.warning(f"{sanitized_msg} {sanitized_meta}")
        else:
            self.logger.warning(sanitized_msg)

    def error(self, message: str, meta: Optional[Any] = None):
        """Log error message with sanitization"""
        sanitized_msg = self._sanitize_log_message(message)
        if meta:
            if isinstance(meta, dict):
                sanitized_meta = {k: self._sanitize_log_message(str(v)) if isinstance(v, str) else v for k, v in meta.items()}
            else:
                sanitized_meta = self._sanitize_log_message(str(meta))
            self.logger.error(f"{sanitized_msg} {sanitized_meta}", exc_info=True)
        else:
            self.logger.error(sanitized_msg)

    def debug(self, message: str, meta: Optional[Any] = None):
        """Log debug message with sanitization"""
        sanitized_msg = self._sanitize_log_message(message)
        if meta:
            if isinstance(meta, dict):
                sanitized_meta = {k: self._sanitize_log_message(str(v)) if isinstance(v, str) else v for k, v in meta.items()}
            else:
                sanitized_meta = self._sanitize_log_message(str(meta))
            self.logger.debug(f"{sanitized_msg} {sanitized_meta}")
        else:
            self.logger.debug(sanitized_msg)

