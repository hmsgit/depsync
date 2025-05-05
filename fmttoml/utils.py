import sys
import logging
from pathlib import Path


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


def find_toml_files(paths: list[str]) -> list[Path]:
    toml_files = []
    for p in paths:
        path = Path(p)
        if path.is_file() and path.suffix == ".toml":
            toml_files.append(path)
        elif path.is_dir():
            for f in path.rglob("*.toml"):
                if not any(part.startswith(".") for part in f.parts if part not in (".", "..")):
                    toml_files.append(f)

    return toml_files
