"""Centralized logging configuration."""

import logging
import sys
from typing import Optional


def get_logger(name: Optional[str] = None, level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (defaults to root logger)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or __name__)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - [%(name)s.%(funcName)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level.upper()))

    return logger
