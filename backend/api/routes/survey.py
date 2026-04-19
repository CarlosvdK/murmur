"""
Survey helper endpoints for the enriched onboarding flow.

- /research-business: Phase 0 auto-lookup via Google Places + Claude
- /scrape-website: Extract business info from a website URL
- /generate-description: AI drafts a business description
- /generate-customer-description: AI drafts a customer description
- /place-autocomplete: Google Places address autocomplete
- /place-details: Structured address from place ID
"""

import json
import logging
import re
from typing import Optional
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from anthropic import AsyncAnthropic
from backend.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/survey", tags=["survey"])

# All business types (used in Claude synthesis)
ALL_BUSINESS_TYPES = (
    # Food & Drink
    "restaurant|cafe|bar|bakery|food_truck|catering|desserts|pizzeria|sushi|fast_food|fine_dining|juice_bar|brewery|winery|"
    # Health & Wellness
    "barbershop|hair_salon|nail_salon|spa|tattoo|gym|yoga|physio|personal_trainer|crossfit|martial_arts|dance_studio|beauty_salon|"
    # Retail
    "grocery|clothing|bookshop|gift_shop|florist|sports|electronics|toy_shop|pet_shop|furniture|jewelry|shoe_store|thrift_store|hardware|pharmacy|optical|convenience|"
    # Services
    "auto|dry_cleaning|photography|printing|cleaning|plumbing|electrical|landscaping|pest_control|moving_company|locksmith|car_wash|tailor|pet_grooming|"
    # Professional
    "accountant|legal|consulting|freelance|marketing_agency|financial_advisor|insurance|real_estate|recruitment|architecture|coaching|"
    # Technology
    "saas|ecommerce|app|it_services|web_design|hosting|cybersecurity|data_analytics|marketplace|"
    # B2B
    "b2b_services|logistics|wholesale|manufacturing|commercial_cleaning|construction|"
    # Hospitality
    "hotel|hostel|campsite|tour_operator|activity_centre|airbnb|event_venue|wedding_venue|travel_agency|resort|"
    # Healthcare
    "healthcare_clinic|dental|veterinary|mental_health|optometry|dermatology|chiropractor|"
    # Education
    "education|childcare|driving_school|tutoring|language_school|music_school|coding_bootcamp|online_course|"
    # Entertainment
    "cinema|bowling|arcade|escape_room|mini_golf|theme_park|museum|nightclub|comedy_club|"
    # Property & Creative & Community
    "coworking|storage|laundromat|recording_studio|graphic_design|content_creation|charity|community_centre|sports_club|"
    "other"
)


def _is_url(text: str) -> bool:
    """Check if input looks like a URL."""
    t = text.strip().lower()
    if t.startswith(("http://", "https://", "www.")):
        return True
    # Check for domain-like pattern (something.something)
    if re.match(r"^[a-z0-9][-a-z0-9]*\.[a-z]{2,}", t):
        return True
    return False


def _normalize_url(url: str) -> str:
    """Ensure URL has a scheme."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


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


class ScrapeWebsiteRequest(BaseModel):
    url: str


@router.post("/scrape-website")
async def scrape_website(data: ScrapeWebsiteRequest):
    """Scrape a website URL and extract business information using Claude."""
    settings = get_settings()
    url = _normalize_url(data.url)

    # Fetch the page
    scraped_text = ""
    final_url = url
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True, max_redirects=5) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; MurmurBot/1.0)",
                "Accept": "text/html,application/xhtml+xml",
            })
            resp.raise_for_status()
            final_url = str(resp.url)
            html = resp.text

            # Extract text from HTML (strip tags, scripts, styles)
            import re as _re
            # Remove script and style blocks
            html = _re.sub(r"<script[^>]*>.*?</script>", "", html, flags=_re.DOTALL | _re.IGNORECASE)
            html = _re.sub(r"<style[^>]*>.*?</style>", "", html, flags=_re.DOTALL | _re.IGNORECASE)
            # Remove HTML tags
            text = _re.sub(r"<[^>]+>", " ", html)
            # Collapse whitespace
            text = _re.sub(r"\s+", " ", text).strip()
            # Truncate to avoid huge prompts
            scraped_text = text[:6000]
    except Exception as e:
        logger.error("Website scrape failed for %s: %s", url, e)
        return {"confidence": "low", "error": f"Could not fetch website: {str(e)}", "website": url}

    if len(scraped_text) < 50:
        return {"confidence": "low", "error": "Website returned too little content", "website": url}

    # Use Claude to extract business information
    try:
        ai_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await ai_client.messages.create(
            model=settings.model_name,
            max_tokens=800,
            messages=[{
                "role": "user",
                "content": (
                    f"Extract business information from this website content. "
                    f"The URL is: {final_url}\n\n"
                    f"Website text (truncated):\n{scraped_text}\n\n"
                    f"Extract as much as you can. Return ONLY valid JSON:\n"
                    f'{{"name": "business name or null",'
                    f' "type": "one of: {ALL_BUSINESS_TYPES}",'
                    f' "formatted_address": "full address if found or null",'
                    f' "description": "3-5 sentence description from the owner perspective. What the business does, who comes, what makes it different, the vibe. No marketing language. Concrete and specific.",'
                    f' "location_city": "city if found or null",'
                    f' "location_country": "ISO 2-letter country code if determinable or null",'
                    f' "years_open_estimate": "one of: <1|1-3|3-10|10+ or null",'
                    f' "confidence": "high|medium|low"}}'
                ),
            }],
        )
        result = _parse_json_response(response.content[0].text)
        result["website"] = final_url
        result["source"] = "website_scrape"
        return result
    except Exception as e:
        logger.error("Claude website extraction failed: %s", e)
        return {"confidence": "low", "website": final_url, "error": "Could not extract info"}


@router.post("/research-business")
async def research_business(data: BusinessResearchRequest):
    """Phase 0 lookup. Handles business names, URLs, and Google Maps links.

    Strategy:
    1. If input looks like a URL -> scrape the website first for info
    2. Search Google Places for the business (using name or URL domain)
    3. Claude synthesises all available data into a pre-fill package
    """
    settings = get_settings()
    input_text = data.input.strip()

    # Step 0: If input is a URL, scrape the website first
    website_data = {}
    if _is_url(input_text):
        try:
            scrape_req = ScrapeWebsiteRequest(url=input_text)
            website_data = await scrape_website(scrape_req)
            if website_data.get("confidence") != "low":
                logger.info("Website scrape successful: %s", website_data.get("name"))
        except Exception as e:
            logger.warning("Website scrape failed (non-fatal): %s", e)

    # Step 1: Search Google Places
    places_result = {}
    if settings.google_places_api_key:
        # Use scraped name if available, otherwise use raw input
        search_query = website_data.get("name") or input_text
        # If we only have a URL, try the domain name as search hint
        if _is_url(search_query):
            parsed = urlparse(_normalize_url(search_query))
            domain = parsed.hostname or ""
            # Strip common prefixes/suffixes
            domain = domain.replace("www.", "").split(".")[0]
            search_query = domain if domain else input_text

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
                    json={"textQuery": search_query, "maxResultCount": 1},
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

    # If we have neither website data nor places data, return low confidence
    if not website_data and not places_result:
        return {"confidence": "low", "name": input_text}

    # Step 2: Claude synthesises all available data
    all_data = {}
    if website_data:
        all_data["website_scrape"] = {
            k: v for k, v in website_data.items()
            if k not in ("source", "error") and v is not None
        }
    if places_result:
        all_data["google_places"] = places_result

    try:
        ai_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await ai_client.messages.create(
            model=settings.model_name,
            max_tokens=800,
            messages=[{
                "role": "user",
                "content": (
                    f"Combine this data about a business into a pre-fill package. "
                    f"Use ALL available sources. Be realistic and specific, not generic.\n\n"
                    f"Available data: {json.dumps(all_data)}\n"
                    f"User query: {input_text}\n\n"
                    f"Return ONLY valid JSON:\n"
                    f'{{"name": "business name",'
                    f' "type": "one of: {ALL_BUSINESS_TYPES}",'
                    f' "formatted_address": "full address",'
                    f' "description": "3-5 sentence description from the owner perspective. What the business does, who comes, what makes it different, the vibe. No marketing language. Concrete and specific.",'
                    f' "location_city": "city if known",'
                    f' "location_country": "ISO 2-letter code if known",'
                    f' "years_open_estimate": "one of: <1|1-3|3-10|10+ or null",'
                    f' "confidence": "high|medium|low"}}'
                ),
            }],
        )
        pre_fill = _parse_json_response(response.content[0].text)
    except Exception as e:
        logger.error("Claude pre-fill synthesis failed: %s", e)
        # Fall back to whatever we have
        pre_fill = dict(website_data) if website_data else {"confidence": "low"}

    # Merge Places data into pre-fill
    if places_result:
        pre_fill.setdefault("google_place_id", places_result.get("place_id"))
        pre_fill.setdefault("rating", places_result.get("rating"))
        pre_fill.setdefault("review_count", places_result.get("review_count"))
    # Prefer website from scrape, fall back to places
    if not pre_fill.get("website"):
        pre_fill["website"] = (
            website_data.get("website")
            or places_result.get("website")
            or (_normalize_url(input_text) if _is_url(input_text) else None)
        )
    if not pre_fill.get("name") or _is_url(pre_fill.get("name", "")):
        pre_fill["name"] = places_result.get("name") or website_data.get("name") or ""
        # Don't fall back to the raw URL as the business name
        if _is_url(pre_fill.get("name", "")):
            pre_fill["name"] = ""
    if not pre_fill.get("formatted_address"):
        pre_fill["formatted_address"] = places_result.get("formatted_address") or website_data.get("formatted_address") or ""

    return pre_fill


@router.post("/generate-description")
async def generate_description(data: DescriptionRequest):
    """AI drafts a business description the owner can edit."""
    settings = get_settings()
    ai_client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    response = await ai_client.messages.create(
        model=settings.model_name,
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (
                f"Write a description of this business that will be used to simulate "
                f"realistic customer reactions. This is NOT marketing copy -- it needs "
                f"to capture what actually makes this place tick.\n\n"
                f"Business name: {data.name}\n"
                f"Type: {data.type}\n"
                f"Location: {data.location or 'unknown'}\n"
                f"Years open: {data.years_open or 'unknown'}\n\n"
                f"Include:\n"
                f"- What the business actually does/sells (specific, not vague)\n"
                f"- What kind of customers typically come and why\n"
                f"- What makes it different from competitors in the area\n"
                f"- The general price range and positioning\n"
                f"- The vibe or atmosphere (casual, professional, homey, etc.)\n\n"
                f"Rules:\n"
                f"- Write from the owner's perspective, as if they are explaining their "
                f"business to someone who will interview their customers\n"
                f"- Be specific and concrete, not generic ('we serve hand-pulled noodles' "
                f"not 'we serve food')\n"
                f"- 3-5 sentences, around 80 words\n"
                f"- Do NOT write marketing copy or use words like 'enjoy', 'experience', "
                f"'discover', 'indulge'\n"
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


class PlaceAutocompleteRequest(BaseModel):
    query: str


@router.post("/place-autocomplete")
async def place_autocomplete(data: PlaceAutocompleteRequest):
    """Proxy Google Places Autocomplete for location search."""
    settings = get_settings()
    if not settings.google_places_api_key:
        return {"predictions": []}
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(
                "https://places.googleapis.com/v1/places:autocomplete",
                headers={"X-Goog-Api-Key": settings.google_places_api_key},
                json={"input": data.query, "includedPrimaryTypes": ["establishment"]},
            )
            resp.raise_for_status()
            result = resp.json()
        suggestions = result.get("suggestions", [])
        return {"predictions": [
            {"description": (s.get("placePrediction", {}).get("text") or {}).get("text", ""),
             "place_id": s.get("placePrediction", {}).get("placeId", "")}
            for s in suggestions[:5]
        ]}
    except Exception as e:
        logger.error("Places autocomplete failed: %s", e)
        return {"predictions": []}


class PlaceDetailsRequest(BaseModel):
    place_id: str


@router.post("/place-details")
async def place_details(data: PlaceDetailsRequest):
    """Fetch structured address from a Google Place ID."""
    settings = get_settings()
    if not settings.google_places_api_key:
        return {}
    try:
        # Ensure place_id has the 'places/' prefix for the API
        place_id = data.place_id
        if not place_id.startswith("places/"):
            place_id = f"places/{place_id}"

        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"https://places.googleapis.com/v1/{place_id}",
                headers={
                    "X-Goog-Api-Key": settings.google_places_api_key,
                    "X-Goog-FieldMask": "displayName,formattedAddress,addressComponents,location",
                },
            )
            resp.raise_for_status()
            place = resp.json()

        components = place.get("addressComponents", [])
        address: dict = {}
        for c in components:
            types = c.get("types", [])
            text = c.get("longText", c.get("shortText", ""))
            if "street_number" in types:
                address["number"] = text
            elif "route" in types:
                address["street"] = text
            elif "postal_code" in types:
                address["postcode"] = text
            elif "locality" in types or "administrative_area_level_2" in types:
                if "city" not in address:  # locality takes precedence
                    address["city"] = text
            elif "sublocality" in types or "sublocality_level_1" in types or "neighborhood" in types:
                address["neighbourhood"] = text
            elif "country" in types:
                # Use shortText for country code (e.g., "NL" instead of "Netherlands")
                address["country"] = c.get("shortText", text)

        loc = place.get("location", {})
        address["lat"] = loc.get("latitude")
        address["lng"] = loc.get("longitude")
        address["formatted"] = place.get("formattedAddress", "")
        address["name"] = (place.get("displayName") or {}).get("text", "")

        # Fallback: if we got a formatted address but no parsed fields,
        # try to extract city/country from the formatted string
        formatted = address.get("formatted", "")
        if formatted and not address.get("city"):
            parts = [p.strip() for p in formatted.split(",")]
            if len(parts) >= 2:
                # Last part is usually country, second-to-last is usually city
                address["country"] = address.get("country") or parts[-1].strip()
                # City is often the part before the country, possibly with postcode
                city_part = parts[-2].strip()
                # Remove postcode from city part if present
                city_clean = re.sub(r"\d{4,}\s*[A-Z]*", "", city_part).strip()
                if city_clean:
                    address["city"] = address.get("city") or city_clean
            if len(parts) >= 3 and not address.get("street"):
                # First part often contains street + number
                street_part = parts[0].strip()
                # Try to split "Streetname 13" into street and number
                street_match = re.match(r"^(.+?)\s+(\d+\S*)$", street_part)
                if street_match:
                    address["street"] = address.get("street") or street_match.group(1)
                    address["number"] = address.get("number") or street_match.group(2)
                else:
                    address["street"] = address.get("street") or street_part
            if len(parts) >= 4 and not address.get("postcode"):
                # Postcode might be embedded in one of the middle parts
                for p in parts[1:-1]:
                    pc_match = re.search(r"\b(\d{4,5}\s*[A-Z]{0,2})\b", p)
                    if pc_match:
                        address["postcode"] = pc_match.group(1).strip()
                        break

        logger.info("Place details parsed: %s", {k: v for k, v in address.items() if k not in ("lat", "lng")})
        return address
    except Exception as e:
        logger.error("Place details failed: %s", e)
        return {}


class AutofillRequest(BaseModel):
    url: str


@router.post("/autofill")
async def autofill_from_url(data: AutofillRequest):
    """Auto-fill business details from a URL (website, Google Maps, or Google Business Profile)."""
    settings = get_settings()

    # Try to use the existing research_business logic
    # by passing the URL as the input
    research_data = BusinessResearchRequest(input=data.url)
    result = await research_business(research_data)

    found = {}
    not_found = []

    for field in ["name", "type", "formatted_address", "description", "website", "rating", "review_count", "google_place_id", "years_open_estimate"]:
        val = result.get(field)
        val_str = str(val).strip() if val else ""
        # Filter out URL-like values returned as names or descriptions
        if field == "website" and val_str.startswith("http"):
            found[field] = val_str
        elif val_str and not val_str.startswith("http") and val_str != data.url:
            found[field] = val_str
        else:
            not_found.append(field)

    return {
        "found": found,
        "not_found": not_found,
        "confidence": result.get("confidence", "low"),
    }
