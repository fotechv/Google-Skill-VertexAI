"""
Authentication — API key verification for MCP server protection.

When MCP_API_KEY is set in the environment, every tool call must include
a matching `api_key` argument. This follows the MCP Authorization spec
for STDIO servers (environment-variable-based secrets).
"""

import hashlib
import hmac
import logging

from config import settings

log = logging.getLogger("weather-mcp.auth")


def verify_api_key(provided_key: str | None) -> bool:
    """
    Constant-time comparison to prevent timing attacks.
    Returns True if auth is disabled OR the key matches.
    """
    if not settings.require_auth:
        return True

    if not provided_key:
        log.warning("Auth failed: no api_key provided in tool arguments")
        return False

    expected = settings.mcp_api_key or ""

    # Use hmac.compare_digest for constant-time comparison
    valid = hmac.compare_digest(
        hashlib.sha256(provided_key.encode()).digest(),
        hashlib.sha256(expected.encode()).digest(),
    )

    if not valid:
        log.warning("Auth failed: invalid api_key provided")
    else:
        log.debug("Auth succeeded")

    return valid
