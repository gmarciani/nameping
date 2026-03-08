# Copyright (c) 2026, Giacomo Marciani
# Licensed under the MIT License

"""Configuration commands for Nameping."""

import click
import logging
import json
from nameping.config.configuration import (
    load_config,
    save_config,
    get_config_path,
)

logger = logging.getLogger(__name__)


@click.group(help="Manage configurations.")
def config_cmd() -> None:
    """Config command group implementation."""


@config_cmd.command(help="Set a configuration value.")
@click.argument("key")
@click.argument("value")
def set_cmd(key: str, value: str) -> None:
    """Set command implementation."""
    cfg = load_config()
    old_value = cfg.get(key)
    cfg[key] = value
    save_config(cfg)

    result = {"key": key, "value": value, "oldValue": old_value}
    print(json.dumps(result, indent=2))


@config_cmd.command(help="Get a configuration value.")
@click.argument("key")
def get_cmd(key: str) -> None:
    """Get command implementation."""
    cfg = load_config()
    if key not in cfg:
        logger.error(f"Unknown configuration key '{key}'")
        return

    result = {"key": key, "value": cfg[key]}
    print(json.dumps(result, indent=2))


@config_cmd.command(help="Unset a configuration value (set to None).")
@click.argument("key")
def unset_cmd(key: str) -> None:
    """Unset command implementation."""
    cfg = load_config()
    if key not in cfg:
        logger.error(f"Unknown configuration key '{key}'")
        return

    old_value = cfg.get(key)
    cfg[key] = None
    save_config(cfg)

    result = {"key": key, "value": None, "oldValue": old_value}
    print(json.dumps(result, indent=2))


@config_cmd.command(help="Show all configuration values as JSON.")
def show_cmd() -> None:
    """Show command implementation."""
    cfg = load_config()
    print(json.dumps(cfg, indent=2))


@config_cmd.command(
    help="Reset configuration to defaults and delete local config file."
)
def reset_cmd() -> None:
    """Reset command implementation."""
    cfg = load_config()
    print(json.dumps(cfg, indent=2))

    config_path = get_config_path()
    if config_path.exists():
        config_path.unlink()
