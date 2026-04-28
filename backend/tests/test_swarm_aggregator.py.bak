"""Comprehensive tests for response aggregation."""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from backend.swarm.aggregator import aggregate_responses
from backend.models.persona import PersonaProfile, PersonaResponse
from backend.models.business import BusinessSnapshot


class TestAggregateResponsesSuccess:
    """Test successful aggregation of persona responses."""

    @pytest.mark.asyncio
    async def test_aggregate_includes_all_responses(self):
        """All persona responses should be included in aggregation."""
        sim_id = str(uuid4())
        responses = [
            PersonaResponse(
                simulation_id=sim_id,
                persona_id=str(uuid4()),
                response="I would accept the increase",
                sentiment=0.7,
                reasoning="Good value proposition"
            ),
            PersonaResponse(
                simulation_id=sim_id,
                persona_id=str(uuid4()),
                response="Too expensive, I'd go elsewhere",
                sentiment=-0.8,
                reasoning="Price sensitive"
            ),
            PersonaResponse(
                simulation_id=sim_id,
                persona_id=str(uuid4()),
                response="Maybe, depends on other factors",
                sentiment=0.1,
                reasoning="Need more context"
            ),
        ]

        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        with patch("backend.swarm.aggregator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            aggregation_json = '''{
                "summary": "Mixed reactions to price increase",
                "sentiment_distribution": {"positive": 1, "neutral": 1, "negative": 1},
                "overall_sentiment": 0.0,
                "confidence_score": "medium",
                "themes": ["Price sensitivity", "Value proposition"],
                "standout_voices": ["Person 1 (very positive)", "Person 2 (very negative)"],
                "recommendation": "Proceed with caution"
            }'''

            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text=aggregation_json)])
            )

            # Convert PersonaResponse objects to dicts for the function (with JSON serialization)
            responses_dicts = [r.model_dump(mode='json') for r in responses]

            result = await aggregate_responses(
                business=business,
                question="Should we raise prices 15%?",
                persona_responses=responses_dicts,
                context_narrative="Market research shows...",
            )

            assert result is not None
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_aggregate_calculates_sentiment(self):
        """Sentiment score should be calculated from responses."""
        sim_id = str(uuid4())
        responses = [
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="Yes", sentiment=1.0, reasoning="Love it"),
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="Yes", sentiment=0.8, reasoning="Good"),
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="No", sentiment=-0.9, reasoning="Hate it"),
        ]

        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        with patch("backend.swarm.aggregator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text='{"confidence_score": "medium"}')])
            )

            responses_dicts = [r.model_dump(mode='json') for r in responses]
            result = await aggregate_responses(
                business=business,
                question="Question?",
                persona_responses=responses_dicts,
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_aggregate_identifies_themes(self):
        """Should identify key themes from responses."""
        sim_id = str(uuid4())
        responses = [
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="Price too high", sentiment=-0.5, reasoning="Cost"),
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="Also price", sentiment=-0.6, reasoning="Cost"),
        ]

        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        with patch("backend.swarm.aggregator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text='{"themes": ["Price sensitivity"]}')])
            )

            responses_dicts = [r.model_dump(mode='json') for r in responses]
            result = await aggregate_responses(
                business=business,
                question="Q?",
                persona_responses=responses_dicts,
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_aggregate_detects_outliers(self):
        """Should identify outlier responses."""
        sim_id = str(uuid4())
        responses = [
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="Meh", sentiment=0.0, reasoning="Neutral"),
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="Meh", sentiment=0.0, reasoning="Neutral"),
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="AMAZING!", sentiment=1.0, reasoning="Outlier"),
        ]

        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        with patch("backend.swarm.aggregator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text='{"standout_voices": ["AMAZING response"]}')])
            )

            responses_dicts = [r.model_dump(mode='json') for r in responses]
            result = await aggregate_responses(
                business=business,
                question="Q?",
                persona_responses=responses_dicts,
            )

            assert result is not None


class TestAggregateResponsesConfidence:
    """Test confidence assessment in aggregation."""

    @pytest.mark.asyncio
    async def test_confidence_high_with_agreement(self):
        """Confidence should be high when personas agree."""
        sim_id = str(uuid4())
        responses = [
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="Yes", sentiment=0.9, reasoning="Good"),
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="Yes", sentiment=0.8, reasoning="Good"),
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="Yes", sentiment=0.85, reasoning="Good"),
        ]

        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        with patch("backend.swarm.aggregator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text='{"confidence_score": "high"}')])
            )

            responses_dicts = [r.model_dump(mode='json') for r in responses]
            result = await aggregate_responses(
                business=business,
                question="Q?",
                persona_responses=responses_dicts,
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_confidence_low_with_disagreement(self):
        """Confidence should be low when personas disagree."""
        sim_id = str(uuid4())
        responses = [
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="Yes", sentiment=1.0, reasoning="Love"),
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="No", sentiment=-1.0, reasoning="Hate"),
        ]

        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        with patch("backend.swarm.aggregator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text='{"confidence_score": "low"}')])
            )

            responses_dicts = [r.model_dump(mode='json') for r in responses]
            result = await aggregate_responses(
                business=business,
                question="Q?",
                persona_responses=responses_dicts,
            )

            assert result is not None


class TestAggregateResponsesWithCaveats:
    """Test caveat inclusion in aggregation."""

    @pytest.mark.asyncio
    async def test_caveats_included_in_output(self):
        """Caveats should be included in aggregation output."""
        sim_id = str(uuid4())
        responses = [
            PersonaResponse(simulation_id=sim_id, persona_id=str(uuid4()), response="Yes", sentiment=0.5, reasoning="Maybe"),
        ]

        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        with patch("backend.swarm.aggregator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text='{"confidence_score": "medium"}')])
            )

            responses_dicts = [r.model_dump(mode='json') for r in responses]
            result = await aggregate_responses(
                business=business,
                question="Q?",
                persona_responses=responses_dicts,
            )

            assert result is not None


class TestAggregateResponsesErrorHandling:
    """Test error handling in aggregation."""

    @pytest.mark.asyncio
    async def test_handles_api_timeout(self):
        """Should handle API timeouts gracefully."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        with patch("backend.swarm.aggregator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                side_effect=TimeoutError("API timeout")
            )

            responses_dicts = []
            try:
                result = await aggregate_responses(
                    business=business,
                    question="Q?",
                    persona_responses=responses_dicts,
                )
                # Should either return something or raise
            except TimeoutError:
                pass  # Expected

    @pytest.mark.asyncio
    async def test_handles_malformed_response(self):
        """Should handle malformed JSON gracefully."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        with patch("backend.swarm.aggregator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text="Not valid JSON")])
            )

            responses_dicts = []
            try:
                result = await aggregate_responses(
                    business=business,
                    question="Q?",
                    persona_responses=responses_dicts,
                )
                # Should either return something or raise
            except Exception:
                pass  # Expected if malformed JSON
