"""
Test-Driven Development for persona archetype caching.

The key insight: personas represent customer demographics (static),
while context and responses are temporal (always fresh).

Logic:
1. Personas are generated ONCE per business and cached INDEFINITELY
2. Context is ALWAYS refreshed from APIs based on current date/question
3. Responses are ALWAYS generated fresh
4. Delete cached personas ONLY on explicit business profile change
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from backend.models.persona import PersonaProfile
from backend.models.business import BusinessSnapshot
from backend.swarm.persona_archetype import (
    get_or_create_archetype,
    delete_archetype_on_profile_change,
    is_profile_changed,
)


# ============================================================
# TEST: Personas cache indefinitely
# ============================================================

@pytest.mark.asyncio
async def test_personas_reuse_indefinitely():
    """
    Personas generated on Day 1 should be reused on Day 30
    without expiration.
    """
    db = MagicMock()
    business_id = "biz-123"
    business = BusinessSnapshot(name="Coffee Shop", description="Small cafe")
    persona_count = 5

    # Day 1: Generate personas
    mock_personas = [
        PersonaProfile(name="Maria", age=32, income=50000),
        PersonaProfile(name="John", age=45, income=60000),
    ]

    with pytest.mock.patch(
        "backend.swarm.persona_archetype.generate_personas",
        new_callable=AsyncMock,
        return_value=mock_personas,
    ):
        personas_day1, was_generated_day1 = await get_or_create_archetype(
            db, business_id, business, persona_count, manifest=None
        )

    assert was_generated_day1 is True
    assert len(personas_day1) == 2
    assert personas_day1[0].name == "Maria"

    # Day 30: Should reuse same personas (no expiration)
    db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{
            "profiles": [p.dict() for p in mock_personas],
            "expires_at": (datetime.now(timezone.utc)).isoformat(),  # Not expired
        }]
    )

    personas_day30, was_generated_day30 = await get_or_create_archetype(
        db, business_id, business, persona_count, manifest=None
    )

    assert was_generated_day30 is False  # Reused from cache
    assert personas_day30[0].name == "Maria"  # Same personas


# ============================================================
# TEST: Context always updates via APIs
# ============================================================

@pytest.mark.asyncio
async def test_context_refreshed_not_personas():
    """
    When user asks a new question, context should refresh from APIs
    but personas should NOT be regenerated.
    """
    db = MagicMock()
    business_id = "biz-123"
    business = BusinessSnapshot(name="Coffee Shop", description="Small cafe")

    # Question 1 on Day 1
    context_day1 = "Weather: rainy, temp 15C, inflation 3%, Ramadan starting"
    personas_q1, gen_q1 = await get_or_create_archetype(
        db, business_id, business, 5, context_narrative=context_day1
    )

    # Question 2 on Day 2 (different context, same personas)
    context_day2 = "Weather: sunny, temp 22C, inflation 3.2%, post-Ramadan"
    # Mock DB to return cached personas
    db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{
            "profiles": [p.dict() for p in personas_q1],
            "expires_at": (datetime.now(timezone.utc)).isoformat(),
        }]
    )

    personas_q2, gen_q2 = await get_or_create_archetype(
        db, business_id, business, 5, context_narrative=context_day2
    )

    # Same personas (gen_q2 should be False)
    assert gen_q2 is False
    # Context is different but personas are the same
    # (Context would be passed separately to the interview phase)


# ============================================================
# TEST: Personas deleted on business profile change
# ============================================================

@pytest.mark.asyncio
async def test_delete_personas_on_profile_change():
    """
    If the business profile changes significantly (different industry,
    different customer base), the persona cache should be invalidated.
    """
    db = MagicMock()
    business_id = "biz-123"

    # Original profile
    old_profile = BusinessSnapshot(
        name="Coffee Shop",
        description="High-end espresso bar, customers are professionals",
        industry="Food & Beverage"
    )

    # Changed profile (different customer base)
    new_profile = BusinessSnapshot(
        name="Budget Cafe",
        description="Low-cost diner, customers are students and workers",
        industry="Food & Beverage"
    )

    # Check if profiles are significantly different
    changed = is_profile_changed(old_profile, new_profile, threshold=0.5)
    assert changed is True

    # If changed, delete cached personas
    if changed:
        await delete_archetype_on_profile_change(db, business_id)
        db.table.return_value.delete.assert_called()


# ============================================================
# TEST: Backtest mode (no DB) still works
# ============================================================

@pytest.mark.asyncio
async def test_backtest_mode_no_cache():
    """
    When db=None (backtest mode), personas should be generated fresh
    every time, never cached.
    """
    db = None  # No database in backtest
    business_id = "biz-backtest"
    business = BusinessSnapshot(name="Test Business", description="Test")

    personas1, was_generated1 = await get_or_create_archetype(
        db, business_id, business, 5
    )
    assert was_generated1 is True

    personas2, was_generated2 = await get_or_create_archetype(
        db, business_id, business, 5
    )
    # In backtest, should generate fresh every time
    assert was_generated2 is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
