"""
Converts CustomerSegmentProfile into a PersonaGenerationManifest.

This is where the NeurIPS 2025 / ICLR 2024 findings are enforced:
structured demographic anchoring FIRST, narrative SECOND.

Every PersonaSpec has fixed structured fields that the LLM
cannot override. The LLM only adds narrative colour within
those constraints.
"""

import logging
import random
from dataclasses import dataclass, field

from backend.reviewer_intelligence.customer_segment_builder import (
    CustomerSegmentProfile,
    CustomerSegment,
)

logger = logging.getLogger(__name__)


@dataclass
class PersonaSpec:
    """Structured anchor for a single persona. Fixed before LLM generation."""
    segment: str
    age: int
    income_tier: str
    visit_frequency: str
    price_sensitivity: str
    is_silent_majority: bool
    is_tourist: bool
    is_reviewer_type: bool

    # Constraints for narrative generation
    must_include_traits: list[str] = field(default_factory=list)
    must_not_include_traits: list[str] = field(default_factory=list)


@dataclass
class PersonaGenerationManifest:
    persona_specs: list[PersonaSpec]
    total_count: int
    distribution_summary: str
    anti_bias_instructions: str
    diversity_requirements: str
    based_on: list[str]
    confidence: str
    key_caveats: list[str]


def _parse_age_range(age_range: str) -> tuple[int, int]:
    """Parse '25-45' into (25, 45)."""
    parts = age_range.replace(" ", "").split("-")
    try:
        return int(parts[0]), int(parts[1])
    except (IndexError, ValueError):
        return 25, 55


def _sample_age(age_range: str) -> int:
    lo, hi = _parse_age_range(age_range)
    return random.randint(lo, hi)


def calibrate_personas(
    profile: CustomerSegmentProfile,
    persona_count: int = 15,
) -> PersonaGenerationManifest:
    """Convert segment profile into a manifest of persona specs.

    Each persona is assigned to a segment proportionally, with structured
    anchor fields fixed before any LLM narrative generation.
    """

    specs: list[PersonaSpec] = []
    assigned_ages: list[int] = []

    # Assign personas to segments proportionally
    remaining = persona_count
    segment_counts: list[tuple[CustomerSegment, int]] = []

    for i, segment in enumerate(profile.segments):
        if i == len(profile.segments) - 1:
            count = remaining  # Last segment gets the rest
        else:
            count = max(1, round(segment.estimated_proportion * persona_count))
            count = min(count, remaining)
        remaining -= count
        remaining = max(remaining, 0)
        segment_counts.append((segment, count))

    # Build PersonaSpec for each assigned persona
    for segment, count in segment_counts:
        for _ in range(count):
            age = _sample_age(segment.age_range)
            assigned_ages.append(age)

            # Anti-optimism traits based on segment
            must_not = [
                "unusually enthusiastic about this type of business",
                "always positive about everything",
                "defines their identity through consuming this product or service",
            ]
            if segment.is_silent_majority:
                must_not.append("has ever written an online review")
                must_not.append("thinks in terms of star ratings")

            must_include = list(segment.key_decision_factors[:2])
            if segment.price_sensitivity in ("high", "moderate to high"):
                must_include.append("genuinely feels the difference between small price changes")

            specs.append(PersonaSpec(
                segment=segment.name,
                age=age,
                income_tier=segment.income_tier,
                visit_frequency=segment.visit_frequency,
                price_sensitivity=segment.price_sensitivity,
                is_silent_majority=segment.is_silent_majority,
                is_tourist="Tourist" in segment.name or "One-time" in segment.name,
                is_reviewer_type=not segment.is_silent_majority and segment.name != "Frustrated Customers",
                must_include_traits=must_include,
                must_not_include_traits=must_not,
            ))

    # Verify diversity
    age_span = max(assigned_ages) - min(assigned_ages) if assigned_ages else 0
    silent_count = sum(1 for s in specs if s.is_silent_majority)

    # Build distribution summary
    dist_lines = []
    for segment, count in segment_counts:
        pct = int(segment.estimated_proportion * 100)
        dist_lines.append(f"  {segment.name} ({pct}%): {count} {'person' if count == 1 else 'people'}")

    distribution = "\n".join(dist_lines)

    anti_bias = (
        "ANTI-BIAS INSTRUCTIONS (based on peer-reviewed research -- mandatory):\n"
        "1. This persona is NOT predisposed to be positive. They have realistic friction "
        "points, tight budgets, and competing priorities.\n"
        "2. Do not make this persona unusually engaged or enthusiastic about this business type.\n"
        "3. This persona has normal human inconsistency -- they do not always behave rationally.\n"
        "4. If price_sensitivity is 'high', this persona genuinely feels the difference "
        "between small price changes in their daily budget.\n"
        "5. If is_silent_majority is True, this persona has NEVER written a review in their "
        "life and does not think in terms of 'ratings.'\n"
        "6. This persona is a real person, not a customer archetype. Give them a life that "
        "extends well beyond this business."
    )

    diversity = (
        f"Age span in swarm: {age_span} years (target: 40+). "
        f"Silent majority: {silent_count}/{len(specs)} ({int(silent_count/max(len(specs),1)*100)}%). "
        "Must include mix of employed/self-employed/retired where demographically appropriate."
    )

    caveats = [
        "Persona distribution is based on review signals and bias corrections, not a census.",
        "Silent majority personas are estimates -- their actual behaviour can only be validated by comparing predictions to real outcomes.",
        profile.plain_english_summary,
    ]

    logger.info(
        "Persona manifest: %d specs, age_span=%d, silent_majority=%d/%d",
        len(specs), age_span, silent_count, len(specs),
    )

    return PersonaGenerationManifest(
        persona_specs=specs,
        total_count=len(specs),
        distribution_summary=distribution,
        anti_bias_instructions=anti_bias,
        diversity_requirements=diversity,
        based_on=profile.signals_used,
        confidence=profile.confidence_level,
        key_caveats=caveats,
    )
