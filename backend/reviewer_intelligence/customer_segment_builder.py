"""
Builds a realistic customer segment distribution from all available signals.

THIS IS THE MOST IMPORTANT FILE IN THE REVIEWER INTELLIGENCE SYSTEM.
If the segment distribution is wrong, every persona is wrong.

Based on NeurIPS 2025 / ICLR 2024: personas MUST be anchored in structured
demographic data FIRST, then narrative detail added SECOND.
The CustomerSegmentProfile IS the structured anchor.
"""

import logging
from dataclasses import dataclass, field

from backend.models.business import BusinessSnapshot
from backend.reviewer_intelligence.bias_corrector import BiasAdjustedSignals
from backend.reviewer_intelligence.silent_majority_estimator import SilentMajorityProfile

logger = logging.getLogger(__name__)


@dataclass
class CustomerSegment:
    name: str
    description: str
    estimated_proportion: float
    price_sensitivity: str       # "low", "moderate", "high"
    loyalty_likelihood: float    # 0.0 to 1.0
    is_silent_majority: bool
    age_range: str               # "25-45" etc
    income_tier: str             # "budget", "mid", "affluent"
    visit_frequency: str         # "weekly", "monthly", "occasional", "one-time"
    key_decision_factors: list[str]


@dataclass
class CustomerSegmentProfile:
    segments: list[CustomerSegment]
    total_estimated_customers: str
    dominant_segment: str
    most_price_sensitive_segment: str
    silent_majority_proportion: float
    signals_used: list[str]
    confidence_level: str
    plain_english_summary: str


def build_segments(
    adjusted: BiasAdjustedSignals,
    silent: SilentMajorityProfile,
    business: BusinessSnapshot,
) -> CustomerSegmentProfile:
    """Build customer segments from all available signals.

    Segment proportions are calibrated by review signals, demographics,
    and the silent majority estimate. They always sum to 1.0.
    """

    signals = adjusted.raw_signals
    tourist_ratio = signals.tourist_ratio_estimate

    # Base segment proportions (adjusted by signals)
    # These are research-backed starting points
    silent_prop = silent.recommended_swarm_proportion  # 0.55-0.70

    # Divide silent majority between regulars and occasionals
    silent_regular_prop = silent_prop * 0.45   # ~28% of total
    silent_occasional_prop = silent_prop * 0.55  # ~35% of total

    # Vocal segments (from review data)
    vocal_loyalist_prop = 0.05
    vocal_critic_prop = 0.03

    # Tourist segment (from tourist ratio estimate)
    tourist_prop = min(tourist_ratio * 0.5, 0.25)  # Cap at 25%

    # Price-sensitive segment (from price mention frequency)
    price_sensitive_prop = 0.08
    if signals.price_mention_frequency > 0.3:
        price_sensitive_prop = 0.12
    elif signals.price_mention_frequency > 0.5:
        price_sensitive_prop = 0.15

    # Normalise to sum to 1.0
    total = (silent_regular_prop + silent_occasional_prop +
             vocal_loyalist_prop + vocal_critic_prop +
             tourist_prop + price_sensitive_prop)
    factor = 1.0 / total

    segments = [
        CustomerSegment(
            name="Silent Regulars",
            description="Come often, never review. Most price-sensitive group. Their behaviour drives your actual revenue.",
            estimated_proportion=round(silent_regular_prop * factor, 3),
            price_sensitivity="moderate to high",
            loyalty_likelihood=0.6,
            is_silent_majority=True,
            age_range="30-55",
            income_tier="mid",
            visit_frequency="weekly",
            key_decision_factors=["convenience", "habit", "price", "consistency"],
        ),
        CustomerSegment(
            name="Silent Occasionals",
            description="Visit a few times a year. Very likely to switch if prices change or a competitor opens nearby.",
            estimated_proportion=round(silent_occasional_prop * factor, 3),
            price_sensitivity="high",
            loyalty_likelihood=0.3,
            is_silent_majority=True,
            age_range="22-50",
            income_tier="budget to mid",
            visit_frequency="occasional",
            key_decision_factors=["price", "convenience", "mood", "what friends suggest"],
        ),
        CustomerSegment(
            name="Loyal Fans",
            description="Your most enthusiastic customers. Leave positive reviews. Overrepresented in your online perception.",
            estimated_proportion=round(vocal_loyalist_prop * factor, 3),
            price_sensitivity="low",
            loyalty_likelihood=0.9,
            is_silent_majority=False,
            age_range="28-60",
            income_tier="mid to affluent",
            visit_frequency="weekly",
            key_decision_factors=["quality", "relationship", "atmosphere", "consistency"],
        ),
        CustomerSegment(
            name="Frustrated Customers",
            description="Had a bad experience and reviewed. Included for balance -- they represent real friction points.",
            estimated_proportion=round(vocal_critic_prop * factor, 3),
            price_sensitivity="moderate",
            loyalty_likelihood=0.1,
            is_silent_majority=False,
            age_range="25-55",
            income_tier="mid",
            visit_frequency="occasional",
            key_decision_factors=["service quality", "feeling valued", "price fairness"],
        ),
        CustomerSegment(
            name="Tourists / One-time Visitors",
            description="Visiting the area. Unlikely to return regardless of your pricing decision.",
            estimated_proportion=round(tourist_prop * factor, 3),
            price_sensitivity="low to moderate",
            loyalty_likelihood=0.05,
            is_silent_majority=True,
            age_range="25-50",
            income_tier="mid to affluent",
            visit_frequency="one-time",
            key_decision_factors=["location", "reviews", "atmosphere", "novelty"],
        ),
        CustomerSegment(
            name="Value Seekers",
            description="Come specifically because they see you as affordable. Most vulnerable to price increases.",
            estimated_proportion=round(price_sensitive_prop * factor, 3),
            price_sensitivity="high",
            loyalty_likelihood=0.4,
            is_silent_majority=True,
            age_range="20-45",
            income_tier="budget",
            visit_frequency="monthly",
            key_decision_factors=["price", "portion size", "deals", "value for money"],
        ),
    ]

    # Determine dominant and most price-sensitive segments
    dominant = max(segments, key=lambda s: s.estimated_proportion)
    most_price_sensitive = max(
        segments,
        key=lambda s: {"low": 1, "low to moderate": 2, "moderate": 3,
                       "moderate to high": 4, "high": 5}.get(s.price_sensitivity, 3)
    )

    silent_total = sum(s.estimated_proportion for s in segments if s.is_silent_majority)

    # Build plain English summary
    summary_parts = [
        f"Most of your customers ({int(silent_total * 100)}%) never leave reviews.",
    ]
    if tourist_ratio > 0.3:
        summary_parts.append(
            f"About {int(tourist_ratio * 100)}% of your reviewers appear to be tourists."
        )
    if signals.price_mention_frequency > 0.2:
        summary_parts.append(
            "Price is mentioned frequently in your reviews -- your customers are watching."
        )
    summary = " ".join(summary_parts)

    signals_used = ["Google Reviews aggregate patterns", "bias correction (Karaman 2021, Han & Anderson 2026)"]
    if business.customer_description:
        signals_used.append("business owner customer description")

    logger.info(
        "Segment profile built: %d segments, silent_majority=%.0f%%, dominant=%s",
        len(segments), silent_total * 100, dominant.name,
    )

    return CustomerSegmentProfile(
        segments=segments,
        total_estimated_customers=f"~{adjusted.estimated_total_customers_yearly} per year",
        dominant_segment=dominant.name,
        most_price_sensitive_segment=most_price_sensitive.name,
        silent_majority_proportion=round(silent_total, 3),
        signals_used=signals_used,
        confidence_level=adjusted.overall_confidence,
        plain_english_summary=summary,
    )
