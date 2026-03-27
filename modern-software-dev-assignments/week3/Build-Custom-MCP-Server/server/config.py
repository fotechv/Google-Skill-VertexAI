"""
Configuration — loads from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    # OpenWeatherMap
    owm_api_key: str
    owm_base_url: str = "https://api.openweathermap.org/data/2.5"
    owm_geo_url: str = "http://api.openweathermap.org/geo/1.0"
    owm_air_url: str = "http://api.openweathermap.org/data/2.5/air_pollution"

    # MCP Server auth
    mcp_api_key: str | None = None  # If set, clients must pass this key
    require_auth: bool = False

    # HTTP client
    request_timeout: int = 10          # seconds
    max_retries: int = 3
    retry_backoff_base: float = 1.5    # exponential backoff multiplier

    # Rate-limit awareness (OWM free tier: 60 calls/min)
    rate_limit_calls: int = 55         # conservative limit
    rate_limit_window: int = 60        # seconds


def load_settings() -> Settings:
    owm_key = os.getenv("OWM_API_KEY", "")
    if not owm_key:
        import sys
        print(
            "ERROR: OWM_API_KEY environment variable is not set.\n"
            "Get a free key at https://openweathermap.org/api",
            file=sys.stderr,
        )
        # Don't exit — let the server start so Claude Desktop can load it;
        # tools will return a helpful error message instead.

    mcp_key = os.getenv("MCP_API_KEY", None)

    return Settings(
        owm_api_key=owm_key,
        mcp_api_key=mcp_key,
        require_auth=bool(mcp_key),
    )


settings = load_settings()
