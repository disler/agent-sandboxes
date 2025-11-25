"""
Logging utilities for agent-sandboxes applications.

Provides consistent logging configuration and formatters
across all apps using Rich for beautiful console output.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler


# Global console instance for consistent output
console = Console()


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[Path] = None,
    rich_tracebacks: bool = True,
) -> logging.Logger:
    """
    Set up a logger with Rich formatting.

    Args:
        name: Logger name (typically __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
        rich_tracebacks: Enable rich tracebacks for exceptions

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear any existing handlers
    logger.handlers.clear()

    # Add Rich handler for console output
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=rich_tracebacks,
        tracebacks_show_locals=False,
        show_time=True,
        show_path=False,
    )
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a basic one.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set up basic configuration
    if not logger.handlers:
        setup_logger(name)

    return logger


class LoggerContext:
    """
    Context manager for temporary logging configuration.

    Usage:
        with LoggerContext("myapp", level="DEBUG", log_file=Path("debug.log")):
            logger = get_logger("myapp")
            logger.debug("This goes to file and console")
    """

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        log_file: Optional[Path] = None,
    ):
        self.name = name
        self.level = level
        self.log_file = log_file
        self.original_handlers = []
        self.original_level = None

    def __enter__(self):
        logger = logging.getLogger(self.name)
        self.original_handlers = logger.handlers.copy()
        self.original_level = logger.level

        # Set up new configuration
        setup_logger(self.name, self.level, self.log_file)
        return logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger = logging.getLogger(self.name)
        logger.handlers = self.original_handlers
        logger.level = self.original_level
        return False
