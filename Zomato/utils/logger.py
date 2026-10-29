"""
utils/logger.py
───────────────
Centralized logging setup for the Zomato AI Recommendation System.
All modules should use get_logger(__name__) to obtain a logger.
"""

import logging
import sys


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Return a named logger with a consistent format.

    Args:
        name:  Module name — use __name__ when calling from a module.
        level: Logging level (default: INFO).

    Returns:
        Configured logging.Logger instance.

    Example:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Application started.")
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger was already configured
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console handler (stdout) — Streamlit captures stdout cleanly
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger (avoids duplicate output)
    logger.propagate = False

    return logger

