"""Tests for backend.context.engine -- gather_context behavior."""

import pytest
from unittest.mock import patch, AsyncMock

from backend.context.engine import gather_context
from backend.models.business import BusinessSnapshot
from backend.models.context import BusinessContext


def _business():
    return BusinessSnapshot(
        name="Corner Cafe",
        type="cafe",
        description="Specialty coffee and pastries.",
    )


# ---------------------------------------------------------------------------
# Context disabled
# ---------------------------------------------------------------------------

class TestContextDisabled:
    @pytest.mark.asyncio
    async def test_returns_empty_when_disabled(self):
        """When context_enabled=False, should return empty BusinessContext."""
        from backend.config import Settings

        disabled_settings = Settings(
            anthropic_api_key="fake",
            supabase_url="https://fake.supabase.co",
            supabase_key="fake",
            context_enabled=False,
        )
        with patch("backend.context.engine.get_settings", return_value=disabled_settings):
            result = await gather_context(_business(), "Any question?")

        assert isinstance(result, BusinessContext)
        assert result.filtered_narrative == ""
        assert result.tools_planned == []
        assert result.tools_succeeded == 0


# ---------------------------------------------------------------------------
# Never raises
# ---------------------------------------------------------------------------

class TestNeverRaises:
    @pytest.mark.asyncio
    async def test_returns_empty_on_orchestrator_failure(self):
        """gather_context must never raise -- returns empty on failure."""
        from backend.config import Settings

        settings = Settings(
            anthropic_api_key="fake",
            supabase_url="https://fake.supabase.co",
            supabase_key="fake",
            context_enabled=True,
            context_timeout=5,
        )
        with patch("backend.context.engine.get_settings", return_value=settings), \
             patch("backend.context.engine.plan_research", side_effect=RuntimeError("boom")):
            result = await gather_context(_business(), "What if we raise prices?")

        assert isinstance(result, BusinessContext)
        assert result.filtered_narrative == ""

    @pytest.mark.asyncio
    async def test_returns_empty_on_timeout(self):
        """gather_context handles timeout gracefully."""
        import asyncio
        from backend.config import Settings

        settings = Settings(
            anthropic_api_key="fake",
            supabase_url="https://fake.supabase.co",
            supabase_key="fake",
            context_enabled=True,
            context_timeout=1,  # 1 second timeout
        )

        async def slow_plan(*args, **kwargs):
            await asyncio.sleep(10)

        with patch("backend.context.engine.get_settings", return_value=settings), \
             patch("backend.context.engine.plan_research", side_effect=slow_plan):
            result = await gather_context(_business(), "Q?")

        assert isinstance(result, BusinessContext)
        assert result.filtered_narrative == ""

    @pytest.mark.asyncio
    async def test_progress_callback_on_failure(self):
        """Progress callback should be called when context fails."""
        from backend.config import Settings

        settings = Settings(
            anthropic_api_key="fake",
            supabase_url="https://fake.supabase.co",
            supabase_key="fake",
            context_enabled=True,
            context_timeout=5,
        )
        progress_messages = []

        with patch("backend.context.engine.get_settings", return_value=settings), \
             patch("backend.context.engine.plan_research", side_effect=RuntimeError("fail")):
            await gather_context(
                _business(), "Q?",
                on_progress=lambda msg: progress_messages.append(msg),
            )

        assert len(progress_messages) > 0
        assert any("failed" in msg.lower() or "proceeding" in msg.lower() for msg in progress_messages)
