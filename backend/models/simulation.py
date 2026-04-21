from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class SimulationStatus(str, Enum):
    PENDING = "pending"
    GATHERING_CONTEXT = "gathering_context"
    GENERATING_PERSONAS = "generating_personas"
    SIMULATING = "simulating"
    AGGREGATING = "aggregating"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationCreate(BaseModel):
    business_id: UUID
    question: str
    variant_a: Optional[str] = None
    variant_b: Optional[str] = None
    persona_count: int = 15


class Simulation(BaseModel):
    id: UUID
    business_id: UUID
    question: str
    variant_a: Optional[str] = None
    variant_b: Optional[str] = None
    status: SimulationStatus
    persona_count: int
    prompt_version: str
    business_snapshot: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class SimulationProgress(BaseModel):
    """Real-time progress for the frontend — inspired by MiroFish status cards."""
    simulation_id: UUID
    status: SimulationStatus
    step: str  # Human-readable current step
    personas_generated: int = 0
    personas_interviewed: int = 0
    personas_total: int = 0
    current_persona: Optional[str] = None  # Name of persona being interviewed
    elapsed_seconds: float = 0


class Theme(BaseModel):
    label: str
    summary: str
    count: int


class StandoutVoice(BaseModel):
    persona_name: str
    quote: str


class Citation(BaseModel):
    """A research section that informed the simulation result."""
    domain: str
    title: str
    similarity: float = Field(ge=0.0, le=1.0)


class SimulationResult(BaseModel):
    id: UUID
    simulation_id: UUID
    summary: str
    recommendation: Optional[str] = None
    confidence_score: str  # "high", "medium", "low"
    confidence_reasoning: Optional[str] = None
    winner: Optional[str] = None  # For A/B: "A", "B", "tie", "depends"
    winner_reasoning: Optional[str] = None
    themes: Optional[List[Theme]] = None
    standout_voices: Optional[List[StandoutVoice]] = None
    # Focus group data (Phase 5)
    baseline_summary: Optional[str] = None  # Summary of Turn 1 warmup data
    behavioral_prediction: Optional[dict] = None  # Turn 3 predicted behavior
    stated_vs_actual_gap: Optional[str] = None  # Aggregate say-do gap analysis
    demographic_breakdown: Optional[List[dict]] = None  # Responses grouped by segment
    citations: Optional[List[Citation]] = None  # Research sections that informed this result
    raw_output: dict = {}
    created_at: datetime
