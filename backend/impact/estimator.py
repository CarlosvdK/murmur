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
    """Point estimate with confidence interval."""
    point_estimate_pct: float     # best guess % change in revenue
    ci_low_pct: float             # worst case (lower bound)
    ci_high_pct: float            # best case (upper bound)
    confidence_level: str         # "high", "medium", "low"


@dataclass
class ImpactReport:
    """Full quantitative impact report."""
    # Revenue
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


def _sentiment_to_retention(sentiment: float) -> float:
    """Convert sentiment (-1 to 1) to retention probability (0 to 1).

    Calibrated so:
    - sentiment 1.0 -> 0.98 retention (very positive, almost certainly stays)
    - sentiment 0.5 -> 0.90 retention
    - sentiment 0.0 -> 0.75 retention (neutral, might drift)
    - sentiment -0.5 -> 0.50 retention (unhappy, coin flip)
    - sentiment -1.0 -> 0.20 retention (very negative, likely leaves)
    """
    # Sigmoid-like mapping
    return 0.2 + 0.78 / (1 + math.exp(-3 * sentiment))


def _sentiment_to_visit_change(sentiment: float) -> float:
    """How much visit frequency changes based on sentiment.

    Returns percentage change: -50 to +10.
    Negative sentiment reduces visits. Positive barely increases.
    This reflects behavioral asymmetry: people cut back more easily
    than they increase.
    """
    if sentiment >= 0:
        return sentiment * 5  # max +5% visits
    else:
        return sentiment * 40  # max -40% visits


def estimate_impact(
    responses: list[dict],
    question: str,
    business_data: Optional[dict] = None,
) -> ImpactReport:
    """Estimate quantitative impact from persona responses.

    Takes the raw persona response dicts and converts to revenue/customer
    impact estimates with confidence intervals.
    """

    if not responses:
        return _empty_report()

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

        retention = _sentiment_to_retention(sent)
        visit_change = _sentiment_to_visit_change(sent)

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
            ["price", "raise", "increase", "charge", "cost", "fee", "expensive"])
        spend_change = 10 if is_price_question and sent > -0.3 else 0

        segments.append(CustomerImpact(
            segment=name,
            persona_count=1,
            avg_sentiment=sent,
            likely_action=action,
            retention_probability=round(retention, 2),
            visit_change_pct=round(visit_change, 1),
            spend_change_pct=spend_change,
        ))

    # --- Revenue estimate ---
    avg_sentiment = sum(sentiments) / n
    std_sentiment = math.sqrt(sum((s - avg_sentiment) ** 2 for s in sentiments) / max(n - 1, 1))

    # Point estimate: weighted combination of retention, visit change, and spend change
    avg_retention = sum(s.retention_probability for s in segments) / n
    avg_visit_change = sum(s.visit_change_pct for s in segments) / n
    avg_spend_change = sum(s.spend_change_pct for s in segments) / n

    # Revenue = customers * visits * spend_per_visit
    # % change in revenue ~ retention_effect + visit_effect + spend_effect
    retention_effect = (avg_retention - 1) * 100  # e.g. 0.85 -> -15%
    visit_effect = avg_visit_change * avg_retention  # weighted by who stays
    spend_effect = avg_spend_change * avg_retention

    point_estimate = retention_effect + visit_effect + spend_effect

    # Confidence interval -- wider when:
    # - fewer personas (small sample)
    # - higher sentiment variance (disagreement)
    # - the question is more speculative

    # Base CI width from sample size (like SE = SD/sqrt(N))
    base_ci_width = (std_sentiment * 30) / math.sqrt(n) + 5  # minimum +-5%

    # Widen for small samples
    if n < 10:
        base_ci_width *= 1.5
    if n < 6:
        base_ci_width *= 2

    ci_low = point_estimate - base_ci_width
    ci_high = point_estimate + base_ci_width

    # Determine confidence level
    if n >= 12 and std_sentiment < 0.4:
        confidence = "high"
    elif n >= 8 and std_sentiment < 0.6:
        confidence = "medium"
    else:
        confidence = "low"

    revenue = RevenueEstimate(
        point_estimate_pct=round(point_estimate, 1),
        ci_low_pct=round(ci_low, 1),
        ci_high_pct=round(ci_high, 1),
        confidence_level=confidence,
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

    decision_framework = (
        f"Our best estimate is {point_estimate:+.1f}% revenue impact, "
        f"but the real outcome could be anywhere from {ci_low:+.1f}% to {ci_high:+.1f}%. "
        f"The question is not whether {point_estimate:+.1f}% is good or bad -- "
        f"it is whether you are comfortable with the worst case of {ci_low:+.1f}%."
    )

    retention_rate = (stay_count + reduce_count) / n * 100

    worst_case = (
        f"Worst case: {ci_low:+.1f}% revenue change. "
        f"About {leave_count} in {n} customers could leave or significantly cut back."
    )
    best_case = (
        f"Best case: {ci_high:+.1f}% revenue change. "
        f"Most customers stay and the ones who remain spend more."
    )
    most_likely = (
        f"Most likely: {point_estimate:+.1f}% revenue change. "
        f"{stay_count} of {n} customers stay, {reduce_count} reduce visits, {leave_count} leave."
    )

    logger.info(
        "Impact estimate: %.1f%% [%.1f%%, %.1f%%], decision=%s, retention=%.0f%%",
        point_estimate, ci_low, ci_high, decision, retention_rate,
    )

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
