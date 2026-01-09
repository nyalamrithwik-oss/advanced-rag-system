"""
Logger Configuration Module

Sets up structured logging with:
- File rotation (10MB per file, keep 5 files)
- JSON format for easy parsing
- Console output for development
- Different log levels: INFO, WARNING, ERROR

Usage:
    from .logger_config import setup_logging
    logger = setup_logging(__name__)
    logger.info("Message", extra={"key": "value"})
"""

import logging
import json
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional, Dict, Any


class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs JSON logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in [
                    'name', 'msg', 'args', 'created', 'filename',
                    'funcName', 'levelname', 'levelno', 'lineno',
                    'module', 'msecs', 'message', 'pathname', 'process',
                    'processName', 'relativeCreated', 'thread', 'threadName',
                    'exc_info', 'exc_text', 'stack_info', 'getMessage',
                ]:
                    log_data[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class ConsoleFormatter(logging.Formatter):
    """Custom formatter for console output (human-readable)"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record for console"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        level_color = {
            "DEBUG": "\033[36m",     # Cyan
            "INFO": "\033[32m",      # Green
            "WARNING": "\033[33m",   # Yellow
            "ERROR": "\033[31m",     # Red
            "CRITICAL": "\033[35m",  # Magenta
        }
        reset = "\033[0m"
        
        color = level_color.get(record.levelname, "")
        message = record.getMessage()
        
        log_msg = f"{timestamp} {color}[{record.levelname}]{reset} {record.name}: {message}"
        
        if record.exc_info:
            log_msg += f"\n{self.formatException(record.exc_info)}"
        
        return log_msg


def setup_logging(
    name: str,
    log_level: str = "INFO",
    log_dir: str = "logs",
    json_format: bool = True,
) -> logging.Logger:
    """
    Setup structured logging for a module
    
    Parameters:
        name: Logger name (usually __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        json_format: Use JSON format for file logs
    
    Returns:
        Configured logger instance
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Get logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler (development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ConsoleFormatter())
    logger.addHandler(console_handler)
    
    # File handler with rotation (production)
    log_file = log_path / "app.log"
    file_handler = RotatingFileHandler(
        filename=str(log_file),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,  # Keep 5 backup files
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    
    if json_format:
        file_handler.setFormatter(JsonFormatter())
    else:
        file_handler.setFormatter(ConsoleFormatter())
    
    logger.addHandler(file_handler)
    
    # Error file handler (errors only)
    error_file = log_path / "errors.log"
    error_handler = RotatingFileHandler(
        filename=str(error_file),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JsonFormatter())
    logger.addHandler(error_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get existing logger or create new one"""
    return setup_logging(name)


# Root logger setup
root_logger = setup_logging("rag_api")
