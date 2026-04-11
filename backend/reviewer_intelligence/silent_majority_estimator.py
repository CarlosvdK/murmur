"""
Explicitly models the customers who leave no reviews.

Research basis (Gao et al. 2015, MIS Quarterly):
The silent majority has opinions -- they just lack motivation to express them.
Their BEHAVIOUR (returning or not, switching or staying) drives actual business
outcomes. The vocal minority controls perception. The silent majority controls results.

This is Murmur's key differentiator: every other tool analyses who IS talking.
Murmur explicitly models who ISN'T.
"""

import logging
from dataclasses import dataclass

from backend.reviewer_intelligence.bias_corrector import BiasAdjustedSignals

logger = logging.getLogger(__name__)


@dataclass
class SilentMajorityProfile:
    estimated_size_vs_reviewers: str
    estimated_satisfaction: str
    estimated_price_sensitivity: str
    estimated_loyalty: str
    estimated_switching_risk: str
    recommended_swarm_proportion: float  # 0.55 to 0.70
    persona_guidance: str
    confidence_note: str


def estimate_silent_majority(
    adjusted: BiasAdjustedSignals,
    tourist_ratio: float = 0.3,
) -> SilentMajorityProfile:
    """Build a profile of who ISN'T in the reviews.

    The silent majority:
    - Satisfaction: slightly below positive reviewers (positive reviewers inflate perception)
    - Price sensitivity: HIGHER than reviewers suggest (price-sensitive people just stop coming)
    - Loyalty: LOWER than reviewers suggest (loyal customers over-review)
    - Switching: HIGHER than reviewers suggest (silent leavers don't announce departure)
    """

    # Base proportion: 55-70% of swarm should be silent majority
    # Adjust based on tourist ratio (tourists = more transient silent customers)
    base_proportion = 0.60
    if tourist_ratio > 0.5:
        base_proportion = 0.55  # Slightly less -- tourists are accounted for separately
    elif tourist_ratio < 0.15:
        base_proportion = 0.65  # More local = more silent regulars

    # Satisfaction estimate
    raw_avg = adjusted.raw_signals.average_rating
    if raw_avg >= 4.0:
        satisfaction = "moderately positive -- satisfied enough to keep coming but not enthusiastic enough to review"
    elif raw_avg >= 3.0:
        satisfaction = "lukewarm -- they come out of habit or convenience, not passion"
    else:
        satisfaction = "mixed to negative -- many may be actively looking for alternatives"

    # Price sensitivity -- always higher than reviewers suggest
    price_sensitivity = "higher than reviews suggest"
    if adjusted.raw_signals.price_mention_frequency > 0.3:
        price_sensitivity = "significantly higher than reviews suggest -- price is already a frequent complaint among the vocal minority"

    # Loyalty -- always lower than reviewers suggest
    loyalty = "lower than reviews suggest -- many come because it is convenient, not because they love it"
    if adjusted.raw_signals.loyalty_signal_frequency > 0.3:
        loyalty = "moderate -- some genuine loyalty exists but silent customers are less committed than the regulars who review"

    # Switching risk
    switching = "higher than reviews suggest -- silent customers leave without warning"
    if adjusted.raw_signals.switching_signal_frequency > 0.15:
        switching = "elevated -- even vocal customers are mentioning competitors, silent ones are likely already trying them"

    guidance = (
        f"Generate {int(base_proportion * 100)}% of the swarm as silent majority personas. "
        "These people have NEVER written a review or posted feedback online. They do not "
        "think in terms of star ratings or NPS scores. They are moderately satisfied but "
        "not enthusiastic. They are more price-sensitive than the vocal minority suggests. "
        "They would not describe themselves as 'loyal customers' even if they engage "
        "regularly -- it is just part of their routine or default behavior. "
        "When asked about a change, they will not say 'I understand why you need to do this.' "
        "They will say 'Hmm, that is a bit much' or 'I might look at other options.' "
        "Their responses should be shorter, less articulate, and more gut-reaction than "
        "the enthusiastic reviewers. They are busy people with limited attention for any "
        "single business or service in their life."
    )

    confidence = (
        "This is an estimate based on industry research and the business's review patterns. "
        "The only way to validate it is to compare predictions to actual outcomes over time."
    )

    logger.info(
        "Silent majority estimate: %.0f%% proportion, price_sensitivity=%s",
        base_proportion * 100, price_sensitivity,
    )

    return SilentMajorityProfile(
        estimated_size_vs_reviewers=adjusted.silent_majority_size_vs_reviewers,
        estimated_satisfaction=satisfaction,
        estimated_price_sensitivity=price_sensitivity,
        estimated_loyalty=loyalty,
        estimated_switching_risk=switching,
        recommended_swarm_proportion=base_proportion,
        persona_guidance=guidance,
        confidence_note=confidence,
    )
