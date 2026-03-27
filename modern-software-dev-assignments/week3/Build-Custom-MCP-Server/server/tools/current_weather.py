"""
Tool: get_current_weather
Returns current weather conditions for a given city.
"""

import logging
from mcp.types import TextContent
from http_client import fetch_json, WeatherMCPError
from config import settings

log = logging.getLogger("weather-mcp.tools.current")

# Wind direction helper
_WIND_DIRS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
              "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def _degrees_to_direction(deg: float) -> str:
    idx = round(deg / 22.5) % 16
    return _WIND_DIRS[idx]


def _format_weather(data: dict, units: str) -> str:
    """Format OWM current weather response into readable text."""
    temp_unit = "°C" if units == "metric" else ("°F" if units == "imperial" else "K")
    speed_unit = "m/s" if units == "metric" else ("mph" if units == "imperial" else "m/s")

    city = data.get("name", "Unknown")
    country = data.get("sys", {}).get("country", "")
    location = f"{city}, {country}" if country else city

    main = data.get("main", {})
    weather = data.get("weather", [{}])[0]
    wind = data.get("wind", {})
    clouds = data.get("clouds", {})
    visibility = data.get("visibility", None)
    rain = data.get("rain", {})
    snow = data.get("snow", {})

    temp = main.get("temp", "N/A")
    feels_like = main.get("feels_like", "N/A")
    temp_min = main.get("temp_min", "N/A")
    temp_max = main.get("temp_max", "N/A")
    humidity = main.get("humidity", "N/A")
    pressure = main.get("pressure", "N/A")

    wind_speed = wind.get("speed", 0)
    wind_dir = _degrees_to_direction(wind.get("deg", 0)) if "deg" in wind else "N/A"
    wind_gust = wind.get("gust", None)

    description = weather.get("description", "N/A").capitalize()
    cloud_cover = clouds.get("all", 0)

    lines = [
        f"🌍 **{location}**",
        f"🌤 **Condition:** {description}",
        f"🌡 **Temperature:** {temp}{temp_unit} (feels like {feels_like}{temp_unit})",
        f"   Min: {temp_min}{temp_unit} | Max: {temp_max}{temp_unit}",
        f"💧 **Humidity:** {humidity}%",
        f"🌬 **Wind:** {wind_speed} {speed_unit} from {wind_dir}",
    ]

    if wind_gust:
        lines.append(f"   Gusts up to: {wind_gust} {speed_unit}")

    lines.append(f"☁ **Cloud cover:** {cloud_cover}%")
    lines.append(f"🔵 **Pressure:** {pressure} hPa")

    if visibility is not None:
        lines.append(f"👁 **Visibility:** {visibility / 1000:.1f} km")

    if rain:
        lines.append(f"🌧 **Rain (last hour):** {rain.get('1h', 0):.1f} mm")
    if snow:
        lines.append(f"❄ **Snow (last hour):** {snow.get('1h', 0):.1f} mm")

    return "\n".join(lines)


async def handle_get_current_weather(args: dict) -> list[TextContent]:
    city: str = args.get("city", "").strip()
    units: str = args.get("units", "metric").lower()

    # Input validation
    if not city:
        return [TextContent(type="text", text="❌ `city` parameter is required.")]
    if units not in ("metric", "imperial", "standard"):
        return [TextContent(type="text", text="❌ `units` must be one of: metric, imperial, standard.")]

    try:
        data = await fetch_json(
            f"{settings.owm_base_url}/weather",
            params={"q": city, "units": units, "appid": settings.owm_api_key},
        )
        result = _format_weather(data, units)
        log.info("Current weather fetched for '%s'", city)
        return [TextContent(type="text", text=result)]

    except WeatherMCPError as exc:
        log.error("Error fetching current weather for '%s': %s", city, exc)
        return [TextContent(type="text", text=f"⚠️ {exc}")]
