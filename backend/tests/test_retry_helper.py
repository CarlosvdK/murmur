"""Tests for the shared retry_get_json helper + representative tool migrations."""
from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest
import respx


# ---------------------------------------------------------------------------
# retry_get_json: the reusable helper
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retry_get_json_retries_on_500_then_returns_payload():
    from backend.context.tools.retry import retry_get_json

    with respx.mock(assert_all_called=True) as rx:
        rx.get("https://api.example.com/v1/thing").mock(
            side_effect=[
                httpx.Response(500),
                httpx.Response(500),
                httpx.Response(200, json={"ok": True}),
            ]
        )
        payload = await retry_get_json(
            "https://api.example.com/v1/thing",
            params={"q": "x"},
            timeout=5,
            max_attempts=3,
            # Zero wait so the test is fast.
            min_wait=0,
            max_wait=0,
        )
    assert payload == {"ok": True}


@pytest.mark.asyncio
async def test_retry_get_json_does_not_retry_on_401():
    from backend.context.tools.retry import retry_get_json

    with respx.mock(assert_all_called=True) as rx:
        route = rx.get("https://api.example.com/x").mock(
            return_value=httpx.Response(401)
        )
        with pytest.raises(httpx.HTTPStatusError):
            await retry_get_json(
                "https://api.example.com/x",
                params={},
                timeout=5,
                max_attempts=3,
                min_wait=0,
                max_wait=0,
            )
    assert route.call_count == 1


@pytest.mark.asyncio
async def test_retry_get_json_gives_up_after_max_attempts():
    from backend.context.tools.retry import retry_get_json

    with respx.mock() as rx:
        route = rx.get("https://api.example.com/x").mock(
            return_value=httpx.Response(500)
        )
        with pytest.raises(httpx.HTTPStatusError):
            await retry_get_json(
                "https://api.example.com/x",
                params={},
                timeout=5,
                max_attempts=3,
                min_wait=0,
                max_wait=0,
            )
    assert route.call_count == 3


# ---------------------------------------------------------------------------
# PriceIndexTool migrates to retry_get_json for the World Bank call
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_price_index_world_bank_retries_on_500():
    from backend.context.tools.price_index import PriceIndexTool

    tool = PriceIndexTool()
    url = "https://api.worldbank.org/v2/country/US/indicator/FP.CPI.TOTL.ZG"

    with respx.mock(assert_all_called=True) as rx:
        rx.get(url).mock(
            side_effect=[
                httpx.Response(500),
                httpx.Response(200, json=[{}, [{"date": "2024", "value": 3.1}]]),
            ]
        )
        # Force retry helper to use zero backoff for test speed.
        from backend.context.tools import retry as retry_mod
        original = retry_mod.retry_get_json

        async def fast(*args, **kwargs):
            kwargs.setdefault("min_wait", 0)
            kwargs.setdefault("max_wait", 0)
            return await original(*args, **kwargs)

        with patch("backend.context.tools.price_index.retry_get_json", side_effect=fast):
            result = await tool._fetch_world_bank("US")

    assert result["latest_rate"] == 3.1
    assert result["source"] == "world_bank"
