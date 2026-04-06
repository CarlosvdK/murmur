"""
Extracts AGGREGATE signals from Google Reviews using the Places API.

LEGAL CONSTRAINTS:
- Use Google Places API (New) only -- no scraping
- NEVER store reviewer names or any individually-identifying data
- Process reviews in memory, discard individual records before returning
- Output is aggregate statistics only -- no individual profiles

Based on:
- Karaman (2021): extremity bias in unsolicited reviews
- Han & Anderson (2026): platform-specific biases
- Gao et al. (2015): vocal minority vs silent majority
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

import httpx

from backend.config import get_settings

logger = logging.getLogger(__name__)

# Keywords for theme detection (applied across all reviews, never attributed to individuals)
PRICE_WORDS = {"expensive", "cheap", "pricey", "overpriced", "affordable", "value",
               "worth it", "rip off", "great price", "good price", "fair price",
               "too much", "cost", "prices went up", "price increase", "used to be cheaper"}
LOYALTY_WORDS = {"regular", "always come", "every week", "favourite", "favorite",
                 "our spot", "go-to", "come back", "returning", "loyal", "years"}
SWITCHING_WORDS = {"last time", "won't return", "went elsewhere", "never again",
                   "better options", "switched to", "tried instead", "competitor",
                   "used to come", "stopped coming"}
TOURIST_WORDS = {"visiting", "on holiday", "vacation", "trip to", "tourist",
                 "staying nearby", "hotel", "travel", "first time visiting"}
LOCAL_WORDS = {"local", "neighbourhood", "neighborhood", "live nearby",
               "work nearby", "office", "lunch break", "commute"}


@dataclass
class AggregateReviewSignals:
    place_id: str
    business_name: str
    total_review_count: int
    average_rating: float
    rating_distribution: dict[int, int]  # {1: 23, 2: 12, ...}

    # Sentiment themes (frequency as proportion of total reviews)
    price_mention_frequency: float
    value_positive_ratio: float
    loyalty_signal_frequency: float
    switching_signal_frequency: float

    # Customer type signals
    tourist_ratio_estimate: float
    local_ratio_estimate: float

    # Temporal patterns
    peak_days: list[str]

    # Price change history
    price_change_detected: bool
    price_change_sentiment: Optional[str]  # "negative", "neutral", "positive"

    # Review volume trend
    review_trend: str  # "growing", "stable", "declining"

    # Themes
    top_positive_themes: list[str]
    top_negative_themes: list[str]

    # Data quality
    signal_confidence: str  # "high" (100+), "medium" (20-99), "low" (<20)
    bias_warning: str


def _count_keyword_hits(text: str, keywords: set[str]) -> int:
    """Count how many keywords appear in a text (case-insensitive)."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def _detect_price_change(texts: list[str]) -> tuple[bool, Optional[str]]:
    """Detect mentions of price changes across all review texts."""
    change_phrases = ["prices went up", "raised prices", "more expensive than before",
                      "used to be cheaper", "since they raised", "price increase",
                      "cost more now", "prices have gone up"]
    positive_change = ["still worth it", "fair increase", "understandable"]
    negative_change = ["too expensive now", "not worth it anymore", "won't come back"]

    detected = False
    pos = 0
    neg = 0
    for text in texts:
        text_lower = text.lower()
        if any(phrase in text_lower for phrase in change_phrases):
            detected = True
            if any(p in text_lower for p in positive_change):
                pos += 1
            if any(p in text_lower for p in negative_change):
                neg += 1

    if not detected:
        return False, None
    if neg > pos:
        return True, "negative"
    if pos > neg:
        return True, "positive"
    return True, "neutral"


async def extract_review_signals(
    business_name: str,
    location: Optional[str],
    on_progress=None,
) -> Optional[AggregateReviewSignals]:
    """Extract aggregate review signals. Returns None if business not found."""
    settings = get_settings()
    api_key = settings.google_places_api_key

    if not api_key:
        logger.info("No Google Places API key -- skipping review extraction")
        return None

    if on_progress:
        on_progress("Searching for your business on Google...")

    # Step 1: Find the business
    search_query = f"{business_name} {location or ''}"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://places.googleapis.com/v1/places:searchText",
                headers={
                    "X-Goog-Api-Key": api_key,
                    "X-Goog-FieldMask": (
                        "places.id,places.displayName,places.rating,"
                        "places.userRatingCount,places.reviews"
                    ),
                },
                json={"textQuery": search_query, "maxResultCount": 1},
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.error("Google Places search failed: %s", e)
        return None

    places = data.get("places", [])
    if not places:
        logger.info("Business not found on Google Places: %s", search_query)
        return None

    place = places[0]
    place_id = place.get("id", "")
    display_name = (place.get("displayName") or {}).get("text", business_name)
    avg_rating = place.get("rating", 0.0)
    total_count = place.get("userRatingCount", 0)

    if on_progress:
        on_progress(f"Found {display_name} with {total_count} reviews -- analysing patterns...")

    # Step 2: Extract all available review texts for aggregate analysis
    # Google Places API returns up to 5 reviews per request
    raw_reviews = place.get("reviews") or []

    # Process reviews in memory -- extract text and rating only
    review_texts: list[str] = []
    review_ratings: list[int] = []

    for review in raw_reviews:
        text = (review.get("text") or {}).get("text", "")
        rating = review.get("rating", 3)
        if text:
            review_texts.append(text)
            review_ratings.append(rating)

    # Step 3: Build aggregate signals from all review texts
    n = len(review_texts)
    if n == 0:
        return AggregateReviewSignals(
            place_id=place_id,
            business_name=display_name,
            total_review_count=total_count,
            average_rating=avg_rating,
            rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            price_mention_frequency=0,
            value_positive_ratio=0,
            loyalty_signal_frequency=0,
            switching_signal_frequency=0,
            tourist_ratio_estimate=0.5,
            local_ratio_estimate=0.5,
            peak_days=[],
            price_change_detected=False,
            price_change_sentiment=None,
            review_trend="unknown",
            top_positive_themes=[],
            top_negative_themes=[],
            signal_confidence="low",
            bias_warning="Very few review texts available via API. Signals are directional only.",
        )

    # Rating distribution from available reviews
    rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in review_ratings:
        rating_dist[max(1, min(5, r))] = rating_dist.get(max(1, min(5, r)), 0) + 1

    # Theme frequencies
    price_hits = sum(1 for t in review_texts if _count_keyword_hits(t, PRICE_WORDS) > 0)
    loyalty_hits = sum(1 for t in review_texts if _count_keyword_hits(t, LOYALTY_WORDS) > 0)
    switching_hits = sum(1 for t in review_texts if _count_keyword_hits(t, SWITCHING_WORDS) > 0)
    tourist_hits = sum(1 for t in review_texts if _count_keyword_hits(t, TOURIST_WORDS) > 0)
    local_hits = sum(1 for t in review_texts if _count_keyword_hits(t, LOCAL_WORDS) > 0)

    # Value sentiment among price mentions
    value_positive = 0
    for t in review_texts:
        if _count_keyword_hits(t, PRICE_WORDS) > 0:
            t_lower = t.lower()
            if any(w in t_lower for w in ["worth it", "great value", "good price", "fair price", "affordable"]):
                value_positive += 1

    # Price change detection
    price_change, price_sentiment = _detect_price_change(review_texts)

    # Tourist vs local ratio estimate
    total_type_hits = tourist_hits + local_hits
    if total_type_hits > 0:
        tourist_ratio = tourist_hits / total_type_hits
    else:
        tourist_ratio = 0.3  # default assumption

    # Confidence level based on total review count (not just API-returned reviews)
    if total_count >= 100:
        confidence = "high"
    elif total_count >= 20:
        confidence = "medium"
    else:
        confidence = "low"

    signals = AggregateReviewSignals(
        place_id=place_id,
        business_name=display_name,
        total_review_count=total_count,
        average_rating=avg_rating,
        rating_distribution=rating_dist,
        price_mention_frequency=price_hits / n if n > 0 else 0,
        value_positive_ratio=value_positive / max(price_hits, 1),
        loyalty_signal_frequency=loyalty_hits / n if n > 0 else 0,
        switching_signal_frequency=switching_hits / n if n > 0 else 0,
        tourist_ratio_estimate=tourist_ratio,
        local_ratio_estimate=1 - tourist_ratio,
        peak_days=[],  # Would need timestamp data from API
        price_change_detected=price_change,
        price_change_sentiment=price_sentiment,
        review_trend="unknown",  # Would need historical data
        top_positive_themes=[],
        top_negative_themes=[],
        signal_confidence=confidence,
        bias_warning=(
            "Reviews represent less than 1% of actual customers. "
            "Reviewers skew toward extreme opinions (very happy or very unhappy). "
            "The moderate majority almost never reviews."
        ),
    )

    # CRITICAL: Discard all individual review data before returning
    del review_texts
    del review_ratings
    del raw_reviews

    logger.info(
        "Review signals extracted: %s, %d reviews, %.1f avg rating, confidence=%s",
        display_name, total_count, avg_rating, confidence,
    )

    return signals
