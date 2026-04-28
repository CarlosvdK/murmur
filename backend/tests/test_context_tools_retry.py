"""Tests for HTTP retry behavior with tenacity in context tools."""
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
import respx
from backend.context.tools.web_search import WebSearchTool
from backend.context.tools.news_search import NewsSearchTool


@pytest.fixture
def mock_extract_insight():
    """Mock the Anthropic API call for insight extraction."""
    with patch.object(
        WebSearchTool,
        "_extract_insight",
        new_callable=AsyncMock,
        return_value="Test insight"
    ) as mock:
        yield mock


class TestWebSearchRetry:
    """Test retry behavior on web search API failures."""

    @pytest.mark.asyncio
    async def test_retries_on_429_rate_limit(self, mock_extract_insight):
        """Should retry on 429 rate limit and eventually succeed."""
        tool = WebSearchTool()

        with respx.mock:
            # First two calls return 429, third returns 200
            respx.get("https://api.search.brave.com/res/v1/web/search").mock(
                side_effect=[
                    httpx.Response(429, json={"error": "rate limit"}),
                    httpx.Response(429, json={"error": "rate limit"}),
                    httpx.Response(200, json={
                        "web": {"results": [
                            {"title": "Result", "url": "https://example.com", "description": "Result desc"}
                        ]}
                    }),
                ]
            )

            result = await tool.execute(
                business_name="Test Restaurant",
                business_type="restaurant",
                location="SF",
                question="What affects prices?",
                hints={},
            )
            assert result["result_count"] > 0

    @pytest.mark.asyncio
    async def test_retries_on_500_server_error(self, mock_extract_insight):
        """Should retry on 500 server error and eventually succeed."""
        tool = WebSearchTool()

        with respx.mock:
            respx.get("https://api.search.brave.com/res/v1/web/search").mock(
                side_effect=[
                    httpx.Response(500, json={"error": "server error"}),
                    httpx.Response(500, json={"error": "server error"}),
                    httpx.Response(200, json={
                        "web": {"results": [
                            {"title": "Result", "url": "https://example.com", "description": "Result desc"}
                        ]}
                    }),
                ]
            )

            result = await tool.execute(
                business_name="Test Restaurant",
                business_type="restaurant",
                location="SF",
                question="What affects prices?",
                hints={},
            )
            assert result["result_count"] > 0

    @pytest.mark.asyncio
    async def test_no_retry_on_401_auth_error(self):
        """Should NOT retry on 401 auth error — fail immediately."""
        tool = WebSearchTool()

        with respx.mock:
            respx.get("https://api.search.brave.com/res/v1/web/search").mock(
                return_value=httpx.Response(401, json={"error": "unauthorized"})
            )

            with pytest.raises(Exception):
                # Should raise immediately without retries
                await tool.execute(
                    business_name="Test Restaurant",
                    business_type="restaurant",
                    location="SF",
                    question="What affects prices?",
                    hints={},
                )

    @pytest.mark.asyncio
    async def test_no_retry_on_403_forbidden(self):
        """Should NOT retry on 403 forbidden — fail immediately."""
        tool = WebSearchTool()

        with respx.mock:
            respx.get("https://api.search.brave.com/res/v1/web/search").mock(
                return_value=httpx.Response(403, json={"error": "forbidden"})
            )

            with pytest.raises(Exception):
                await tool.execute(
                    business_name="Test Restaurant",
                    business_type="restaurant",
                    location="SF",
                    question="What affects prices?",
                    hints={},
                )

    @pytest.mark.asyncio
    async def test_raises_after_max_retries(self):
        """Should raise after exhausting retries (e.g., always 429)."""
        tool = WebSearchTool()

        with respx.mock:
            # Always return 429 — should eventually give up
            respx.get("https://api.search.brave.com/res/v1/web/search").mock(
                side_effect=httpx.Response(429, json={"error": "rate limit"})
            )

            with pytest.raises(Exception):
                await tool.execute(
                    business_name="Test Restaurant",
                    business_type="restaurant",
                    location="SF",
                    question="What affects prices?",
                    hints={},
                )


class TestNewsSearchRetry:
    """Test retry behavior on news search API."""

    @pytest.mark.asyncio
    async def test_retries_on_429(self):
        """Should retry on 429 rate limit."""
        tool = NewsSearchTool()

        with respx.mock:
            respx.get("https://api.search.brave.com/res/v1/news/search").mock(
                side_effect=[
                    httpx.Response(429, json={"error": "rate limit"}),
                    httpx.Response(200, json={
                        "results": [
                            {"title": "News", "url": "https://example.com", "description": "News desc"}
                        ]
                    }),
                ]
            )

            result = await tool.execute(
                business_name="Test Restaurant",
                business_type="restaurant",
                location="SF",
                question="What's happening?",
                hints={},
            )
            assert result["article_count"] > 0

    @pytest.mark.asyncio
    async def test_raises_after_max_retries(self):
        """Should raise after exhausting retries."""
        tool = NewsSearchTool()

        with respx.mock:
            respx.get("https://api.search.brave.com/res/v1/news/search").mock(
                side_effect=httpx.Response(429, json={"error": "rate limit"})
            )

            with pytest.raises(Exception):
                await tool.execute(
                    business_name="Test Restaurant",
                    business_type="restaurant",
                    location="SF",
                    question="What's happening?",
                    hints={},
                )
