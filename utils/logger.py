"""
Structured logging utility for the Sleep Optimizer Agent.
"""
import logging
import json
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from config import Config

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add context if available
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'task_id'):
            log_entry['task_id'] = record.task_id
        if hasattr(record, 'context'):
            log_entry['context'] = record.context
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def setup_logger(name='sleep_optimizer_agent', log_file=None, level=None):
    """
    Set up and configure the logger.
    
    Args:
        name: Logger name
        log_file: Path to log file (defaults to Config.LOG_FILE)
        level: Logging level (defaults to Config.LOG_LEVEL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level or Config.LOG_LEVEL, logging.INFO))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create logs directory if it doesn't exist (handled below)
    # Redundant block removed
    
    # File handler with rotation (only if writable)
    file_path = log_file or Config.LOG_FILE
    if file_path:
        try:
            file_dir = os.path.dirname(file_path)
            if file_dir and not os.path.exists(file_dir):
                os.makedirs(file_dir, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                file_path,
                maxBytes=Config.LOG_MAX_BYTES,
                backupCount=Config.LOG_BACKUP_COUNT
            )
            file_handler.setFormatter(JSONFormatter())
            logger.addHandler(file_handler)
        except OSError:
            # Fallback for read-only file systems (like Vercel)
            pass
        except Exception as e:
            print(f"Failed to setup file logging: {e}")
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    return logger

# Global logger instance
logger = setup_logger()

def log_with_context(logger_instance, level, message, user_id=None, task_id=None, context=None):
    """
    Log a message with additional context.
    
    Args:
        logger_instance: Logger to use
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        message: Log message
        user_id: Optional user ID
        task_id: Optional task ID
        context: Optional context dictionary
    """
    extra = {}
    if user_id:
        extra['user_id'] = user_id
    if task_id:
        extra['task_id'] = task_id
    if context:
        extra['context'] = context
    
    getattr(logger_instance, level.lower())(message, extra=extra)

