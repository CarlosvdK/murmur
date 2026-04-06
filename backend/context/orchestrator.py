"""
The Orchestrator decides which context tools to run for a given simulation.

It makes a single Claude API call that reasons about the business and question,
then returns a structured plan of tool calls with specific parameters.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable

from anthropic import AsyncAnthropic

from backend.config import get_settings
from backend.context.tools import get_tool_descriptions
from backend.models.business import BusinessSnapshot

logger = logging.getLogger(__name__)

PROMPT_DIR = Path(__file__).parent / "prompts"


@dataclass
class ToolCall:
    name: str
    hints: dict = field(default_factory=dict)
    reasoning: str = ""
    priority: int = 2


@dataclass
class ResearchPlan:
    tool_calls: list[ToolCall]
    reasoning: str = ""
    hypothesis: str = ""


def _load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text()


def _parse_json(raw: str) -> dict:
    """Parse JSON from Claude response, stripping markdown fences if present."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


async def plan_research(
    business: BusinessSnapshot,
    question: str,
    on_progress: Optional[Callable[[str], None]] = None,
) -> ResearchPlan:
    """Ask Claude to decide which tools to run and why.

    Returns a ResearchPlan. If the orchestrator call fails, returns
    an empty plan so the pipeline can continue without context.
    """
    settings = get_settings()

    if on_progress:
        on_progress("Planning research strategy...")

    tool_descs = get_tool_descriptions(settings)

    if not tool_descs:
        logger.info("No context tools available (no API keys configured)")
        if on_progress:
            on_progress("No research tools available -- proceeding with business profile only")
        return ResearchPlan(tool_calls=[], reasoning="No tools available")

    system_prompt = _load_prompt("orchestrator.txt")

    business_profile = {
        "name": business.name,
        "type": business.type,
        "description": business.description,
        "customer_description": business.customer_description or "Not provided",
        "location": business.location or "Not specified",
    }

    user_message = (
        f"BUSINESS PROFILE:\n{json.dumps(business_profile, indent=2)}\n\n"
        f"QUESTION:\n{question}\n\n"
        f"AVAILABLE TOOLS:\n{json.dumps(tool_descs, indent=2)}"
    )

    try:
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await client.messages.create(
            model=settings.model_name,
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        plan_dict = _parse_json(response.content[0].text)

        tool_calls = []
        for tc in plan_dict.get("tools", []):
            tool_calls.append(ToolCall(
                name=tc["name"],
                hints=tc.get("hints", {}),
                reasoning=tc.get("reasoning", ""),
                priority=tc.get("priority", 2),
            ))

        # Respect max tools limit
        tool_calls = sorted(tool_calls, key=lambda t: t.priority)
        tool_calls = tool_calls[:settings.context_max_tools]

        plan = ResearchPlan(
            tool_calls=tool_calls,
            reasoning=plan_dict.get("reasoning", ""),
            hypothesis=plan_dict.get("hypothesis", ""),
        )

        logger.info(
            "Orchestrator plan: %d tools selected -- %s",
            len(tool_calls),
            ", ".join(tc.name for tc in tool_calls),
        )

        if on_progress:
            tool_names = ", ".join(tc.name.replace("_", " ") for tc in tool_calls)
            on_progress(f"Research plan ready: checking {tool_names}")

        return plan

    except Exception as e:
        logger.error("Orchestrator failed: %s", e)
        if on_progress:
            on_progress("Research planning failed -- proceeding with business profile only")
        return ResearchPlan(tool_calls=[], reasoning=f"Orchestrator error: {e}")
