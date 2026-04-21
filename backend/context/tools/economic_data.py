"""
Economic data tool: FRED API + World Bank API
Provides inflation, employment, GDP, interest rates context
"""

import httpx
import asyncio
from typing import Optional


class EconomicDataTool:
    """Gather economic indicators (inflation, unemployment, GDP, interest rates)."""

    def __init__(self, fred_api_key: str, world_bank_api_key: Optional[str] = None):
        self.fred_api_key = fred_api_key
        self.world_bank_api_key = world_bank_api_key
        self.fred_base = "https://api.stlouisfed.org/fred"
        self.world_bank_base = "https://api.worldbank.org/v2"

    async def get_us_inflation_rate(self) -> dict:
        """Get current US inflation rate (CPI-U)."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # CPIAUCSL = Consumer Price Index for All Urban Consumers
                response = await client.get(
                    f"{self.fred_base}/series/observations",
                    params={
                        "series_id": "CPIAUCSL",
                        "api_key": self.fred_api_key,
                        "limit": 1,
                        "sort_order": "desc",
                    },
                )
                response.raise_for_status()
                data = response.json()

                if data.get("observations"):
                    latest = data["observations"][0]
                    return {
                        "metric": "inflation_rate",
                        "value": float(latest["value"]),
                        "date": latest["date"],
                        "unit": "percent",
                    }
        except Exception as e:
            return {"error": str(e), "metric": "inflation_rate"}

        return {"error": "No data", "metric": "inflation_rate"}

    async def get_unemployment_rate(self) -> dict:
        """Get current US unemployment rate."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # UNRATE = Civilian Unemployment Rate
                response = await client.get(
                    f"{self.fred_base}/series/observations",
                    params={
                        "series_id": "UNRATE",
                        "api_key": self.fred_api_key,
                        "limit": 1,
                        "sort_order": "desc",
                    },
                )
                response.raise_for_status()
                data = response.json()

                if data.get("observations"):
                    latest = data["observations"][0]
                    return {
                        "metric": "unemployment_rate",
                        "value": float(latest["value"]),
                        "date": latest["date"],
                        "unit": "percent",
                    }
        except Exception as e:
            return {"error": str(e), "metric": "unemployment_rate"}

        return {"error": "No data", "metric": "unemployment_rate"}

    async def get_federal_funds_rate(self) -> dict:
        """Get current federal funds effective rate."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # FEDFUNDS = Effective Federal Funds Rate
                response = await client.get(
                    f"{self.fred_base}/series/observations",
                    params={
                        "series_id": "FEDFUNDS",
                        "api_key": self.fred_api_key,
                        "limit": 1,
                        "sort_order": "desc",
                    },
                )
                response.raise_for_status()
                data = response.json()

                if data.get("observations"):
                    latest = data["observations"][0]
                    return {
                        "metric": "federal_funds_rate",
                        "value": float(latest["value"]),
                        "date": latest["date"],
                        "unit": "percent",
                    }
        except Exception as e:
            return {"error": str(e), "metric": "federal_funds_rate"}

        return {"error": "No data", "metric": "federal_funds_rate"}

    async def get_world_bank_data(self, country_code: str, indicator: str) -> dict:
        """Get World Bank indicator data for a country."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.world_bank_base}/country/{country_code}/indicator/{indicator}",
                    params={"format": "json", "per_page": 1},
                )
                response.raise_for_status()
                data = response.json()

                if len(data) > 1 and data[1]:
                    latest = data[1][0]
                    return {
                        "metric": indicator,
                        "country": country_code,
                        "value": latest.get("value"),
                        "date": latest.get("date"),
                    }
        except Exception as e:
            return {"error": str(e), "metric": indicator, "country": country_code}

        return {"error": "No data", "metric": indicator}

    async def execute(self, location: str) -> str:
        """Execute: gather economic data and return as narrative."""
        # Get US economic data
        inflation = await self.get_inflation_rate()
        unemployment = await self.get_unemployment_rate()
        fed_rate = await self.get_federal_funds_rate()

        # Extract country code from location (simplified)
        country_map = {
            "US": "USA",
            "United States": "USA",
            "Canada": "CAN",
            "UK": "GBR",
            "United Kingdom": "GBR",
            "Germany": "DEU",
            "France": "FRA",
            "Japan": "JPN",
            "China": "CHN",
        }

        country_code = None
        for key, code in country_map.items():
            if key.lower() in location.lower():
                country_code = code
                break

        narrative_parts = []

        # Add US economic context
        if "inflation" in inflation and isinstance(inflation["value"], (int, float)):
            narrative_parts.append(
                f"Current inflation rate: {inflation['value']:.1f}% (as of {inflation.get('date', 'recent')})"
            )

        if "unemployment" in unemployment and isinstance(unemployment["value"], (int, float)):
            narrative_parts.append(
                f"Unemployment rate: {unemployment['value']:.1f}% (as of {unemployment.get('date', 'recent')})"
            )

        if "federal" in fed_rate and isinstance(fed_rate["value"], (int, float)):
            narrative_parts.append(
                f"Federal funds rate: {fed_rate['value']:.2f}% (affecting borrowing costs)"
            )

        # Add country-specific data if applicable
        if country_code and country_code != "USA":
            gdp_growth = await self.get_world_bank_data(country_code, "NY.GDP.MKTP.KD.ZS.AD.XD")
            if gdp_growth.get("value"):
                narrative_parts.append(
                    f"{country_code} GDP growth: {float(gdp_growth['value']):.1f}%"
                )

        narrative = "Economic Context: " + ". ".join(narrative_parts) if narrative_parts else ""
        return narrative if narrative else "Economic data unavailable"


if __name__ == "__main__":
    import os

    fred_key = os.getenv("FRED_API_KEY")
    tool = EconomicDataTool(fred_key)

    # Test
    async def test():
        inflation = await tool.get_us_inflation_rate()
        print("Inflation:", inflation)

        unemployment = await tool.get_unemployment_rate()
        print("Unemployment:", unemployment)

        result = await tool.execute("San Francisco, USA")
        print("Result:", result)

    asyncio.run(test())
