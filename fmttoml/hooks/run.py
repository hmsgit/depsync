#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess

from ..utils import get_logger

logger = get_logger(__name__)


def main():
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


if __name__ == "__main__":
    sys.exit(main())
