import logging
import sys

# ANSI escape codes
RESET = "\033[0m"
COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow (used here as "orange-ish")
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[1;31m",  # Bold red
}


def setup_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    # formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    formatter = ColoredFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    handler.setFormatter(formatter)

    # Avoid adding multiple handlers if setup_logging is called more than once
    if not logger.handlers:
        logger.addHandler(handler)


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_color = COLORS.get(record.levelname, RESET)
        message = super().format(record)
        return f"{log_color}{message}{RESET}"
