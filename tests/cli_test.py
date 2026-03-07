# Copyright (c) 2026, Giacomo Marciani
# Licensed under the MIT License

"""Tests for the main CLI module."""

from click.testing import CliRunner

from nameping.cli import main


def test_main_help():
    """Test main command help."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Nameping" in result.output


def test_version():
    """Test version option."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
