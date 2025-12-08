"""
Logging utility using Python logging
"""

import logging
import sys
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

            # File handlers
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)

            error_handler = logging.FileHandler('logs/error.log')
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(console_format)
            self.logger.addHandler(error_handler)

            combined_handler = logging.FileHandler('logs/combined.log')
            combined_handler.setLevel(logging.INFO)
            combined_handler.setFormatter(console_format)
            self.logger.addHandler(combined_handler)

    def info(self, message: str, meta: Optional[Any] = None):
        """Log info message"""
        if meta:
            self.logger.info(f"{message} {meta}")
        else:
            self.logger.info(message)

    def warn(self, message: str, meta: Optional[Any] = None):
        """Log warning message"""
        if meta:
            self.logger.warning(f"{message} {meta}")
        else:
            self.logger.warning(message)

    def error(self, message: str, meta: Optional[Any] = None):
        """Log error message"""
        if meta:
            self.logger.error(f"{message} {meta}", exc_info=True)
        else:
            self.logger.error(message)

    def debug(self, message: str, meta: Optional[Any] = None):
        """Log debug message"""
        if meta:
            self.logger.debug(f"{message} {meta}")
        else:
            self.logger.debug(message)

