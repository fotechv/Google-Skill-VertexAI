"""
Tool: get_weather_alerts
Returns severe weather alerts for a city using OWM One Call API.
Falls back gracefully when no alerts are active.
"""

import logging
from datetime import datetime, timezone

from mcp.types import TextContent

from config import settings
from http_client import fetch_json, WeatherMCPError

log = logging.getLogger("weather-mcp.tools.alerts")


async def _geocode(city: str) -> tuple[float, float, str]:
    results = await fetch_json(
        f"{settings.owm_geo_url}/direct",
        params={"q": city, "limit": 1, "appid": settings.owm_api_key},
    )
    if not results:
        from http_client import NotFoundError
        raise NotFoundError(f"Could not geocode '{city}'.")
    loc = results[0]
    return loc["lat"], loc["lon"], f"{loc['name']}, {loc.get('country', '')}"


def _fmt_ts(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _format_alerts(data: dict, location: str) -> str:
    alerts = data.get("alerts", [])

    if not alerts:
        return f"✅ **No active weather alerts for {location}.**\n\nThe skies are clear of any official warnings at this time."

    lines = [f"⚠️ **Weather Alerts — {location}** ({len(alerts)} active)\n"]

    for i, alert in enumerate(alerts, 1):
        sender = alert.get("sender_name", "Unknown source")
        event = alert.get("event", "Weather alert")
        start = _fmt_ts(alert.get("start", 0))
        end = _fmt_ts(alert.get("end", 0))
        description = alert.get("description", "No details available.").strip()
        tags = alert.get("tags", [])

        lines.append(f"### Alert {i}: {event}")
        lines.append(f"  🏛 **Issued by:** {sender}")
        lines.append(f"  🕐 **From:** {start}")
        lines.append(f"  🕕 **Until:** {end}")
        if tags:
            lines.append(f"  🏷 **Tags:** {', '.join(tags)}")
        lines.append(f"  📝 **Details:**\n  {description[:500]}{'...' if len(description) > 500 else ''}")
        lines.append("")

    return "\n".join(lines)


async def handle_get_weather_alerts(args: dict) -> list[TextContent]:
    city: str = args.get("city", "").strip()

    if not city:
        return [TextContent(type="text", text="❌ `city` parameter is required.")]

    try:
        lat, lon, display_name = await _geocode(city)

        # One Call API 3.0 — alerts field
        data = await fetch_json(
            "https://api.openweathermap.org/data/3.0/onecall",
            params={
                "lat": lat,
                "lon": lon,
                "exclude": "current,minutely,hourly,daily",
                "appid": settings.owm_api_key,
            },
        )
        result = _format_alerts(data, display_name)
        log.info("Weather alerts fetched for '%s'", city)
        return [TextContent(type="text", text=result)]

    except WeatherMCPError as exc:
        log.error("Error fetching alerts for '%s': %s", city, exc)
        return [TextContent(type="text", text=f"⚠️ {exc}")]
