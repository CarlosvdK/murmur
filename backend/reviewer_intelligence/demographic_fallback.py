"""
Demographic-only fallback for reviewer intelligence.

When Google Places review data is unavailable (no API key, business not
indexed, timeout), we previously dropped the entire manifest and fell
back to freeform persona generation -- losing all the NeurIPS 2025
structured-anchoring benefits the rest of the pipeline was designed
around.

This module builds a ``AggregateReviewSignals`` stub from just the
business type and location, using defensible industry priors. The
resulting manifest is marked with ``signal_confidence="low"`` and an
explicit bias warning so downstream caveats can call it out.

This is deliberately conservative: the numbers chosen are not meant to
be precise, they are meant to be *less wrong than freeform generation*
and clearly flagged as estimates.
"""

import logging
from typing import Optional

from backend.reviewer_intelligence.review_signal_extractor import (
    AggregateReviewSignals,
)

logger = logging.getLogger(__name__)


# Business-type priors. These come from industry averages and are rough.
# The point is: a barber shop is mostly locals on habit, a tourist-beach
# restaurant is mostly one-off visitors, a B2B SaaS has no meaningful
# tourist/local concept. Each row has:
#   (avg_rating, price_mention_freq, loyalty_freq, switching_freq,
#    tourist_ratio, local_ratio, review_trend, bias_warning_extra)
_BUSINESS_TYPE_PRIORS: dict[str, tuple] = {
    "restaurant": (4.1, 0.18, 0.15, 0.08, 0.30, 0.70, "stable", ""),
    "cafe": (4.2, 0.12, 0.22, 0.10, 0.25, 0.75, "stable", ""),
    "bar": (4.0, 0.15, 0.14, 0.10, 0.35, 0.65, "stable", ""),
    "bakery": (4.3, 0.10, 0.25, 0.06, 0.20, 0.80, "stable", ""),
    "barbershop": (4.4, 0.08, 0.30, 0.09, 0.10, 0.90, "stable", ""),
    "salon": (4.3, 0.14, 0.28, 0.11, 0.15, 0.85, "stable", ""),
    "gym": (4.2, 0.20, 0.25, 0.14, 0.05, 0.95, "stable", ""),
    "retail": (4.0, 0.17, 0.12, 0.10, 0.35, 0.65, "stable", ""),
    "grocery": (4.1, 0.22, 0.18, 0.07, 0.10, 0.90, "stable", ""),
    "hotel": (4.0, 0.20, 0.08, 0.14, 0.75, 0.25, "stable", ""),
    "food_truck": (4.3, 0.10, 0.10, 0.05, 0.40, 0.60, "stable", ""),
    "saas": (4.1, 0.24, 0.18, 0.16, 0.00, 0.00,
             "stable", "Tourist/local ratios do not apply to SaaS."),
    "b2b": (4.0, 0.22, 0.20, 0.14, 0.00, 0.00,
            "stable", "Tourist/local ratios do not apply to B2B."),
    "ecommerce": (4.0, 0.22, 0.10, 0.18, 0.00, 0.00,
                  "stable", "Tourist/local ratios do not apply online."),
    "clinic": (4.3, 0.15, 0.35, 0.07, 0.05, 0.95, "stable", ""),
    "consulting": (4.3, 0.20, 0.25, 0.12, 0.00, 0.00,
                   "stable", "Tourist/local ratios do not apply."),
}


def _match_business_type(business_type: str) -> tuple:
    """Return the closest prior for an arbitrary business_type string."""
    t = (business_type or "").lower()
    for key, prior in _BUSINESS_TYPE_PRIORS.items():
        if key in t:
            return prior
    # Generic default -- neutral signals.
    return (4.0, 0.15, 0.15, 0.10, 0.20, 0.80, "stable",
            "No business-type prior matched. Using generic defaults.")


def build_fallback_signals(
    business_name: str,
    business_type: str,
    location: Optional[str] = None,
) -> AggregateReviewSignals:
    """Build a low-confidence AggregateReviewSignals purely from priors.

    This runs when review data is unavailable. The resulting signals
    carry ``signal_confidence="low"`` and a ``bias_warning`` that names
    the source so downstream caveats can surface the degraded quality.
    """
    (avg_rating, price_freq, loyalty_freq, switching_freq,
     tourist_ratio, local_ratio, trend, extra_warning
     ) = _match_business_type(business_type)

    # Rating distribution implied by the average (not meant to be exact).
    # Assume a mild positive skew typical of review platforms.
    dist = {
        5: 50, 4: 25, 3: 12, 2: 7, 1: 6,
    }

    warning = (
        "Fallback mode: Google Places review data was not available for "
        "this business. These signals are industry priors, not observed "
        "review patterns. Confidence is LOW and downstream estimates "
        "should be treated as indicative only."
    )
    if extra_warning:
        warning = f"{warning} {extra_warning}"

    logger.info(
        "Building demographic fallback signals for %s (type=%s, location=%s)",
        business_name, business_type, location,
    )

    return AggregateReviewSignals(
        place_id=f"fallback::{business_name}",
        business_name=business_name,
        total_review_count=0,
        average_rating=avg_rating,
        rating_distribution=dist,
        price_mention_frequency=price_freq,
        value_positive_ratio=0.5,
        loyalty_signal_frequency=loyalty_freq,
        switching_signal_frequency=switching_freq,
        tourist_ratio_estimate=tourist_ratio,
        local_ratio_estimate=local_ratio,
        peak_days=[],
        price_change_detected=False,
        price_change_sentiment=None,
        review_trend=trend,
        top_positive_themes=[],
        top_negative_themes=[],
        signal_confidence="low",
        bias_warning=warning,
    )
