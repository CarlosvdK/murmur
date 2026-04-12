"""
Targeted RAG Article Selector -- chooses which research domains to include
based on business type, question type, and customer demographics.

Replaces the dump-everything approach where all 9 domains were loaded
regardless of relevance. Now selects 3-5 domains max, reducing context
tokens by ~50% while increasing relevance.
"""

import re
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RAGSelection:
    """Result of targeted article selection."""
    domains_selected: list[str] = field(default_factory=list)
    question_type: str = "general"
    selection_reasoning: str = ""
    total_chars: int = 0


# ---------------------------------------------------------------------------
# Question type detection
# ---------------------------------------------------------------------------

QUESTION_TYPE_PATTERNS = {
    "pricing": [
        r"(raise|increase|lower|reduce|change|adjust)\s.*(price|cost|fee|rate|charge)",
        r"(more expensive|cheaper|discount|surcharge|markup|premium)",
        r"\d+\s*%",
        r"(subscription|tier|plan)\s*(price|cost|change)",
        r"(charge more|charge less|free trial|freemium)",
    ],
    "feature": [
        r"(new|launch|add|introduce|remove|drop|build|create)\s.*(feature|product|service|tool|option|offering)",
        r"(update|upgrade|redesign|revamp|overhaul)",
        r"(menu item|new item|new product|new service)",
        r"(mobile app|online|website|dashboard|integration|api)",
    ],
    "operations": [
        r"(open|close|change|extend|reduce)\s.*(hours|days|schedule|timing)",
        r"(sunday|weekend|evening|morning|late night|24.7|overnight)",
        r"(staffing|hiring|capacity|seating|delivery|pickup|shipping)",
        r"(renovate|remodel|move|relocate|expand)",
    ],
    "retention": [
        r"(loyalty|reward|membership|subscription|retention|churn)",
        r"(loyalty card|loyalty program|points|cashback|referral)",
        r"(cancel|unsubscribe|leave|switch|competitor)",
        r"(renew|retain|keep|win back|reactivate)",
    ],
    "brand": [
        r"(rebrand|rename|logo|identity|image|positioning)",
        r"(marketing|advertising|promotion|campaign|social media)",
        r"(target audience|target market|brand perception)",
    ],
}


def detect_question_type(question: str) -> str:
    """Detect the question type from the question text.

    Returns one of: pricing, feature, operations, retention, brand, general.
    """
    q = question.lower()
    scores: dict[str, int] = {}

    for qtype, patterns in QUESTION_TYPE_PATTERNS.items():
        score = sum(1 for p in patterns if re.search(p, q))
        if score > 0:
            scores[qtype] = score

    if not scores:
        return "general"

    return max(scores, key=scores.get)


# ---------------------------------------------------------------------------
# Domain relevance scoring
# ---------------------------------------------------------------------------

# Which domains are relevant for which question types
DOMAIN_RELEVANCE = {
    "pricing": {
        "consumer_psychology": 1.0,
        "pricing_psychology": 1.0,     # price elasticity, reference prices, fairness
        "behavioral_economics": 1.0,
        "country_profiles": 0.8,
        "persuasion_tactics": 0.8,
        "loyalty_retention": 0.6,      # price-driven churn
        "simulation_methodology": 0.6,
        "qualitative_interview_methodology": 0.5,
        "retail_customer_behavior": 0.5,
        "review_bias": 0.4,
        "digital_twins": 0.5,
        "b2b_buying_behavior": 0.3,
        "personality_models": 0.3,
        "decision_making": 0.4,
        "negotiation_psychology": 0.2,
    },
    "feature": {
        "digital_twins": 1.0,
        "decision_making": 1.0,
        "innovation_adoption": 0.9,
        "consumer_psychology": 0.7,
        "digital_experience": 0.7,
        "persuasion_tactics": 0.8,
        "personality_models": 0.6,
        "simulation_methodology": 0.5,
        "qualitative_interview_methodology": 0.5,
        "service_quality": 0.4,
        "behavioral_economics": 0.4,
        "country_profiles": 0.3,
        "review_bias": 0.2,
    },
    "operations": {
        "service_quality": 0.9,
        "consumer_psychology": 0.8,
        "retail_customer_behavior": 0.7,
        "digital_experience": 0.6,
        "simulation_methodology": 0.6,
        "qualitative_interview_methodology": 0.5,
        "persuasion_tactics": 0.8,
        "country_profiles": 0.5,
        "behavioral_economics": 0.4,
        "digital_twins": 0.4,
        "review_bias": 0.3,
        "decision_making": 0.3,
    },
    "retention": {
        "loyalty_retention": 1.0,
        "consumer_psychology": 1.0,
        "behavioral_economics": 0.8,
        "service_quality": 0.7,
        "digital_twins": 0.7,
        "persuasion_tactics": 0.8,
        "decision_making": 0.6,
        "personality_models": 0.5,
        "simulation_methodology": 0.5,
        "qualitative_interview_methodology": 0.5,
        "innovation_adoption": 0.4,
        "country_profiles": 0.4,
        "review_bias": 0.3,
    },
    "brand": {
        "consumer_psychology": 0.8,
        "personality_models": 0.7,
        "retail_customer_behavior": 0.6,
        "decision_making": 0.6,
        "persuasion_tactics": 0.8,
        "digital_twins": 0.5,
        "country_profiles": 0.5,
        "qualitative_interview_methodology": 0.5,
        "digital_experience": 0.4,
        "behavioral_economics": 0.4,
        "simulation_methodology": 0.4,
        "review_bias": 0.3,
    },
    "general": {
        "consumer_psychology": 0.8,
        "simulation_methodology": 0.7,
        "digital_twins": 0.6,
        "persuasion_tactics": 0.8,
        "qualitative_interview_methodology": 0.5,
        "behavioral_economics": 0.5,
        "service_quality": 0.5,
        "country_profiles": 0.5,
        "digital_experience": 0.4,
        "retail_customer_behavior": 0.4,
        "personality_models": 0.4,
        "loyalty_retention": 0.3,
        "innovation_adoption": 0.3,
        "review_bias": 0.3,
        "decision_making": 0.3,
    },
}

# Industry-specific domain boosts
INDUSTRY_BOOSTS = {
    # B2B
    "b2b_services": {"negotiation_psychology": +0.5, "b2b_buying_behavior": +0.5, "review_bias": -0.3},
    "consulting": {"negotiation_psychology": +0.4, "b2b_buying_behavior": +0.4, "review_bias": -0.2},
    "logistics": {"negotiation_psychology": +0.4, "b2b_buying_behavior": +0.3, "review_bias": -0.3},
    "wholesale": {"negotiation_psychology": +0.4, "b2b_buying_behavior": +0.3, "review_bias": -0.2},
    "manufacturing": {"negotiation_psychology": +0.3, "b2b_buying_behavior": +0.3, "review_bias": -0.3},
    # Technology
    "saas": {"digital_twins": +0.3, "digital_experience": +0.3, "innovation_adoption": +0.3, "review_bias": -0.2},
    "ecommerce": {"behavioral_economics": +0.2, "digital_experience": +0.3, "convenience_friction": +0.2},
    "app": {"digital_twins": +0.3, "digital_experience": +0.3, "innovation_adoption": +0.3, "onboarding_first_impressions": +0.2},
    # Food & Drink
    "restaurant": {"food_hospitality_psychology": +0.8, "review_bias": +0.3, "group_decision_making": +0.3, "pricing_presentation": +0.3},
    "cafe": {"food_hospitality_psychology": +0.7, "review_bias": +0.3, "seasonal_temporal_effects": +0.3},
    # Health & Wellness
    "barbershop": {"review_bias": +0.2, "trust_credibility": +0.2},
    "gym": {"fitness_wellness_retention": +0.8, "onboarding_first_impressions": +0.3},
    "yoga": {"fitness_wellness_retention": +0.4},
    "spa": {"luxury_premium_psychology": +0.3, "service_quality": +0.2},
    # Healthcare
    "healthcare_clinic": {"healthcare_patient_behavior": +0.8, "trust_credibility": +0.4, "complaint_feedback_behavior": +0.3},
    "dental": {"healthcare_patient_behavior": +0.7, "trust_credibility": +0.4},
    "veterinary": {"healthcare_patient_behavior": +0.3},
    # Hospitality
    "hotel": {"food_hospitality_psychology": +0.3, "review_bias": +0.3, "seasonal_temporal_effects": +0.3},
    # Retail
    "clothing": {"retail_customer_behavior": +0.3, "generational_demographics": +0.2},
    "grocery": {"retail_customer_behavior": +0.3, "pricing_presentation": +0.2},
    # Education
    "education": {"innovation_adoption": +0.3, "onboarding_first_impressions": +0.3},
    "tutoring": {"onboarding_first_impressions": +0.2},
    # Luxury
    "jewelry": {"luxury_premium_psychology": +0.5},
    "fine_dining": {"luxury_premium_psychology": +0.4, "food_hospitality_psychology": +0.3},
}

# Map all business types to their base type for boost lookup
BUSINESS_TYPE_TO_BASE = {
    "restaurant": "restaurant", "cafe": "cafe", "bar": "restaurant",
    "bakery": "cafe", "food_truck": "restaurant", "catering": "b2b_services",
    "desserts": "cafe",
    "gym": "barbershop", "yoga": "barbershop", "spa": "barbershop",
    "barbershop": "barbershop", "hair_salon": "barbershop",
    "nail_salon": "barbershop", "tattoo": "barbershop", "physio": "barbershop",
    "grocery": "restaurant", "clothing": "ecommerce",
    "bookshop": "ecommerce", "gift_shop": "ecommerce",
    "florist": "ecommerce", "sports": "ecommerce",
    "electronics": "ecommerce", "toy_shop": "ecommerce", "pet_shop": "ecommerce",
    "auto": "barbershop", "dry_cleaning": "barbershop",
    "photography": "consulting", "printing": "barbershop",
    "accountant": "consulting", "legal": "consulting",
    "consulting": "consulting", "freelance": "consulting",
    "marketing_agency": "consulting", "cleaning": "barbershop",
    "tutoring": "consulting",
    "saas": "saas", "ecommerce": "ecommerce", "app": "app",
    "it_services": "saas",
    "b2b_services": "b2b_services", "logistics": "logistics",
    "wholesale": "wholesale", "manufacturing": "manufacturing",
    "hotel": "hotel", "hostel": "hotel", "campsite": "hotel",
    "tour_operator": "hotel", "activity_centre": "hotel",
    "healthcare_clinic": "barbershop", "dental": "barbershop",
    "pharmacy": "restaurant", "veterinary": "barbershop",
    "education": "consulting", "childcare": "barbershop",
    "driving_school": "consulting",
    "other": "restaurant",
}


def select_rag_articles(
    business_type: str,
    question: str,
    demographics: dict | None = None,
    max_domains: int = 8,
    has_country: bool = False,
) -> RAGSelection:
    """Select the most relevant research domains for this simulation.

    Args:
        business_type: The business type from the survey
        question: The user's simulation question
        demographics: Optional dict with age/income/digital data
        max_domains: Maximum number of domains to include (default 5)
        has_country: Whether we have a country code for Hofstede data

    Returns:
        RAGSelection with ordered list of domains to include
    """
    question_type = detect_question_type(question)

    # Get base relevance scores for this question type
    base_scores = dict(DOMAIN_RELEVANCE.get(question_type, DOMAIN_RELEVANCE["general"]))

    # Apply industry-specific boosts
    base_type = BUSINESS_TYPE_TO_BASE.get(business_type, "restaurant")
    boosts = INDUSTRY_BOOSTS.get(base_type, {})
    for domain, boost in boosts.items():
        base_scores[domain] = max(0, base_scores.get(domain, 0) + boost)

    # Boost country_profiles if we actually have country data
    if has_country:
        base_scores["country_profiles"] = base_scores.get("country_profiles", 0) + 0.2

    # Always include simulation_methodology (calibration rules)
    base_scores["simulation_methodology"] = max(
        base_scores.get("simulation_methodology", 0), 0.5
    )

    # Always include persuasion_tactics (stated-vs-revealed calibration)
    base_scores["persuasion_tactics"] = max(
        base_scores.get("persuasion_tactics", 0), 0.7
    )

    # Sort by score and take top N
    ranked = sorted(base_scores.items(), key=lambda x: x[1], reverse=True)

    # Filter: only include domains scoring above 0.3
    selected = [(domain, score) for domain, score in ranked if score >= 0.3]
    selected = selected[:max_domains]

    domains = [d for d, _ in selected]

    # Ensure industry-specific domains from boosts make the cut
    # (replace the lowest-scoring generic domain if needed)
    for boost_domain in boosts:
        if boost_domain not in domains and boosts[boost_domain] >= 0.5:
            # This is a high-priority industry domain that got pushed out
            if len(domains) >= max_domains:
                domains[-1] = boost_domain  # replace lowest scorer
            else:
                domains.append(boost_domain)
    reasoning_parts = [f"{d} ({s:.1f})" for d, s in selected]

    selection = RAGSelection(
        domains_selected=domains,
        question_type=question_type,
        selection_reasoning=(
            f"Question type: {question_type}. "
            f"Business type: {business_type} (base: {base_type}). "
            f"Selected {len(domains)} domains: {', '.join(reasoning_parts)}."
        ),
    )

    logger.info(
        "RAG selection: question_type=%s, business=%s, domains=%s",
        question_type, business_type, domains,
    )

    return selection
