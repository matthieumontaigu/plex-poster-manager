import logging
import sys


def setup_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)

    # Avoid adding multiple handlers if setup_logging is called more than once
    if not logger.handlers:
        logger.addHandler(handler)
