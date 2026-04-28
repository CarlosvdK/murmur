"""Tests for backend.swarm.simulator -- helper functions only (no API calls)."""

import json
from unittest.mock import patch, MagicMock

from backend.swarm.simulator import (
    _handle_conditional_block,
    _parse_json_response,
    _build_interview_prompt,
    _build_warmup_prompt,
    _build_core_prompt,
    _build_depth_prompt,
)
from backend.models.business import BusinessSnapshot
from backend.models.persona import PersonaProfile


# ---------------------------------------------------------------------------
# Fixtures (local, not from conftest, to keep tests self-contained)
# ---------------------------------------------------------------------------

def _persona():
    return PersonaProfile(
        name="Elena",
        age=31,
        occupation="UX designer",
        engagement_pattern="3x per week",
        spend_model="$8 per visit",
        personality="Quietly opinionated",
        relationship_to_business="Regular",
        quirk="Judges milk steaming",
    )


def _business():
    return BusinessSnapshot(
        name="Corner Cafe",
        type="cafe",
        description="Specialty coffee and pastries.",
    )


# ---------------------------------------------------------------------------
# _handle_conditional_block
# ---------------------------------------------------------------------------

class TestHandleConditionalBlock:
    def test_include_true_removes_tags_keeps_content(self):
        prompt = "Before {{#if foo}}CONTENT{{/if}} After"
        result = _handle_conditional_block(prompt, "foo", include=True)
        assert "CONTENT" in result
        assert "{{#if" not in result
        assert "{{/if}}" not in result

    def test_include_false_removes_block_entirely(self):
        prompt = "Before {{#if foo}}CONTENT{{/if}} After"
        result = _handle_conditional_block(prompt, "foo", include=False)
        assert "CONTENT" not in result
        assert "Before" in result
        assert "After" in result

    def test_include_true_with_multiline_content(self):
        prompt = "Start\n{{#if ctx}}Line1\nLine2{{/if}}\nEnd"
        result = _handle_conditional_block(prompt, "ctx", include=True)
        assert "Line1" in result
        assert "Line2" in result

    def test_include_false_with_multiline_content(self):
        prompt = "Start\n{{#if ctx}}Line1\nLine2{{/if}}\nEnd"
        result = _handle_conditional_block(prompt, "ctx", include=False)
        assert "Line1" not in result
        assert "Start" in result
        assert "End" in result


# ---------------------------------------------------------------------------
# _parse_json_response
# ---------------------------------------------------------------------------

class TestParseJsonResponse:
    def test_valid_json(self):
        raw = '{"reaction": "I like it", "sentiment": 0.7}'
        result = _parse_json_response(raw)
        assert result["reaction"] == "I like it"
        assert result["sentiment"] == 0.7

    def test_markdown_fenced_json(self):
        raw = '```json\n{"reaction": "Sounds good", "sentiment": 0.5}\n```'
        result = _parse_json_response(raw)
        assert result["reaction"] == "Sounds good"

    def test_markdown_fenced_without_json_label(self):
        raw = '```\n{"reaction": "OK", "sentiment": 0.0}\n```'
        result = _parse_json_response(raw)
        assert result["reaction"] == "OK"

    def test_invalid_json_returns_fallback(self):
        raw = "This is not JSON at all, just rambling text."
        result = _parse_json_response(raw, turn_label="test")
        assert "_parse_error" in result
        assert "raw_text" in result

    def test_empty_string_returns_fallback(self):
        result = _parse_json_response("")
        assert "_parse_error" in result


# ---------------------------------------------------------------------------
# _build_interview_prompt
# ---------------------------------------------------------------------------

class TestBuildInterviewPrompt:
    @patch("backend.swarm.simulator._load_prompt")
    def test_replaces_all_template_variables(self, mock_load):
        mock_load.return_value = (
            "{{persona_name}} is {{persona_age}}, a {{persona_occupation}}. "
            "Business: {{business_name}} ({{business_type}}). "
            "{{business_description}} "
            "Visits: {{visit_frequency}}, spends: {{avg_spend}}. "
            "Personality: {{personality}}. "
            "Relationship: {{relationship_to_business}}. "
            "Quirk: {{quirk}}. "
            "Question: {{question}}"
        )
        prompt = _build_interview_prompt(_persona(), _business(), "Raise prices?")
        assert "Elena" in prompt
        assert "31" in prompt
        assert "UX designer" in prompt
        assert "Corner Cafe" in prompt
        assert "cafe" in prompt
        assert "Raise prices?" in prompt
        assert "{{" not in prompt

    @patch("backend.swarm.simulator._load_prompt")
    def test_context_narrative_included(self, mock_load):
        mock_load.return_value = (
            "{{persona_name}} {{question}} "
            "{{#if context_narrative}}Context: {{context_narrative}}{{/if}}"
        )
        prompt = _build_interview_prompt(
            _persona(), _business(), "Q?",
            context_narrative="Local area is gentrifying.",
        )
        assert "Local area is gentrifying." in prompt

    @patch("backend.swarm.simulator._load_prompt")
    def test_context_narrative_excluded(self, mock_load):
        mock_load.return_value = (
            "{{persona_name}} {{question}} "
            "{{#if context_narrative}}Context: {{context_narrative}}{{/if}}"
        )
        prompt = _build_interview_prompt(_persona(), _business(), "Q?")
        assert "Context:" not in prompt

    @patch("backend.swarm.simulator._load_prompt")
    def test_ab_variants_included(self, mock_load):
        mock_load.return_value = (
            "{{question}} "
            "{{#if variant_a}}A: {{variant_a}} vs B: {{variant_b}}{{/if}}"
        )
        prompt = _build_interview_prompt(
            _persona(), _business(), "Which?",
            variant_a="Option A", variant_b="Option B",
        )
        assert "Option A" in prompt
        assert "Option B" in prompt


# ---------------------------------------------------------------------------
# _build_warmup_prompt, _build_core_prompt, _build_depth_prompt
# ---------------------------------------------------------------------------

class TestFocusGroupPromptBuilders:
    @patch("backend.swarm.simulator._load_prompt")
    def test_warmup_replaces_business_name(self, mock_load):
        mock_load.return_value = "Tell me about your experience at {{business_name}}."
        result = _build_warmup_prompt(_business())
        assert "Corner Cafe" in result

    @patch("backend.swarm.simulator._load_prompt")
    def test_core_replaces_question(self, mock_load):
        mock_load.return_value = (
            "The owner is considering: {{question}} "
            "{{#if variant_a}}A={{variant_a}} B={{variant_b}}{{/if}}"
        )
        result = _build_core_prompt("Raise prices?")
        assert "Raise prices?" in result
        # No variants -> block removed
        assert "A=" not in result

    @patch("backend.swarm.simulator._load_prompt")
    def test_core_with_variants(self, mock_load):
        mock_load.return_value = (
            "{{question}} "
            "{{#if variant_a}}Compare: {{variant_a}} vs {{variant_b}}{{/if}}"
        )
        result = _build_core_prompt("Which menu?", variant_a="Old", variant_b="New")
        assert "Old" in result
        assert "New" in result

    @patch("backend.swarm.simulator._load_prompt")
    def test_depth_returns_template_as_is(self, mock_load):
        mock_load.return_value = "Now think about long-term behavior changes."
        result = _build_depth_prompt()
        assert result == "Now think about long-term behavior changes."
