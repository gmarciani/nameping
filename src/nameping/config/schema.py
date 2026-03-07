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

import re
from typing import Literal, Any, get_type_hints, get_origin, get_args

from pydantic import BaseModel, Field, field_validator
from pydantic.fields import FieldInfo


class Config(BaseModel):
    """Nameping configuration schema."""

    # Search Criteria
    TopLevelDomains: list[str] = Field(
        default=["com", "us"],
        description="Top level domains to check.",
    )
    CompanyTypes: list[str] = Field(
        default=["llc", "corp"],
        description="Types of companies to check.",
    )

    # API client settings
    Timeout: int = Field(
        default=30,
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
    OutputFormat: Literal["json", "table", "yaml"] = Field(
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

    @classmethod
    def get_field_info(cls, field_name: str) -> FieldInfo | None:
        """Get field info for a specific field."""
        return cls.model_fields.get(field_name)

    @classmethod
    def get_field_description(cls, field_name: str) -> str:
        """Get the description for a specific field."""
        field_info = cls.get_field_info(field_name)
        if field_info and field_info.description:
            return field_info.description
        return ""

    @classmethod
    def get_field_default(cls, field_name: str) -> Any:
        """Get the default value for a specific field."""
        field_info = cls.get_field_info(field_name)
        if field_info:
            if field_info.default is not None:
                return field_info.default
            if field_info.default_factory is not None:
                return field_info.default_factory()  # type: ignore[call-arg]
        return None

    @classmethod
    def get_all_fields_metadata(cls) -> list[dict[str, Any]]:
        """Get metadata for all fields in schema order.

        Returns a list of dicts with: name, description, default, type_hint
        """
        from pydantic_core import PydanticUndefined

        fields_metadata = []
        type_hints = get_type_hints(cls)

        for field_name, field_info in cls.model_fields.items():
            # Handle default values properly
            if field_info.default is not PydanticUndefined:
                default = field_info.default
            elif field_info.default_factory is not None:
                default = field_info.default_factory()  # type: ignore[call-arg]
            else:
                default = None

            # Get type hint for display
            type_hint = type_hints.get(field_name)
            type_str = cls._format_type_hint(type_hint)

            fields_metadata.append(
                {
                    "name": field_name,
                    "description": field_info.description or "",
                    "default": default,
                    "type_hint": type_str,
                }
            )

        return fields_metadata

    @classmethod
    def _format_type_hint(cls, type_hint: Any) -> str:
        """Format a type hint for display in comments."""
        import types

        if type_hint is None:
            return "Any"

        origin = get_origin(type_hint)
        args = get_args(type_hint)

        if origin is Literal:
            return "one of: " + ", ".join(repr(a) for a in args)
        elif origin is list:
            return "list"
        elif origin is dict:
            return "dict"
        # Handle Union types (including Optional which is Union[X, None])
        elif origin is types.UnionType:
            # Filter out NoneType for cleaner display
            non_none_args = [a for a in args if a is not type(None)]
            if len(non_none_args) == 1:
                return cls._format_type_hint(non_none_args[0]) + " (optional)"
            return " | ".join(cls._format_type_hint(a) for a in non_none_args)
        elif hasattr(type_hint, "__name__"):
            return str(type_hint.__name__)
        else:
            # Handle str | None style unions in string form
            type_str = str(type_hint)
            if " | None" in type_str:
                return type_str.replace(" | None", "") + " (optional)"
            return type_str
