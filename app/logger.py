"""Logger configuration"""

import logging
import sys

from dataclasses import dataclass


@dataclass
class LogColors:
    """
    Class for colorized logging levels.

    Attributes
    ----------
    RESET : str
        Reset color (None)
    INFO : str
        Info level color (Green)
    WARNING : str
        Warning level color (Yellow)
    ERROR : str
        Error level color (Red)
    DEBUG : str
        Debug level color (Blue)
    """

    RESET = "\x1b[0m"
    INFO = "\x1b[32m"  # Green
    WARNING = "\x1b[33m"  # Yellow
    ERROR = "\x1b[31m"  # Red
    DEBUG = "\x1b[34m"  # Blue


class CustomFormatter(logging.Formatter):
    """Custom logging formatter with colorized output."""

    def format(self, record):
        color = LogColors.RESET

        if record.levelno == logging.INFO:
            color = LogColors.INFO
        elif record.levelno == logging.WARNING:
            color = LogColors.WARNING
        elif record.levelno == logging.ERROR:
            color = LogColors.ERROR
        elif record.levelno == logging.DEBUG:
            color = LogColors.DEBUG

        record.levelname = f"{color}{record.levelname}{LogColors.RESET}"

        return super().format(record)


def configure_logging(debug: bool = False) -> None:
    """Configure logging with colors like FastAPI / Uvicorn style.

    Parameters
    ----------
    debug : bool, optional
        Enable debug mode (default: False).
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        CustomFormatter(
            "[%(levelname)s] %(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )

    logging.basicConfig(
        level=logging.INFO if not debug else logging.DEBUG,
        handlers=[handler],
    )
