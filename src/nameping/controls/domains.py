# Copyright (c) 2026, Giacomo Marciani
# Licensed under the MIT License

"""WHOIS domain availability checker."""

import logging
import socket
from dataclasses import dataclass

import whois  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


@dataclass
class DomainResult:
    """Result of a domain availability check."""

    domain: str
    available: bool
    registrar: str | None = None
    expiration_date: str | None = None
    error: str | None = None


def check_domain(
    domain: str,
    timeout: int = 30,
    retry_max_attempts: int = 3,
    retry_backoff_factor: float = 0.5,
) -> DomainResult:
    """Check if a domain is available via WHOIS lookup.

    Args:
        domain: Fully qualified domain name (e.g. "example.com").
        timeout: Socket timeout in seconds.
        retry_max_attempts: Maximum number of retry attempts.
        retry_backoff_factor: Backoff factor between retries.

    Returns:
        DomainResult with availability info.
    """
    import time

    old_timeout = socket.getdefaulttimeout()
    for attempt in range(max(1, retry_max_attempts)):
        try:
            socket.setdefaulttimeout(timeout)
            w = whois.whois(domain)

            # A domain is considered registered if it has a domain_name
            if w.domain_name is None:
                return DomainResult(domain=domain, available=True)

            registrar = w.registrar if isinstance(w.registrar, str) else None

            expiration = None
            if w.expiration_date is not None:
                exp = w.expiration_date
                if isinstance(exp, list):
                    exp = exp[0]
                expiration = str(exp)

            return DomainResult(
                domain=domain,
                available=False,
                registrar=registrar,
                expiration_date=expiration,
            )
        except whois.exceptions.WhoisDomainNotFoundError:
            return DomainResult(domain=domain, available=True)
        except whois.exceptions.PywhoisError:
            # Generic whois error — treat as available (no match)
            return DomainResult(domain=domain, available=True)
        except Exception as e:
            logger.debug(
                "WHOIS lookup failed for %s (attempt %d): %s",
                domain,
                attempt + 1,
                e,
            )
            if attempt + 1 < retry_max_attempts:
                time.sleep(retry_backoff_factor * (2**attempt))
                continue
            return DomainResult(domain=domain, available=False, error=str(e))
        finally:
            socket.setdefaulttimeout(old_timeout)

    # Should not reach here, but just in case
    return DomainResult(domain=domain, available=False, error="Max retries exceeded")
