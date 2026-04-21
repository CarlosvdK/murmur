"""Phase 1 RED: observability + health tests.

Covers:
  - /api/health deep check (DB ping, version, env, git sha)
  - Request-ID middleware (adds + propagates X-Request-ID)
  - Structured JSON logging with request_id bound
  - Sentry init + capture wiring

All tests stub external systems (no real Supabase / Sentry DSN hits).
"""
from __future__ import annotations

import io
import json
import logging
import os
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_returns_ok_when_db_reachable(client):
    """Happy path: DB ping returns OK, health returns 200 with db=='ok'."""
    fake_db = MagicMock()
    fake_db.table.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
    with patch("backend.api.main.get_supabase", return_value=fake_db):
        resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["checks"]["db"] == "ok"


def test_health_returns_503_when_db_unreachable(client):
    """If DB ping raises, health reports degraded with 503."""
    def boom():
        raise RuntimeError("cannot reach Supabase")
    with patch("backend.api.main.get_supabase", side_effect=boom):
        resp = client.get("/api/health")
    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["db"] == "error"


def test_health_includes_version_and_environment(client):
    with patch("backend.api.main.get_supabase", return_value=MagicMock()):
        resp = client.get("/api/health")
    body = resp.json()
    assert "version" in body
    assert "environment" in body  # e.g. "development", "production"


def test_health_includes_git_sha_when_env_var_set(client, monkeypatch):
    monkeypatch.setenv("GIT_SHA", "abc1234")
    with patch("backend.api.main.get_supabase", return_value=MagicMock()):
        resp = client.get("/api/health")
    assert resp.json()["git_sha"] == "abc1234"


# ---------------------------------------------------------------------------
# Request-ID middleware
# ---------------------------------------------------------------------------


def test_response_has_x_request_id_header(client):
    """Every response should include X-Request-ID."""
    with patch("backend.api.main.get_supabase", return_value=MagicMock()):
        resp = client.get("/api/health")
    request_id = resp.headers.get("X-Request-ID") or resp.headers.get("x-request-id")
    assert request_id, "response missing X-Request-ID header"
    # Should be a UUID-ish token (not empty, reasonably long)
    assert len(request_id) >= 8


def test_incoming_x_request_id_is_echoed(client):
    """If caller sends X-Request-ID, server echoes the same value."""
    given = "trace-" + uuid.uuid4().hex[:12]
    with patch("backend.api.main.get_supabase", return_value=MagicMock()):
        resp = client.get("/api/health", headers={"X-Request-ID": given})
    echoed = resp.headers.get("X-Request-ID") or resp.headers.get("x-request-id")
    assert echoed == given


def test_each_request_gets_distinct_request_id(client):
    with patch("backend.api.main.get_supabase", return_value=MagicMock()):
        r1 = client.get("/api/health")
        r2 = client.get("/api/health")
    id1 = r1.headers.get("X-Request-ID") or r1.headers.get("x-request-id")
    id2 = r2.headers.get("X-Request-ID") or r2.headers.get("x-request-id")
    assert id1 and id2 and id1 != id2


# ---------------------------------------------------------------------------
# Structured JSON logging
# ---------------------------------------------------------------------------


def test_logger_emits_json_with_required_fields(caplog):
    """Application logs must serialize to JSON with timestamp/level/message."""
    from backend.observability.logging import configure_logging, get_logger

    buf = io.StringIO()
    handler = logging.StreamHandler(buf)
    configure_logging(handler=handler, level=logging.INFO)

    log = get_logger("murmur.test")
    log.info("hello world", extra={"foo": "bar"})

    # One of the buffered lines should parse as JSON with our fields
    for line in buf.getvalue().splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("message") == "hello world":
            assert rec.get("level", "").lower() == "info"
            assert "timestamp" in rec
            assert rec.get("foo") == "bar"
            return
    pytest.fail(f"No JSON log with message 'hello world' in: {buf.getvalue()!r}")


def test_request_id_is_bound_into_logs_during_request(client, caplog):
    """Inside a request, log records should carry the request_id."""
    from backend.observability.logging import get_logger

    with patch("backend.api.main.get_supabase", return_value=MagicMock()):
        with caplog.at_level(logging.INFO, logger="murmur"):
            resp = client.get("/api/health", headers={"X-Request-ID": "rid-abc-123"})

    assert resp.status_code == 200
    # At least one record logged within the request must carry the id.
    matching = [r for r in caplog.records if getattr(r, "request_id", None) == "rid-abc-123"]
    assert matching, (
        "expected at least one log record with request_id='rid-abc-123' during request; "
        f"records seen: {[(r.name, getattr(r, 'request_id', None)) for r in caplog.records]}"
    )


# ---------------------------------------------------------------------------
# Sentry integration
# ---------------------------------------------------------------------------


def test_sentry_initialized_when_dsn_set(monkeypatch):
    """If SENTRY_DSN is set, backend.observability.sentry.init() should
    call sentry_sdk.init with that DSN + sample rates from env."""
    monkeypatch.setenv("SENTRY_DSN", "https://public@o0.ingest.sentry.io/0")
    monkeypatch.setenv("SENTRY_TRACES_SAMPLE_RATE", "0.25")

    with patch("sentry_sdk.init") as sentry_init:
        from backend.observability.sentry import init_sentry
        init_sentry()

    assert sentry_init.called, "sentry_sdk.init should be called when DSN is set"
    kwargs = sentry_init.call_args.kwargs
    assert kwargs.get("dsn") == "https://public@o0.ingest.sentry.io/0"
    assert kwargs.get("traces_sample_rate") == 0.25


def test_sentry_noop_when_dsn_missing(monkeypatch):
    """No DSN -> no Sentry init call (local dev should be silent)."""
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    with patch("sentry_sdk.init") as sentry_init:
        from backend.observability.sentry import init_sentry
        init_sentry()
    assert not sentry_init.called
