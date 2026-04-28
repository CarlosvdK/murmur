"""Week 2: Tests for new context tools (FRED, Alpha Vantage, Google Trends)."""
import pytest
import respx
from unittest.mock import patch


class TestEconomicDataTool:
    """Test FRED API integration for economic data."""

    @pytest.mark.asyncio
    async def test_fred_api_returns_inflation_data(self, respx_mock):
        """FRED API should return current inflation rate."""
        from backend.context.tools.economic_data import EconomicDataTool

        respx_mock.get("https://api.stlouisfed.org/fred/series/observations").mock(
            return_value=respx.MockResponse(
                200,
                json={"observations": [{"date": "2026-03-01", "value": "3.2"}]},
            )
        )

        tool = EconomicDataTool("fake_key")
        result = await tool.get_us_inflation_rate()

        assert result["metric"] == "inflation_rate"
        assert result["value"] == 3.2

    @pytest.mark.asyncio
    async def test_fred_api_returns_unemployment_data(self, respx_mock):
        """FRED API should return unemployment rate."""
        from backend.context.tools.economic_data import EconomicDataTool

        respx_mock.get("https://api.stlouisfed.org/fred/series/observations").mock(
            return_value=respx.MockResponse(
                200,
                json={"observations": [{"date": "2026-03-01", "value": "4.1"}]},
            )
        )

        tool = EconomicDataTool("fake_key")
        result = await tool.get_unemployment_rate()

        assert result["metric"] == "unemployment_rate"
        assert result["value"] == 4.1

    @pytest.mark.asyncio
    async def test_fred_api_returns_fed_funds_rate(self, respx_mock):
        """FRED API should return federal funds effective rate."""
        from backend.context.tools.economic_data import EconomicDataTool

        respx_mock.get("https://api.stlouisfed.org/fred/series/observations").mock(
            return_value=respx.MockResponse(
                200,
                json={"observations": [{"date": "2026-03-01", "value": "5.33"}]},
            )
        )

        tool = EconomicDataTool("fake_key")
        result = await tool.get_federal_funds_rate()

        assert result["metric"] == "federal_funds_rate"
        assert result["value"] == 5.33

    @pytest.mark.asyncio
    async def test_economic_tool_gracefully_handles_error(self, respx_mock):
        """Tool should handle API errors gracefully."""
        from backend.context.tools.economic_data import EconomicDataTool

        respx_mock.get("https://api.stlouisfed.org/fred/series/observations").mock(
            return_value=respx.MockResponse(500, text="Internal Server Error")
        )

        tool = EconomicDataTool("fake_key")
        result = await tool.get_us_inflation_rate()

        assert "error" in result or "metric" in result


class TestMarketDataTool:
    """Test Alpha Vantage API integration for market data."""

    @pytest.mark.asyncio
    async def test_alpha_vantage_returns_sp500_data(self, respx_mock):
        """Alpha Vantage should return S&P 500 index data."""
        from backend.context.tools.market_data import MarketDataTool

        respx_mock.get("https://www.alphavantage.co/query").mock(
            return_value=respx.MockResponse(
                200,
                json={
                    "Global Quote": {
                        "01. symbol": "^GSPC",
                        "05. price": "5234.80",
                        "09. change": "45.23",
                        "10. change percent": "0.87%",
                        "07. latest trading day": "2026-04-20",
                    }
                },
            )
        )

        tool = MarketDataTool("fake_key")
        result = await tool.get_index_data("^GSPC")

        assert result["symbol"] == "^GSPC"
        assert result["price"] == 5234.80
        assert result["change_percent"] == 0.87

    @pytest.mark.asyncio
    async def test_alpha_vantage_returns_currency_rate(self, respx_mock):
        """Alpha Vantage should return currency exchange rates."""
        from backend.context.tools.market_data import MarketDataTool

        respx_mock.get("https://www.alphavantage.co/query").mock(
            return_value=respx.MockResponse(
                200,
                json={
                    "Realtime Currency Exchange Rate": {
                        "1. From_Currency Code": "USD",
                        "3. To_Currency Code": "EUR",
                        "5. Exchange Rate": "0.9234",
                        "6. Last Refreshed": "2026-04-20 15:30:00",
                    }
                },
            )
        )

        tool = MarketDataTool("fake_key")
        result = await tool.get_currency_exchange_rate("USD", "EUR")

        assert result["from"] == "USD"
        assert result["to"] == "EUR"
        assert result["rate"] == 0.9234

    @pytest.mark.asyncio
    async def test_market_tool_gracefully_handles_error(self, respx_mock):
        """Tool should handle API errors gracefully."""
        from backend.context.tools.market_data import MarketDataTool

        respx_mock.get("https://www.alphavantage.co/query").mock(
            return_value=respx.MockResponse(500, text="Internal Server Error")
        )

        tool = MarketDataTool("fake_key")
        result = await tool.get_index_data("^GSPC")

        assert "error" in result or "symbol" in result


class TestGoogleTrendsTool:
    """Test Google Trends (pytrends) integration."""

    def test_google_trends_get_business_keywords(self):
        """Should map business type to relevant keywords."""
        from backend.context.tools.trends_data import GoogleTrendsTool

        tool = GoogleTrendsTool()

        # Test restaurant - should map to relevant keywords
        keywords = tool._get_business_keywords("restaurant")
        assert len(keywords) > 0
        assert isinstance(keywords, list)
        assert any("restaurant" in k.lower() or "food" in k.lower() or "dining" in k.lower() for k in keywords)

        # Test retail
        keywords = tool._get_business_keywords("retail")
        assert len(keywords) > 0
        assert any("shopping" in k.lower() or "retail" in k.lower() for k in keywords)

        # Test saas
        keywords = tool._get_business_keywords("saas")
        assert len(keywords) > 0
        assert any("software" in k.lower() or "cloud" in k.lower() for k in keywords)

    @pytest.mark.asyncio
    async def test_trends_tool_handles_missing_pytrends(self):
        """Tool should gracefully handle missing pytrends library."""
        from backend.context.tools.trends_data import GoogleTrendsTool

        tool = GoogleTrendsTool()

        # Simulate missing import by mocking at function level
        with patch("pytrends.request.TrendReq", side_effect=ImportError):
            result = await tool.get_trending_searches()
            assert "error" in result


class TestContextToolsIntegration:
    """Test that new tools integrate with context engine."""

    @pytest.mark.asyncio
    async def test_economic_data_tool_has_execute_method(self):
        """Economic tool should have execute method."""
        from backend.context.tools.economic_data import EconomicDataTool

        tool = EconomicDataTool("fake_key")
        assert hasattr(tool, "execute")
        assert callable(tool.execute)

    @pytest.mark.asyncio
    async def test_market_data_tool_has_execute_method(self):
        """Market tool should have execute method."""
        from backend.context.tools.market_data import MarketDataTool

        tool = MarketDataTool("fake_key")
        assert hasattr(tool, "execute")
        assert callable(tool.execute)

    @pytest.mark.asyncio
    async def test_trends_tool_has_execute_method(self):
        """Trends tool should have execute method."""
        from backend.context.tools.trends_data import GoogleTrendsTool

        tool = GoogleTrendsTool()
        assert hasattr(tool, "execute")
        assert callable(tool.execute)

    def test_tools_follow_standard_interface(self):
        """All tools should follow execute(location) → str pattern."""
        from backend.context.tools.economic_data import EconomicDataTool
        from backend.context.tools.market_data import MarketDataTool
        from backend.context.tools.trends_data import GoogleTrendsTool

        tools = [
            EconomicDataTool("key"),
            MarketDataTool("key"),
            GoogleTrendsTool(),
        ]

        for tool in tools:
            assert hasattr(tool, "execute")
            assert callable(tool.execute)
