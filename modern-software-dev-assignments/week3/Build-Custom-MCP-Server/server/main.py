"""
Weather MCP Server — OpenWeatherMap Integration
STDIO transport with API key authentication.
"""

import asyncio
import logging
import sys

import mcp.server.stdio
from mcp.server import Server

from tools.current_weather import handle_get_current_weather
from tools.forecast import handle_get_forecast
from tools.air_quality import handle_get_air_quality
from tools.weather_alerts import handle_get_weather_alerts
from auth import verify_api_key
from config import settings
from mcp_definitions import TOOLS, RESOURCES, PROMPTS, handle_resource, handle_prompt

# ── Logging: MUST go to stderr for STDIO servers (never stdout) ──────────────
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("weather-mcp")

# ── Server instance ──────────────────────────────────────────────────────────
server = Server("weather-mcp")


# ── Tool handlers ────────────────────────────────────────────────────────────
@server.list_tools()
async def list_tools():
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    log.info("Tool called: %s with args: %s", name, arguments)

    # Auth check: verify MCP_API_KEY if protection is enabled
    if settings.require_auth:
        client_key = arguments.pop("api_key", None)
        if not verify_api_key(client_key):
            from mcp.types import TextContent
            return [TextContent(type="text", text="❌ Unauthorized: invalid or missing api_key.")]

    match name:
        case "get_current_weather":
            return await handle_get_current_weather(arguments)
        case "get_forecast":
            return await handle_get_forecast(arguments)
        case "get_air_quality":
            return await handle_get_air_quality(arguments)
        case "get_weather_alerts":
            return await handle_get_weather_alerts(arguments)
        case _:
            from mcp.types import TextContent
            return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]


# ── Resource handlers ────────────────────────────────────────────────────────
@server.list_resources()
async def list_resources():
    return RESOURCES


@server.read_resource()
async def read_resource(uri: str):
    return await handle_resource(uri)


# ── Prompt handlers ──────────────────────────────────────────────────────────
@server.list_prompts()
async def list_prompts():
    return PROMPTS


@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None):
    return await handle_prompt(name, arguments or {})


# ── Entrypoint ───────────────────────────────────────────────────────────────
async def main():
    log.info("Starting Weather MCP Server (STDIO transport)")
    log.info("Auth required: %s", settings.require_auth)
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
