"""
Psychological Profile Builder -- assembles a multi-layer behavioral profile
from survey data, Hofstede cultural dimensions, demographic research, and
industry-specific behavioral norms.

This profile flows into persona generation and interview prompts to ground
synthetic customers in research-backed behavioral patterns.

Works for ALL business types -- not industry-specific.
"""

import logging
from dataclasses import dataclass, field

from backend.models.business import BusinessSnapshot

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Industry behavioral norms
# ---------------------------------------------------------------------------

INDUSTRY_NORMS = {
    # Physical, per-visit businesses
    "restaurant": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "frequency",
        "loyalty_driver": "habit_and_convenience",
        "typical_decision_style": "impulsive_to_moderate",
        "key_behavioral_note": (
            "Customers decide quickly, often based on mood and convenience. "
            "Regulars develop strong habits and resist change to their routine. "
            "Price increases are felt immediately because of high visit frequency."
        ),
    },
    "cafe": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "frequency",
        "loyalty_driver": "habit_and_routine",
        "typical_decision_style": "impulsive",
        "key_behavioral_note": (
            "Coffee shop loyalty is routine-driven. Customers are highly price-aware "
            "on daily purchases. Small price changes are amplified by visit frequency."
        ),
    },
    "barbershop": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "relationship",
        "loyalty_driver": "trust_and_skill",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Personal service creates moderate switching costs. Customers value the "
            "relationship with their barber/stylist. Trust takes time to build and is "
            "not easily replaced."
        ),
    },
    "hair_salon": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "relationship",
        "loyalty_driver": "trust_and_skill",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "High-trust relationship. Customers are reluctant to switch because finding "
            "a stylist who understands their preferences takes effort."
        ),
    },
    "gym": {
        "engagement_model": "subscription",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "perceived_value",
        "loyalty_driver": "habit_and_community",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Subscription model means customers evaluate value monthly. High initial "
            "motivation often declines. Community and convenience drive retention more "
            "than equipment quality."
        ),
    },
    # Retail
    "grocery": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "frequency_and_basket",
        "loyalty_driver": "convenience_and_price",
        "typical_decision_style": "habitual",
        "key_behavioral_note": (
            "Grocery shopping is habitual. Customers are very price-aware on staples, "
            "less so on treats. Location and convenience dominate loyalty."
        ),
    },
    "clothing": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "low",
        "price_sensitivity_driver": "brand_and_style",
        "loyalty_driver": "brand_identity",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Fashion purchases are emotionally driven. Brand loyalty exists but "
            "customers are always open to alternatives. Sales and promotions drive "
            "significant behavior changes."
        ),
    },
    # Technology
    "saas": {
        "engagement_model": "subscription",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "roi_and_alternatives",
        "loyalty_driver": "integration_and_workflow",
        "typical_decision_style": "deliberate_committee",
        "key_behavioral_note": (
            "Software decisions involve evaluating ROI, integration effort, and "
            "team adoption. Switching costs are high due to data migration and "
            "workflow disruption. Price sensitivity is measured against value delivered, "
            "not absolute cost. Decisions may involve multiple stakeholders."
        ),
    },
    "ecommerce": {
        "engagement_model": "per_transaction",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "comparison_shopping",
        "loyalty_driver": "experience_and_trust",
        "typical_decision_style": "impulsive_to_moderate",
        "key_behavioral_note": (
            "Online shoppers compare prices instantly. Loyalty is driven by trust, "
            "delivery speed, and return policies. Impulse purchases are common but "
            "cart abandonment is high."
        ),
    },
    "app": {
        "engagement_model": "subscription_or_freemium",
        "decision_speed": "fast",
        "switching_cost": "low_to_moderate",
        "price_sensitivity_driver": "perceived_value",
        "loyalty_driver": "habit_and_data_lock_in",
        "typical_decision_style": "impulsive",
        "key_behavioral_note": (
            "App users decide in seconds. Free alternatives are always available. "
            "Habit formation is critical for retention. Data stored in the app "
            "creates moderate switching costs."
        ),
    },
    # B2B
    "b2b_services": {
        "engagement_model": "contract",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "budget_and_roi",
        "loyalty_driver": "relationship_and_reliability",
        "typical_decision_style": "committee",
        "key_behavioral_note": (
            "B2B decisions involve procurement processes, budget approvals, and "
            "multiple decision-makers. Relationships matter enormously. Switching "
            "requires re-evaluating vendors, which is time-consuming. Price is "
            "evaluated against business impact, not personal budget."
        ),
    },
    "consulting": {
        "engagement_model": "project_or_retainer",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "expertise_value",
        "loyalty_driver": "trust_and_results",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Consulting relationships are built on trust and track record. Clients "
            "are reluctant to switch because onboarding a new consultant takes time. "
            "Price is secondary to demonstrated expertise."
        ),
    },
    "logistics": {
        "engagement_model": "contract",
        "decision_speed": "slow",
        "switching_cost": "very_high",
        "price_sensitivity_driver": "total_cost_of_operations",
        "loyalty_driver": "reliability_and_integration",
        "typical_decision_style": "committee",
        "key_behavioral_note": (
            "Logistics decisions are operational and affect the entire supply chain. "
            "Switching providers is extremely disruptive. Reliability and on-time "
            "delivery matter more than price. Contracts are long-term."
        ),
    },
    "wholesale": {
        "engagement_model": "contract_or_recurring",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "margin_pressure",
        "loyalty_driver": "reliability_and_terms",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Wholesale buyers are margin-conscious. They compare prices actively "
            "but value reliable supply and favorable payment terms."
        ),
    },
    # Healthcare
    "healthcare_clinic": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "moderate_to_high",
        "price_sensitivity_driver": "insurance_and_trust",
        "loyalty_driver": "trust_and_continuity",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Healthcare decisions are trust-intensive. Patients value continuity of "
            "care and are reluctant to switch providers. Price sensitivity depends "
            "heavily on insurance coverage."
        ),
    },
    "dental": {
        "engagement_model": "per_visit",
        "decision_speed": "slow",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "insurance_and_anxiety",
        "loyalty_driver": "trust_and_comfort",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Dental patients are anxiety-driven. Finding a dentist they trust and "
            "feel comfortable with is a high-effort decision. Once settled, they "
            "rarely switch unless forced to."
        ),
    },
    # Hospitality
    "hotel": {
        "engagement_model": "per_stay",
        "decision_speed": "moderate",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "comparison_and_occasion",
        "loyalty_driver": "loyalty_program_and_experience",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Hotel guests compare prices across platforms. Loyalty programs create "
            "some stickiness but most guests prioritize price and location. "
            "Business travelers are less price-sensitive than leisure travelers."
        ),
    },
}

# Map business types to their industry norm key
INDUSTRY_TYPE_MAP = {
    "restaurant": "restaurant", "cafe": "cafe", "bar": "restaurant",
    "bakery": "cafe", "food_truck": "restaurant", "catering": "b2b_services",
    "desserts": "cafe",
    "gym": "gym", "yoga": "gym", "spa": "barbershop",
    "barbershop": "barbershop", "hair_salon": "hair_salon",
    "nail_salon": "hair_salon", "tattoo": "barbershop", "physio": "healthcare_clinic",
    "grocery": "grocery", "clothing": "clothing", "bookshop": "clothing",
    "gift_shop": "clothing", "florist": "clothing", "sports": "clothing",
    "electronics": "clothing", "toy_shop": "clothing", "pet_shop": "grocery",
    "auto": "barbershop", "dry_cleaning": "barbershop",
    "photography": "consulting", "printing": "barbershop",
    "accountant": "consulting", "legal": "consulting",
    "consulting": "consulting", "freelance": "consulting",
    "marketing_agency": "consulting", "cleaning": "barbershop",
    "tutoring": "consulting",
    "saas": "saas", "ecommerce": "ecommerce", "app": "app",
    "it_services": "saas",
    "b2b_services": "b2b_services", "logistics": "logistics",
    "wholesale": "wholesale", "manufacturing": "logistics",
    "hotel": "hotel", "hostel": "hotel", "campsite": "hotel",
    "tour_operator": "hotel", "activity_centre": "hotel",
    "healthcare_clinic": "healthcare_clinic", "dental": "dental",
    "pharmacy": "grocery", "veterinary": "healthcare_clinic",
    "education": "consulting", "childcare": "healthcare_clinic",
    "driving_school": "consulting",
    "other": "restaurant",  # default fallback
}


# ---------------------------------------------------------------------------
# Demographic behavioral research
# ---------------------------------------------------------------------------

AGE_BEHAVIORAL_PROFILES = {
    "18-24": {
        "impulsivity": "high",
        "loyalty": "low",
        "price_sensitivity": "high",
        "digital_expectation": "very_high",
        "change_openness": "high",
        "social_proof_reliance": "very_high",
        "note": (
            "Young adults are digitally native, highly influenced by social proof "
            "and peer behavior. They switch easily, are price-conscious but will "
            "pay for status/experience. Highly responsive to trends and novelty."
        ),
    },
    "25-34": {
        "impulsivity": "moderate_to_high",
        "loyalty": "moderate",
        "price_sensitivity": "moderate",
        "digital_expectation": "high",
        "change_openness": "moderate_to_high",
        "social_proof_reliance": "high",
        "note": (
            "Early career professionals balancing aspiration with budget. Building "
            "brand preferences but still exploring. Value convenience and quality. "
            "Comfortable with technology."
        ),
    },
    "35-44": {
        "impulsivity": "moderate",
        "loyalty": "moderate_to_high",
        "price_sensitivity": "moderate",
        "digital_expectation": "moderate_to_high",
        "change_openness": "moderate",
        "social_proof_reliance": "moderate",
        "note": (
            "Established preferences, growing brand loyalty. Often family-oriented, "
            "which affects spending priorities. Value reliability and consistency. "
            "Less swayed by trends, more by proven quality."
        ),
    },
    "45-54": {
        "impulsivity": "low_to_moderate",
        "loyalty": "high",
        "price_sensitivity": "moderate",
        "digital_expectation": "moderate",
        "change_openness": "low_to_moderate",
        "social_proof_reliance": "low_to_moderate",
        "note": (
            "Strong established habits and brand preferences. Resist change unless "
            "clearly beneficial. Value personal service and relationships. Peak "
            "earning years but cautious about unnecessary spending."
        ),
    },
    "55-64": {
        "impulsivity": "low",
        "loyalty": "very_high",
        "price_sensitivity": "moderate_to_high",
        "digital_expectation": "low_to_moderate",
        "change_openness": "low",
        "social_proof_reliance": "low",
        "note": (
            "Strong status quo bias. Very loyal to established routines and "
            "businesses. May resist digital-first changes. Value personal interaction "
            "and familiar experiences. Price-aware as retirement approaches."
        ),
    },
    "65+": {
        "impulsivity": "very_low",
        "loyalty": "very_high",
        "price_sensitivity": "high",
        "digital_expectation": "low",
        "change_openness": "very_low",
        "social_proof_reliance": "low",
        "note": (
            "Strongest status quo bias. Extremely loyal to known businesses. Fixed "
            "income increases price sensitivity. May struggle with technology-driven "
            "changes. Value personal relationships and familiarity above all."
        ),
    },
}

INCOME_BEHAVIORAL_PROFILES = {
    "budget": {
        "price_sensitivity": "very_high",
        "value_orientation": "price_first",
        "switching_trigger": "any_price_increase",
        "note": (
            "Every price change is felt immediately. Customers actively seek "
            "alternatives and compare prices. Loyalty exists only when the business "
            "is the cheapest viable option."
        ),
    },
    "lower_middle": {
        "price_sensitivity": "high",
        "value_orientation": "value_for_money",
        "switching_trigger": "perceived_unfairness",
        "note": (
            "Price-aware but willing to pay slightly more for quality or convenience. "
            "React strongly to perceived unfairness. Moderate brand loyalty when "
            "value proposition is clear."
        ),
    },
    "middle": {
        "price_sensitivity": "moderate",
        "value_orientation": "balanced",
        "switching_trigger": "quality_decline_or_major_price_jump",
        "note": (
            "Balance quality, convenience, and price. Tolerate moderate price increases "
            "if quality is maintained. Willing to try alternatives but not actively "
            "seeking them."
        ),
    },
    "upper_middle": {
        "price_sensitivity": "low_to_moderate",
        "value_orientation": "quality_first",
        "switching_trigger": "quality_or_experience_decline",
        "note": (
            "Price is secondary to quality and experience. Will pay a premium for "
            "superior service. More sensitive to quality decline than price increases. "
            "Value exclusivity and differentiation."
        ),
    },
    "affluent": {
        "price_sensitivity": "low",
        "value_orientation": "experience_and_status",
        "switching_trigger": "status_or_experience_mismatch",
        "note": (
            "Price is not a decision factor. Value exclusivity, superior experience, "
            "and personal recognition. May actually view price increases positively "
            "if they signal quality. Switch when a brand no longer matches their "
            "self-image."
        ),
    },
    "mixed": {
        "price_sensitivity": "varied",
        "value_orientation": "segment_dependent",
        "switching_trigger": "varies",
        "note": (
            "Mixed income base means different customers react very differently to "
            "the same change. Price increases may retain affluent customers while "
            "losing budget-conscious ones. Segmented analysis is essential."
        ),
    },
}


# ---------------------------------------------------------------------------
# Profile builder
# ---------------------------------------------------------------------------

@dataclass
class PsychologicalProfile:
    """Multi-layer behavioral profile assembled from survey + research."""
    cultural_layer: dict = field(default_factory=dict)
    demographic_layer: dict = field(default_factory=dict)
    industry_layer: dict = field(default_factory=dict)
    behavioral_layer: dict = field(default_factory=dict)
    summary: str = ""
    confidence: str = "low"


def build_profile(
    business: BusinessSnapshot,
    country_code: str = "",
) -> PsychologicalProfile:
    """Build a multi-layer psychological profile for simulation.

    Layers:
    1. Cultural (Hofstede dimensions if country known)
    2. Demographic (age/income behavioral research)
    3. Industry (business-type behavioral norms)
    4. Behavioral (composite predictions)

    Returns a PsychologicalProfile with a plain-English summary
    suitable for injection into prompts.
    """
    profile = PsychologicalProfile()
    summary_parts = []
    confidence_score = 0

    # --- Layer 1: Cultural ---
    try:
        from research.rag_library import get_country_profile, get_persona_cultural_modifier
        country = country_code or (business.location or "").split(",")[-1].strip()
        cultural = get_country_profile(country)
        if cultural:
            profile.cultural_layer = cultural
            modifier = get_persona_cultural_modifier(country)
            if modifier:
                summary_parts.append(f"CULTURAL CONTEXT:\n{modifier}")
                confidence_score += 2
    except Exception as e:
        logger.warning("Cultural layer failed (non-fatal): %s", e)

    # --- Layer 2: Demographic ---
    demo_parts = []

    if business.customer_age_distribution:
        age_notes = []
        for bracket in business.customer_age_distribution:
            age_profile = AGE_BEHAVIORAL_PROFILES.get(bracket)
            if age_profile:
                age_notes.append(f"Age {bracket}: {age_profile['note']}")
        if age_notes:
            profile.demographic_layer["age_profiles"] = age_notes
            demo_parts.append("AGE BEHAVIOR:\n" + "\n".join(age_notes))
            confidence_score += 2

    if business.customer_income_bracket:
        income = INCOME_BEHAVIORAL_PROFILES.get(business.customer_income_bracket)
        if income:
            profile.demographic_layer["income_profile"] = income
            demo_parts.append(
                f"INCOME BEHAVIOR ({business.customer_income_bracket}):\n{income['note']}"
            )
            confidence_score += 2

    if business.customer_gender_split and business.customer_gender_split != "unknown":
        profile.demographic_layer["gender_split"] = business.customer_gender_split

    if business.local_vs_visitor_ratio:
        profile.demographic_layer["local_visitor"] = business.local_vs_visitor_ratio
        if business.local_vs_visitor_ratio == "all_online":
            demo_parts.append(
                "CHANNEL: All online -- no physical location. Personas should interact "
                "digitally, not in-person. Switching costs are lower online."
            )
        elif business.local_vs_visitor_ratio == "mostly_visitors":
            demo_parts.append(
                "CUSTOMER BASE: Mostly new or one-time customers. Low baseline loyalty. "
                "First impressions and discovery channels matter more than retention."
            )

    if business.digital_savviness:
        profile.demographic_layer["digital_savviness"] = business.digital_savviness

    if demo_parts:
        summary_parts.append("\n\n".join(demo_parts))

    # --- Layer 3: Industry ---
    norm_key = INDUSTRY_TYPE_MAP.get(business.type, "restaurant")
    norms = INDUSTRY_NORMS.get(norm_key)
    if norms:
        profile.industry_layer = norms
        industry_text = (
            f"INDUSTRY BEHAVIORAL NORMS ({business.type}):\n"
            f"Engagement model: {norms['engagement_model']}\n"
            f"Decision speed: {norms['decision_speed']}\n"
            f"Switching cost: {norms['switching_cost']}\n"
            f"Loyalty driver: {norms['loyalty_driver']}\n"
            f"{norms['key_behavioral_note']}"
        )
        summary_parts.append(industry_text)
        confidence_score += 1

    # --- Layer 4: Behavioral composite ---
    behavioral = {}

    # Composite price sensitivity
    if business.price_range:
        range_map = {
            "budget": "very_high",
            "mid_range": "moderate",
            "premium": "low_to_moderate",
            "luxury": "low",
        }
        behavioral["price_sensitivity_from_tier"] = range_map.get(
            business.price_range, "moderate"
        )

    if business.average_transaction_value:
        behavioral["baseline_transaction_value"] = business.average_transaction_value

    if norms:
        behavioral["engagement_model"] = norms["engagement_model"]
        behavioral["switching_cost"] = norms["switching_cost"]
        behavioral["decision_style"] = norms["typical_decision_style"]

    profile.behavioral_layer = behavioral

    if business.price_range and business.average_transaction_value:
        summary_parts.append(
            f"PRICING CONTEXT:\n"
            f"Price positioning: {business.price_range}. "
            f"Average transaction: {business.average_transaction_value}. "
            f"Personas should calibrate their price reactions to this baseline."
        )
        confidence_score += 1

    # --- Assemble ---
    profile.summary = "\n\n---\n\n".join(summary_parts) if summary_parts else ""

    if confidence_score >= 5:
        profile.confidence = "high"
    elif confidence_score >= 3:
        profile.confidence = "medium"
    else:
        profile.confidence = "low"

    logger.info(
        "Psychological profile built: %d layers, %d chars, confidence=%s",
        len([p for p in [profile.cultural_layer, profile.demographic_layer,
                         profile.industry_layer, profile.behavioral_layer] if p]),
        len(profile.summary),
        profile.confidence,
    )

    return profile
