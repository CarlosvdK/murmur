"""
Simulator — runs a question through all personas in parallel.

Architecture inspired by:
- OASIS: Interview Action pattern with asyncio.Semaphore for rate limiting,
  asyncio.gather() for parallel execution, graceful failure handling
- CAMEL: ChatAgent step() pattern — system message + user message → response
- Synthetic-user-research: Researcher-persona interview flow

Each persona is interviewed independently (no cross-contamination) to avoid
the herd mentality bias identified in synthetic user research.

Supports two interview modes:
- Single-shot: one prompt, one response (original behavior)
- Focus group: 3-turn multi-turn interview (warmup, core, depth) using a
  single Claude conversation for richer, more consistent persona responses.
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
    prompt = prompt.replace("{{visit_frequency}}", persona.engagement_pattern)
    prompt = prompt.replace("{{avg_spend}}", persona.spend_model)
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


# ---------------------------------------------------------------------------
# Focus group prompt builders (multi-turn interview)
# ---------------------------------------------------------------------------


def _build_warmup_prompt(
    business: BusinessSnapshot,
) -> str:
    """Build Turn 1 (warmup) prompt from interview_turn1_warmup.txt."""
    template = _load_prompt("interview_turn1_warmup.txt")
    prompt = template.replace("{{business_name}}", business.name)
    return prompt


def _build_core_prompt(
    question: str,
    variant_a: str | None = None,
    variant_b: str | None = None,
) -> str:
    """Build Turn 2 (core) prompt from interview_turn2_core.txt."""
    template = _load_prompt("interview_turn2_core.txt")
    prompt = template.replace("{{question}}", question)

    # Handle A/B variant blocks
    if variant_a and variant_b:
        prompt = prompt.replace("{{variant_a}}", variant_a)
        prompt = prompt.replace("{{variant_b}}", variant_b)
    prompt = _handle_conditional_block(prompt, "variant_a", bool(variant_a and variant_b))

    return prompt


def _build_depth_prompt() -> str:
    """Build Turn 3 (depth) prompt from interview_turn3_depth.txt."""
    return _load_prompt("interview_turn3_depth.txt")


def _build_ab_compare_prompt(question: str) -> str:
    """Build Turn 4 (A/B comparison) prompt from interview_ab_compare.txt.

    Only used for non-A/B questions (no explicit variant_a/variant_b) to
    compare the proposed change against the status quo.
    """
    template = _load_prompt("interview_ab_compare.txt")
    return template.replace("{{question}}", question)


# ---------------------------------------------------------------------------
# JSON response parsing
# ---------------------------------------------------------------------------


def _parse_json_response(raw_text: str, turn_label: str = "") -> dict:
    """Parse a JSON response from Claude, with markdown-fence fallback.

    Uses the same error-handling pattern as the original _interview_persona.
    Returns a dict -- on total failure, returns a minimal fallback dict.
    """
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    # Fallback: try extracting from markdown code fence
    if "```" in raw_text:
        try:
            json_str = raw_text.split("```")[1]
            if json_str.startswith("json"):
                json_str = json_str[4:]
            return json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError):
            pass

    # Total failure -- return what we can
    label = f" ({turn_label})" if turn_label else ""
    logger.warning("Failed to parse JSON from response%s, using raw text fallback", label)
    return {
        "raw_text": raw_text[:500],
        "_parse_error": f"Could not parse JSON{label}",
    }


# ---------------------------------------------------------------------------
# Single-shot interview (original, unchanged)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Multi-turn focus group interview
# ---------------------------------------------------------------------------


async def _interview_persona_focus_group(
    client: AsyncAnthropic,
    semaphore: asyncio.Semaphore,
    persona: PersonaProfile,
    business: BusinessSnapshot,
    question: str,
    variant_a: str | None,
    variant_b: str | None,
    model: str,
    context_narrative: str | None = None,
    on_turn_progress: Optional[Callable[[str, str], None]] = None,
    ab_compare: bool = True,
) -> dict:
    """Conduct a multi-turn focus group interview with a single persona.

    The entire interview is one atomic operation -- the semaphore is acquired
    once and held for all turns. This keeps the conversation coherent and
    avoids interleaving turns with other personas under rate limiting.

    Turns:
        1. Warmup  -- establish current relationship with the business
        2. Core    -- present the question / change and get reaction
        3. Depth   -- forward-looking behavioral prediction
        4. A/B Compare (optional) -- compare change vs status quo
           Only runs when ab_compare=True AND the question is NOT already
           an explicit A/B comparison (variant_a and variant_b are both None).

    Returns a dict with per-turn data plus backward-compatible top-level
    fields (reaction, reasoning, sentiment, preference, preference_strength)
    extracted from the core turn.
    """
    system = (
        f"You are {persona.name}, a {persona.age}-year-old {persona.occupation}. "
        f"Stay completely in character. Return valid JSON only -- no markdown, no explanation."
    )

    # context_narrative is reserved for future use in the warmup template;
    # currently unused but accepted to match the _interview_persona interface.
    _ = context_narrative

    warmup_prompt = _build_warmup_prompt(business)
    core_prompt = _build_core_prompt(question, variant_a, variant_b)
    depth_prompt = _build_depth_prompt()

    async with semaphore:
        # -- Turn 1: Warmup --------------------------------------------------
        logger.info("Interviewing persona: %s (turn 1)", persona.name)
        if on_turn_progress:
            on_turn_progress(persona.name, "warmup")

        messages = [{"role": "user", "content": warmup_prompt}]

        t1 = await client.messages.create(
            model=model,
            max_tokens=512,
            system=system,
            messages=messages,
        )
        t1_text = t1.content[0].text
        warmup_data = _parse_json_response(t1_text, "turn 1 warmup")

        # -- Turn 2: Core ----------------------------------------------------
        logger.info("Interviewing persona: %s (turn 2)", persona.name)
        if on_turn_progress:
            on_turn_progress(persona.name, "core")

        messages.append({"role": "assistant", "content": t1_text})
        messages.append({"role": "user", "content": core_prompt})

        t2 = await client.messages.create(
            model=model,
            max_tokens=768,
            system=system,
            messages=messages,
        )
        t2_text = t2.content[0].text
        core_data = _parse_json_response(t2_text, "turn 2 core")

        # -- Turn 3: Depth ---------------------------------------------------
        logger.info("Interviewing persona: %s (turn 3)", persona.name)
        if on_turn_progress:
            on_turn_progress(persona.name, "depth")

        messages.append({"role": "assistant", "content": t2_text})
        messages.append({"role": "user", "content": depth_prompt})

        t3 = await client.messages.create(
            model=model,
            max_tokens=512,
            system=system,
            messages=messages,
        )
        t3_text = t3.content[0].text
        depth_data = _parse_json_response(t3_text, "turn 3 depth")

        # -- Turn 4: A/B Comparison (optional) ---------------------------------
        ab_comparison_data = None
        if ab_compare and variant_a is None and variant_b is None:
            logger.info("Interviewing persona: %s (turn 4 ab_compare)", persona.name)
            if on_turn_progress:
                on_turn_progress(persona.name, "ab_compare")

            ab_compare_prompt = _build_ab_compare_prompt(question)
            messages.append({"role": "assistant", "content": t3_text})
            messages.append({"role": "user", "content": ab_compare_prompt})

            t4 = await client.messages.create(
                model=model,
                max_tokens=512,
                system=system,
                messages=messages,
            )
            t4_text = t4.content[0].text
            ab_comparison_data = _parse_json_response(t4_text, "turn 4 ab_compare")

    # -- Assemble result ------------------------------------------------------
    # Top-level sentiment comes from the core turn for backward compat with
    # the impact estimator.
    sentiment_raw = core_data.get("sentiment", 0.0)
    try:
        sentiment = float(sentiment_raw)
    except (TypeError, ValueError):
        sentiment = 0.0

    result = {
        "persona_name": persona.name,
        # Per-turn data
        "warmup": warmup_data,
        "core": core_data,
        "depth": depth_data,
        # Backward-compatible top-level fields (from core turn)
        "reaction": core_data.get("reaction", ""),
        "reasoning": core_data.get("reasoning", ""),
        "sentiment": sentiment,
        "preference": core_data.get("preference"),
        "preference_strength": core_data.get("preference_strength"),
    }

    if ab_comparison_data is not None:
        result["ab_comparison"] = ab_comparison_data

    return result


# ---------------------------------------------------------------------------
# Simulation runner
# ---------------------------------------------------------------------------


async def run_simulation(
    personas: List[PersonaProfile],
    business: BusinessSnapshot,
    question: str,
    variant_a: str | None = None,
    variant_b: str | None = None,
    on_progress: Optional[Callable[[str, int], None]] = None,
    context_narrative: str | None = None,
    focus_group: bool = True,
    ab_compare: bool = True,
) -> List[dict]:
    """Run the question through all personas in parallel.

    Uses OASIS's pattern:
    - asyncio.Semaphore to limit concurrent API calls
    - asyncio.gather(*tasks, return_exceptions=True) for parallel execution
    - Filter successes, log failures, continue if >60% succeed

    The on_progress callback fires after each persona completes,
    enabling MiroFish-style live progress updates.

    When focus_group=True (default), each persona goes through a 3-turn
    multi-turn interview (warmup -> core -> depth). When False, uses the
    original single-shot interview for backward compatibility.
    """
    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    semaphore = asyncio.Semaphore(settings.concurrency_limit)

    start_time = time.monotonic()
    completed_count = 0

    async def interview_with_progress(persona: PersonaProfile) -> dict:
        nonlocal completed_count

        if focus_group:
            def turn_progress(name: str, turn: str) -> None:
                if on_progress:
                    on_progress(f"{name} ({turn})", completed_count)

            result = await _interview_persona_focus_group(
                client, semaphore, persona, business, question,
                variant_a, variant_b, settings.model_name, context_narrative,
                on_turn_progress=turn_progress,
                ab_compare=ab_compare,
            )
        else:
            result = await _interview_persona(
                client, semaphore, persona, business, question,
                variant_a, variant_b, settings.model_name, context_narrative,
            )

        completed_count += 1
        if on_progress:
            on_progress(persona.name, completed_count)
        return result

    mode_label = "focus group" if focus_group else "single-shot"
    logger.info(
        "Starting simulation (%s): %d personas, question='%s'",
        mode_label, len(personas), question[:80]
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
