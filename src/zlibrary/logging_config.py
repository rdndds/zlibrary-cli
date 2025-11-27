"""
Logging configuration for Z-Library Search Application
"""
import logging
import logging.handlers
import sys
import os
from typing import Optional
from zlibrary.config import Config


def setup_logging(config: Config) -> None:
    """
    Set up logging based on configuration

    Args:
        config: Configuration object with logging settings
    """
    # Get the root logger
    root_logger = logging.getLogger()
    # Clear any existing handlers to avoid duplicate logs
    root_logger.handlers = []

    # Set the logging level
    log_level = config.get('log_level', 'INFO')
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Define formats (no color)
    console_format = config.get('console_log_format', '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')
    file_format = config.get('file_log_format', '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')

    # Add console handler if enabled (without colors)
    if config.get('log_to_console', True):
        formatter = logging.Formatter(
            console_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Add file handler with rotation if enabled
    if config.get('log_to_file', True):
        log_file = config.get('log_file', 'logs/zlibrary.log')

        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        max_bytes = config.get('log_max_bytes', 10485760)  # 10MB
        backup_count = config.get('log_backup_count', 5)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            file_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name

    Args:
        name: Name of the logger

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


import uuid


def generate_operation_id() -> str:
    """
    Generate a unique operation ID for tracking operations

    Returns:
        A unique operation identifier
    """
    return str(uuid.uuid4())[:8]  # Shortened UUID for readability


def create_contextual_logger(name: str, operation_id: str = None) -> logging.LoggerAdapter:
    """
    Create a logger with contextual information including operation ID

    Args:
        name: Name for the logger
        operation_id: Optional operation ID to include in logs

    Returns:
        LoggerAdapter with contextual information
    """
    if operation_id is None:
        operation_id = generate_operation_id()

    logger = logging.getLogger(name)
    context = {'operation_id': operation_id}
    return logging.LoggerAdapter(logger, context)


def add_logging_context(logger, context: dict) -> logging.LoggerAdapter:
    """
    Add contextual information to a logger

    Args:
        logger: The base logger
        context: Dictionary of contextual information

    Returns:
        LoggerAdapter with contextual information
    """
    return logging.LoggerAdapter(logger, context)