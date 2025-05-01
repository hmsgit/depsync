import sys
import argparse
import subprocess
from pathlib import Path

from .utils import get_logger
from .linter import lint_toml_file

logger = get_logger(__name__)


def run():
    if len(sys.argv) < 2:
        logger.info("Usage: hooks/run.py <command> [args and files...]")
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    cmd = [command] + args
    try:
        result = subprocess.run(cmd)
        return result.returncode
    except FileNotFoundError:
        logger.error(f"Error: Command '{command}' not found")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Check or fix operator spacing in TOML files.")
    parser.add_argument("--fix", action="store_true", help="Automatically fix operator spacing")
    parser.add_argument("paths", nargs="+", help="Files or directories to process")
    args = parser.parse_args()
    logger.info(f"fmttoml {' '.join(sys.argv[1:])}")

    failed_files = []
    for file_path in args.paths:
        if lint_toml_file(Path(file_path), fix=args.fix):
            failed_files.append(file_path)

    if failed_files:
        if args.fix:
            logger.info("Operator spacing issues fixed in:")
        else:
            logger.warning("Operator spacing issues found in:")
        for f in failed_files:
            logger.info(f"  - {f}")
        exit(1)


if __name__ == "__main__":
    main()
