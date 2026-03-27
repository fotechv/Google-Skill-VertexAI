"""
Tool: get_forecast
Returns a 5-day / 3-hour weather forecast for a given city.
"""

import logging
from collections import defaultdict
from datetime import datetime, timezone

from mcp.types import TextContent

from config import settings
from http_client import fetch_json, WeatherMCPError

log = logging.getLogger("weather-mcp.tools.forecast")

_WIND_DIRS = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]


def _deg_to_dir(deg: float) -> str:
    return _WIND_DIRS[round(deg / 22.5) % 16]


def _format_forecast(data: dict, units: str, days: int) -> str:
    temp_unit = "°C" if units == "metric" else ("°F" if units == "imperial" else "K")
    speed_unit = "m/s" if units == "metric" else "mph"

    city = data.get("city", {}).get("name", "Unknown")
    country = data.get("city", {}).get("country", "")
    location = f"{city}, {country}" if country else city

    # Group forecast entries by calendar date
    by_day: dict[str, list[dict]] = defaultdict(list)
    for entry in data.get("list", []):
        dt = datetime.fromtimestamp(entry["dt"], tz=timezone.utc)
        day_key = dt.strftime("%A, %b %d")
        by_day[day_key].append(entry)

    lines = [f"📅 **5-Day Forecast — {location}**", ""]

    for day_key, entries in list(by_day.items())[:days]:
        temps = [e["main"]["temp"] for e in entries]
        humidities = [e["main"]["humidity"] for e in entries]
        winds = [e["wind"]["speed"] for e in entries]
        descriptions = [e["weather"][0]["description"] for e in entries]
        pops = [e.get("pop", 0) * 100 for e in entries]  # probability of precipitation

        # Most frequent description
        main_desc = max(set(descriptions), key=descriptions.count).capitalize()
        max_pop = max(pops)

        lines.append(f"### {day_key}")
        lines.append(f"  🌤 {main_desc}")
        lines.append(f"  🌡 {min(temps):.1f}{temp_unit} – {max(temps):.1f}{temp_unit}")
        lines.append(f"  💧 Humidity: {sum(humidities)//len(humidities)}%")
        lines.append(f"  🌬 Wind avg: {sum(winds)/len(winds):.1f} {speed_unit}")
        if max_pop > 0:
            lines.append(f"  🌧 Rain chance: {max_pop:.0f}%")

        # Hourly breakdown
        lines.append("  **Hourly:**")
        for entry in entries:
            dt = datetime.fromtimestamp(entry["dt"], tz=timezone.utc)
            time_str = dt.strftime("%H:%M")
            temp = entry["main"]["temp"]
            desc = entry["weather"][0]["description"]
            pop = entry.get("pop", 0) * 100
            wind_spd = entry["wind"]["speed"]
            wind_dir = _deg_to_dir(entry["wind"].get("deg", 0))
            pop_str = f" 🌧{pop:.0f}%" if pop > 10 else ""
            lines.append(f"    {time_str} — {temp:.1f}{temp_unit}, {desc}, 💨{wind_spd:.1f}{speed_unit} {wind_dir}{pop_str}")

        lines.append("")

    return "\n".join(lines)


async def handle_get_forecast(args: dict) -> list[TextContent]:
    city: str = args.get("city", "").strip()
    units: str = args.get("units", "metric").lower()
    days: int = args.get("days", 5)

    if not city:
        return [TextContent(type="text", text="❌ `city` parameter is required.")]
    if units not in ("metric", "imperial", "standard"):
        return [TextContent(type="text", text="❌ `units` must be one of: metric, imperial, standard.")]
    if not isinstance(days, int) or not (1 <= days <= 5):
        return [TextContent(type="text", text="❌ `days` must be an integer between 1 and 5.")]

    try:
        data = await fetch_json(
            f"{settings.owm_base_url}/forecast",
            params={"q": city, "units": units, "appid": settings.owm_api_key},
        )
        result = _format_forecast(data, units, days)
        log.info("Forecast fetched for '%s' (%d days)", city, days)
        return [TextContent(type="text", text=result)]

    except WeatherMCPError as exc:
        log.error("Error fetching forecast for '%s': %s", city, exc)
        return [TextContent(type="text", text=f"⚠️ {exc}")]
