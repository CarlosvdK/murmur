"""
General-purpose web search via Brave Search API.

The orchestrator passes specific search queries. This tool executes them
and uses a small Claude call to extract the specific signal requested,
rather than returning raw search results.

Brave Search free tier: 2000 queries/month.
"""

import json
import logging
from typing import Optional

import httpx
from anthropic import AsyncAnthropic
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
)

from backend.config import get_settings
from backend.context.tools.base import ContextTool

logger = logging.getLogger(__name__)


def _is_retryable_error(response):
    """Check if httpx.Response should be retried."""
    if isinstance(response, Exception):
        return False
    # Retry on 429 (rate limit) and 5xx (server errors)
    return response.status_code in (429, 500, 502, 503, 504)


def _should_not_retry_auth(exc):
    """Return True if we should NOT retry (auth errors)."""
    if isinstance(exc, httpx.HTTPStatusError):
        # Don't retry on 401, 403
        return exc.response.status_code not in (401, 403)
    return True


class WebSearchTool(ContextTool):
    name = "web_search"
    description = (
        "General web search. Use for any question that can be answered by "
        "searching the internet: competitor information, industry trends, "
        "local business news, pricing benchmarks, customer complaints. "
        "Provide a specific search_query in hints."
    )
    required_config = ["brave_search_api_key"]

    async def execute(
        self,
        business_name: str,
        business_type: str,
        location: Optional[str],
        question: str,
        hints: dict,
    ) -> dict:
        settings = get_settings()
        search_query = hints.get("search_query", f"{business_type} {location} {question}")

        data = await self._fetch_with_retry(search_query, settings.brave_search_api_key)

        results = []
        for item in data.get("web", {}).get("results", [])[:8]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("description", ""),
                "url": item.get("url", ""),
                "age": item.get("age", ""),
            })

        if not results:
            return {"search_query": search_query, "results": [], "extracted_insight": ""}

        # Use Claude to extract the relevant signal from search results
        extraction = await self._extract_insight(search_query, results, question)

        return {
            "search_query": search_query,
            "result_count": len(results),
            "results": results,
            "extracted_insight": extraction,
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        reraise=True,
    )
    async def _fetch_with_retry(self, search_query: str, api_key: str) -> dict:
        """Fetch search results with retry on transient errors."""
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={"X-Subscription-Token": api_key},
                params={"q": search_query, "count": 8, "freshness": "py"},
            )
            # Don't retry on auth errors (401, 403)
            if resp.status_code in (401, 403):
                raise httpx.HTTPStatusError(
                    f"Auth error: {resp.status_code}",
                    request=resp.request,
                    response=resp,
                )
            resp.raise_for_status()
            return resp.json()

    async def _extract_insight(
        self, query: str, results: list[dict], question: str
    ) -> str:
        """Use Claude to extract a concise insight from raw search results."""
        settings = get_settings()
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)

        results_text = "\n".join(
            f"- {r['title']}: {r['snippet']}" for r in results
        )

        resp = await client.messages.create(
            model=settings.model_name,
            max_tokens=300,
            system=(
                "Extract the single most relevant insight from these search results "
                "for someone asking this business question. Be specific and concise. "
                "One paragraph, no more than 3 sentences. If nothing is relevant, "
                "say 'No relevant findings.'"
            ),
            messages=[{
                "role": "user",
                "content": f"Search: {query}\nBusiness question: {question}\n\nResults:\n{results_text}",
            }],
        )
        return resp.content[0].text.strip()
