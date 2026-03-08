# Copyright (c) 2026, Giacomo Marciani
# Licensed under the MIT License

"""Shared utilities for check commands."""

import csv
import io
import json
from pathlib import Path

import click


def prepare_output_file(output_path: Path) -> bool:
    """Check if output file can be written, prompting for overwrite if it exists.

    Returns True if writing should proceed, False if the user declined.
    """
    if output_path.exists():
        if not click.confirm(f"File {output_path} already exists. Overwrite?"):
            click.echo("Aborted.")
            return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return True


def format_results(results: list[dict], fmt: str) -> str:
    """Format a list of result dicts as json, csv, or table."""
    if fmt == "json":
        return json.dumps(results, indent=2)

    if not results:
        return ""

    # Collect all keys across results for consistent columns
    columns = list(dict.fromkeys(k for r in results for k in r))

    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)
        return buf.getvalue().rstrip("\n")

    # table (markdown format)
    col_widths = {c: len(c) for c in columns}
    for r in results:
        for c in columns:
            col_widths[c] = max(col_widths[c], len(str(r.get(c, ""))))

    header = "| " + " | ".join(c.ljust(col_widths[c]) for c in columns) + " |"
    separator = "| " + " | ".join("-" * col_widths[c] for c in columns) + " |"
    rows = [
        "| "
        + " | ".join(str(r.get(c, "")).ljust(col_widths[c]) for c in columns)
        + " |"
        for r in results
    ]
    return "\n".join([header, separator, *rows])


def stream_entry(
    out_file: io.TextIOWrapper,
    entry: dict,
    fmt: str,
    written: int,
    columns: list[str],
) -> None:
    """Write a single entry to the output file in the given format.

    Note: table format is not streamed — it requires the full dataset
    for proper column alignment. Use format_results at the end instead.
    """
    if fmt == "json":
        prefix = "  " if written == 0 else ",\n  "
        out_file.write(prefix + json.dumps(entry))
    elif fmt == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=columns)
        writer.writerow(entry)
        out_file.write(buf.getvalue())
    # table is written at the end via format_results
    out_file.flush()


def collect_names(names: str | None, file: Path | None) -> list[str]:
    """Build a deduplicated list of names from --names and --file.

    Names are normalized: whitespace is removed and the result is lowercased.
    """
    collected: list[str] = []

    if names:
        collected.extend(n.strip() for n in names.split(",") if n.strip())

    if file:
        text = file.read_text()
        collected.extend(line.strip() for line in text.splitlines() if line.strip())

    # Normalize: remove spaces and lowercase
    collected = [n.replace(" ", "").lower() for n in collected]

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for n in collected:
        if n not in seen:
            seen.add(n)
            unique.append(n)
    return unique
