# Copyright (c) 2026, Giacomo Marciani
# Licensed under the MIT License

"""Main CLI module for Nameping."""

import click
import logging
from nameping.constants import __version__
from nameping.commands.config import config


@click.group(
    help="Nameping - Check name availability across domains and business registries."
)
@click.version_option(version=__version__, prog_name="nameping")
@click.option("--debug", "-d", is_flag=True, help="Enable debug output")
@click.pass_context
def main(ctx: click.Context, debug: bool) -> None:
    """Main CLI entry point."""
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug

    # Configure logging
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    logging.Formatter.converter = lambda *args: __import__("time").gmtime()


main.add_command(config)


if __name__ == "__main__":
    main()
