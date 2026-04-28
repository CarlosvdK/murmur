"""
Local and industry news search via Brave News API.

Catches signals like:
- "Barcelona restaurant prices rise amid cost of living crisis"
- "New office complex opening near [location]"
- "Local minimum wage increase"

Uses the same Brave API key as web_search.
"""

import logging
from typing import Optional

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from backend.config import get_settings
from backend.context.tools.base import ContextTool

logger = logging.getLogger(__name__)


class NewsSearchTool(ContextTool):
    name = "news_search"
    description = (
        "Search recent news for local events, industry trends, economic "
        "changes, or developments that would affect customer behaviour. "
        "Provide a search_query in hints focused on the location and topic."
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
        search_query = hints.get(
            "search_query",
            f"{business_type} {location or ''} news",
        )

        data = await self._fetch_with_retry(search_query, settings.brave_search_api_key)

        articles = []
        for item in data.get("results", [])[:8]:
            articles.append({
                "title": item.get("title", ""),
                "snippet": item.get("description", ""),
                "url": item.get("url", ""),
                "source": item.get("meta_url", {}).get("hostname", ""),
                "age": item.get("age", ""),
            })

        return {
            "search_query": search_query,
            "article_count": len(articles),
            "articles": articles,
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        reraise=True,
    )
    async def _fetch_with_retry(self, search_query: str, api_key: str) -> dict:
        """Fetch news with retry on transient errors."""
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/news/search",
                headers={"X-Subscription-Token": api_key},
                params={"q": search_query, "count": 8, "freshness": "pm"},
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
