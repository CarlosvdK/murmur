"""
Market data tool: Alpha Vantage API
Provides stock prices, market indices, sector performance
"""

import httpx
from typing import Optional


class MarketDataTool:
    """Gather market data: stock indices, sector trends, equity performance."""

    def __init__(self, alpha_vantage_api_key: str):
        self.api_key = alpha_vantage_api_key
        self.base_url = "https://www.alphavantage.co/query"

    async def get_index_data(self, symbol: str = "^GSPC") -> dict:
        """
        Get stock index data (S&P 500, Dow Jones, Nasdaq, etc).
        Symbols: ^GSPC (S&P 500), ^INDY (Dow), ^CCMP (Nasdaq)
        """
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "function": "GLOBAL_QUOTE",
                        "symbol": symbol,
                        "apikey": self.api_key,
                    },
                )
                response.raise_for_status()
                data = response.json()

                if "Global Quote" in data and data["Global Quote"].get("05. price"):
                    quote = data["Global Quote"]
                    return {
                        "symbol": symbol,
                        "price": float(quote.get("05. price", 0)),
                        "change": float(quote.get("09. change", 0)),
                        "change_percent": float(quote.get("10. change percent", "0").rstrip("%")),
                        "timestamp": quote.get("07. latest trading day", ""),
                    }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

        return {"error": "No data", "symbol": symbol}

    async def get_sector_performance(self) -> dict:
        """Get real-time sector performance."""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "function": "SECTOR",
                        "apikey": self.api_key,
                    },
                )
                response.raise_for_status()
                data = response.json()

                sectors = {}
                for key, value in data.items():
                    if "Rank" in key and isinstance(value, str):
                        # Parse rank strings like "1. Energy"
                        sector_name = value.split(". ", 1)[1] if ". " in value else value
                        rank_change = data.get(key.replace("Rank", "Change"), "0")
                        sectors[sector_name] = {
                            "rank": value,
                            "change": float(rank_change.rstrip("%")) if rank_change else 0,
                        }

                return {"sectors": sectors}
        except Exception as e:
            return {"error": str(e)}

        return {"error": "No data"}

    async def get_currency_exchange_rate(
        self, from_currency: str = "USD", to_currency: str = "EUR"
    ) -> dict:
        """Get currency exchange rate (useful for international businesses)."""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "function": "CURRENCY_EXCHANGE_RATE",
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "apikey": self.api_key,
                    },
                )
                response.raise_for_status()
                data = response.json()

                if "Realtime Currency Exchange Rate" in data:
                    rate_data = data["Realtime Currency Exchange Rate"]
                    return {
                        "from": rate_data.get("1. From_Currency Code"),
                        "to": rate_data.get("3. To_Currency Code"),
                        "rate": float(rate_data.get("5. Exchange Rate", 0)),
                        "timestamp": rate_data.get("6. Last Refreshed", ""),
                    }
        except Exception as e:
            return {"error": str(e), "from": from_currency, "to": to_currency}

        return {"error": "No data", "from": from_currency, "to": to_currency}

    async def execute(self, location: str) -> str:
        """Execute: gather market data and return as narrative."""
        narrative_parts = []

        # Get S&P 500 performance
        sp500 = await self.get_index_data("^GSPC")
        if sp500.get("price"):
            change_str = (
                f"+{sp500['change_percent']:.2f}%"
                if sp500["change_percent"] >= 0
                else f"{sp500['change_percent']:.2f}%"
            )
            narrative_parts.append(f"S&P 500 at {sp500['price']:.2f} ({change_str})")

        # Get sector performance
        sectors = await self.get_sector_performance()
        if sectors.get("sectors"):
            top_sector = next(iter(sectors["sectors"].items())) if sectors["sectors"] else None
            if top_sector:
                sector_name, sector_data = top_sector
                narrative_parts.append(f"Leading sector: {sector_name}")

        # Check for international location and get currency rates
        if any(
            country in location.lower()
            for country in ["canada", "europe", "uk", "japan", "australia"]
        ):
            currency_map = {
                "canada": ("USD", "CAD"),
                "europe": ("USD", "EUR"),
                "uk": ("USD", "GBP"),
                "japan": ("USD", "JPY"),
                "australia": ("USD", "AUD"),
            }

            for country, (from_curr, to_curr) in currency_map.items():
                if country in location.lower():
                    rate = await self.get_currency_exchange_rate(from_curr, to_curr)
                    if rate.get("rate"):
                        narrative_parts.append(f"Exchange rate: 1 {from_curr} = {rate['rate']:.2f} {to_curr}")
                    break

        narrative = "Market Context: " + ". ".join(narrative_parts) if narrative_parts else ""
        return narrative if narrative else "Market data unavailable"


if __name__ == "__main__":
    import os
    import asyncio

    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    tool = MarketDataTool(api_key)

    async def test():
        sp500 = await tool.get_index_data()
        print("S&P 500:", sp500)

        sectors = await tool.get_sector_performance()
        print("Sectors:", sectors)

        result = await tool.execute("San Francisco, USA")
        print("Result:", result)

    asyncio.run(test())
