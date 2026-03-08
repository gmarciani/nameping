# Copyright (c) 2026, Giacomo Marciani
# Licensed under the MIT License

"""Configuration schema for Nameping.

This schema is the single source of truth for:
- Parameter names (PascalCase)
- Parameter descriptions (used in prompts and generated config comments)
- Default values
- Validation rules

The schema parameters are used directly as Jinja2 template variables.
"""

from typing import Literal

from pydantic import BaseModel, Field


class Config(BaseModel):
    """Nameping configuration schema."""

    # Search Criteria
    TopLevelDomains: list[str] = Field(
        default=["com"],
        description="Top level domains to check.",
    )
    CompanyTypes: list[str] = Field(
        default=["llc"],
        description="Types of companies to check.",
    )
    CompanyRegistries: list[str] = Field(
        default=["delaware"],
        description="Registry to check company names from.",
    )

    # API client settings
    Timeout: int = Field(
        default=10,
        ge=1,
        description="Request timeout in seconds",
    )
    RetryMaxAttempts: int = Field(
        default=3,
        ge=0,
        description="Retry max attempts",
    )
    RetryBackoffFactor: float = Field(
        default=0.5,
        ge=0,
        description="Retry backoff factor",
    )
    OpenCorporatesApiKey: str | None = Field(
        default=None,
        description="API key for OpenCorporates",
    )

    # Output formatting
    OutputFormat: Literal["json", "csv", "table"] = Field(
        default="json",
        description="Default output format",
    )
    JsonIndent: int = Field(
        default=2,
        ge=0,
        description="JSON indentation",
    )
    TableStyle: Literal["ascii", "rounded", "minimal", "markdown"] = Field(
        default="rounded",
        description="Table style",
    )
