"""
Persona Generator — builds N synthetic customer personas from a business profile.

Architecture inspired by:
- OASIS: SocialAgent initialization with UserInfo profiles
- Synthetic-user-research: OCEAN personality model integration
- CAMEL: System message construction patterns

Each persona is a unique, opinionated synthetic customer with OCEAN-derived
personality traits, specific behavioral quirks, and a relationship to the business.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from anthropic import AsyncAnthropic

from backend.config import get_settings
from backend.models.business import BusinessSnapshot
from backend.models.persona import PersonaProfile
from backend.reviewer_intelligence.persona_calibrator import (
    PersonaGenerationManifest,
    PersonaSpec,
)

logger = logging.getLogger(__name__)

PROMPT_DIR = Path(__file__).parent / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text()


def _build_generation_prompt(
    business: BusinessSnapshot,
    persona_count: int,
    uploaded_data_summary: str | None = None,
    context_narrative: str | None = None,
) -> str:
    """Build the persona generation prompt from template + business profile.

    Follows CAMEL's pattern of constructing system messages from templates
    with variable injection.
    """
    template = _load_prompt("persona_base.txt")

    # Simple template variable replacement
    prompt = template.replace("{{persona_count}}", str(persona_count))
    prompt = prompt.replace("{{business_name}}", business.name)
    prompt = prompt.replace("{{business_type}}", business.type)
    prompt = prompt.replace("{{business_description}}", business.description)
    prompt = prompt.replace(
        "{{customer_description}}", business.customer_description or "Not provided"
    )
    prompt = prompt.replace("{{location}}", business.location or "Not specified")

    # Handle optional uploaded data block
    if uploaded_data_summary:
        prompt = prompt.replace(
            "{{#if uploaded_data}}\n- Additional data: {{uploaded_data_summary}}\n{{/if}}",
            f"- Additional data: {uploaded_data_summary}",
        )
    else:
        prompt = prompt.replace(
            "{{#if uploaded_data}}\n- Additional data: {{uploaded_data_summary}}\n{{/if}}",
            "",
        )

    # Handle optional context narrative block
    if context_narrative:
        prompt = prompt.replace("{{context_narrative}}", context_narrative)
        prompt = prompt.replace("{{#if context_narrative}}", "")
        prompt = prompt.replace("{{/if}}", "")
    else:
        # Remove the entire context block
        import re
        prompt = re.sub(
            r"\{\{#if context_narrative\}\}.*?\{\{/if\}\}",
            "",
            prompt,
            flags=re.DOTALL,
        )

    return prompt


async def generate_personas(
    business: BusinessSnapshot,
    persona_count: int = 15,
    uploaded_data_summary: str | None = None,
    context_narrative: str | None = None,
    manifest: Optional[PersonaGenerationManifest] = None,
) -> List[PersonaProfile]:
    """Generate N diverse customer personas for a business.

    Two paths:
    1. If manifest is provided: generate personas constrained by PersonaSpecs
       (structured anchor fixed, narrative added by LLM). This is the
       research-grounded path from the Reviewer Intelligence System.
    2. If no manifest: freeform generation from business profile (legacy path).
    """
    if manifest is not None:
        return await _generate_from_manifest(business, manifest)
    return await _generate_freeform(business, persona_count, uploaded_data_summary, context_narrative)


async def _generate_freeform(
    business: BusinessSnapshot,
    persona_count: int,
    uploaded_data_summary: str | None,
    context_narrative: str | None,
) -> List[PersonaProfile]:
    """Legacy freeform generation -- single API call, no structured anchoring."""
    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    prompt = _build_generation_prompt(business, persona_count, uploaded_data_summary, context_narrative)

    logger.info("Generating %d personas (freeform) for '%s'", persona_count, business.name)

    response = await client.messages.create(
        model=settings.model_name,
        max_tokens=4096,
        system="You are a customer persona generator. Return valid JSON only -- an array of persona objects. No markdown, no explanation, just the JSON array.",
        messages=[{"role": "user", "content": prompt}],
    )

    return _parse_personas_response(response.content[0].text)


async def _generate_from_manifest(
    business: BusinessSnapshot,
    manifest: PersonaGenerationManifest,
) -> List[PersonaProfile]:
    """Research-grounded generation: structured anchor first, narrative second.

    Based on NeurIPS 2025 / ICLR 2024: structured demographic anchoring
    produces more accurate personas than freeform creative generation.

    Sends all specs in a single API call for efficiency.
    """
    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    logger.info(
        "Generating %d personas (manifest-constrained) for '%s'",
        manifest.total_count, business.name,
    )

    # Build a batch prompt with all specs
    spec_descriptions = []
    for i, spec in enumerate(manifest.persona_specs):
        spec_descriptions.append(
            f"PERSONA {i+1}:\n"
            f"  Segment: {spec.segment}\n"
            f"  Age: {spec.age}\n"
            f"  Income tier: {spec.income_tier}\n"
            f"  Visit frequency: {spec.visit_frequency}\n"
            f"  Price sensitivity: {spec.price_sensitivity}\n"
            f"  Is silent majority: {spec.is_silent_majority}\n"
            f"  Is tourist: {spec.is_tourist}\n"
            f"  Must include traits: {', '.join(spec.must_include_traits)}\n"
            f"  Must NOT include: {', '.join(spec.must_not_include_traits)}"
        )

    template = _load_prompt("persona_from_spec.txt")

    # Inject business details
    prompt = template.replace("{{business_name}}", business.name)
    prompt = prompt.replace("{{business_type}}", business.type)
    prompt = prompt.replace("{{business_description}}", business.description)
    prompt = prompt.replace("{{location}}", business.location or "Not specified")

    # Replace single-spec placeholders with batch instruction
    batch_instruction = (
        f"Generate {manifest.total_count} personas, one for each spec below. "
        f"Return a JSON ARRAY of {manifest.total_count} objects.\n\n"
        f"DISTRIBUTION:\n{manifest.distribution_summary}\n\n"
        + "\n\n".join(spec_descriptions)
    )

    # Replace template placeholders with batch content
    for placeholder in ["{{segment}}", "{{age}}", "{{income_tier}}", "{{visit_frequency}}",
                        "{{price_sensitivity}}", "{{is_silent_majority}}", "{{is_tourist}}",
                        "{{must_include_traits}}", "{{must_not_include_traits}}"]:
        prompt = prompt.replace(placeholder, "")

    prompt = prompt.replace("{{anti_bias_instructions}}", manifest.anti_bias_instructions)

    # Append the batch specs after the template
    prompt += "\n\n" + batch_instruction

    response = await client.messages.create(
        model=settings.model_name,
        max_tokens=8192,
        system=(
            f"You are generating {manifest.total_count} customer personas for a business "
            "simulation. Each persona has a FIXED structured profile that you must not "
            "override. Add realistic narrative detail within those constraints. "
            "Return a JSON array. No markdown, no explanation."
        ),
        messages=[{"role": "user", "content": prompt}],
    )

    personas = _parse_personas_response(response.content[0].text)

    # Overlay structured anchor fields from specs onto parsed personas
    # This ensures the LLM cannot override the fixed fields
    for i, persona in enumerate(personas):
        if i < len(manifest.persona_specs):
            spec = manifest.persona_specs[i]
            persona.age = spec.age
            persona.visit_frequency = spec.visit_frequency

    logger.info("Generated %d personas (manifest-constrained) successfully", len(personas))
    return personas


def _parse_personas_response(raw_text: str) -> List[PersonaProfile]:
    """Parse Claude's JSON response into PersonaProfile objects."""
    try:
        personas_data = json.loads(raw_text)
    except json.JSONDecodeError:
        if "```" in raw_text:
            json_str = raw_text.split("```")[1]
            if json_str.startswith("json"):
                json_str = json_str[4:]
            personas_data = json.loads(json_str.strip())
        else:
            raise ValueError(f"Failed to parse persona JSON: {raw_text[:200]}")

    personas = []
    for p in personas_data:
        personality = p.get("personality", "")
        if isinstance(personality, list):
            personality = ", ".join(str(t) for t in personality)

        relationship = p.get("relationship_to_business", "")
        if isinstance(relationship, list):
            relationship = ". ".join(str(t) for t in relationship)

        persona = PersonaProfile(
            name=p.get("name", "Unknown"),
            age=p.get("age", 30),
            occupation=p.get("occupation", "Unknown"),
            visit_frequency=p.get("visit_frequency", "Unknown"),
            avg_spend=float(p.get("avg_spend", 0)),
            personality=personality,
            relationship_to_business=relationship,
            quirk=p.get("quirk", ""),
            openness=p.get("openness"),
            conscientiousness=p.get("conscientiousness"),
            extraversion=p.get("extraversion"),
            agreeableness=p.get("agreeableness"),
            neuroticism=p.get("neuroticism"),
        )
        personas.append(persona)

    return personas
