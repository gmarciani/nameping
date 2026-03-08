# Copyright (c) 2026, Giacomo Marciani
# Licensed under the MIT License

"""Check command for company name availability."""

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
from nameping.controls.companies import check_company

logger = logging.getLogger(__name__)


SUPPORTED_REGISTRIES = {"delaware"}


@click.command(
    name="check-company",
    help="Check company name availability in business registries.",
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
    "--company-type",
    "-c",
    default=None,
    help="Comma-separated company type(s) to check (e.g. llc,corp). "
    "Defaults to CompanyTypes from config.",
)
@click.option(
    "--registries",
    "-r",
    default=None,
    help="Comma-separated registries to search (e.g. delaware). "
    "Defaults to CompanyRegistries from config.",
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
    "--exclude-taken",
    is_flag=True,
    default=False,
    help="Only include available names in the output.",
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
    "--output-format",
    "output_format",
    default=None,
    type=click.Choice(["json", "csv", "table"], case_sensitive=False),
    help="Output format (json, csv, table). Overrides OutputFormat from config.",
)
@click.pass_context
def check_company_cmd(
    ctx: click.Context,
    names: str | None,
    file_path: Path | None,
    company_type: str | None,
    registries: str | None,
    from_index: int | None,
    to_index: int | None,
    exclude_taken: bool,
    output_path: Path | None,
    output_format: str | None,
) -> None:
    """Check company name availability for each name + type + registry combination."""
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
    fmt = output_format or cfg.get("OutputFormat", "json")
    types = (
        [t.strip() for t in company_type.split(",") if t.strip()]
        if company_type
        else cfg.get("CompanyTypes", ["llc"])
    )
    registry_list = (
        [r.strip().lower() for r in registries.split(",") if r.strip()]
        if registries
        else cfg.get("CompanyRegistries", ["delaware"])
    )

    # Validate registries
    unsupported = set(registry_list) - SUPPORTED_REGISTRIES
    if unsupported:
        raise click.UsageError(
            f"Unsupported registry: {', '.join(sorted(unsupported))}. "
            f"Supported registries: {', '.join(sorted(SUPPORTED_REGISTRIES))}."
        )

    # Columns for csv/table streaming
    company_columns = [
        "name",
        "company_type",
        "registry",
        "full_name",
        "available",
        "error",
    ]

    total = len(all_names) * len(registry_list) * len(types)
    completed = 0
    pct_width = 3
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
                out_file.write(",".join(company_columns) + "\n")

    results = []
    written = 0
    for name in all_names:
        for registry in registry_list:
            for ct in types:
                logger.debug("Checking %s %s in %s", name, ct, registry)
                if registry == "delaware":
                    result = check_company(
                        name,
                        ct,
                        timeout=timeout,
                        retry_max_attempts=retry_max,
                        retry_backoff_factor=retry_backoff,
                    )
                entry = {
                    "name": name,
                    "company_type": ct,
                    "registry": registry,
                    "full_name": result.name,
                    "available": result.available,
                    **({"error": result.error} if result.error else {}),
                }

                status = "✓" if result.available else "✗"
                if result.error:
                    status = "⚠"

                completed += 1
                pct = completed * 100 // total
                logger.info(
                    "[%s%% - %s/%s] %s %s %s (%s)",
                    str(pct).rjust(pct_width),
                    str(completed).rjust(total_width),
                    total,
                    status,
                    name,
                    ct,
                    registry,
                )

                # Filter if --exclude-taken
                if not exclude_taken or result.available:
                    results.append(entry)
                    if out_file:
                        stream_entry(out_file, entry, fmt, written, company_columns)
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
