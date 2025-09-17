"""
Logging configuration for the IBS Wellness Companion API.
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings


def setup_logging() -> None:
    """Setup logging configuration."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Logging configuration
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "detailed",
                "filename": log_dir / "app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": log_dir / "error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "app": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "error_file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file"],
        },
    }
    
    # Apply logging configuration
    logging.config.dictConfig(config)
    
    # Set up logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration initialized")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(f"app.{name}")


# Structured logging helpers
class StructuredLogger:
    """Helper class for structured logging."""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def log_request(self, method: str, path: str, user_id: str = None, **kwargs):
        """Log HTTP request."""
        extra = {
            "event_type": "http_request",
            "method": method,
            "path": path,
            "user_id": user_id,
            **kwargs
        }
        self.logger.info("HTTP request", extra=extra)
    
    def log_response(self, status_code: int, response_time: float, **kwargs):
        """Log HTTP response."""
        extra = {
            "event_type": "http_response",
            "status_code": status_code,
            "response_time": response_time,
            **kwargs
        }
        self.logger.info("HTTP response", extra=extra)
    
    def log_error(self, error: Exception, context: str = None, **kwargs):
        """Log error with context."""
        extra = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            **kwargs
        }
        self.logger.error("Error occurred", extra=extra, exc_info=True)
    
    def log_ml_prediction(self, model_name: str, prediction_time: float, **kwargs):
        """Log ML prediction."""
        extra = {
            "event_type": "ml_prediction",
            "model_name": model_name,
            "prediction_time": prediction_time,
            **kwargs
        }
        self.logger.info("ML prediction", extra=extra)
    
    def log_database_operation(self, operation: str, table: str, duration: float, **kwargs):
        """Log database operation."""
        extra = {
            "event_type": "database_operation",
            "operation": operation,
            "table": table,
            "duration": duration,
            **kwargs
        }
        self.logger.info("Database operation", extra=extra)