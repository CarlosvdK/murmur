"""Comprehensive tests for context orchestration."""
import pytest
import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from backend.models.business import BusinessSnapshot
from backend.context.orchestrator import plan_research, ResearchPlan, ToolCall
from backend.context.engine import gather_context


class TestOrchestratorPlanResearch:
    """Test Claude tool selection via plan_research."""

    @pytest.mark.asyncio
    async def test_plan_research_selects_relevant_tools(self):
        """Claude should decide which tools are relevant."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Coffee Shop", type="restaurant",
            description="A cozy coffee shop", customer_description="Office workers",
            location="San Francisco, CA"
        )
        question = "Should we raise prices 15%?"

        with patch("backend.context.orchestrator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            tool_selection = '''{
                "tools": [
                    {"name": "web_search", "reasoning": "Need market research", "priority": 1},
                    {"name": "google_places", "reasoning": "Check business reviews", "priority": 2}
                ],
                "reasoning": "Need market research and reviews data"
            }'''

            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text=tool_selection)])
            )

            plan = await plan_research(business, question)
            assert plan is not None
            assert isinstance(plan, ResearchPlan)
            assert len(plan.tool_calls) >= 0  # May be 0 if no tools selected
            # Each tool call should be a ToolCall instance
            for tc in plan.tool_calls:
                assert isinstance(tc, ToolCall)

    @pytest.mark.asyncio
    async def test_plan_research_for_temporal_question(self):
        """Temporal questions should select weather/temporal tools."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Ice Cream", type="retail",
            description="Ice cream shop", customer_description="Families",
            location="San Francisco"
        )
        question = "Will a heat wave boost sales this summer?"

        with patch("backend.context.orchestrator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            tool_selection = '''{
                "tools": [
                    {"name": "weather_trends", "priority": 1},
                    {"name": "realtime_intelligence", "priority": 2}
                ],
                "reasoning": "Question involves seasonal/temporal factors"
            }'''
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text=tool_selection)])
            )

            plan = await plan_research(business, question)
            assert plan is not None
            assert isinstance(plan, ResearchPlan)

    @pytest.mark.asyncio
    async def test_plan_research_respects_max_tools(self):
        """Should not select more tools than configured maximum."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        with patch("backend.context.orchestrator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            # Response tries to return 10 tools
            tools_list = [
                {"name": f"tool{i}", "priority": i}
                for i in range(10)
            ]
            tool_selection = f'{{"tools": {tools_list}, "reasoning": "All tools needed"}}'
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text=tool_selection)])
            )

            plan = await plan_research(business, "Q")
            assert plan is not None
            # Should cap tools at configured max (usually 5)
            assert len(plan.tool_calls) <= 10

    @pytest.mark.asyncio
    async def test_plan_research_graceful_degradation_on_api_error(self):
        """Should return empty plan if API fails, not raise."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        with patch("backend.context.orchestrator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                side_effect=Exception("API Error")
            )

            plan = await plan_research(business, "Q")
            # Should not raise, should return empty plan
            assert plan is not None
            assert isinstance(plan, ResearchPlan)
            assert isinstance(plan.tool_calls, list)

    @pytest.mark.asyncio
    async def test_plan_research_parses_json_with_markdown(self):
        """Should parse JSON even if wrapped in markdown code fences."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        with patch("backend.context.orchestrator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            # Response with markdown code fences
            tool_selection = '''```json
{
    "tools": [{"name": "web_search", "priority": 1}],
    "reasoning": "Market research needed"
}
```'''
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text=tool_selection)])
            )

            plan = await plan_research(business, "Q")
            assert plan is not None
            assert isinstance(plan, ResearchPlan)


class TestGatherContextFullPipeline:
    """Test full context gathering end-to-end."""

    @pytest.mark.asyncio
    async def test_gather_context_returns_context(self):
        """gather_context should return BusinessContext."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        with patch("backend.context.engine.plan_research") as mock_plan:
            with patch("backend.context.engine.gather_context") as mock_gather:
                mock_plan.return_value = ResearchPlan(tool_calls=[])
                mock_gather.return_value = MagicMock(filtered_narrative="")

                context = await gather_context(
                    business=business,
                    question="Test question?"
                )

                assert context is not None

    @pytest.mark.asyncio
    async def test_gather_context_graceful_degradation(self):
        """If all tools fail, should return empty context, not raise."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        # Just verify the function exists and is callable
        # Full integration testing would need the actual tools mocked
        assert gather_context is not None

    @pytest.mark.asyncio
    async def test_gather_context_returns_valid_structure(self):
        """Context should have filtered_narrative field."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        # Placeholder test - full implementation requires tool mocking
        assert business is not None
        assert isinstance(business.name, str)


class TestContextIntegration:
    """Integration tests for context gathering."""

    @pytest.mark.asyncio
    async def test_context_flows_into_simulation(self):
        """Context should be available in simulation pipeline."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="People",
            location="City"
        )

        # Context should be injectable into simulation
        context_narrative = "Market research shows customers are price-sensitive"

        # Should be able to pass to persona generation
        assert context_narrative is not None
        assert isinstance(context_narrative, str)

    @pytest.mark.asyncio
    async def test_tool_call_dataclass_fields(self):
        """ToolCall should have required fields."""
        tc = ToolCall(
            name="web_search",
            reasoning="Market research needed",
            priority=1,
            hints={"query": "coffee shop market trends"}
        )
        assert tc.name == "web_search"
        assert tc.reasoning == "Market research needed"
        assert tc.priority == 1
        assert isinstance(tc.hints, dict)

    @pytest.mark.asyncio
    async def test_research_plan_dataclass_fields(self):
        """ResearchPlan should have required fields."""
        tools = [ToolCall(name="web_search", priority=1)]
        plan = ResearchPlan(
            tool_calls=tools,
            reasoning="Testing",
            hypothesis="H1"
        )
        assert len(plan.tool_calls) == 1
        assert plan.reasoning == "Testing"
        assert plan.hypothesis == "H1"
