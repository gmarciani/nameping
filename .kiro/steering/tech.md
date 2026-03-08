# Tech Stack

- Language: Python >=3.12 (targets 3.12, 3.13, 3.14)
- Build system: setuptools with `pyproject.toml`
- CLI framework: Click
- Config validation: Pydantic v2
- Config file format: YAML (PyYAML)
- Templating: Jinja2
- HTTP client: requests
- WHOIS client: python-whois
- Type checking: mypy (strict — `disallow_untyped_defs = true`)
- Formatter: black (line-length 88, target py312)
- Linter: flake8 (max-line-length 88, ignores E203/E501)
- Testing: pytest with pytest-cov
- Task runner: tox
- Pre-commit hooks: trailing whitespace, black, AST checks, credential detection
- Docs: Sphinx with sphinx-click and RTD theme

## Common Commands

```shell
# Setup dev environment (pyenv + virtualenv)
make setup

# Run all checks (test + lint + type + coverage)
tox

# Run only tests
tox -e test

# Run only linting
tox -e lint

# Run only type checking
tox -e type

# Auto-format code
tox -e format

# Generate coverage report
tox -e coverage

# Build docs
make build-docs
```

## Code Style

- All functions must have type annotations (enforced by mypy)
- Use `str | None` union syntax (not `Optional`)
- Black formatting with 88-char line length
- Copyright header on every source file: `# Copyright (c) 2026, Giacomo Marciani`
- License header: `# Licensed under the MIT License`
- Module-level docstrings describing purpose
- Logging via `logging.getLogger(__name__)`
