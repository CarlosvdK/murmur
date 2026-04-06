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

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/news/search",
                headers={"X-Subscription-Token": settings.brave_search_api_key},
                params={"q": search_query, "count": 8, "freshness": "pm"},
            )
            resp.raise_for_status()
            data = resp.json()

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
