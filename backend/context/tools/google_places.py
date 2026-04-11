"""
Competitor discovery and review extraction via Google Places API (New).

Finds nearby businesses of the same type and extracts:
- Price levels, ratings, review counts
- Recent review text mentioning price, value, alternatives

Fallback: if no API key, tool reports as unavailable and orchestrator skips it.
"""

import logging
from typing import Optional

import httpx

from backend.config import get_settings
from backend.context.tools.base import ContextTool

logger = logging.getLogger(__name__)


ONLINE_ONLY_TYPES = {
    "saas", "ecommerce", "app", "it_services", "web_design", "hosting",
    "cybersecurity", "data_analytics", "b2b_services", "staffing",
    "marketing_agency", "freelance",
}


class GooglePlacesTool(ContextTool):
    name = "google_places"
    description = (
        "Find nearby competitor businesses with ratings, price levels, and "
        "review counts. Use to understand the competitive landscape within "
        "walking distance. Provide competitor_type and search_radius in hints. "
        "Not applicable for online-only businesses (SaaS, e-commerce, etc.)."
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
        # Skip for online-only businesses
        if business_type in ONLINE_ONLY_TYPES:
            logger.info("Skipping google_places for online business type: %s", business_type)
            return {
                "status": "skipped",
                "reason": f"Not applicable for {business_type} businesses (no physical location)",
                "competitors": [],
            }

        settings = get_settings()
        api_key = settings.google_places_api_key
        competitor_type = hints.get("competitor_type", business_type)
        search_query = f"{competitor_type} near {location or 'me'}"

        async with httpx.AsyncClient(timeout=15) as client:
            # Text Search (New) endpoint
            resp = await client.post(
                "https://places.googleapis.com/v1/places:searchText",
                headers={
                    "X-Goog-Api-Key": api_key,
                    "X-Goog-FieldMask": (
                        "places.displayName,places.rating,places.userRatingCount,"
                        "places.priceLevel,places.formattedAddress,places.reviews"
                    ),
                },
                json={"textQuery": search_query, "maxResultCount": 10},
            )
            resp.raise_for_status()
            data = resp.json()

        competitors = []
        for place in data.get("places", [])[:10]:
            reviews_text = []
            for review in (place.get("reviews") or [])[:3]:
                text = (review.get("text") or {}).get("text", "")
                if text:
                    reviews_text.append(text[:200])

            competitors.append({
                "name": (place.get("displayName") or {}).get("text", "Unknown"),
                "rating": place.get("rating"),
                "review_count": place.get("userRatingCount", 0),
                "price_level": place.get("priceLevel", "unknown"),
                "address": place.get("formattedAddress", ""),
                "sample_reviews": reviews_text,
            })

        return {
            "search_query": search_query,
            "competitor_count": len(competitors),
            "competitors": competitors,
        }
