import sys
import logging


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            fmt="[%(name)s] %(asctime)s [%(levelname)-9s] %(message)s", datefmt="%Y-%m-%d %H:%M.%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


getLogger = get_logger
