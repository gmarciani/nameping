# Copyright (c) 2026, Giacomo Marciani
# Licensed under the MIT License

"""Constants for Nameping."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("nameping")
except PackageNotFoundError:
    __version__ = "0.0.0"

CONFIG_FILE_NAME = "nameping.yaml"
