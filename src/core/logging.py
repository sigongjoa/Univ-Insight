"""
Structured JSON logging configuration for Univ-Insight.

Provides consistent logging across all services with:
- JSON formatted logs (Time, Level, Component, Message)
- Structured fields for debugging
- Log rotation and file handling
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import os


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: LogRecord to format

        Returns:
            JSON formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields if present
        if hasattr(record, "component"):
            log_data["component"] = record.component
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> None:
    """
    Configure structured logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        enable_console: Whether to log to console
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    formatter = StructuredFormatter()

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler with rotation
    if log_file:
        # Ensure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5  # Keep 5 backup files
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Suppress noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.LoggerAdapter:
    """
    Get a logger adapter for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        LoggerAdapter for structured logging
    """
    logger = logging.getLogger(name)
    return logging.LoggerAdapter(logger, {"component": name})


# Initialize logging on module import
_log_level = os.getenv("LOG_LEVEL", "INFO")
_log_file = os.getenv("LOG_FILE", None)
setup_logging(level=_log_level, log_file=_log_file, enable_console=True)
