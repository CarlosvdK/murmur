"""
Seasonal and weather patterns via Open-Meteo API.

Completely free, no API key needed.
https://open-meteo.com/

Only useful when the question has a temporal or seasonal dimension.
The orchestrator decides when to invoke this.
"""

import logging
from typing import Optional

import httpx

from backend.context.tools.base import ContextTool

logger = logging.getLogger(__name__)

# Common city coordinates (extend as needed)
CITY_COORDS = {
    "barcelona": (41.39, 2.17),
    "madrid": (40.42, -3.70),
    "london": (51.51, -0.13),
    "paris": (48.86, 2.35),
    "new york": (40.71, -74.01),
    "los angeles": (34.05, -118.24),
    "austin": (30.27, -97.74),
    "berlin": (52.52, 13.41),
    "amsterdam": (52.37, 4.90),
    "lisbon": (38.72, -9.14),
    "rome": (41.90, 12.50),
    "milan": (45.46, 9.19),
    "dublin": (53.35, -6.26),
}


def _get_coords(location: str) -> Optional[tuple[float, float]]:
    if not location:
        return None
    loc_lower = location.lower()
    for city, coords in CITY_COORDS.items():
        if city in loc_lower:
            return coords
    return None


ONLINE_ONLY_TYPES = {
    "saas", "ecommerce", "app", "it_services", "web_design", "hosting",
    "cybersecurity", "data_analytics", "b2b_services", "staffing",
    "marketing_agency", "freelance",
}


class WeatherTrendsTool(ContextTool):
    name = "weather_trends"
    description = (
        "Get seasonal weather patterns and current conditions for the "
        "business location. Useful when the question involves timing, "
        "seasons, outdoor areas, or foot traffic patterns. "
        "Not applicable for online-only businesses. No API key required."
    )
    required_config = []  # Free API

    async def execute(
        self,
        business_name: str,
        business_type: str,
        location: Optional[str],
        question: str,
        hints: dict,
    ) -> dict:
        # Skip for online-only businesses
        if business_type in ONLINE_ONLY_TYPES:
            logger.info("Skipping weather_trends for online business type: %s", business_type)
            return {
                "available": False,
                "reason": f"Weather data not relevant for {business_type} businesses",
            }

        coords = _get_coords(location or "")
        if not coords:
            return {
                "available": False,
                "reason": f"Could not determine coordinates for '{location}'",
            }

        lat, lon = coords
        async with httpx.AsyncClient(timeout=15) as client:
            # Current weather + monthly climate normals
            resp = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                    "timezone": "auto",
                    "forecast_days": 14,
                },
            )
            resp.raise_for_status()
            forecast = resp.json()

            # Historical climate for seasonal context
            resp2 = await client.get(
                "https://climate-api.open-meteo.com/v1/climate",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "models": "EC_Earth3P_HR",
                    "monthly": "temperature_2m_mean",
                    "start_date": "2020-01-01",
                    "end_date": "2024-12-31",
                },
            )
            climate = resp2.json() if resp2.status_code == 200 else {}

        daily = forecast.get("daily", {})
        dates = daily.get("time", [])
        temps_max = daily.get("temperature_2m_max", [])
        temps_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])

        forecast_summary = []
        for i, date in enumerate(dates[:7]):
            forecast_summary.append({
                "date": date,
                "high_c": temps_max[i] if i < len(temps_max) else None,
                "low_c": temps_min[i] if i < len(temps_min) else None,
                "precip_mm": precip[i] if i < len(precip) else None,
            })

        return {
            "location": location,
            "coordinates": {"lat": lat, "lon": lon},
            "forecast_7day": forecast_summary,
            "climate_data_available": bool(climate.get("monthly")),
        }
