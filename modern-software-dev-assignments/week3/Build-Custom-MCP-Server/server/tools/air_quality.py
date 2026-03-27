"""
Tool: get_air_quality
Returns Air Quality Index and pollutant concentrations for a city.
Uses OWM Geocoding API to resolve city → coordinates, then Air Pollution API.
"""

import logging

from mcp.types import TextContent

from config import settings
from http_client import fetch_json, WeatherMCPError

log = logging.getLogger("weather-mcp.tools.aqi")

AQI_LABELS = {
    1: ("Good", "✅", "Air quality is considered satisfactory."),
    2: ("Fair", "🟡", "Air quality is acceptable. Some pollutants may be a concern."),
    3: ("Moderate", "🟠", "Members of sensitive groups may experience effects."),
    4: ("Poor", "🔴", "Everyone may begin to experience health effects."),
    5: ("Very Poor", "☠️", "Health warnings of emergency conditions."),
}


async def _geocode(city: str) -> tuple[float, float, str]:
    """Resolve city name to (lat, lon, display_name) via OWM Geocoding."""
    results = await fetch_json(
        f"{settings.owm_geo_url}/direct",
        params={"q": city, "limit": 1, "appid": settings.owm_api_key},
    )
    if not results:
        from http_client import NotFoundError
        raise NotFoundError(f"Could not geocode '{city}'. Try a more specific name.")
    loc = results[0]
    display = f"{loc['name']}, {loc.get('country', '')}"
    return loc["lat"], loc["lon"], display


def _format_aqi(data: dict, location: str) -> str:
    aqi = data["list"][0]["main"]["aqi"]
    components = data["list"][0]["components"]

    label, emoji, advice = AQI_LABELS.get(aqi, ("Unknown", "❓", ""))

    lines = [
        f"🌍 **Air Quality — {location}**",
        f"{emoji} **AQI: {aqi}/5 — {label}**",
        f"   {advice}",
        "",
        "**Pollutant Concentrations (μg/m³):**",
        f"  CO   (Carbon Monoxide):    {components.get('co', 'N/A'):.1f}",
        f"  NO   (Nitric Oxide):       {components.get('no', 'N/A'):.2f}",
        f"  NO₂  (Nitrogen Dioxide):   {components.get('no2', 'N/A'):.2f}",
        f"  O₃   (Ozone):              {components.get('o3', 'N/A'):.2f}",
        f"  SO₂  (Sulfur Dioxide):     {components.get('so2', 'N/A'):.2f}",
        f"  PM2.5 (Fine particles):    {components.get('pm2_5', 'N/A'):.2f}",
        f"  PM10  (Coarse particles):  {components.get('pm10', 'N/A'):.2f}",
        f"  NH₃  (Ammonia):            {components.get('nh3', 'N/A'):.2f}",
    ]
    return "\n".join(lines)


async def handle_get_air_quality(args: dict) -> list[TextContent]:
    city: str = args.get("city", "").strip()

    if not city:
        return [TextContent(type="text", text="❌ `city` parameter is required.")]

    try:
        lat, lon, display_name = await _geocode(city)
        data = await fetch_json(
            settings.owm_air_url,
            params={"lat": lat, "lon": lon, "appid": settings.owm_api_key},
        )
        result = _format_aqi(data, display_name)
        log.info("Air quality fetched for '%s'", city)
        return [TextContent(type="text", text=result)]

    except WeatherMCPError as exc:
        log.error("Error fetching AQI for '%s': %s", city, exc)
        return [TextContent(type="text", text=f"⚠️ {exc}")]
