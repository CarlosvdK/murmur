"""Tests for backend.swarm.aggregator -- helper functions."""

from unittest.mock import patch

from backend.swarm.aggregator import _handle_conditional_block, _build_aggregation_prompt
from backend.models.business import BusinessSnapshot


def _business():
    return BusinessSnapshot(
        name="Corner Cafe",
        type="cafe",
        description="Specialty coffee and pastries.",
    )


# ---------------------------------------------------------------------------
# _handle_conditional_block (aggregator's own copy)
# ---------------------------------------------------------------------------

class TestHandleConditionalBlock:
    def test_include_true(self):
        prompt = "Before {{#if ctx}}MIDDLE{{/if}} After"
        result = _handle_conditional_block(prompt, "ctx", include=True)
        assert "MIDDLE" in result
        assert "{{#if" not in result
        assert "{{/if}}" not in result

    def test_include_false(self):
        prompt = "Before {{#if ctx}}MIDDLE{{/if}} After"
        result = _handle_conditional_block(prompt, "ctx", include=False)
        assert "MIDDLE" not in result
        assert "Before" in result
        assert "After" in result

    def test_multiline_block_included(self):
        prompt = "A\n{{#if x}}B\nC{{/if}}\nD"
        result = _handle_conditional_block(prompt, "x", include=True)
        assert "B" in result
        assert "C" in result

    def test_multiline_block_excluded(self):
        prompt = "A\n{{#if x}}B\nC{{/if}}\nD"
        result = _handle_conditional_block(prompt, "x", include=False)
        assert "B" not in result
        assert "D" in result


# ---------------------------------------------------------------------------
# _build_aggregation_prompt
# ---------------------------------------------------------------------------

class TestBuildAggregationPrompt:
    @patch("backend.swarm.aggregator._load_prompt")
    def test_replaces_basic_variables(self, mock_load):
        mock_load.return_value = (
            "Business: {{business_name}} ({{business_type}}). "
            "Description: {{business_description}}. "
            "Question: {{question}}. "
            "Count: {{response_count}}. "
            "Responses: {{persona_responses_json}}"
        )
        responses = [{"persona_name": "Elena", "sentiment": 0.5}]
        result = _build_aggregation_prompt(
            _business(), "Raise prices?", responses,
        )
        assert "Corner Cafe" in result
        assert "cafe" in result
        assert "Raise prices?" in result
        assert "1" in result  # response_count
        assert "Elena" in result

    @patch("backend.swarm.aggregator._load_prompt")
    def test_context_narrative_included(self, mock_load):
        mock_load.return_value = (
            "{{question}} "
            "{{#if context_narrative}}Context: {{context_narrative}}{{/if}}"
        )
        result = _build_aggregation_prompt(
            _business(), "Q?", [],
            context_narrative="Area is gentrifying.",
        )
        assert "Area is gentrifying." in result

    @patch("backend.swarm.aggregator._load_prompt")
    def test_context_narrative_excluded(self, mock_load):
        mock_load.return_value = (
            "{{question}} "
            "{{#if context_narrative}}Context: {{context_narrative}}{{/if}}"
        )
        result = _build_aggregation_prompt(_business(), "Q?", [])
        assert "Context:" not in result

    @patch("backend.swarm.aggregator._load_prompt")
    def test_ab_variants_included(self, mock_load):
        mock_load.return_value = (
            "{{question}} "
            "{{#if variant_a}}A={{variant_a}} B={{variant_b}}{{/if}}"
        )
        result = _build_aggregation_prompt(
            _business(), "Which?", [],
            variant_a="Old", variant_b="New",
        )
        assert "Old" in result
        assert "New" in result

    @patch("backend.swarm.aggregator._load_prompt")
    def test_ab_variants_excluded(self, mock_load):
        mock_load.return_value = (
            "{{question}} "
            "{{#if variant_a}}A={{variant_a}} B={{variant_b}}{{/if}}"
        )
        result = _build_aggregation_prompt(_business(), "Q?", [])
        assert "A=" not in result
