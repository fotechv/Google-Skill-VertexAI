"""
HTTP client wrapper — retry logic, timeouts, rate-limit awareness.
"""

import asyncio
import logging
import time
from collections import deque
from typing import Any

import httpx

from config import settings

log = logging.getLogger("weather-mcp.http")

# ── Simple in-process rate limiter ──────────────────────────────────────────
_call_timestamps: deque[float] = deque()


def _check_rate_limit() -> tuple[bool, float]:
    """
    Returns (ok, retry_after_seconds).
    Prunes timestamps older than the window before checking.
    """
    now = time.monotonic()
    window_start = now - settings.rate_limit_window

    # Drop old entries
    while _call_timestamps and _call_timestamps[0] < window_start:
        _call_timestamps.popleft()

    if len(_call_timestamps) >= settings.rate_limit_calls:
        oldest = _call_timestamps[0]
        retry_after = settings.rate_limit_window - (now - oldest) + 0.5
        return False, retry_after

    _call_timestamps.append(now)
    return True, 0.0


# ── Main fetch helper ────────────────────────────────────────────────────────
async def fetch_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    """
    Fetches a JSON endpoint with:
    - Rate-limit pre-check
    - Configurable timeout
    - Exponential backoff retries on transient errors
    - Structured error propagation
    """
    ok, retry_after = _check_rate_limit()
    if not ok:
        raise RateLimitError(
            f"Rate limit reached. Please wait ~{retry_after:.0f}s before retrying."
        )

    last_exc: Exception | None = None

    for attempt in range(1, settings.max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
                log.debug("GET %s (attempt %d)", url, attempt)
                response = await client.get(url, params=params)

            if response.status_code == 429:
                wait = float(response.headers.get("Retry-After", settings.retry_backoff_base ** attempt))
                log.warning("429 rate limit from upstream. Waiting %.1fs", wait)
                await asyncio.sleep(wait)
                continue

            if response.status_code == 401:
                raise AuthError("Invalid OpenWeatherMap API key. Check OWM_API_KEY.")

            if response.status_code == 404:
                raise NotFoundError("Location not found. Try a more specific city name.")

            response.raise_for_status()
            data = response.json()

            # OWM returns cod=404 inside 200 responses for some endpoints
            if isinstance(data, dict) and data.get("cod") not in (None, 200, "200"):
                msg = data.get("message", "Unknown API error")
                raise APIError(f"OpenWeatherMap error: {msg}")

            return data

        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            last_exc = exc
            wait = settings.retry_backoff_base ** attempt
            log.warning("Network error on attempt %d: %s. Retrying in %.1fs", attempt, exc, wait)
            await asyncio.sleep(wait)

        except (RateLimitError, AuthError, NotFoundError, APIError):
            raise  # Don't retry these

        except httpx.HTTPStatusError as exc:
            last_exc = exc
            wait = settings.retry_backoff_base ** attempt
            log.warning("HTTP %d on attempt %d. Retrying in %.1fs", exc.response.status_code, attempt, wait)
            await asyncio.sleep(wait)

    raise NetworkError(
        f"Failed after {settings.max_retries} attempts. Last error: {last_exc}"
    )


# ── Custom exceptions ────────────────────────────────────────────────────────
class WeatherMCPError(Exception):
    """Base exception for all weather MCP errors."""


class RateLimitError(WeatherMCPError):
    pass


class AuthError(WeatherMCPError):
    pass


class NotFoundError(WeatherMCPError):
    pass


class APIError(WeatherMCPError):
    pass


class NetworkError(WeatherMCPError):
    pass
