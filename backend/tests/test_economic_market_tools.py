"""RED: ContextTool wrappers for EconomicData + MarketData.

The raw classes exist but use a non-ContextTool shape (init takes the
API key, execute takes just `location`). We need wrappers that plug
into the orchestrator's registry.

Contract:
  - Each wrapper is a subclass of ContextTool.
  - `name` and `description` are populated.
  - `required_config` lists the Settings field(s) that must be non-empty.
  - `available()` returns False when the config key is empty.
  - `execute(...)` returns a dict (never raises).
  - The tool registry lists them among available tools when keys are set.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.context.tools.base import ContextTool


# ---------------------------------------------------------------------------
# Economic data wrapper
# ---------------------------------------------------------------------------


def test_economic_data_tool_is_a_context_tool():
    from backend.context.tools.economic_data_tool import EconomicDataContextTool

    tool = EconomicDataContextTool()
    assert isinstance(tool, ContextTool)
    assert tool.name and "economic" in tool.name
    assert tool.description
    assert "fred_api_key" in tool.required_config


def test_economic_data_unavailable_without_fred_key():
    from backend.context.tools.economic_data_tool import EconomicDataContextTool

    tool = EconomicDataContextTool()
    settings_empty = SimpleNamespace(fred_api_key="")
    settings_set = SimpleNamespace(fred_api_key="abc")

    assert tool.available(settings_empty) is False
    assert tool.available(settings_set) is True


@pytest.mark.asyncio
async def test_economic_data_execute_returns_dict_with_narrative():
    from backend.context.tools import economic_data_tool as mod

    fake_inner = AsyncMock()
    fake_inner.execute = AsyncMock(
        return_value="Economic Context: inflation 3.2%, unemployment 4.1%"
    )

    with patch.object(mod, "EconomicDataTool", return_value=fake_inner):
        tool = mod.EconomicDataContextTool()
        result = await tool.execute(
            business_name="Cafe Luna",
            business_type="restaurant",
            location="San Francisco, USA",
            question="What if I raise prices 15%?",
            hints={},
        )
    assert isinstance(result, dict)
    assert "narrative" in result
    assert "inflation" in result["narrative"].lower()


# ---------------------------------------------------------------------------
# Market data wrapper
# ---------------------------------------------------------------------------


def test_market_data_tool_is_a_context_tool():
    from backend.context.tools.market_data_tool import MarketDataContextTool

    tool = MarketDataContextTool()
    assert isinstance(tool, ContextTool)
    assert "market" in tool.name
    assert "alpha_vantage_api_key" in tool.required_config


def test_market_data_unavailable_without_alpha_vantage_key():
    from backend.context.tools.market_data_tool import MarketDataContextTool

    tool = MarketDataContextTool()
    assert tool.available(SimpleNamespace(alpha_vantage_api_key="")) is False
    assert tool.available(SimpleNamespace(alpha_vantage_api_key="xyz")) is True


@pytest.mark.asyncio
async def test_market_data_execute_returns_dict_with_narrative():
    from backend.context.tools import market_data_tool as mod

    fake_inner = AsyncMock()
    fake_inner.execute = AsyncMock(
        return_value="Market Context: S&P 500 up 2.3% over the last week"
    )

    with patch.object(mod, "MarketDataTool", return_value=fake_inner):
        tool = mod.MarketDataContextTool()
        result = await tool.execute(
            business_name="Cafe Luna",
            business_type="restaurant",
            location="San Francisco, USA",
            question="How are competitors pricing?",
            hints={},
        )
    assert isinstance(result, dict)
    assert "narrative" in result
    assert "market" in result["narrative"].lower()


# ---------------------------------------------------------------------------
# Registry integration
# ---------------------------------------------------------------------------


def test_tool_registry_includes_economic_and_market_when_keys_set():
    from backend.context.tools import get_available_tools

    settings = SimpleNamespace(
        fred_api_key="fred",
        alpha_vantage_api_key="av",
        # Other tools' keys are empty -- they're filtered out.
        google_places_api_key="",
        brave_search_api_key="",
        reddit_client_id="",
        reddit_client_secret="",
    )
    tools = get_available_tools(settings)
    names = {t.name for t in tools}
    assert any("economic" in n for n in names), f"saw: {names}"
    assert any("market" in n for n in names), f"saw: {names}"


def test_tool_registry_omits_economic_and_market_without_keys():
    from backend.context.tools import get_available_tools

    settings = SimpleNamespace(
        fred_api_key="",
        alpha_vantage_api_key="",
        google_places_api_key="",
        brave_search_api_key="",
        reddit_client_id="",
        reddit_client_secret="",
    )
    tools = get_available_tools(settings)
    names = {t.name for t in tools}
    assert not any("economic" in n for n in names)
    assert not any("market" in n for n in names)
