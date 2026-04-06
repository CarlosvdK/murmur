from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class ToolStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ToolResult(BaseModel):
    """Result from a single context tool execution."""

    tool_name: str
    status: ToolStatus
    raw_data: dict = {}
    summary: str = ""
    relevance_score: float = 0.0
    elapsed_seconds: float = 0.0
    error: Optional[str] = None


class BusinessContext(BaseModel):
    """Enriched context gathered before persona generation.

    Contains both raw tool results (for audit/logging) and a single
    filtered narrative block (for prompt injection).
    """

    tool_results: list[ToolResult] = []
    filtered_narrative: str = ""
    tools_planned: list[str] = []
    tools_succeeded: int = 0
    tools_failed: int = 0
    total_elapsed_seconds: float = 0.0
    orchestrator_reasoning: str = ""
    created_at: Optional[datetime] = None
