"""
Public social sentiment from Reddit.

Searches for discussions about the business type/location/topic.
Lower priority tool -- only invoked when the orchestrator identifies
a specific social sentiment angle.
"""

import logging
from typing import Optional

import httpx

from backend.config import get_settings
from backend.context.tools.base import ContextTool

logger = logging.getLogger(__name__)


class SocialSentimentTool(ContextTool):
    name = "social_sentiment"
    description = (
        "Search Reddit for public discussions about the business type, "
        "location, or topic. Captures real customer sentiment and "
        "concerns that may not appear in reviews. Lower priority."
    )
    required_config = ["reddit_client_id", "reddit_client_secret"]

    async def execute(
        self,
        business_name: str,
        business_type: str,
        location: Optional[str],
        question: str,
        hints: dict,
    ) -> dict:
        settings = get_settings()
        access_token = await self._get_token(settings)
        if not access_token:
            return {"available": False, "reason": "Reddit auth failed"}

        search_query = hints.get(
            "search_query",
            f"{business_type} {location or ''} price",
        )
        subreddit = hints.get("subreddit", "")

        url = "https://oauth.reddit.com/search"
        if subreddit:
            url = f"https://oauth.reddit.com/r/{subreddit}/search"

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "User-Agent": "Murmur/1.0",
                },
                params={
                    "q": search_query,
                    "sort": "relevance",
                    "limit": 10,
                    "t": "year",
                    "restrict_sr": "on" if subreddit else "off",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        posts = []
        for child in data.get("data", {}).get("children", [])[:10]:
            post = child.get("data", {})
            posts.append({
                "title": post.get("title", ""),
                "selftext": (post.get("selftext") or "")[:300],
                "subreddit": post.get("subreddit", ""),
                "score": post.get("score", 0),
                "num_comments": post.get("num_comments", 0),
                "url": f"https://reddit.com{post.get('permalink', '')}",
            })

        return {
            "search_query": search_query,
            "post_count": len(posts),
            "posts": posts,
        }

    async def _get_token(self, settings) -> Optional[str]:
        """Get Reddit OAuth2 access token."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    "https://www.reddit.com/api/v1/access_token",
                    auth=(settings.reddit_client_id, settings.reddit_client_secret),
                    data={"grant_type": "client_credentials"},
                    headers={"User-Agent": "Murmur/1.0"},
                )
                resp.raise_for_status()
                return resp.json().get("access_token")
        except Exception as e:
            logger.error("Reddit auth failed: %s", e)
            return None
