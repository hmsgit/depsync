# fmttoml

`fmttoml` is a formatter and linter for TOML files that enforces consistent spacing around version operators (e.g., `>=`, `==`) in dependency specifications. It works well as a command-line tool and as a pre-commit hook.

---

## Features

- Ensures proper spacing around `>=`, `<=`, `==`, etc.
- Supports automatic fixing or lint-style checking.
- Pre-commit hook support for automated checks.

---

## Installation

Install via pip:

```bash
pip install .
```

Or install dependencies manually:

```bash
pip install -r requirements.txt
```

---

## CLI Usage

Run check:

```bash
python -m fmttoml.cli pyproject.toml
```

Auto-fix issues:

```bash
python -m fmttoml.cli --fix pyproject.toml
```

---

## Pre-commit Hook Setup

1. Install pre-commit if you haven't:

```bash
pip install pre-commit
```

2. Add this to your `.pre-commit-config.yaml`:

```yaml
repos:
-   repo: https://github.com/hmsgit/fmttoml
    rev: v0.1.0
    hooks:
    -   id: toml-sort  # Run toml-sort
        args: [--all, --in-place, --ignore-case, --sort-first, "name,version"]
    -   id: fmttoml  # Check
    -   id: fmttoml
        args: [--fix]

```

3. Install the hook:

```bash
pre-commit install
```

4. Run on all files:

```bash
pre-commit run --all-files
```

---

---

## License

MIT
