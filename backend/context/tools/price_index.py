"""
Economic context: inflation, cost of living, consumer spending.

All free APIs, no key required:
- Eurostat (EU countries)
- World Bank (global fallback)

A 15% price increase in a high-inflation environment where customers
are already squeezed hits differently than the same increase in a
booming economy.
"""

import logging
import re
from typing import Optional

import httpx

from backend.context.tools.base import ContextTool

logger = logging.getLogger(__name__)

# Map common locations to Eurostat country codes
EUROSTAT_COUNTRY_MAP = {
    "spain": "ES", "barcelona": "ES", "madrid": "ES",
    "france": "FR", "paris": "FR",
    "germany": "DE", "berlin": "DE", "munich": "DE",
    "italy": "IT", "rome": "IT", "milan": "IT",
    "uk": "GB", "london": "GB", "england": "GB",
    "portugal": "PT", "lisbon": "PT",
    "netherlands": "NL", "amsterdam": "NL",
    "ireland": "IE", "dublin": "IE",
}


def _guess_country_code(location: str) -> Optional[str]:
    if not location:
        return None
    loc_lower = location.lower()
    for keyword, code in EUROSTAT_COUNTRY_MAP.items():
        if keyword in loc_lower:
            return code
    return None


class PriceIndexTool(ContextTool):
    name = "price_index"
    description = (
        "Get inflation rates, consumer price index trends, and cost of "
        "living indicators for the business location. Helps calibrate "
        "how price-sensitive customers are likely to be right now. "
        "No API key required."
    )
    required_config = []  # Free APIs

    async def execute(
        self,
        business_name: str,
        business_type: str,
        location: Optional[str],
        question: str,
        hints: dict,
    ) -> dict:
        country_code = hints.get("country_code") or _guess_country_code(location or "")

        if country_code and country_code in {c for c in EUROSTAT_COUNTRY_MAP.values()}:
            return await self._fetch_eurostat(country_code)
        else:
            return await self._fetch_world_bank(country_code or "WLD")

    async def _fetch_eurostat(self, country_code: str) -> dict:
        """Fetch HICP (inflation) from Eurostat."""
        # HICP annual rate of change, all items
        url = (
            "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
            "prc_hicp_manr"
        )
        params = {
            "geo": country_code,
            "coicop": "CP00",  # All items
            "format": "JSON",
            "lang": "en",
            "lastTimePeriod": 12,
        }

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                logger.warning("Eurostat returned %d, falling back to World Bank", resp.status_code)
                return await self._fetch_world_bank(country_code)

            data = resp.json()

        # Parse Eurostat JSON-stat format
        values = data.get("value", {})
        dimensions = data.get("dimension", {})
        time_dim = dimensions.get("time", {}).get("category", {}).get("index", {})

        inflation_points = {}
        for time_label, time_idx in time_dim.items():
            val = values.get(str(time_idx))
            if val is not None:
                inflation_points[time_label] = val

        latest_period = max(inflation_points.keys()) if inflation_points else "unknown"
        latest_rate = inflation_points.get(latest_period)

        return {
            "source": "eurostat",
            "country": country_code,
            "indicator": "HICP annual inflation rate (%)",
            "latest_period": latest_period,
            "latest_rate": latest_rate,
            "trend": inflation_points,
        }

    async def _fetch_world_bank(self, country_code: str) -> dict:
        """Fallback: fetch CPI from World Bank."""
        url = (
            f"https://api.worldbank.org/v2/country/{country_code}/indicator/"
            "FP.CPI.TOTL.ZG"  # Consumer price inflation
        )
        params = {"format": "json", "per_page": 5, "mrv": 5}

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        points = {}
        if len(data) > 1 and data[1]:
            for entry in data[1]:
                if entry.get("value") is not None:
                    points[entry["date"]] = round(entry["value"], 2)

        latest_year = max(points.keys()) if points else "unknown"
        latest_rate = points.get(latest_year)

        return {
            "source": "world_bank",
            "country": country_code,
            "indicator": "Consumer price inflation, annual %",
            "latest_period": latest_year,
            "latest_rate": latest_rate,
            "trend": points,
        }
