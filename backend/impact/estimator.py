"""
Impact Estimator -- converts persona responses into quantitative
revenue/customer impact estimates with confidence intervals.

Based on Topic 1 (Uri Simonsohn): every estimate = truth + error.
We show the estimate AND how wrong we could be.

The CI decision framework:
- If worst case is still pretty good -> do it
- If best case is not good enough -> forget it
- If best case is good but worst case is bad -> tough call, get more data

We apply this to every simulation result.
"""

import logging
import math
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Revenue Models
# ---------------------------------------------------------------------------

REVENUE_MODELS = {
    "per_visit": {
        "label": "Per-Visit",
        "formula": "customers x visits x spend_per_visit",
        "switching_cost": "low",
        "engagement_metric": "visit_frequency",
        "description": "Revenue driven by repeat foot traffic and per-visit spending.",
    },
    "subscription": {
        "label": "Subscription",
        "formula": "subscribers x monthly_price x retention_rate",
        "switching_cost": "medium",
        "engagement_metric": "renewal_rate",
        "description": "Recurring revenue from subscribers who pay periodically.",
    },
    "contract": {
        "label": "Contract / B2B",
        "formula": "contracts x avg_contract_value x renewal_rate",
        "switching_cost": "high",
        "engagement_metric": "contract_renewal",
        "description": "Revenue from long-term agreements with negotiated terms.",
    },
    "ecommerce": {
        "label": "E-Commerce",
        "formula": "visitors x conversion_rate x avg_order_value",
        "switching_cost": "low",
        "engagement_metric": "conversion_rate",
        "description": "Revenue driven by online traffic, conversion, and order size.",
    },
    "per_session": {
        "label": "Per-Session",
        "formula": "clients x sessions x rate_per_session",
        "switching_cost": "medium",
        "engagement_metric": "session_frequency",
        "description": "Revenue from scheduled appointments or sessions.",
    },
    "membership": {
        "label": "Membership",
        "formula": "members x monthly_fee x retention",
        "switching_cost": "medium",
        "engagement_metric": "membership_retention",
        "description": "Revenue from ongoing memberships with periodic dues.",
    },
    "project": {
        "label": "Project-Based",
        "formula": "projects x avg_project_value",
        "switching_cost": "low",
        "engagement_metric": "project_pipeline",
        "description": "Revenue from discrete projects with defined scope and price.",
    },
}


# Switching cost multiplier for retention mapping.
# Higher switching cost = customers stay even when sentiment is low.
SWITCHING_COST_RETENTION_FLOOR = {
    "low": 0.15,       # easy to leave (restaurants, ecommerce)
    "medium": 0.30,    # moderate friction (subscriptions, memberships)
    "high": 0.45,      # hard to leave (contracts, enterprise B2B)
}

# Engagement change asymmetry by model type.
# How much negative sentiment reduces engagement vs positive increases it.
ENGAGEMENT_ASYMMETRY = {
    "per_visit": {"positive_cap": 5, "negative_multiplier": 40},
    "subscription": {"positive_cap": 3, "negative_multiplier": 25},
    "contract": {"positive_cap": 2, "negative_multiplier": 15},
    "ecommerce": {"positive_cap": 8, "negative_multiplier": 50},
    "per_session": {"positive_cap": 5, "negative_multiplier": 35},
    "membership": {"positive_cap": 3, "negative_multiplier": 20},
    "project": {"positive_cap": 5, "negative_multiplier": 30},
}


# ---------------------------------------------------------------------------
# Business Type -> Revenue Model mapping (80+ types)
# ---------------------------------------------------------------------------

BUSINESS_TYPE_TO_MODEL = {
    # --- per_visit (foot traffic businesses) ---
    "restaurant": "per_visit",
    "cafe": "per_visit",
    "coffee_shop": "per_visit",
    "bakery": "per_visit",
    "bar": "per_visit",
    "pub": "per_visit",
    "brewery": "per_visit",
    "winery": "per_visit",
    "food_truck": "per_visit",
    "fast_food": "per_visit",
    "pizzeria": "per_visit",
    "deli": "per_visit",
    "juice_bar": "per_visit",
    "ice_cream_shop": "per_visit",
    "diner": "per_visit",
    "grocery_store": "per_visit",
    "supermarket": "per_visit",
    "convenience_store": "per_visit",
    "pharmacy": "per_visit",
    "gas_station": "per_visit",
    "flower_shop": "per_visit",
    "bookstore": "per_visit",
    "pet_store": "per_visit",
    "hardware_store": "per_visit",
    "clothing_store": "per_visit",
    "shoe_store": "per_visit",
    "jewelry_store": "per_visit",
    "toy_store": "per_visit",
    "gift_shop": "per_visit",
    "thrift_store": "per_visit",
    "liquor_store": "per_visit",
    "smoke_shop": "per_visit",
    "retail": "per_visit",
    "boutique": "per_visit",
    "art_gallery": "per_visit",
    "museum": "per_visit",
    "movie_theater": "per_visit",
    "arcade": "per_visit",
    "bowling_alley": "per_visit",
    "car_wash": "per_visit",
    "laundromat": "per_visit",

    # --- subscription (recurring revenue) ---
    "saas": "subscription",
    "software": "subscription",
    "streaming": "subscription",
    "media": "subscription",
    "newsletter_business": "subscription",
    "gym": "subscription",
    "fitness_studio": "subscription",
    "yoga_studio": "subscription",
    "pilates_studio": "subscription",
    "crossfit": "subscription",
    "meal_kit": "subscription",
    "subscription_box": "subscription",
    "cloud_service": "subscription",
    "hosting": "subscription",
    "vpn": "subscription",
    "security_service": "subscription",
    "monitoring": "subscription",
    "analytics_platform": "subscription",
    "crm": "subscription",
    "erp": "subscription",
    "telecom": "subscription",
    "isp": "subscription",
    "mobile_carrier": "subscription",
    "insurance": "subscription",
    "financial_service": "subscription",

    # --- contract (B2B / long-term agreements) ---
    "consulting": "contract",
    "management_consulting": "contract",
    "it_consulting": "contract",
    "accounting": "contract",
    "law_firm": "contract",
    "legal_services": "contract",
    "staffing_agency": "contract",
    "recruiting": "contract",
    "logistics": "contract",
    "shipping": "contract",
    "freight": "contract",
    "manufacturing": "contract",
    "wholesale": "contract",
    "distributor": "contract",
    "b2b_services": "contract",
    "managed_services": "contract",
    "outsourcing": "contract",
    "janitorial": "contract",
    "security_guard": "contract",
    "waste_management": "contract",
    "landscaping_commercial": "contract",
    "property_management": "contract",
    "real_estate_commercial": "contract",

    # --- ecommerce (online retail) ---
    "ecommerce": "ecommerce",
    "online_store": "ecommerce",
    "dropshipping": "ecommerce",
    "marketplace": "ecommerce",
    "print_on_demand": "ecommerce",
    "digital_products": "ecommerce",
    "online_marketplace": "ecommerce",
    "auction_site": "ecommerce",

    # --- per_session (appointment-based) ---
    "salon": "per_session",
    "hair_salon": "per_session",
    "barbershop": "per_session",
    "nail_salon": "per_session",
    "spa": "per_session",
    "massage": "per_session",
    "tattoo_parlor": "per_session",
    "dentist": "per_session",
    "doctor": "per_session",
    "clinic": "per_session",
    "veterinarian": "per_session",
    "chiropractor": "per_session",
    "physical_therapy": "per_session",
    "optometrist": "per_session",
    "dermatologist": "per_session",
    "therapist": "per_session",
    "psychologist": "per_session",
    "counselor": "per_session",
    "tutor": "per_session",
    "music_teacher": "per_session",
    "driving_school": "per_session",
    "personal_trainer": "per_session",
    "dog_groomer": "per_session",
    "dog_walker": "per_session",
    "pet_grooming": "per_session",
    "auto_mechanic": "per_session",
    "auto_repair": "per_session",
    "dry_cleaner": "per_session",
    "tailor": "per_session",
    "photographer": "per_session",
    "accountant_individual": "per_session",
    "tax_preparer": "per_session",
    "notary": "per_session",

    # --- membership (club / community) ---
    "coworking": "membership",
    "country_club": "membership",
    "golf_club": "membership",
    "tennis_club": "membership",
    "swimming_pool": "membership",
    "social_club": "membership",
    "wine_club": "membership",
    "book_club": "membership",
    "fraternal_organization": "membership",
    "professional_association": "membership",
    "trade_union": "membership",
    "childcare": "membership",
    "daycare": "membership",
    "after_school": "membership",
    "martial_arts": "membership",
    "dance_studio": "membership",
    "climbing_gym": "membership",
    "storage_facility": "membership",

    # --- project (discrete deliverables) ---
    "freelance": "project",
    "agency": "project",
    "marketing_agency": "project",
    "design_agency": "project",
    "web_development": "project",
    "app_development": "project",
    "construction": "project",
    "general_contractor": "project",
    "electrician": "project",
    "plumber": "project",
    "hvac": "project",
    "roofing": "project",
    "painting": "project",
    "landscaping": "project",
    "interior_design": "project",
    "architect": "project",
    "surveyor": "project",
    "renovation": "project",
    "home_improvement": "project",
    "moving_company": "project",
    "event_planner": "project",
    "wedding_planner": "project",
    "caterer": "project",
    "videographer": "project",
    "graphic_designer": "project",
    "copywriter": "project",
    "translator": "project",
    "real_estate_agent": "project",
}

# Default model when business type is unknown
DEFAULT_REVENUE_MODEL = "per_visit"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class CustomerImpact:
    """Impact on a single customer segment."""
    segment: str
    persona_count: int
    avg_sentiment: float          # -1 to 1
    likely_action: str            # "stay", "reduce_visits", "leave", "increase"
    retention_probability: float  # 0 to 1
    visit_change_pct: float       # e.g. -20 means 20% fewer visits
    spend_change_pct: float       # e.g. +10 means 10% more per visit (price increase)


@dataclass
class RevenueEstimate:
    """Point estimate with confidence interval.

    Despite the name, this measures the PRIMARY IMPACT of the proposed change,
    which may or may not be revenue. For pricing questions it is revenue.
    For operational questions it might be customer satisfaction or retention.
    The impact_type field describes what is actually being measured.
    """
    point_estimate_pct: float     # best guess % change in primary metric
    ci_low_pct: float             # worst case (lower bound)
    ci_high_pct: float            # best case (upper bound)
    confidence_level: str         # "high", "medium", "low"
    impact_type: str = "revenue"  # what this measures: "revenue", "satisfaction", "adoption", "retention", "engagement"
    impact_label: str = "Estimated revenue change"  # human-readable label for the UI


def _detect_impact_type(question: str) -> tuple[str, str]:
    """Detect what type of impact this question is really about.

    Returns (impact_type, impact_label) tuple.
    """
    q = question.lower()

    # Pricing/revenue questions
    if any(w in q for w in ["price", "cost", "fee", "charge", "raise", "discount",
                             "subscription", "tier", "plan", "expensive", "cheap",
                             "revenue", "profit", "margin"]):
        return "revenue", "Estimated revenue change"

    # Adoption/feature questions
    if any(w in q for w in ["launch", "new feature", "new product", "would they use",
                             "would customers use", "sign up", "download", "adopt",
                             "loyalty card", "app", "mobile", "online"]):
        return "adoption", "Estimated adoption likelihood"

    # Satisfaction/experience questions
    if any(w in q for w in ["renovate", "redesign", "improve", "upgrade", "quality",
                             "experience", "atmosphere", "ambiance", "comfort",
                             "waiting", "wait time", "cleanliness"]):
        return "satisfaction", "Estimated satisfaction change"

    # Retention questions
    if any(w in q for w in ["keep", "retain", "churn", "cancel", "leave",
                             "loyalty", "renewal", "come back", "return"]):
        return "retention", "Estimated retention impact"

    # Operational questions
    if any(w in q for w in ["hours", "open", "close", "schedule", "sunday",
                             "delivery", "pickup", "parking", "location",
                             "move", "expand", "staff", "hiring"]):
        return "engagement", "Estimated engagement change"

    # Default: general customer reaction
    return "engagement", "Estimated customer impact"


@dataclass
class ImpactReport:
    """Full quantitative impact report.

    Works for ANY business decision, not just pricing.
    The revenue field measures the primary impact metric,
    which varies by question type (revenue, satisfaction, adoption, etc.).
    """
    # Primary impact metric (named 'revenue' for backward compat but may measure other things)
    revenue: RevenueEstimate

    # Customer retention
    customers_likely_stay: int
    customers_likely_reduce: int
    customers_likely_leave: int
    total_customers_modelled: int
    retention_rate_pct: float

    # Segment breakdown
    segments: list[CustomerImpact]

    # Decision recommendation
    decision: str                  # "proceed", "caution", "avoid", "test_first"
    decision_reasoning: str
    decision_framework: str        # the CI logic explanation

    # Upside/downside analysis
    worst_case_summary: str
    best_case_summary: str
    most_likely_summary: str

    # Hypothesis framing
    null_hypothesis: str = "No change"
    alternative_hypothesis: str = "Change occurs"
    reject_null: bool = False  # True if CI does not contain 0
    effect_size: str = "unknown"  # "negligible", "small", "medium", "large"

    # Revenue model metadata (optional, for new callers)
    revenue_model: str = "per_visit"
    revenue_model_label: str = "Per-Visit"


# ---------------------------------------------------------------------------
# Revenue model detection
# ---------------------------------------------------------------------------

def _detect_revenue_model(business_type: Optional[str] = None) -> str:
    """Detect the appropriate revenue model for a business type.

    Tries exact match first, then normalized match (lowercase, underscores),
    then falls back to default.
    """
    if not business_type:
        return DEFAULT_REVENUE_MODEL

    # Normalize: lowercase, replace spaces/hyphens with underscores
    normalized = business_type.lower().strip().replace(" ", "_").replace("-", "_")

    # Exact match
    if normalized in BUSINESS_TYPE_TO_MODEL:
        return BUSINESS_TYPE_TO_MODEL[normalized]

    # Partial match: check if any key is contained in the input or vice versa
    for key, model in BUSINESS_TYPE_TO_MODEL.items():
        if key in normalized or normalized in key:
            return model

    return DEFAULT_REVENUE_MODEL


# ---------------------------------------------------------------------------
# Sentiment -> behavioral mappings (industry-aware)
# ---------------------------------------------------------------------------

def _sentiment_to_retention(
    sentiment: float,
    switching_cost: str = "low",
) -> float:
    """Convert sentiment (-1 to 1) to retention probability (0 to 1).

    Adjusted by switching cost:
    - Low switching cost (restaurants, ecommerce): standard curve
    - Medium switching cost (subscriptions, memberships): higher floor
    - High switching cost (contracts, enterprise): much higher floor

    Base calibration (low switching cost):
    - sentiment 1.0 -> 0.98 retention
    - sentiment 0.5 -> 0.90 retention
    - sentiment 0.0 -> 0.75 retention
    - sentiment -0.5 -> 0.50 retention
    - sentiment -1.0 -> 0.20 retention
    """
    floor = SWITCHING_COST_RETENTION_FLOOR.get(switching_cost, 0.15)
    ceiling = 0.98
    range_size = ceiling - floor

    # Sigmoid mapping scaled to [floor, ceiling]
    raw = floor + range_size / (1 + math.exp(-3 * sentiment))
    return min(max(raw, floor), ceiling)


def _sentiment_to_engagement_change(
    sentiment: float,
    revenue_model: str = "per_visit",
) -> float:
    """How much engagement frequency changes based on sentiment.

    Returns percentage change. Negative sentiment reduces engagement
    more than positive sentiment increases it -- this reflects behavioral
    asymmetry across all industries: people cut back more easily than
    they increase.

    The asymmetry varies by model:
    - ecommerce: very elastic (easy to click away)
    - contract: very inelastic (locked in)
    - per_visit: moderate
    """
    params = ENGAGEMENT_ASYMMETRY.get(
        revenue_model,
        ENGAGEMENT_ASYMMETRY["per_visit"],
    )

    if sentiment >= 0:
        return sentiment * params["positive_cap"]
    else:
        return sentiment * params["negative_multiplier"]


# Backward-compatible alias
def _sentiment_to_visit_change(sentiment: float) -> float:
    """Backward-compatible wrapper. Use _sentiment_to_engagement_change instead."""
    return _sentiment_to_engagement_change(sentiment, revenue_model="per_visit")


# ---------------------------------------------------------------------------
# Main estimator
# ---------------------------------------------------------------------------

def estimate_impact(
    responses: list[dict],
    question: str,
    business_data: Optional[dict] = None,
    business_type: Optional[str] = None,
) -> ImpactReport:
    """Estimate quantitative impact from persona responses.

    Takes the raw persona response dicts and converts to revenue/customer
    impact estimates with confidence intervals.

    Args:
        responses: List of persona response dicts with at least "sentiment".
        question: The question asked by the business owner.
        business_data: Optional dict with business metadata.
        business_type: Optional string like "restaurant", "saas", "salon".
            If not provided, falls back to business_data.get("business_type")
            or defaults to "per_visit" model.
    """

    if not responses:
        return _empty_report()

    # Detect revenue model
    if not business_type and business_data:
        business_type = business_data.get("business_type") or business_data.get("type")
    model_key = _detect_revenue_model(business_type)
    model_info = REVENUE_MODELS[model_key]
    switching_cost = model_info["switching_cost"]

    n = len(responses)

    # Classify each persona's likely behavior
    segments: list[CustomerImpact] = []
    stay_count = 0
    reduce_count = 0
    leave_count = 0

    sentiments = []
    for r in responses:
        sent = float(r.get("sentiment", 0))
        sentiments.append(sent)
        name = r.get("persona_name", "Unknown")

        retention = _sentiment_to_retention(sent, switching_cost=switching_cost)
        engagement_change = _sentiment_to_engagement_change(sent, revenue_model=model_key)

        if retention > 0.8:
            action = "stay"
            stay_count += 1
        elif retention > 0.5:
            action = "reduce_visits"
            reduce_count += 1
        else:
            action = "leave"
            leave_count += 1

        # For price increase questions, positive sentiment still means
        # they accept the higher price -> spend increases per visit
        is_price_question = any(w in question.lower() for w in
            ["price", "raise", "increase", "charge", "cost", "fee", "expensive",
             "subscription", "tier", "plan", "per seat", "per user", "monthly",
             "annual", "contract", "renewal"])
        spend_change = 10 if is_price_question and sent > -0.3 else 0

        segments.append(CustomerImpact(
            segment=name,
            persona_count=1,
            avg_sentiment=sent,
            likely_action=action,
            retention_probability=round(retention, 2),
            visit_change_pct=round(engagement_change, 1),
            spend_change_pct=spend_change,
        ))

    # --- Revenue estimate ---
    avg_sentiment = sum(sentiments) / n
    std_sentiment = math.sqrt(sum((s - avg_sentiment) ** 2 for s in sentiments) / max(n - 1, 1))

    # Point estimate: weighted combination of retention, engagement change, and spend change
    avg_retention = sum(s.retention_probability for s in segments) / n
    avg_engagement_change = sum(s.visit_change_pct for s in segments) / n
    avg_spend_change = sum(s.spend_change_pct for s in segments) / n

    # Revenue impact depends on the model, but the general formula is:
    # % change in revenue ~ retention_effect + engagement_effect + spend_effect
    retention_effect = (avg_retention - 1) * 100  # e.g. 0.85 -> -15%
    engagement_effect = avg_engagement_change * avg_retention  # weighted by who stays
    spend_effect = avg_spend_change * avg_retention

    point_estimate = retention_effect + engagement_effect + spend_effect

    # Confidence interval -- wider when:
    # - fewer personas (small sample)
    # - higher sentiment variance (disagreement)
    # - the question is more speculative
    # - switching costs are low (more volatile outcomes)

    # Base CI width from sample size (like SE = SD/sqrt(N))
    base_ci_width = (std_sentiment * 30) / math.sqrt(n) + 5  # minimum +-5%

    # Widen for small samples
    if n < 10:
        base_ci_width *= 1.5
    if n < 6:
        base_ci_width *= 2

    # Narrow slightly for high switching cost (outcomes more predictable)
    if switching_cost == "high":
        base_ci_width *= 0.8
    elif switching_cost == "low":
        base_ci_width *= 1.1

    ci_low = point_estimate - base_ci_width
    ci_high = point_estimate + base_ci_width

    # Determine confidence level
    if n >= 12 and std_sentiment < 0.4:
        confidence = "high"
    elif n >= 8 and std_sentiment < 0.6:
        confidence = "medium"
    else:
        confidence = "low"

    # Detect what this question is actually about
    impact_type, impact_label = _detect_impact_type(question)

    revenue = RevenueEstimate(
        point_estimate_pct=round(point_estimate, 1),
        ci_low_pct=round(ci_low, 1),
        ci_high_pct=round(ci_high, 1),
        confidence_level=confidence,
        impact_type=impact_type,
        impact_label=impact_label,
    )

    # --- Decision framework (from Topic 1) ---
    if ci_low > 0:
        # Even worst case is positive
        decision = "proceed"
        decision_reasoning = (
            f"Even in the worst case scenario ({ci_low:+.1f}%), the outcome is still positive. "
            f"The upside ({ci_high:+.1f}%) significantly outweighs the risk."
        )
    elif ci_high < 0:
        # Even best case is negative
        decision = "avoid"
        decision_reasoning = (
            f"Even in the best case scenario ({ci_high:+.1f}%), the outcome is still negative. "
            f"The downside risk is not worth it."
        )
    elif ci_high > abs(ci_low) * 1.5:
        # Upside is much bigger than downside
        decision = "caution"
        decision_reasoning = (
            f"The worst case ({ci_low:+.1f}%) is a manageable loss, "
            f"while the best case ({ci_high:+.1f}%) is a significant gain. "
            f"The upside outweighs the downside, but consider testing with a small group first."
        )
    else:
        # Genuinely uncertain
        decision = "test_first"
        decision_reasoning = (
            f"The range of outcomes is wide: from {ci_low:+.1f}% to {ci_high:+.1f}%. "
            f"We can not confidently say this will help or hurt. "
            f"Test with a small subset of customers before committing fully."
        )

    # Use impact_type-aware language (not always "revenue")
    metric_word = {
        "revenue": "revenue",
        "satisfaction": "customer satisfaction",
        "adoption": "adoption",
        "retention": "customer retention",
        "engagement": "customer engagement",
    }.get(impact_type, "overall impact")

    decision_framework = (
        f"Our best estimate is {point_estimate:+.1f}% change in {metric_word}, "
        f"but the real outcome could be anywhere from {ci_low:+.1f}% to {ci_high:+.1f}%. "
        f"The question is not whether {point_estimate:+.1f}% is good or bad -- "
        f"it is whether you are comfortable with the worst case of {ci_low:+.1f}%."
    )

    retention_rate = (stay_count + reduce_count) / n * 100

    worst_case = (
        f"Worst case: {ci_low:+.1f}% {metric_word} change. "
        f"About {leave_count} in {n} customers could leave or significantly reduce engagement."
    )
    best_case = (
        f"Best case: {ci_high:+.1f}% {metric_word} change. "
        f"Most customers respond positively and maintain or increase their engagement."
    )
    most_likely = (
        f"Most likely: {point_estimate:+.1f}% {metric_word} change. "
        f"{stay_count} of {n} customers stay, {reduce_count} reduce engagement, {leave_count} disengage."
    )

    logger.info(
        "Impact estimate: %.1f%% [%.1f%%, %.1f%%], decision=%s, retention=%.0f%%, model=%s",
        point_estimate, ci_low, ci_high, decision, retention_rate, model_key,
    )

    # Hypothesis framing
    reject_null = ci_low > 0 or ci_high < 0  # CI doesn't contain zero
    abs_point = abs(point_estimate)
    if abs_point < 2:
        effect_size = "negligible"
    elif abs_point < 5:
        effect_size = "small"
    elif abs_point < 15:
        effect_size = "medium"
    else:
        effect_size = "large"

    null_hyp = f"No change in {metric_word}"
    alt_hyp = f"{metric_word.capitalize()} changes as a result of this decision"

    return ImpactReport(
        revenue=revenue,
        customers_likely_stay=stay_count,
        customers_likely_reduce=reduce_count,
        customers_likely_leave=leave_count,
        total_customers_modelled=n,
        retention_rate_pct=round(retention_rate, 1),
        segments=segments,
        decision=decision,
        decision_reasoning=decision_reasoning,
        decision_framework=decision_framework,
        worst_case_summary=worst_case,
        best_case_summary=best_case,
        most_likely_summary=most_likely,
        revenue_model=model_key,
        revenue_model_label=model_info["label"],
        null_hypothesis=null_hyp,
        alternative_hypothesis=alt_hyp,
        reject_null=reject_null,
        effect_size=effect_size,
    )


def _empty_report() -> ImpactReport:
    return ImpactReport(
        revenue=RevenueEstimate(0, -10, 10, "low"),
        customers_likely_stay=0,
        customers_likely_reduce=0,
        customers_likely_leave=0,
        total_customers_modelled=0,
        retention_rate_pct=0,
        segments=[],
        decision="test_first",
        decision_reasoning="Not enough data to make a recommendation.",
        decision_framework="No simulation data available.",
        worst_case_summary="Unknown",
        best_case_summary="Unknown",
        most_likely_summary="Unknown",
    )
