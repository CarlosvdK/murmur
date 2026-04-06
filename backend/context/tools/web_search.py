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

from backend.config import get_settings
from backend.context.tools.base import ContextTool

logger = logging.getLogger(__name__)


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

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={"X-Subscription-Token": settings.brave_search_api_key},
                params={"q": search_query, "count": 8, "freshness": "py"},
            )
            resp.raise_for_status()
            data = resp.json()

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
