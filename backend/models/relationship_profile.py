"""
CustomerRelationshipProfile -- the universal signal that feeds ALL simulations.

Derived from the enriched survey data. This is NOT about price or financials.
It is about the emotional and behavioural relationship between the business
and its customers. This single object determines how personas respond to
ANY change -- hours, prices, menu, staff, layout, loyalty, anything.

Based on Bain, NielsenIQ, PwC, and NN/G research on what drives prediction
accuracy for customer behaviour questions.
"""

from pydantic import BaseModel
from typing import Optional


class CustomerRelationshipProfile(BaseModel):
    # What is this business to customers?
    business_role: str  # habit|daily_need|treat|social|convenience|destination

    # How embedded in their routine?
    visit_frequency: str  # daily|weekly|monthly|occasional|mixed
    regular_proportion: str  # almost_none|handful|solid_base|mostly_regulars

    # What specifically do they value?
    value_drivers: list[str]  # e.g. ["atmosphere", "personal_touch"]

    # Social context
    social_context: list[str]  # e.g. ["couple", "friends"]

    # Temporal patterns
    busy_days: list[str]
    busy_times: list[str]

    # Area context
    area_demographics: list[str]
    area_feel: str  # community|transactional|destination|passing_trade
    competitor_count: str  # only_one|one_two|three_five|six_plus

    # Derived scores
    relationship_strength: str  # strong|medium|transactional
    change_sensitivity: str  # high|medium|low

    # Historical context
    has_historical_data: bool = False
    historical_context: Optional[str] = None


def compute_relationship_profile(survey_data: dict) -> CustomerRelationshipProfile:
    """Derive the relationship profile from raw survey answers."""

    # Relationship strength score
    strength_score = 0

    business_role = survey_data.get("business_role", "convenience")
    if business_role in ("habit", "social", "destination"):
        strength_score += 3
    elif business_role in ("treat", "daily_need"):
        strength_score += 1

    visit_freq = survey_data.get("visit_frequency", "mixed")
    if visit_freq == "daily":
        strength_score += 3
    elif visit_freq == "weekly":
        strength_score += 2
    elif visit_freq == "monthly":
        strength_score += 1

    regular_prop = survey_data.get("regular_proportion", "handful")
    if regular_prop == "mostly_regulars":
        strength_score += 3
    elif regular_prop == "solid_base":
        strength_score += 2
    elif regular_prop == "handful":
        strength_score += 1

    value_drivers = set(survey_data.get("customer_value_drivers", []))
    deep_drivers = {"personal_touch", "atmosphere", "social", "specific_product", "consistency"}
    if value_drivers & deep_drivers:
        strength_score += 2

    relationship_strength = (
        "strong" if strength_score >= 7 else
        "medium" if strength_score >= 3 else
        "transactional"
    )

    # Change sensitivity score
    sensitivity_score = 0
    if visit_freq in ("daily", "weekly"):
        sensitivity_score += 2
    if business_role in ("habit", "social"):
        sensitivity_score += 2
    if "personal_touch" in value_drivers:
        sensitivity_score += 2
    if regular_prop in ("solid_base", "mostly_regulars"):
        sensitivity_score += 1

    change_sensitivity = (
        "high" if sensitivity_score >= 5 else
        "medium" if sensitivity_score >= 2 else
        "low"
    )

    return CustomerRelationshipProfile(
        business_role=business_role,
        visit_frequency=visit_freq,
        regular_proportion=regular_prop,
        value_drivers=list(survey_data.get("customer_value_drivers", [])),
        social_context=list(survey_data.get("customer_social_context", [])),
        busy_days=list(survey_data.get("busy_days", [])),
        busy_times=list(survey_data.get("busy_times", [])),
        area_demographics=list(survey_data.get("area_demographics", [])),
        area_feel=survey_data.get("area_feel", "mixed"),
        competitor_count=survey_data.get("competitor_count", "three_five"),
        relationship_strength=relationship_strength,
        change_sensitivity=change_sensitivity,
        has_historical_data=survey_data.get("has_prior_change", False),
        historical_context=survey_data.get("prior_change_description"),
    )
