"""Shared fixtures for backend tests."""

import pytest
from unittest.mock import patch

from backend.models.business import BusinessSnapshot
from backend.models.persona import PersonaProfile


@pytest.fixture
def sample_business() -> BusinessSnapshot:
    """A generic business snapshot for testing."""
    return BusinessSnapshot(
        name="Corner Cafe",
        type="cafe",
        description=(
            "A cozy neighborhood cafe serving specialty coffee and fresh pastries. "
            "We roast our own beans and bake everything in-house. Most customers "
            "are local professionals who stop by on their commute or freelancers "
            "who work here for hours. We are known for our single-origin pour-overs "
            "and the quiet atmosphere."
        ),
        customer_description=(
            "Mix of young professionals, remote workers, and retirees. "
            "Most live within a 10-minute walk."
        ),
        location="Portland, OR",
        years_open="3-10",
        visit_frequency="daily",
        regular_proportion="mostly_regulars",
    )


@pytest.fixture
def sample_persona() -> PersonaProfile:
    """A generic persona for testing."""
    return PersonaProfile(
        name="Elena",
        age=31,
        occupation="UX designer",
        engagement_pattern="3x per week",
        spend_model="$8 per visit",
        personality="Open and agreeable but quietly opinionated. Notices small details.",
        relationship_to_business="Regular who always sits at the window table",
        quirk="Judges a cafe by how they steam milk",
    )


@pytest.fixture
def saas_business() -> BusinessSnapshot:
    """A SaaS business snapshot for testing non-restaurant scenarios."""
    return BusinessSnapshot(
        name="TaskFlow",
        type="saas",
        description=(
            "Project management SaaS for small agencies. We help creative teams "
            "track projects, assign tasks, and bill clients from one dashboard. "
            "Most users are 5-20 person agencies paying $49/mo per seat."
        ),
        customer_description="Small creative agencies and freelance teams.",
        location="Remote / US-based",
    )


@pytest.fixture
def saas_persona() -> PersonaProfile:
    """A SaaS persona for testing."""
    return PersonaProfile(
        name="Marcus",
        age=38,
        occupation="Agency owner",
        engagement_pattern="daily user",
        spend_model="$49/mo subscription",
        personality="Pragmatic, impatient with bad UX, values reliability over flashiness.",
        relationship_to_business="Power user since beta, admin for 12-seat team",
        quirk="Keeps a spreadsheet rating every tool his team uses",
    )


@pytest.fixture
def mock_settings():
    """Patch get_settings to return safe test defaults (no real API keys)."""
    from backend.config import Settings

    test_settings = Settings(
        anthropic_api_key="test-key-not-real",
        supabase_url="https://fake.supabase.co",
        supabase_key="fake-key",
        supabase_service_role_key="fake-service-key",
        redis_url="redis://localhost:6379",
        persona_count=15,
        concurrency_limit=5,
        model_name="claude-sonnet-4-20250514",
        context_enabled=True,
        context_timeout=90,
        context_tool_timeout=30,
        context_max_tools=5,
    )
    with patch("backend.config.get_settings", return_value=test_settings):
        yield test_settings
