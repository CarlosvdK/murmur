"""
Aggregator — synthesises N persona responses into a human-readable output.

Architecture inspired by:
- Synthetic-user-research: SummaryAgent pattern — feed full transcript,
  produce structured findings with pain points and recommendations
- CAMEL: Structured output patterns
- MiroFish: Report generation with sections (headline, themes, standout voices)

The aggregator is the voice of Murmur. It must NEVER sound like an AI report.
It must sound like a trusted advisor who just finished talking to real customers.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from anthropic import AsyncAnthropic

from backend.config import get_settings
from backend.models.business import BusinessSnapshot

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
        return prompt.replace("{{/if}}", "", 1) if "{{/if}}" in prompt else prompt
    else:
        pattern = re.escape(tag_open) + r".*?" + re.escape("{{/if}}")
        return re.sub(pattern, "", prompt, count=1, flags=re.DOTALL)


def _build_aggregation_prompt(
    business: BusinessSnapshot,
    question: str,
    persona_responses: List[dict],
    variant_a: str | None = None,
    variant_b: str | None = None,
    context_narrative: str | None = None,
) -> str:
    """Build the aggregation prompt from template + all persona responses."""
    template = _load_prompt("aggregation.txt")

    prompt = template.replace("{{business_name}}", business.name)
    prompt = prompt.replace("{{business_type}}", business.type)
    prompt = prompt.replace("{{business_description}}", business.description)
    prompt = prompt.replace("{{question}}", question)
    prompt = prompt.replace("{{response_count}}", str(len(persona_responses)))
    prompt = prompt.replace(
        "{{persona_responses_json}}",
        json.dumps(persona_responses, indent=2),
    )

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


def _apply_confidence_cap(
    result: dict,
    business: BusinessSnapshot,
    persona_responses: List[dict],
    context_narrative: str | None,
    expected_persona_count: int | None = None,
) -> dict:
    """Downgrade the LLM-declared confidence when structural conditions fail.

    The aggregator prompt asks Claude to follow a rubric, but LLMs drift
    toward "high" when the narrative reads confident. This pass re-checks
    the hard conditions and caps confidence if any fail. It NEVER upgrades
    confidence -- it only caps.

    Conditions that force a cap to at most "medium":
    - Business profile is thin (description OR customer_description < 100
      chars, or missing).
    - Fewer than 60% of personas produced a reaction.
    - Context narrative is empty or very short.

    Conditions that force a cap to "low":
    - Fewer than 40% of personas produced a reaction.
    - Both business description and customer description are empty.
    """
    current = (result.get("confidence_score") or "medium").lower()
    rank = {"low": 0, "medium": 1, "high": 2}
    cap = rank.get(current, 1)
    reasons: List[str] = []

    desc = (business.description or "").strip()
    cust = (getattr(business, "customer_description", "") or "").strip()
    thin_profile = len(desc) < 100 or len(cust) < 100
    missing_profile = not desc and not cust

    expected = expected_persona_count or max(len(persona_responses), 1)
    success_rate = len(persona_responses) / expected if expected else 0

    ctx_chars = len(context_narrative or "")

    if missing_profile or success_rate < 0.40:
        cap = min(cap, 0)
        if missing_profile:
            reasons.append("business profile is missing")
        if success_rate < 0.40:
            reasons.append(f"only {int(success_rate*100)}% of personas produced a reaction")
    else:
        if thin_profile:
            cap = min(cap, 1)
            reasons.append("business/customer description is thin")
        if success_rate < 0.60:
            cap = min(cap, 1)
            reasons.append(f"only {int(success_rate*100)}% of personas succeeded")
        if ctx_chars < 400:
            cap = min(cap, 1)
            reasons.append("real-world context is sparse")

    new_level = {0: "low", 1: "medium", 2: "high"}[cap]
    if rank.get(current, 1) > cap:
        logger.info(
            "Confidence capped: %s -> %s. Reasons: %s",
            current, new_level, "; ".join(reasons),
        )
        result["confidence_score"] = new_level
        existing_reason = (result.get("confidence_reasoning") or "").strip()
        cap_note = "Capped to " + new_level + " because " + "; ".join(reasons) + "."
        result["confidence_reasoning"] = (
            cap_note if not existing_reason else f"{existing_reason} {cap_note}"
        )
        result["confidence_capped"] = True
        result["confidence_cap_reasons"] = reasons
    return result


async def aggregate_responses(
    business: BusinessSnapshot,
    question: str,
    persona_responses: List[dict],
    variant_a: str | None = None,
    variant_b: str | None = None,
    context_narrative: str | None = None,
    expected_persona_count: int | None = None,
) -> dict:
    """Synthesise all persona responses into a structured result.

    Returns a dict matching the SimulationResult schema:
    - headline (summary)
    - themes[]
    - standout_voices[]
    - confidence + reasoning
    - recommendation
    - winner + winner_reasoning (for A/B)
    """
    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    prompt = _build_aggregation_prompt(
        business, question, persona_responses, variant_a, variant_b, context_narrative
    )

    logger.info(
        "Aggregating %d responses for question: '%s'",
        len(persona_responses), question[:80]
    )

    response = await client.messages.create(
        model=settings.model_name,
        max_tokens=2048,
        system=(
            "You are a customer insight synthesiser for small businesses. "
            "Return valid JSON only — no markdown, no explanation. "
            "Write like a trusted advisor, not an AI. Use customer names. "
            "Never say 'based on the simulation' or 'our AI suggests'."
        ),
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        if "```" in raw_text:
            json_str = raw_text.split("```")[1]
            if json_str.startswith("json"):
                json_str = json_str[4:]
            result = json.loads(json_str.strip())
        else:
            raise ValueError(f"Failed to parse aggregation JSON: {raw_text[:200]}")

    logger.info(
        "Aggregation complete — confidence: %s", result.get("confidence", "unknown")
    )

    out = {
        "summary": result.get("headline", ""),
        "recommendation": result.get("recommendation", ""),
        "confidence_score": result.get("confidence", "medium"),
        "confidence_reasoning": (
            result["confidence"]
            if isinstance(result.get("confidence"), str)
            else result.get("confidence_reasoning", "")
        ),
        "winner": result.get("winner"),
        "winner_reasoning": result.get("winner_reasoning"),
        "themes": result.get("themes", []),
        "standout_voices": result.get("standout_voices", []),
        # Focus group data (Phase 5)
        "baseline_summary": result.get("baseline_summary"),
        "behavioral_prediction": result.get("behavioral_prediction"),
        "stated_vs_actual_gap": result.get("stated_vs_actual_gap"),
        "raw_output": result,
    }

    # Apply the structural confidence cap. The LLM may claim "high" when
    # the profile is thin or many personas failed -- cap it here.
    out = _apply_confidence_cap(
        out, business, persona_responses, context_narrative,
        expected_persona_count=expected_persona_count,
    )
    return out
