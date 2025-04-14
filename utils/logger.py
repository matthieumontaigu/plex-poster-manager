import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# ANSI escape codes
RESET = "\033[0m"
COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow (used here as "orange-ish")
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[1;31m",  # Bold red
}


def setup_logging(log_path: str | None = None) -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    record = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    logger.handlers = []

    console_handler = logging.StreamHandler(sys.stderr)
    colored_formatter = ColoredFormatter(record)
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)

    if log_path:
        file_path = Path(log_path) / "plex-poster-manager.log"
        file_handler = TimedRotatingFileHandler(
            "app.log", when="midnight", interval=1, backupCount=7
        )
        file_handler.suffix = "%Y-%m-%d"
        formatter = logging.Formatter(record)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_color = COLORS.get(record.levelname, RESET)
        message = super().format(record)
        return f"{log_color}{message}{RESET}"
