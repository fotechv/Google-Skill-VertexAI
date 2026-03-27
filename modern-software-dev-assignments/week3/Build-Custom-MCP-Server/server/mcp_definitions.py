"""
MCP capability definitions — tools, resources, and prompts.
"""

from mcp.types import (
    Tool,
    Resource,
    Prompt,
    PromptMessage,
    TextContent,
    GetPromptResult,
)
from config import settings

# ── Auth parameter injected into every tool when auth is enabled ─────────────
_AUTH_PARAM = {
    "api_key": {
        "type": "string",
        "description": "MCP server API key (required when server auth is enabled).",
    }
} if settings.require_auth else {}


# ── Tool definitions ─────────────────────────────────────────────────────────
TOOLS = [
    Tool(
        name="get_current_weather",
        description=(
            "Get the current weather conditions for a city. "
            "Returns temperature, humidity, wind, pressure, visibility, "
            "and weather description."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": 'City name, optionally with country code. E.g. "Hanoi" or "London,GB".',
                },
                "units": {
                    "type": "string",
                    "enum": ["metric", "imperial", "standard"],
                    "default": "metric",
                    "description": "Temperature units: metric (°C), imperial (°F), or standard (K).",
                },
                **_AUTH_PARAM,
            },
            "required": ["city"],
        },
    ),
    Tool(
        name="get_forecast",
        description=(
            "Get a 5-day weather forecast (3-hour intervals) for a city. "
            "Returns daily summaries with hourly breakdowns, temperature ranges, "
            "humidity, wind, and precipitation probability."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": 'City name, optionally with country code. E.g. "Tokyo,JP".',
                },
                "days": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "default": 5,
                    "description": "Number of forecast days to return (1–5).",
                },
                "units": {
                    "type": "string",
                    "enum": ["metric", "imperial", "standard"],
                    "default": "metric",
                    "description": "Temperature units.",
                },
                **_AUTH_PARAM,
            },
            "required": ["city"],
        },
    ),
    Tool(
        name="get_air_quality",
        description=(
            "Get the Air Quality Index (AQI) and pollutant concentrations "
            "(CO, NO, NO₂, O₃, SO₂, PM2.5, PM10, NH₃) for a city."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name to check air quality for.",
                },
                **_AUTH_PARAM,
            },
            "required": ["city"],
        },
    ),
    Tool(
        name="get_weather_alerts",
        description=(
            "Get active severe weather alerts and warnings for a city. "
            "Returns official government or meteorological alerts including "
            "event type, issuer, validity period, and description."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name to check weather alerts for.",
                },
                **_AUTH_PARAM,
            },
            "required": ["city"],
        },
    ),
]


# ── Resource definitions ─────────────────────────────────────────────────────
RESOURCES = [
    Resource(
        uri="weather://server/info",
        name="Server Info",
        description="Configuration and status of the Weather MCP server.",
        mimeType="text/plain",
    ),
    Resource(
        uri="weather://units/reference",
        name="Units Reference",
        description="Reference guide for measurement units used in weather data.",
        mimeType="text/plain",
    ),
]


async def handle_resource(uri: str) -> str:
    if uri == "weather://server/info":
        return (
            f"Weather MCP Server\n"
            f"Transport: STDIO\n"
            f"Auth enabled: {settings.require_auth}\n"
            f"Rate limit: {settings.rate_limit_calls} calls / {settings.rate_limit_window}s\n"
            f"Tools: get_current_weather, get_forecast, get_air_quality, get_weather_alerts\n"
        )
    if uri == "weather://units/reference":
        return (
            "Units Reference:\n"
            "  metric   — Temperature: °C, Wind: m/s\n"
            "  imperial — Temperature: °F, Wind: mph\n"
            "  standard — Temperature: K,  Wind: m/s\n\n"
            "AQI Scale (1–5):\n"
            "  1 = Good | 2 = Fair | 3 = Moderate | 4 = Poor | 5 = Very Poor\n\n"
            "Pressure: hPa (hectopascals)\n"
            "Visibility: kilometres\n"
            "Precipitation probability: 0–100%\n"
        )
    return f"Unknown resource: {uri}"


# ── Prompt definitions ───────────────────────────────────────────────────────
PROMPTS = [
    Prompt(
        name="weather_report",
        description="Generate a comprehensive weather briefing for a city.",
        arguments=[
            {"name": "city", "description": "The city to report on.", "required": True},
            {"name": "style", "description": "Report style: formal, casual, or broadcast.", "required": False},
        ],
    ),
    Prompt(
        name="travel_weather_advice",
        description="Get weather-based travel advice for a destination.",
        arguments=[
            {"name": "city", "description": "Travel destination city.", "required": True},
            {"name": "trip_duration", "description": "Trip duration in days (default 3).", "required": False},
        ],
    ),
]


async def handle_prompt(name: str, args: dict) -> GetPromptResult:
    if name == "weather_report":
        city = args.get("city", "your city")
        style = args.get("style", "casual")
        return GetPromptResult(
            description=f"Weather report for {city}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=(
                            f"Please provide a comprehensive weather report for {city}. "
                            f"Use a {style} tone. Include:\n"
                            "1. Current conditions (use get_current_weather)\n"
                            "2. 3-day forecast (use get_forecast with days=3)\n"
                            "3. Air quality summary (use get_air_quality)\n"
                            "4. Any active alerts (use get_weather_alerts)\n"
                            "Synthesize all data into a cohesive, easy-to-read report."
                        ),
                    ),
                )
            ],
        )

    if name == "travel_weather_advice":
        city = args.get("city", "your destination")
        days = args.get("trip_duration", "3")
        return GetPromptResult(
            description=f"Travel weather advice for {city}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=(
                            f"I'm planning a {days}-day trip to {city}. "
                            "Please check the weather forecast and air quality, then advise me on:\n"
                            "- What clothes to pack\n"
                            "- Best times of day for outdoor activities\n"
                            "- Any weather risks I should prepare for\n"
                            "- Whether air quality is a concern\n"
                            "Use the available weather tools to get accurate, current data."
                        ),
                    ),
                )
            ],
        )

    return GetPromptResult(
        description="Unknown prompt",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=f"Unknown prompt: {name}"),
            )
        ],
    )
