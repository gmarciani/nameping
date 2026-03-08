# Project Structure

```
src/nameping/              # Main package (src layout)
  cli.py                   # Click CLI entry point and command group
  constants.py             # Version and global constants
  commands/                # CLI subcommands
    check_domain.py        # `check-domain` command
    check_company.py       # `check-company` command
    config.py              # `config` command group (set/get/unset/show/reset)
    common.py              # Shared CLI utilities (name collection, output formatting, file streaming)
  config/                  # Configuration layer
    schema.py              # Pydantic Config model — single source of truth for defaults and validation
    configuration.py       # Load/save YAML config from ~/.nameping/nameping.yaml
  controls/                # Business logic / external service integrations
    domains.py             # WHOIS domain availability checker
    companies.py           # Delaware registry company name checker

tests/                     # Test suite
  cli_test.py              # CLI-level tests
  nameping/                # Unit tests mirroring src structure
    constants_test.py

docs/                      # Sphinx documentation source
resources/                 # Static resources (branding, etc.)
```

## Conventions

- Source lives under `src/` (PEP 517 src layout)
- Test files use `_test.py` suffix (not `test_` prefix)
- Controls layer handles external API calls with retry + timeout patterns
- Commands layer wires CLI options to controls and formats output
- Config schema uses PascalCase keys (e.g. `TopLevelDomains`, `OutputFormat`)
- Dataclasses for result types in controls (`DomainResult`, `CompanyResult`)
- Version is read from the `VERSION` file at the project root
