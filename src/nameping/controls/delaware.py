# Copyright (c) 2026, Giacomo Marciani
# Licensed under the MIT License

"""Delaware Division of Corporations company name search."""

import logging
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)

DELAWARE_SEARCH_URL = (
    "https://icis.corp.delaware.gov/ecorp/entitysearch/namesearch.aspx"
)


@dataclass
class CompanyResult:
    """Result of a company name availability check."""

    name: str
    company_type: str
    available: bool
    error: str | None = None


def check_company(
    name: str,
    company_type: str,
    timeout: int = 30,
    retry_max_attempts: int = 3,
    retry_backoff_factor: float = 0.5,
) -> CompanyResult:
    """Check if a company name is available in the Delaware registry.

    Searches the Delaware Division of Corporations ECORP entity search.
    A name is considered available if no exact match is found.

    Args:
        name: Company name to search for.
        company_type: Company type suffix (e.g. "llc", "corp").
        timeout: Request timeout in seconds.
        retry_max_attempts: Maximum number of retry attempts.
        retry_backoff_factor: Backoff factor between retries.

    Returns:
        CompanyResult with availability info.
    """
    import time

    full_name = f"{name} {company_type}".strip().upper()

    for attempt in range(max(1, retry_max_attempts)):
        try:
            with requests.Session() as session:
                # First GET to obtain viewstate tokens
                resp = session.get(DELAWARE_SEARCH_URL, timeout=timeout)
                resp.raise_for_status()

                # Parse hidden form fields for ASP.NET postback
                from html.parser import HTMLParser

                hidden_fields: dict[str, str] = {}

                class _HiddenFieldParser(HTMLParser):
                    def handle_starttag(self, tag: str, attrs: list) -> None:
                        if tag == "input":
                            attr_dict = dict(attrs)
                            if attr_dict.get("type", "").lower() == "hidden":
                                field_name = attr_dict.get("name", "")
                                field_value = attr_dict.get("value", "")
                                if field_name:
                                    hidden_fields[field_name] = field_value

                _HiddenFieldParser().feed(resp.text)

                # POST the search form
                form_data = {
                    **hidden_fields,
                    "ctl00$ContentPlaceHolder1$frmEntityName": full_name,
                    "ctl00$ContentPlaceHolder1$frmFileNumber": "",
                    "ctl00$ContentPlaceHolder1$btnSubmit": "Search",
                }

                search_resp = session.post(
                    DELAWARE_SEARCH_URL,
                    data=form_data,
                    timeout=timeout,
                )
                search_resp.raise_for_status()

                # Check if the exact name appears in results
                available = full_name not in search_resp.text.upper()

                return CompanyResult(
                    name=full_name,
                    company_type=company_type,
                    available=available,
                )

        except Exception as e:
            logger.debug(
                "Delaware lookup failed for %s (attempt %d): %s",
                full_name,
                attempt + 1,
                e,
            )
            if attempt + 1 < retry_max_attempts:
                time.sleep(retry_backoff_factor * (2**attempt))
                continue
            return CompanyResult(
                name=full_name,
                company_type=company_type,
                available=False,
                error=str(e),
            )

    # Should not reach here, but just in case
    return CompanyResult(
        name=full_name,
        company_type=company_type,
        available=False,
        error="Max retries exceeded",
    )
