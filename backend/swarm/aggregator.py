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


async def aggregate_responses(
    business: BusinessSnapshot,
    question: str,
    persona_responses: List[dict],
    variant_a: str | None = None,
    variant_b: str | None = None,
    context_narrative: str | None = None,
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

    return {
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
        "raw_output": result,
    }
