from __future__ import annotations

import re
import copy
import subprocess
from abc import ABC, abstractmethod
from typing import Type, Literal, Iterator
from pathlib import Path
from functools import reduce

import tomlkit
from packaging.version import Version, InvalidVersion

from .utils import get_logger
from .formatter import linebreak_array, enforce_double_quotes

logger = get_logger(__name__)


class VersionUpdater(ABC):
    def __init__(self): ...

    @abstractmethod
    def paths(self) -> tuple[str, ...]: ...

    @abstractmethod
    def update_table(self, table, project_dir): ...

    def update(self, doc: dict, fix: bool = False, project_dir: Path | None = None) -> bool:
        changed = False
        for path in yielder(doc, self.paths()):
            doc_section = get_nested(doc, path)
            if doc_section is None:
                logger.info(f"Cannot find {path}")
                continue

            updated_section = self.update_table(doc_section, project_dir=project_dir)
            if updated_section != doc_section:
                changed = True
                if fix:
                    set_nested(doc, path, updated_section)

        return changed

    def check(self, doc: dict) -> bool:
        return self.update(doc, fix=False)

    @staticmethod
    def get_pkg_version_cmd(package_name: str, project_dir: Path | None = None) -> list[str]:
        return [
            "python",
            "-c",
            f"import importlib.metadata as m; print(m.version('{package_name}'))",
        ]

    def get_installed_version(
        self, package_name: str, project_dir: Path | None = None
    ) -> str | None:
        try:
            result = subprocess.run(
                self.get_pkg_version_cmd(package_name, project_dir=project_dir),
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    @staticmethod
    def instance(doc: dict, tool: Literal["poetry", "uv"] | None = None) -> VersionUpdater:
        tool = (
            tool
            if tool
            else (
                "poetry"
                if "tool" in doc and "poetry" in doc["tool"]
                else "uv"
                if "tool" in doc and "uv" in doc["tool"]
                else tool
            )
        )

        if not tool:
            logger.error("Cannot detect project tool (poetry or uv). Use --tool to specify.")
            raise TypeError("Cannot detect project tool (poetry or uv). Use --tool to specify.")

        updater_cls: dict[str, Type[VersionUpdater]] = {
            "uv": UvVersionUpdater,
            "poetry": PoetryVersionUpdater,
        }

        return updater_cls[tool]()


class PoetryVersionUpdater(VersionUpdater):
    def paths(self) -> tuple[str, ...]:
        return (
            "tool.poetry.dependencies",
            "tool.poetry.dev-dependencies",
        )

    @staticmethod
    def get_pkg_version_cmd(package_name: str, project_dir: Path | None = None) -> list[str]:
        return ["poetry", "run"] + VersionUpdater.get_pkg_version_cmd(package_name)

    @staticmethod
    def update_table(self, table: dict, project_dir: Path | None = None) -> dict:
        copy.deepcopy(table)
        raise NotImplementedError
        # for name, value in table.items():
        #     if isinstance(value, str):
        #         prefix, base_ver, parts = parse_version_string(value)
        #         installed = self.get_installed_version(name)
        #         if installed:
        #             try:
        #                 if Version(installed) > Version(base_ver):
        #                     new_ver = format_version(installed, parts)
        #                     new_table[name] = f"{prefix}{new_ver}"
        #             except InvalidVersion:
        #                 logger.warning("Could not compare versions for %s", name)
        # return new_table


class UvVersionUpdater(VersionUpdater):
    def paths(self) -> tuple[str, ...]:
        return (
            "project.dependencies",
            "project.optional-dependencies.*",
            "tool.uv.dev-dependencies",
        )

    @staticmethod
    def get_pkg_version_cmd(package_name: str, project_dir: Path | None = None) -> list[str]:
        uv_run = ["uv", "--project", str(project_dir), "run"] if project_dir else ["uv", "run"]
        return uv_run + VersionUpdater.get_pkg_version_cmd(package_name)

    def update_table(self, table: list[str], project_dir: Path | None = None) -> list[str]:
        new_list = table.copy()
        for i, dep_str in enumerate(table):
            if not isinstance(dep_str, str):
                logger.info(f"Not a string: {dep_str}")
                continue
            match = re.match(r"^([a-zA-Z0-9_.\-]+)(\[[^\]]+\])?\s*(.*)$", dep_str)
            if not match:
                logger.info(
                    f"Doesn't match <name>[<extras>] <operator> <version> format: {dep_str}"
                )
                continue

            pkg, extras, ver = (
                match.group(i).strip() if match.group(i) else "" for i in range(1, 4)
            )
            comparator, required, parts = parse_version_string(ver)
            installed = self.get_installed_version(package_name=pkg, project_dir=project_dir)

            if not installed:
                logger.info(f"No installed version for {dep_str}")
                continue

            try:
                if Version(".".join(installed.split(".")[:parts])) > Version(required):
                    new_ver = format_version(installed, parts)
                    new_list[i] = f"{pkg}{extras} {comparator} {new_ver}".strip()
                    logger.info(
                        f"Outdated requirement {pkg + extras:<25} "
                        f"{comparator + required:<10} ->   {comparator}{new_ver}"
                    )
            except InvalidVersion:
                logger.warning("Could not compare versions for %s", pkg)

        return new_list


def update_dependency_requirements(
    file_path: Path,
    fix: bool = False,
    tool: Literal["poetry", "uv", "auto"] = "auto",
    force_multiline_array_over_line_length: int | None = None,
) -> bool:
    content = file_path.read_text(encoding="utf-8")
    doc = tomlkit.parse(content)

    updater = VersionUpdater.instance(doc, tool=None if tool == "auto" else tool)
    changed = updater.update(doc, fix, project_dir=file_path.parent)

    # if changed and fix:
    toml_text = tomlkit.dumps(
        linebreak_array(doc, max_line_length=force_multiline_array_over_line_length)
        if force_multiline_array_over_line_length
        else doc
    )
    file_path.write_text(enforce_double_quotes(toml_text), encoding="utf-8")

    return changed


def parse_version_string(version_str: str) -> tuple[str, str, int]:
    match = re.match(r"^(>=|<=|==|!=|~=|\^|>|<)?\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?", version_str)
    if not match:
        return "", version_str, 0
    prefix = match.group(1) or ""
    parts = match.groups()[1:]
    version_only = ".".join(p for p in parts if p is not None)
    count = sum(1 for p in parts if p is not None)
    return prefix, version_only, count


def format_version(version: str, parts_count: int) -> str:
    return ".".join(version.split(".")[:parts_count])


def get_nested(data, keys: str, default=None):
    try:
        return reduce(lambda d, k: d[k], keys.split("."), data)
    except (KeyError, TypeError):
        return default


def set_nested(data, keys: str, value):
    parts = keys.split(".")
    current = data
    for key in parts[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[parts[-1]] = value


def yielder(doc: dict, paths: tuple[str, ...]) -> Iterator[str]:
    for path in paths:
        if not path.endswith(".*"):
            yield path
        else:
            base_path = path[:-2]
            dep_table = get_nested(doc, base_path)
            if isinstance(dep_table, dict):
                yield from [f"{base_path}.{key}" for key in dep_table]
