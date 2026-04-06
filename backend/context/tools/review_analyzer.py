"""
Deep review sentiment analysis using Claude.

Goes beyond star ratings. Extracts:
- Specific themes (value, atmosphere, service, price)
- Loyalty signals ("always come here", "regular")
- Switching signals ("went elsewhere", "last time")

Requires Google Places API to fetch reviews.
"""

import logging
from typing import Optional

import httpx
from anthropic import AsyncAnthropic

from backend.config import get_settings
from backend.context.tools.base import ContextTool

logger = logging.getLogger(__name__)


class ReviewAnalyzerTool(ContextTool):
    name = "review_analyzer"
    description = (
        "Fetch and analyse customer reviews for the business or its "
        "competitors. Extracts themes around price, value, loyalty, and "
        "switching behaviour. Requires Google Places API."
    )
    required_config = ["google_places_api_key"]

    async def execute(
        self,
        business_name: str,
        business_type: str,
        location: Optional[str],
        question: str,
        hints: dict,
    ) -> dict:
        settings = get_settings()
        api_key = settings.google_places_api_key
        search_target = hints.get("search_target", business_name)
        search_query = f"{search_target} {location or ''}"

        # Find the business on Google Places
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://places.googleapis.com/v1/places:searchText",
                headers={
                    "X-Goog-Api-Key": api_key,
                    "X-Goog-FieldMask": "places.reviews,places.displayName,places.rating",
                },
                json={"textQuery": search_query, "maxResultCount": 3},
            )
            resp.raise_for_status()
            data = resp.json()

        all_reviews = []
        for place in data.get("places", [])[:3]:
            place_name = (place.get("displayName") or {}).get("text", "Unknown")
            for review in (place.get("reviews") or [])[:5]:
                text = (review.get("text") or {}).get("text", "")
                rating = review.get("rating")
                if text:
                    all_reviews.append({
                        "place": place_name,
                        "rating": rating,
                        "text": text[:300],
                    })

        if not all_reviews:
            return {"review_count": 0, "analysis": "No reviews found"}

        # Analyse reviews with Claude
        analysis = await self._analyze_reviews(all_reviews, question)

        return {
            "review_count": len(all_reviews),
            "reviews_sampled": all_reviews[:5],
            "analysis": analysis,
        }

    async def _analyze_reviews(self, reviews: list[dict], question: str) -> str:
        settings = get_settings()
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)

        reviews_text = "\n".join(
            f"[{r['place']}, {r['rating']} stars] {r['text']}" for r in reviews
        )

        resp = await client.messages.create(
            model=settings.model_name,
            max_tokens=400,
            system=(
                "Analyse these customer reviews and extract themes relevant to "
                "the business question. Focus on: price sensitivity, value "
                "perception, loyalty signals, switching behaviour, and common "
                "complaints. Be concise -- 3-5 bullet points max. No preamble."
            ),
            messages=[{
                "role": "user",
                "content": f"Question: {question}\n\nReviews:\n{reviews_text}",
            }],
        )
        return resp.content[0].text.strip()
