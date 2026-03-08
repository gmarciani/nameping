# Copyright (c) 2026, Giacomo Marciani
# Licensed under the MIT License

"""Check command for domain availability."""

import logging
from pathlib import Path

import click

from nameping.commands.common import (
    collect_names,
    format_results,
    prepare_output_file,
    stream_entry,
)
from nameping.config.configuration import load_config
from nameping.controls.domains import check_domain

logger = logging.getLogger(__name__)


@click.command(
    name="check-domain", help="Check domain availability for the given names via WHOIS."
)
@click.option(
    "--names",
    "-n",
    default=None,
    help="Comma-separated list of names to check.",
)
@click.option(
    "--file",
    "-f",
    "file_path",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to a file with one name per line.",
)
@click.option(
    "--tld",
    "-t",
    default=None,
    help="Comma-separated top-level domain(s) to check (e.g. com,net). "
    "Defaults to TopLevelDomains from config.",
)
@click.option(
    "--from",
    "from_index",
    default=None,
    type=int,
    help="1-based start index into the name list (inclusive).",
)
@click.option(
    "--to",
    "to_index",
    default=None,
    type=int,
    help="1-based end index into the name list (inclusive).",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    default=None,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Path to a file where results will be written.",
)
@click.option(
    "--exclude-taken",
    is_flag=True,
    default=False,
    help="Only include available names in the output.",
)
@click.option(
    "--output-format",
    "output_format",
    default=None,
    type=click.Choice(["json", "csv", "table"], case_sensitive=False),
    help="Output format (json, csv, table). Overrides OutputFormat from config.",
)
@click.pass_context
def check_domain_cmd(
    ctx: click.Context,
    names: str | None,
    file_path: Path | None,
    tld: str | None,
    from_index: int | None,
    to_index: int | None,
    exclude_taken: bool,
    output_path: Path | None,
    output_format: str | None,
) -> None:
    """Check domain availability for each name + TLD combination."""
    all_names = collect_names(names, file_path)

    # Apply --from / --to slicing (1-based, inclusive)
    start = (from_index - 1) if from_index is not None else None
    end = to_index if to_index is not None else None
    all_names = all_names[start:end]

    if not all_names:
        raise click.UsageError("At least one of --names or --file must be provided.")

    cfg = load_config()
    timeout: int = cfg.get("Timeout", 30)
    retry_max: int = cfg.get("RetryMaxAttempts", 3)
    retry_backoff: float = cfg.get("RetryBackoffFactor", 0.5)
    tlds = (
        [t.strip() for t in tld.split(",") if t.strip()]
        if tld
        else cfg.get("TopLevelDomains", ["com"])
    )
    fmt = output_format or cfg.get("OutputFormat", "json")

    # Columns for csv/table streaming
    domain_columns = [
        "name",
        "tld",
        "domain",
        "available",
        "registrar",
        "expiration_date",
        "error",
    ]

    total = len(all_names) * len(tlds)
    completed = 0
    pct_width = 3  # "100" is 3 chars
    total_width = len(str(total))

    # Prepare output file if requested (table is written at the end)
    out_file = None
    if output_path:
        if not prepare_output_file(output_path):
            return
        if fmt != "table":
            out_file = open(output_path, "w")
            if fmt == "json":
                out_file.write("[\n")
            elif fmt == "csv":
                out_file.write(",".join(domain_columns) + "\n")

    results = []
    written = 0
    for name in all_names:
        for t in tlds:
            domain = f"{name}.{t}"
            logger.debug("Checking %s", domain)
            result = check_domain(
                domain,
                timeout=timeout,
                retry_max_attempts=retry_max,
                retry_backoff_factor=retry_backoff,
            )
            entry = {
                "name": name,
                "tld": t,
                "domain": result.domain,
                "available": result.available,
                **({"registrar": result.registrar} if result.registrar else {}),
                **(
                    {"expiration_date": result.expiration_date}
                    if result.expiration_date
                    else {}
                ),
                **({"error": result.error} if result.error else {}),
            }

            status = "✓" if result.available else "✗"
            if result.error:
                status = "⚠"

            completed += 1
            pct = completed * 100 // total
            logger.info(
                "[%s%% - %s/%s] %s %s",
                str(pct).rjust(pct_width),
                str(completed).rjust(total_width),
                total,
                status,
                domain,
            )

            # Filter if --exclude-taken
            if not exclude_taken or result.available:
                results.append(entry)
                if out_file:
                    stream_entry(out_file, entry, fmt, written, domain_columns)
                written += 1

    if out_file:
        if fmt == "json":
            out_file.write("\n]\n")
        out_file.close()

    # For table format, write the full aligned table at the end
    if output_path and fmt == "table":
        output_path.write_text(format_results(results, fmt) + "\n")

    if output_path:
        click.echo(f"Results written to {output_path}", err=True)

    click.echo(format_results(results, fmt))
