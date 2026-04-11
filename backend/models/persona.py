from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class PersonaProfile(BaseModel):
    """A synthetic customer persona -- works for ALL business types.

    Core fields are industry-agnostic. engagement_pattern and spend_model
    replace the old visit_frequency and avg_spend to support subscriptions,
    contracts, per-session, and other business models beyond per-visit.
    """
    name: str
    age: int
    occupation: str
    # Industry-agnostic engagement (replaces visit_frequency)
    engagement_pattern: str = ""  # "daily user", "monthly subscriber", "3x/week", "quarterly review"
    # Industry-agnostic spend (replaces avg_spend)
    spend_model: str = ""  # "$49/mo subscription", "$35 per visit", "$5000 annual contract"
    personality: str  # OCEAN-inspired plain-language traits
    relationship_to_business: str
    quirk: str
    # New enriched fields
    segment: Optional[str] = None  # which customer segment
    income_tier: Optional[str] = None
    price_sensitivity: Optional[str] = None
    is_silent_majority: Optional[bool] = None
    digital_behavior: Optional[str] = None  # "mobile-first", "in-person", "desktop"
    decision_style: Optional[str] = None  # "impulsive", "deliberate", "committee"
    # OCEAN scores (0.0-1.0) for diversity tracking
    openness: Optional[float] = None
    conscientiousness: Optional[float] = None
    extraversion: Optional[float] = None
    agreeableness: Optional[float] = None
    neuroticism: Optional[float] = None

    # Backward-compatible aliases
    @property
    def visit_frequency(self) -> str:
        return self.engagement_pattern

    @property
    def avg_spend(self) -> float:
        """Extract a numeric value from spend_model if possible."""
        import re
        nums = re.findall(r"[\d.]+", self.spend_model)
        return float(nums[0]) if nums else 0.0


class Persona(BaseModel):
    id: UUID
    simulation_id: UUID
    name: str
    age: int
    occupation: Optional[str] = None
    visit_frequency: Optional[str] = None
    avg_spend: Optional[float] = None
    personality: Optional[str] = None
    relationship_to_business: Optional[str] = None
    quirk: Optional[str] = None
    profile: dict = {}
    created_at: datetime


class PersonaResponse(BaseModel):
    """A single persona's answer to the simulation question."""
    persona_id: UUID
    simulation_id: UUID
    response: str  # In-character reaction
    reasoning: str  # Why they feel this way
    sentiment: float  # -1.0 to 1.0
    preference: Optional[str] = None  # For A/B: "A", "B", "neither"
    preference_strength: Optional[str] = None  # "strong", "slight", "indifferent"
    raw_output: Optional[dict] = None
