import re
from pathlib import Path

from .utils import get_logger

logger = get_logger(__name__)

PACKAGE_VERSION_PATTERN = re.compile(r'([^\s"\']+?)\s*(>=|<=|==|!=|~=|>|<)\s*([\w.*+-]+)')


def fix_operator_spacing(dep: str) -> str:
    return PACKAGE_VERSION_PATTERN.sub(r"\1 \2 \3", dep)


def lint_toml_file(path: Path, fix: bool = False) -> bool:
    original = path.read_text(encoding="utf-8")
    modified = fix_operator_spacing(original)
    changed = original != modified

    if changed and fix:
        path.write_text(modified, encoding="utf-8")

    return changed
