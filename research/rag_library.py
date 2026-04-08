"""
Murmur RAG Library -- Research-grounded knowledge for simulations.

Provides cultural profiles, consumer psychology insights, and
domain-specific prompt fragments that get injected into every
simulation, persona generation, and twin query.
"""

import json
from pathlib import Path

RESEARCH_DIR = Path(__file__).parent


def get_country_profile(country_code: str) -> dict:
    """Returns Hofstede-based simulation modifiers for a given country.

    Used in every persona generation call to calibrate cultural context.
    Falls back to Western European defaults if country not found.
    """
    with open(RESEARCH_DIR / "processed/hofstede_scores.json") as f:
        scores = json.load(f)
    return scores.get(country_code.upper(), scores.get("DEFAULT", {}))


def get_domain_insights(domain: str) -> str:
    """Returns the prompt fragment for a given research domain.

    Available domains:
    - consumer_psychology
    - cultural_dimensions / country_profiles
    - behavioral_economics
    - review_bias
    - negotiation_psychology
    - personality_models
    - digital_twins
    - simulation_methodology
    - decision_making
    """
    path = RESEARCH_DIR / f"processed/prompts/{domain}.md"
    if path.exists():
        return path.read_text()
    return ""


def get_simulation_context(
    country_code: str,
    simulation_type: str = "consumer",
) -> str:
    """Assembles the full research context to inject into simulation prompts.

    Args:
        country_code: ISO 2-letter country code (e.g. "ES", "GB", "NL")
        simulation_type: "consumer" | "vendor" | "general"

    Returns:
        A ready-to-use string containing:
        - Country cultural profile (Hofstede-based adjustments)
        - Consumer psychology insights (loss aversion, anchoring, etc.)
        - Review bias correction rules
        - Simulation methodology calibration
        - Domain-specific context (vendor negotiation if applicable)
    """
    parts = []

    # Cultural context
    profile = get_country_profile(country_code)
    country_fragment = get_domain_insights("country_profiles")
    if country_fragment:
        parts.append(country_fragment)

    # Consumer psychology (always included)
    consumer = get_domain_insights("consumer_psychology")
    if consumer:
        parts.append(consumer)

    # Behavioral economics
    behavioral = get_domain_insights("behavioral_economics")
    if behavioral:
        parts.append(behavioral)

    # Review bias correction (always included)
    review = get_domain_insights("review_bias")
    if review:
        parts.append(review)

    # Personality models
    personality = get_domain_insights("personality_models")
    if personality:
        parts.append(personality)

    # Simulation methodology
    methodology = get_domain_insights("simulation_methodology")
    if methodology:
        parts.append(methodology)

    # Vendor-specific
    if simulation_type == "vendor":
        negotiation = get_domain_insights("negotiation_psychology")
        if negotiation:
            parts.append(negotiation)

    return "\n\n---\n\n".join(parts)


def get_persona_cultural_modifier(country_code: str) -> str:
    """Returns a short cultural modifier string for persona generation.

    This is a lightweight version of get_simulation_context for when
    the full research context would be too large.
    """
    profile = get_country_profile(country_code)
    if not profile:
        return ""

    sim = profile.get("simulation_profile", {})
    country = profile.get("country", "Unknown")
    ua = profile.get("uncertainty_avoidance", 50)

    lines = [
        f"Cultural context: {country}",
        f"Uncertainty avoidance: {'very high' if ua > 80 else 'high' if ua > 65 else 'moderate' if ua > 45 else 'low'} ({ua}/100)",
        f"Change resistance: {sim.get('change_resistance', 'moderate')}",
        f"Loyalty tendency: {sim.get('loyalty_tendency', 'moderate')}",
        f"Social proof sensitivity: {sim.get('social_proof_sensitivity', 'moderate')}",
        f"Price fairness sensitivity: {sim.get('price_fairness_sensitivity', 'moderate')}",
    ]
    return "\n".join(lines)


def list_available_domains() -> list[str]:
    """Returns list of domains that have prompt fragments available."""
    prompts_dir = RESEARCH_DIR / "processed/prompts"
    if not prompts_dir.exists():
        return []
    return [p.stem for p in prompts_dir.glob("*.md")]
