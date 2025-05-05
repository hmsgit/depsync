import sys
import argparse
import subprocess
from typing import Literal
from dataclasses import dataclass

from .utils import get_logger, find_toml_files

logger = get_logger(__name__)


def run():
    """
    Run any cli command. We'll use this to run pre-commit hooks, e.g.: run toml-sort
    """
    if len(sys.argv) < 2:
        logger.info("Usage: run <command> [args]")
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


@dataclass
class CliArgs:
    fix: bool
    update_requirements: bool
    tool: Literal["auto", "uv", "poetry"]
    force_multiline_array_over_line_length: int
    paths: list[str]


def _parse_args() -> CliArgs:
    parser = argparse.ArgumentParser(description="Check or fix operator spacing in TOML files.")
    parser.add_argument("--fix", action="store_true", help="Automatically fix operator spacing")
    parser.add_argument(
        "--update-requirements",
        action="store_true",
        help="Update dependency versions to match installed ones",
    )
    parser.add_argument(
        "--tool",
        choices=["auto", "uv", "poetry"],
        default="auto",
        help="Specify tool for dependency management",
    )
    parser.add_argument(
        "--force-multiline-array-over-line-length",
        type=int,
        default=40,
        help="If true, makes arrays multiline if longer than ~50 chars",
    )
    parser.add_argument("paths", nargs="+", help="Files or directories to process")
    args = parser.parse_args()

    return CliArgs(
        fix=args.fix,
        tool=args.tool,
        update_requirements=args.update_requirements,
        force_multiline_array_over_line_length=args.force_multiline_array_over_line_length,
        paths=args.paths,
    )


def main():
    from .formatter import lint_toml_file
    from .deps_bumper import update_dependency_requirements

    args = _parse_args()
    logger.info(f"depsync {' '.join(sys.argv[1:])}")

    toml_files = find_toml_files(args.paths)
    if not toml_files:
        logger.warning("No TOML files found in the specified paths")
        return

    spacing_issues = []
    deps_issues = []
    for file_path in toml_files:
        if args.update_requirements:
            if update_dependency_requirements(
                file_path,
                tool=args.tool,
                fix=args.fix,
                force_multiline_array_over_line_length=args.force_multiline_array_over_line_length,
            ):
                logger.info("Dependency versions in %s are outdated", file_path)
                deps_issues.append(file_path)

        if lint_toml_file(file_path, fix=args.fix):
            spacing_issues.append(file_path)

    if spacing_issues:
        if args.fix:
            logger.info("Operator spacing issues fixed in:")
        else:
            logger.info("Operator spacing issues found in:")
        for f in spacing_issues:
            logger.info(f"  - {f}")

    if deps_issues:
        if args.fix:
            logger.info("Operator spacing issues fixed in:")
        else:
            logger.info("Operator spacing issues found in:")
        for f in deps_issues:
            logger.info(f"  - {f}")

    if not args.fix and (spacing_issues or deps_issues):
        logger.info("Please run `depsync --fix` to fix the issues")
        exit(1)


if __name__ == "__main__":
    main()
