"""Pipeline hard-timeout guard.

The simulation pipeline can hang (Claude stall, context tool deadlock, etc).
A bounded wrapper ensures the background task eventually resolves and marks
the simulation FAILED with a clear message instead of silently lingering.
"""
from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_bounded_pipeline_returns_result_when_inner_completes_fast():
    from backend.api.routes.simulations import run_pipeline_with_timeout

    async def inner():
        return "done"

    result = await run_pipeline_with_timeout(inner(), sim_id="sim-1", timeout=2)
    assert result == "done"


@pytest.mark.asyncio
async def test_bounded_pipeline_marks_failed_on_timeout():
    from backend.api.routes import simulations as mod

    async def slow():
        await asyncio.sleep(5)
        return "never"

    failures: list[tuple[str, str]] = []

    def fake_mark_failed(sim_id: str, message: str):
        failures.append((sim_id, message))

    with patch.object(mod, "_mark_simulation_failed", side_effect=fake_mark_failed, create=True):
        result = await mod.run_pipeline_with_timeout(slow(), sim_id="sim-1", timeout=0.1)

    assert result is None
    assert failures, "expected _mark_simulation_failed to be called on timeout"
    sim_id, message = failures[0]
    assert sim_id == "sim-1"
    assert "timed out" in message.lower() or "timeout" in message.lower()


@pytest.mark.asyncio
async def test_bounded_pipeline_propagates_inner_exceptions_after_marking_failed():
    """If the pipeline raises, we still want the sim marked failed."""
    from backend.api.routes import simulations as mod

    async def boom():
        raise RuntimeError("context engine blew up")

    failures: list[tuple[str, str]] = []

    def fake_mark_failed(sim_id: str, message: str):
        failures.append((sim_id, message))

    with patch.object(mod, "_mark_simulation_failed", side_effect=fake_mark_failed, create=True):
        result = await mod.run_pipeline_with_timeout(boom(), sim_id="sim-1", timeout=1)

    assert result is None
    assert failures, "expected _mark_simulation_failed on unhandled exception"
    sim_id, message = failures[0]
    assert "blew up" in message or "RuntimeError" in message
