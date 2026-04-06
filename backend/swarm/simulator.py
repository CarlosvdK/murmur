"""
Simulator — runs a question through all personas in parallel.

Architecture inspired by:
- OASIS: Interview Action pattern with asyncio.Semaphore for rate limiting,
  asyncio.gather() for parallel execution, graceful failure handling
- CAMEL: ChatAgent step() pattern — system message + user message → response
- Synthetic-user-research: Researcher-persona interview flow

Each persona is interviewed independently (no cross-contamination) to avoid
the herd mentality bias identified in synthetic user research.
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import List, Optional, Callable

from anthropic import AsyncAnthropic

from backend.config import get_settings
from backend.models.business import BusinessSnapshot
from backend.models.persona import PersonaProfile, PersonaResponse
from backend.models.simulation import SimulationProgress

logger = logging.getLogger(__name__)

PROMPT_DIR = Path(__file__).parent / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text()


def _handle_conditional_block(prompt: str, block_name: str, include: bool) -> str:
    """Include or remove a {{#if block_name}}...{{/if}} conditional block."""
    import re
    tag_open = "{{#if " + block_name + "}}"
    if include:
        prompt = prompt.replace(tag_open, "")
        # Only remove the FIRST {{/if}} after where the tag was
        # Use a targeted approach: find tag position, then next {{/if}}
        return prompt.replace("{{/if}}", "", 1) if "{{/if}}" in prompt else prompt
    else:
        pattern = re.escape(tag_open) + r".*?" + re.escape("{{/if}}")
        return re.sub(pattern, "", prompt, count=1, flags=re.DOTALL)


def _build_interview_prompt(
    persona: PersonaProfile,
    business: BusinessSnapshot,
    question: str,
    variant_a: str | None = None,
    variant_b: str | None = None,
    context_narrative: str | None = None,
) -> str:
    """Build the interview prompt for a single persona."""
    template = _load_prompt("persona_interview.txt")

    prompt = template.replace("{{persona_name}}", persona.name)
    prompt = prompt.replace("{{persona_age}}", str(persona.age))
    prompt = prompt.replace("{{persona_occupation}}", persona.occupation)
    prompt = prompt.replace("{{business_name}}", business.name)
    prompt = prompt.replace("{{business_type}}", business.type)
    prompt = prompt.replace("{{business_description}}", business.description)
    prompt = prompt.replace("{{visit_frequency}}", persona.visit_frequency)
    prompt = prompt.replace("{{avg_spend}}", str(persona.avg_spend))
    prompt = prompt.replace("{{personality}}", persona.personality)
    prompt = prompt.replace(
        "{{relationship_to_business}}", persona.relationship_to_business
    )
    prompt = prompt.replace("{{quirk}}", persona.quirk)
    prompt = prompt.replace("{{question}}", question)

    # Handle context narrative block
    if context_narrative:
        prompt = prompt.replace("{{context_narrative}}", context_narrative)
    prompt = _handle_conditional_block(prompt, "context_narrative", bool(context_narrative))

    # Handle A/B variant blocks
    if variant_a and variant_b:
        prompt = prompt.replace("{{variant_a}}", variant_a)
        prompt = prompt.replace("{{variant_b}}", variant_b)
    prompt = _handle_conditional_block(prompt, "variant_a", bool(variant_a and variant_b))

    return prompt


async def _interview_persona(
    client: AsyncAnthropic,
    semaphore: asyncio.Semaphore,
    persona: PersonaProfile,
    business: BusinessSnapshot,
    question: str,
    variant_a: str | None,
    variant_b: str | None,
    model: str,
    context_narrative: str | None = None,
) -> dict:
    """Interview a single persona — protected by semaphore.

    Mirrors OASIS's _perform_interview_action pattern:
    async with semaphore → call LLM → return result.
    """
    async with semaphore:
        prompt = _build_interview_prompt(
            persona, business, question, variant_a, variant_b, context_narrative
        )

        logger.info("Interviewing persona: %s (age %d)", persona.name, persona.age)

        response = await client.messages.create(
            model=model,
            max_tokens=1024,
            system=(
                f"You are {persona.name}, a {persona.age}-year-old {persona.occupation}. "
                f"Stay completely in character. Return valid JSON only — no markdown, no explanation."
            ),
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = response.content[0].text

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            if "```" in raw_text:
                json_str = raw_text.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                data = json.loads(json_str.strip())
            else:
                # Fallback: extract what we can
                data = {
                    "reaction": raw_text[:500],
                    "reasoning": "Failed to parse structured response",
                    "sentiment": 0.0,
                }

        return {
            "persona_name": persona.name,
            "reaction": data.get("reaction", ""),
            "reasoning": data.get("reasoning", ""),
            "sentiment": float(data.get("sentiment", 0.0)),
            "preference": data.get("preference"),
            "preference_strength": data.get("preference_strength"),
            "raw": data,
        }


async def run_simulation(
    personas: List[PersonaProfile],
    business: BusinessSnapshot,
    question: str,
    variant_a: str | None = None,
    variant_b: str | None = None,
    on_progress: Optional[Callable[[str, int], None]] = None,
    context_narrative: str | None = None,
) -> List[dict]:
    """Run the question through all personas in parallel.

    Uses OASIS's pattern:
    - asyncio.Semaphore to limit concurrent API calls
    - asyncio.gather(*tasks, return_exceptions=True) for parallel execution
    - Filter successes, log failures, continue if >60% succeed

    The on_progress callback fires after each persona completes,
    enabling MiroFish-style live progress updates.
    """
    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    semaphore = asyncio.Semaphore(settings.concurrency_limit)

    start_time = time.monotonic()
    completed_count = 0

    async def interview_with_progress(persona: PersonaProfile) -> dict:
        nonlocal completed_count
        result = await _interview_persona(
            client, semaphore, persona, business, question,
            variant_a, variant_b, settings.model_name, context_narrative
        )
        completed_count += 1
        if on_progress:
            on_progress(persona.name, completed_count)
        return result

    logger.info(
        "Starting simulation: %d personas, question='%s'",
        len(personas), question[:80]
    )

    # Fire all interviews in parallel (semaphore limits concurrency)
    results = await asyncio.gather(
        *[interview_with_progress(p) for p in personas],
        return_exceptions=True,
    )

    # Separate successes from failures
    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]

    elapsed = time.monotonic() - start_time
    logger.info(
        "Simulation complete: %d/%d succeeded in %.1fs",
        len(successes), len(personas), elapsed
    )

    for f in failures:
        logger.error("Persona interview failed: %s", str(f))

    # Minimum threshold: 60% must succeed
    min_required = int(len(personas) * 0.6)
    if len(successes) < min_required:
        raise RuntimeError(
            f"Too many persona failures: {len(successes)}/{len(personas)} succeeded "
            f"(minimum {min_required} required)"
        )

    return successes
