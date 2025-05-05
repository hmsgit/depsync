import re
import copy
from typing import Final
from pathlib import Path

from tomlkit import array, dumps
from tomlkit.items import Array

from .utils import get_logger

logger = get_logger(__name__)

package_version_pattern: Final[re.Pattern] = re.compile(
    r'([^\s"\']+?)\s*(>=|<=|==|!=|~=|>|<)\s*([\w.*+-]+)'
)


def fix_operator_spacing(dep: str) -> str:
    return package_version_pattern.sub(r"\1 \2 \3", dep)


def lint_toml_file(path: Path, fix: bool = False) -> bool:
    original = path.read_text(encoding="utf-8")
    modified = fix_operator_spacing(original)
    changed = original != modified

    if changed and fix:
        path.write_text(modified, encoding="utf-8")

    return changed


def linebreak_array(doc: dict, max_line_length: int) -> dict:
    def reflow_array(container: dict, key: str, arr: Array):
        try:
            raw_values = [str(i.value) if hasattr(i, "value") else str(i) for i in arr.value]

            test_array = array(raw_values)
            test_array.multiline(False)
            if len(dumps(test_array).strip()) > max_line_length - len(key) - 3:  # 3 for ` = `
                arr.multiline(True)
            else:
                container[key] = test_array

        except Exception:
            """Don't change anything if you cannot parse it"""

    def visit(container: dict) -> dict:
        for k, v in list(container.items()):
            if isinstance(v, dict):
                visit(v)
            elif isinstance(v, Array) and all(isinstance(i, str) for i in v.value):
                reflow_array(container, k, v)

        return container

    return visit(copy.deepcopy(doc))


def enforce_double_quotes(toml: str) -> str:
    """
    Replace single-quoted TOML strings with double quotes,
    only if the string:
    - starts and ends with single quotes
    - contains no single or double quotes inside
    - is not inside an already double-quoted context
    """
    pattern = re.compile(
        r"""(?<!["'])  # not preceded by a quote
        '([^'"]*)'             # single-quoted string without internal quotes
        (?!["'])               # not followed by a quote
        """,
        re.VERBOSE,
    )

    return pattern.sub(r'"\1"', toml)
