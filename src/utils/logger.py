"""
Logging Utilities for Ruohobot

Provides centralized logging configuration for the robot system.
"""

import logging
import logging.handlers
import os
from pathlib import Path


def setup_logging(log_level=logging.DEBUG, log_file=None):  # <-- Set to DEBUG here
    """
    Setup logging configuration for the robot
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path. If None, uses default location.
    """
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Default log file
    if log_file is None:
        log_file = log_dir / "ruohobot.log"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")
    
    # Log startup message
    logging.info("Ruohobot logging initialized")
    logging.info(f"Log level: {logging.getLevelName(log_level)}")
    logging.info(f"Log file: {log_file}")
    
    # If you add handlers manually, set their level to DEBUG too:
    for handler in logging.root.handlers:
        handler.setLevel(logging.DEBUG)


def get_logger(name):
    """Get a logger with the specified name"""
    return logging.getLogger(name)


def set_log_level(level):
    """Change the logging level for all loggers"""
    logging.getLogger().setLevel(level)
    for handler in logging.getLogger().handlers:
        handler.setLevel(level)
