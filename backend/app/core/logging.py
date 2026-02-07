"""
Advanced logging configuration with structured logging support.
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            str: JSON formatted log entry
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


class ContextFilter(logging.Filter):
    """Filter to add contextual information to log records."""
    
    def __init__(self, context: Optional[dict] = None):
        """
        Initialize context filter.
        
        Args:
            context: Additional context to add to logs
        """
        super().__init__()
        self.context = context or {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to record."""
        record.extra_fields = self.context
        return True


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "./logs",
    use_json: bool = False
) -> logging.Logger:
    """
    Configure application logging with rotating file handlers.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files
        use_json: Whether to use JSON formatting
        
    Returns:
        Logger: Configured logger instance
    """
    from logging.handlers import RotatingFileHandler
    
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True, parents=True)
    
    # Configure formatters
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # File handler for all logs
    file_handler = RotatingFileHandler(
        log_path / "app.log",
        maxBytes=10_485_760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        log_path / "error.log",
        maxBytes=10_485_760,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Create application logger
    logger = logging.getLogger("rag_api")
    logger.info(f"Logging initialized at level: {log_level}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger: Logger instance
    """
    return logging.getLogger(f"rag_api.{name}")
