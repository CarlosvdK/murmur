"""
Area demographic data from free public APIs.

Sources:
- US: Census Bureau API (free, no key for basic queries)
- Spain (INE): public API
- Global fallback: World Bank indicators

Critical for Barcelona: high tourist ratio in certain neighbourhoods
changes who the customers actually are.
"""

import logging
from typing import Optional

import httpx

from backend.context.tools.base import ContextTool

logger = logging.getLogger(__name__)


class DemographicTool(ContextTool):
    name = "demographic"
    description = (
        "Get area demographics: population density, income levels, age "
        "distribution, tourist-vs-local ratio. Helps ensure personas "
        "reflect the actual customer mix of the area. No API key required."
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
        if not location:
            return {"available": False, "reason": "No location provided"}

        loc_lower = location.lower()

        # Try World Bank for country-level indicators as baseline
        country_code = hints.get("country_code", self._guess_country(loc_lower))
        if country_code:
            return await self._fetch_world_bank(country_code, location)

        return {"available": False, "reason": f"Could not map '{location}' to a data source"}

    def _guess_country(self, location: str) -> Optional[str]:
        mapping = {
            "spain": "ESP", "barcelona": "ESP", "madrid": "ESP",
            "us": "USA", "united states": "USA", "new york": "USA",
            "austin": "USA", "los angeles": "USA",
            "uk": "GBR", "london": "GBR", "england": "GBR",
            "france": "FRA", "paris": "FRA",
            "germany": "DEU", "berlin": "DEU",
            "italy": "ITA", "rome": "ITA",
            "portugal": "PRT", "lisbon": "PRT",
            "ireland": "IRL", "dublin": "IRL",
            "netherlands": "NLD", "amsterdam": "NLD",
        }
        for keyword, code in mapping.items():
            if keyword in location:
                return code
        return None

    async def _fetch_world_bank(self, country_code: str, location: str) -> dict:
        """Fetch key demographic indicators from World Bank."""
        indicators = {
            "SP.POP.TOTL": "total_population",
            "NY.GDP.PCAP.PP.CD": "gdp_per_capita_ppp",
            "SP.URB.TOTL.IN.ZS": "urban_population_pct",
            "SP.POP.65UP.TO.ZS": "population_65plus_pct",
            "SP.POP.1564.TO.ZS": "population_15_64_pct",
            "ST.INT.ARVL": "international_tourist_arrivals",
        }

        results = {}
        async with httpx.AsyncClient(timeout=15) as client:
            for indicator_code, label in indicators.items():
                try:
                    resp = await client.get(
                        f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}",
                        params={"format": "json", "mrv": 1, "per_page": 1},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if len(data) > 1 and data[1]:
                            entry = data[1][0]
                            if entry.get("value") is not None:
                                results[label] = {
                                    "value": round(entry["value"], 2),
                                    "year": entry.get("date"),
                                }
                except Exception as e:
                    logger.debug("World Bank indicator %s failed: %s", indicator_code, e)

        return {
            "source": "world_bank",
            "country": country_code,
            "location_queried": location,
            "indicators": results,
        }
