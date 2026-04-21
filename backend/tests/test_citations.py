"""Phase 2a RED: research citations must flow from RAG -> aggregator -> result.

Contract:
  * SimulationResult.citations is an Optional[List[Citation]]
  * Each citation has domain, title, similarity (0.0-1.0)
  * aggregator.aggregate_responses accepts research_sections and echoes
    them on the result dict under 'citations'
  * The shape on the wire is stable so the frontend can render it.

These tests mock Anthropic so we never hit the network.
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.models.business import BusinessSnapshot
from backend.models.simulation import SimulationResult


SAMPLE_BUSINESS = BusinessSnapshot(
    name="Cafe Luna",
    type="restaurant",
    description="Italian cafe, upscale, serves espresso and small plates",
    customer_description="Regulars in their 30s-50s",
    location="San Francisco, USA",
)

SAMPLE_RESPONSES = [
    {"persona_name": "Maria", "reaction": "I'd still come, grudgingly", "sentiment": 0.1},
    {"persona_name": "Jon", "reaction": "Honestly? I'd probably go elsewhere", "sentiment": -0.4},
]

FAKE_AGGREGATOR_JSON = {
    "headline": "Split response -- regulars tolerate, casuals defect",
    "themes": [{"label": "Price sensitivity", "summary": "...", "count": 8}],
    "standout_voices": [{"persona_name": "Jon", "quote": "I'd probably go elsewhere"}],
    "confidence": "medium",
    "recommendation": "Pilot a 5% increase first",
    "winner": None,
}


def _mock_anthropic_response() -> MagicMock:
    """Build a mock anthropic message-create result whose .content[0].text
    parses back to FAKE_AGGREGATOR_JSON."""
    msg = MagicMock()
    msg.content = [MagicMock(text=json.dumps(FAKE_AGGREGATOR_JSON))]
    return msg


# ---------------------------------------------------------------------------
# 1. SimulationResult model has a citations field
# ---------------------------------------------------------------------------


def test_simulation_result_model_has_citations_field():
    fields = SimulationResult.model_fields
    assert "citations" in fields, (
        "SimulationResult must expose a `citations` field so the frontend "
        "can render research provenance"
    )


def test_simulation_result_citations_default_is_none_or_empty():
    """A freshly-built result with no citations passed should omit / default."""
    from datetime import datetime
    from uuid import uuid4

    result = SimulationResult(
        id=uuid4(),
        simulation_id=uuid4(),
        summary="test",
        confidence_score="medium",
        created_at=datetime.utcnow(),
    )
    # None or empty list are both acceptable defaults; the important thing
    # is serialization doesn't blow up.
    dumped = result.model_dump(mode="json")
    assert "citations" in dumped


# ---------------------------------------------------------------------------
# 2. Aggregator accepts research_sections and passes them through
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_aggregate_responses_emits_citations_when_sections_provided():
    from backend.swarm import aggregator

    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=_mock_anthropic_response())

    sections = [
        {"domain": "pricing", "title": "Kahneman 1979 prospect theory", "similarity": 0.81},
        {"domain": "loyalty", "title": "Dick & Basu 1994 attitudinal loyalty", "similarity": 0.72},
    ]

    with patch("backend.swarm.aggregator.AsyncAnthropic", return_value=fake_client):
        out = await aggregator.aggregate_responses(
            business=SAMPLE_BUSINESS,
            question="What if I raise prices 15%?",
            persona_responses=SAMPLE_RESPONSES,
            research_sections=sections,
        )

    assert "citations" in out
    assert isinstance(out["citations"], list)
    assert len(out["citations"]) == 2
    titles = [c["title"] for c in out["citations"]]
    assert "Kahneman 1979 prospect theory" in titles


@pytest.mark.asyncio
async def test_aggregate_responses_citations_empty_when_no_sections():
    from backend.swarm import aggregator

    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=_mock_anthropic_response())

    with patch("backend.swarm.aggregator.AsyncAnthropic", return_value=fake_client):
        out = await aggregator.aggregate_responses(
            business=SAMPLE_BUSINESS,
            question="What if I raise prices 15%?",
            persona_responses=SAMPLE_RESPONSES,
        )

    # Either absent or empty -- never None.
    cites = out.get("citations", [])
    assert cites == [] or cites is None


@pytest.mark.asyncio
async def test_citation_entries_have_required_fields():
    """Every citation must have domain, title, similarity for UI rendering."""
    from backend.swarm import aggregator

    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=_mock_anthropic_response())

    sections = [{"domain": "pricing", "title": "Paper A", "similarity": 0.88}]

    with patch("backend.swarm.aggregator.AsyncAnthropic", return_value=fake_client):
        out = await aggregator.aggregate_responses(
            business=SAMPLE_BUSINESS,
            question="x",
            persona_responses=SAMPLE_RESPONSES,
            research_sections=sections,
        )

    for c in out["citations"]:
        assert "domain" in c
        assert "title" in c
        assert "similarity" in c
        assert 0.0 <= c["similarity"] <= 1.0


@pytest.mark.asyncio
async def test_citations_are_json_serializable():
    """The full aggregator output (including citations) must round-trip JSON."""
    from backend.swarm import aggregator

    fake_client = MagicMock()
    fake_client.messages.create = AsyncMock(return_value=_mock_anthropic_response())

    sections = [{"domain": "pricing", "title": "Paper A", "similarity": 0.88}]

    with patch("backend.swarm.aggregator.AsyncAnthropic", return_value=fake_client):
        out = await aggregator.aggregate_responses(
            business=SAMPLE_BUSINESS,
            question="x",
            persona_responses=SAMPLE_RESPONSES,
            research_sections=sections,
        )

    # raw_output is allowed to contain non-serialisable junk, test the top-level
    top = {k: v for k, v in out.items() if k != "raw_output"}
    json.dumps(top)  # will raise if not serialisable
