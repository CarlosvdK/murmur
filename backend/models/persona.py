from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class PersonaProfile(BaseModel):
    """A synthetic customer persona — inspired by OASIS UserInfo
    and synthetic-user-research OCEAN model."""
    name: str
    age: int
    occupation: str
    visit_frequency: str
    avg_spend: float
    personality: str  # OCEAN-inspired plain-language traits
    relationship_to_business: str
    quirk: str
    # OCEAN scores (0.0-1.0) for diversity tracking
    openness: Optional[float] = None
    conscientiousness: Optional[float] = None
    extraversion: Optional[float] = None
    agreeableness: Optional[float] = None
    neuroticism: Optional[float] = None


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
