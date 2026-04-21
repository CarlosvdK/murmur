"""Phase 5 RED: rate limiting + shared HTTP retry.

Goals:
  1. The API enforces a per-IP rate limit on hot endpoints (simulations create,
     outcome submit). Health must NEVER be rate-limited.
  2. We ship one shared `retry_http` helper so new tools don't each reinvent
     tenacity config. It retries on 5xx / 429 / network errors with
     exponential backoff and gives up on other 4xx.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# 1. Rate limiting
# ---------------------------------------------------------------------------


def test_health_endpoint_is_never_rate_limited():
    from backend.api.main import app

    with patch("backend.api.main.get_supabase", return_value=MagicMock()):
        client = TestClient(app)
        # Blast well beyond any reasonable per-minute limit.
        statuses = []
        for _ in range(60):
            statuses.append(client.get("/api/health").status_code)
        # None should be 429.
        assert 429 not in statuses, (
            f"/api/health must not be rate-limited; saw statuses: {set(statuses)}"
        )


def test_simulations_create_returns_429_when_spammed():
    """POST /simulations/ is a hot endpoint -- 20+ bursts must trigger 429.

    We mock the DB so the handler returns fast and we can actually spam it.
    """
    from backend.api.main import app

    fake_db = MagicMock()
    # business lookup -> not found; the handler will 404, but that's fine:
    # slowapi counts BEFORE the handler runs.
    chain = fake_db.table.return_value.select.return_value.eq.return_value.eq
    chain.return_value.maybe_single.return_value.execute.return_value = MagicMock(data=None)

    with patch("backend.api.routes.simulations.get_supabase", return_value=fake_db):
        client = TestClient(app)
        body = {
            "business_id": "00000000-0000-0000-0000-000000000001",
            "question": "x",
        }
        statuses = []
        for _ in range(40):
            r = client.post("/api/simulations/", json=body)
            statuses.append(r.status_code)

    assert 429 in statuses, (
        f"expected at least one 429 after 40 rapid POSTs; saw: {statuses[:25]}..."
    )


# ---------------------------------------------------------------------------
# 2. Shared retry helper
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retry_http_retries_on_500_then_succeeds():
    from backend.context.tools.retry import retry_http

    calls = []

    @retry_http(max_attempts=3)
    async def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise httpx.HTTPStatusError(
                "500", request=httpx.Request("GET", "http://x"),
                response=httpx.Response(500),
            )
        return "ok"

    result = await flaky()
    assert result == "ok"
    assert len(calls) == 3


@pytest.mark.asyncio
async def test_retry_http_retries_on_429():
    from backend.context.tools.retry import retry_http

    calls = []

    @retry_http(max_attempts=3)
    async def rate_limited():
        calls.append(1)
        if len(calls) < 2:
            raise httpx.HTTPStatusError(
                "429", request=httpx.Request("GET", "http://x"),
                response=httpx.Response(429),
            )
        return "ok"

    assert await rate_limited() == "ok"
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_retry_http_does_not_retry_on_401():
    from backend.context.tools.retry import retry_http

    calls = []

    @retry_http(max_attempts=3)
    async def forbidden():
        calls.append(1)
        raise httpx.HTTPStatusError(
            "401", request=httpx.Request("GET", "http://x"),
            response=httpx.Response(401),
        )

    with pytest.raises(httpx.HTTPStatusError):
        await forbidden()
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_retry_http_gives_up_after_max_attempts():
    from backend.context.tools.retry import retry_http

    calls = []

    @retry_http(max_attempts=3)
    async def always_500():
        calls.append(1)
        raise httpx.HTTPStatusError(
            "500", request=httpx.Request("GET", "http://x"),
            response=httpx.Response(500),
        )

    with pytest.raises(httpx.HTTPStatusError):
        await always_500()
    assert len(calls) == 3
