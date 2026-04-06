"""
Survey helper endpoints for the enriched onboarding flow.

- /research-business: Phase 0 auto-lookup via Google Places + Claude
- /generate-description: AI drafts a business description
- /generate-customer-description: AI drafts a customer description
"""

import json
import logging
from typing import Optional

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from anthropic import AsyncAnthropic
from backend.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/survey", tags=["survey"])


class BusinessResearchRequest(BaseModel):
    input: str  # Business name, URL, or Google Maps link


class DescriptionRequest(BaseModel):
    name: str
    type: str
    location: Optional[str] = None
    years_open: Optional[str] = None


class CustomerDescRequest(BaseModel):
    business_name: str
    business_type: str
    location: Optional[str] = None
    business_description: Optional[str] = None


def _parse_json_response(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


@router.post("/research-business")
async def research_business(data: BusinessResearchRequest):
    """Phase 0 lookup. Searches Google Places, fetches website, Claude synthesises pre-fill."""
    settings = get_settings()

    if not settings.google_places_api_key:
        return {"confidence": "low", "name": data.input, "error": "No Google Places API key configured"}

    # Search Google Places
    places_result = {}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://places.googleapis.com/v1/places:searchText",
                headers={
                    "X-Goog-Api-Key": settings.google_places_api_key,
                    "X-Goog-FieldMask": (
                        "places.id,places.displayName,places.formattedAddress,"
                        "places.rating,places.userRatingCount,places.websiteUri,"
                        "places.types,places.priceLevel"
                    ),
                },
                json={"textQuery": data.input, "maxResultCount": 1},
            )
            resp.raise_for_status()
            results = resp.json()

        places = results.get("places", [])
        if places:
            p = places[0]
            places_result = {
                "place_id": p.get("id", ""),
                "name": (p.get("displayName") or {}).get("text", ""),
                "formatted_address": p.get("formattedAddress", ""),
                "rating": p.get("rating"),
                "review_count": p.get("userRatingCount", 0),
                "website": p.get("websiteUri"),
                "types": p.get("types", []),
                "price_level": p.get("priceLevel"),
            }
    except Exception as e:
        logger.error("Google Places search failed: %s", e)
        return {"confidence": "low", "name": data.input}

    if not places_result:
        return {"confidence": "low", "name": data.input}

    # Claude synthesises a pre-fill package
    try:
        ai_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await ai_client.messages.create(
            model=settings.model_name,
            max_tokens=600,
            messages=[{
                "role": "user",
                "content": (
                    f"Based on this Google Places data about a business, extract data to "
                    f"pre-fill an onboarding form. Be realistic and specific, not generic.\n\n"
                    f"Google Places data: {json.dumps(places_result)}\n"
                    f"User query: {data.input}\n\n"
                    f"Return ONLY valid JSON:\n"
                    f'{{"name": "business name", "type": "one of: restaurant|cafe|bar|barbershop|'
                    f'grocery|retail|gym|bakery|auto|other", "formatted_address": "full address", '
                    f'"description": "2-3 sentence description, second person, specific not generic", '
                    f'"years_open_estimate": "one of: <1|1-3|3-10|10+ or null", '
                    f'"confidence": "high|medium|low"}}'
                ),
            }],
        )

        pre_fill = _parse_json_response(response.content[0].text)
    except Exception as e:
        logger.error("Claude pre-fill synthesis failed: %s", e)
        pre_fill = {"confidence": "low"}

    # Merge Places data into pre-fill
    pre_fill["google_place_id"] = places_result.get("place_id")
    pre_fill["rating"] = places_result.get("rating")
    pre_fill["review_count"] = places_result.get("review_count")
    pre_fill["website"] = places_result.get("website")
    if not pre_fill.get("name"):
        pre_fill["name"] = places_result.get("name", data.input)
    if not pre_fill.get("formatted_address"):
        pre_fill["formatted_address"] = places_result.get("formatted_address", "")

    return pre_fill


@router.post("/generate-description")
async def generate_description(data: DescriptionRequest):
    """AI drafts a business description the owner can edit."""
    settings = get_settings()
    ai_client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    response = await ai_client.messages.create(
        model=settings.model_name,
        max_tokens=250,
        messages=[{
            "role": "user",
            "content": (
                f"Write a 2-3 sentence description of this business for the owner to review.\n\n"
                f"Business name: {data.name}\n"
                f"Type: {data.type}\n"
                f"Location: {data.location or 'unknown'}\n"
                f"Years open: {data.years_open or 'unknown'}\n\n"
                f"Rules:\n"
                f"- Write in second person ('You run...', 'Your...')\n"
                f"- Be grounded and specific, not generic marketing\n"
                f"- Keep it conversational\n"
                f"- Maximum 60 words\n"
                f"- Return only the description, no preamble"
            ),
        }],
    )

    return {"description": response.content[0].text.strip()}


@router.post("/generate-customer-description")
async def generate_customer_description(data: CustomerDescRequest):
    """AI drafts a customer description based on what's been filled in so far."""
    settings = get_settings()
    ai_client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    response = await ai_client.messages.create(
        model=settings.model_name,
        max_tokens=250,
        messages=[{
            "role": "user",
            "content": (
                f"Write a 2-3 sentence description of the typical customer for this business.\n\n"
                f"Business: {data.business_name}\n"
                f"Type: {data.business_type}\n"
                f"Location: {data.location or 'unknown'}\n"
                f"Business description: {data.business_description or 'not provided'}\n\n"
                f"Rules:\n"
                f"- Write in second person ('Your typical customer...')\n"
                f"- Describe who they are -- their life, not just demographics\n"
                f"- Include why they likely come\n"
                f"- Be realistic for this type of business in this location\n"
                f"- Maximum 60 words\n"
                f"- Return only the description, no preamble"
            ),
        }],
    )

    return {"description": response.content[0].text.strip()}
