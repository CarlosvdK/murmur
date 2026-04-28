"""Tests for backend.models -- Pydantic models."""

import uuid
from datetime import datetime

from backend.models.business import BusinessSnapshot, BusinessCreate
from backend.models.persona import PersonaProfile, PersonaResponse
from backend.models.simulation import (
    SimulationStatus,
    SimulationCreate,
    SimulationProgress,
)


# ---------------------------------------------------------------------------
# BusinessSnapshot
# ---------------------------------------------------------------------------

class TestBusinessSnapshot:
    def test_minimal_creation(self):
        biz = BusinessSnapshot(name="Test", type="cafe", description="A cafe.")
        assert biz.name == "Test"
        assert biz.type == "cafe"
        assert biz.customer_description is None
        assert biz.location is None

    def test_full_creation(self):
        biz = BusinessSnapshot(
            name="Corner Cafe",
            type="cafe",
            description="Great coffee.",
            customer_description="Local workers",
            location="Portland, OR",
            years_open="3-10",
            visit_frequency="daily",
            regular_proportion="mostly_regulars",
            area_demographics=["young_professionals", "students"],
            competitor_count="three_five",
        )
        assert biz.years_open == "3-10"
        assert biz.area_demographics == ["young_professionals", "students"]

    def test_optional_fields_default_none(self):
        biz = BusinessSnapshot(name="X", type="y", description="z")
        assert biz.customer_age_distribution is None
        assert biz.price_range is None
        assert biz.digital_savviness is None


# ---------------------------------------------------------------------------
# PersonaProfile
# ---------------------------------------------------------------------------

class TestPersonaProfile:
    def test_basic_creation(self):
        p = PersonaProfile(
            name="Elena",
            age=31,
            occupation="Designer",
            personality="Quiet",
            relationship_to_business="Regular",
            quirk="Orders the same thing",
        )
        assert p.name == "Elena"
        assert p.age == 31

    def test_avg_spend_dollars_per_visit(self):
        p = PersonaProfile(
            name="A", age=25, occupation="X",
            spend_model="$35 per visit",
            personality="Y", relationship_to_business="Z", quirk="Q",
        )
        assert p.avg_spend == 35.0

    def test_avg_spend_dollars_per_month(self):
        p = PersonaProfile(
            name="A", age=25, occupation="X",
            spend_model="$49/mo",
            personality="Y", relationship_to_business="Z", quirk="Q",
        )
        assert p.avg_spend == 49.0

    def test_avg_spend_empty(self):
        p = PersonaProfile(
            name="A", age=25, occupation="X",
            spend_model="",
            personality="Y", relationship_to_business="Z", quirk="Q",
        )
        assert p.avg_spend == 0.0

    def test_avg_spend_no_numbers(self):
        p = PersonaProfile(
            name="A", age=25, occupation="X",
            spend_model="varies widely",
            personality="Y", relationship_to_business="Z", quirk="Q",
        )
        assert p.avg_spend == 0.0

    def test_visit_frequency_alias(self):
        p = PersonaProfile(
            name="A", age=25, occupation="X",
            engagement_pattern="3x per week",
            personality="Y", relationship_to_business="Z", quirk="Q",
        )
        assert p.visit_frequency == "3x per week"
        assert p.visit_frequency == p.engagement_pattern

    def test_optional_enrichment_fields(self):
        p = PersonaProfile(
            name="A", age=25, occupation="X",
            personality="Y", relationship_to_business="Z", quirk="Q",
            segment="Silent Regulars",
            income_tier="middle",
            price_sensitivity="high",
            is_silent_majority=True,
            digital_behavior="mobile-first",
            decision_style="deliberate",
            openness=0.7,
            conscientiousness=0.8,
        )
        assert p.segment == "Silent Regulars"
        assert p.is_silent_majority is True
        assert p.openness == 0.7


# ---------------------------------------------------------------------------
# SimulationStatus enum
# ---------------------------------------------------------------------------

class TestSimulationStatus:
    def test_all_values_exist(self):
        expected = {
            "pending", "gathering_context", "generating_personas",
            "simulating", "aggregating", "completed", "failed",
        }
        actual = {s.value for s in SimulationStatus}
        assert actual == expected

    def test_string_comparison(self):
        assert SimulationStatus.COMPLETED == "completed"
        assert SimulationStatus.FAILED == "failed"


# ---------------------------------------------------------------------------
# SimulationCreate validation
# ---------------------------------------------------------------------------

class TestSimulationCreate:
    def test_basic_creation(self):
        sim = SimulationCreate(
            business_id=uuid.uuid4(),
            question="What if we raised prices 10%?",
        )
        assert sim.persona_count == 15  # default
        assert sim.variant_a is None
        assert sim.variant_b is None

    def test_custom_persona_count(self):
        sim = SimulationCreate(
            business_id=uuid.uuid4(),
            question="Test",
            persona_count=25,
        )
        assert sim.persona_count == 25

    def test_ab_variants(self):
        sim = SimulationCreate(
            business_id=uuid.uuid4(),
            question="Which menu is better?",
            variant_a="Current menu",
            variant_b="New seasonal menu",
        )
        assert sim.variant_a == "Current menu"
        assert sim.variant_b == "New seasonal menu"
