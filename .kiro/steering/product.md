# Product

Nameping is a CLI tool that checks name availability across domains (via WHOIS) and business registries (currently Delaware Division of Corporations).

Key capabilities:
- Domain availability lookup across multiple TLDs
- Company name availability search in the Delaware registry
- Batch processing from comma-separated input or files
- Output in JSON, CSV, or markdown table format (console and file)
- Configurable via `~/.nameping/nameping.yaml` with Pydantic-validated schema defaults
- Retry logic with exponential backoff for external lookups

The CLI entry point is `nameping` with subcommands: `check-domain`, `check-company`, and `config`.
