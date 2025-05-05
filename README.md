# depsync – TOML Dependency Formatter and Sync Tool

`depsync` is a command-line utility and pre-commit hook for managing and enforcing consistency in `.toml` files. It formats dependency version constraints, checks for outdated versions, optionally updates them based on the current environment, and supports pre-commit automation.

---

## Features

- `✓` Normalize spacing in dependency version constraints (e.g., `foo>=1.2.3` → `foo >= 1.2.3`)
- `✓` Automatically update `.toml` dependency versions to match installed ones
- `✓` Force inline arrays to multiline if they exceed a configured length
- `✓` Compatible with `poetry` and `uv` managed projects
- `✓` Integrates with pre-commit hooks for CI and developer workflows
- `!` `poetry`-based version bumping is not yet implemented
- `!` Only string-based dependency definitions are handled (tables are ignored)

---

## Installation

To install `depsync` and its dependencies:

```bash
pip install .
```

**Requirements:**

- Python 3.9+
- `tomlkit`
- `packaging`

---

## CLI Usage

```bash
depsync [OPTIONS] PATHS ...
```

### Options

| Option | Description |
|--------|-------------|
| `--fix` | Apply fixes in-place (default is check-only) |
| `--update-requirements` | Update dependency versions to match installed ones |
| `--tool auto|poetry|uv` | Choose dependency manager (default: `auto`) |
| `--force-multiline-array-over-line-length N` | Break arrays into multiple lines if they exceed `N` characters |
| `PATHS...` | One or more file or directory paths to search for `.toml` files |

### Examples

```bash
# Check for spacing and version issues
depsync pyproject.toml

# Fix issues and update dependency versions
depsync --fix --update-requirements .

# Format arrays as multiline if they exceed 60 characters
depsync --fix --force-multiline-array-over-line-length 60 .
```

---

## Using with toml-sort

To ensure the final `.toml` output is clean and consistently ordered, we recommend running [`toml-sort`](https://pypi.org/project/toml-sort/) **after** `depsync`:

```bash
toml-sort --in-place pyproject.toml
```

This can be automated via pre-commit as shown below.

---

## Pre-Commit Hook

Use `depsync` with [pre-commit](https://pre-commit.com) to automatically enforce formatting before each commit.

### 1. Install pre-commit

```bash
pip install pre-commit
```

### 2. Add hooks to `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/hmsgit/depsync
    rev: v0.1.2
    hooks:
    -   id: depsync
        args: [--fix, --update-requirements]
    -   id: toml-sort
        args: [--all, --in-place, --ignore-case, --sort-first, "name,version,project"]

```

### 3. Install the hooks

```bash
pre-commit install
```

### 4. Run the hooks manually

```bash
pre-commit run --all-files
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
