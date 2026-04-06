"""
Relevance filter: distils raw tool results into a concise narrative
for prompt injection.

If <=3 tool results, skips the Claude call and builds a simple narrative
from tool summaries. Only invokes the full filter when there is enough
data to warrant it.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Callable

from anthropic import AsyncAnthropic

from backend.config import get_settings
from backend.models.business import BusinessSnapshot
from backend.models.context import ToolResult, ToolStatus

logger = logging.getLogger(__name__)

PROMPT_DIR = Path(__file__).parent / "prompts"

# Skip the Claude filter call if we have this many or fewer results
SIMPLE_THRESHOLD = 3


def _load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text()


def _parse_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


def _format_tool_data(results: list[ToolResult]) -> str:
    """Format tool results as readable text for the filter prompt."""
    sections = []
    for r in results:
        if r.status != ToolStatus.COMPLETED:
            continue
        sections.append(
            f"--- {r.tool_name} ---\n{json.dumps(r.raw_data, indent=2, default=str)[:2000]}"
        )
    return "\n\n".join(sections)


def _build_simple_narrative(results: list[ToolResult]) -> str:
    """For small result sets, build a narrative without a Claude call."""
    parts = []
    for r in results:
        if r.status == ToolStatus.COMPLETED and r.raw_data:
            # Use extracted_insight if available (web_search), else analysis (review_analyzer)
            insight = (
                r.raw_data.get("extracted_insight")
                or r.raw_data.get("analysis")
                or ""
            )
            if insight and insight != "No relevant findings.":
                parts.append(insight)

            # For price_index, build a human sentence
            if r.tool_name == "price_index":
                rate = r.raw_data.get("latest_rate")
                period = r.raw_data.get("latest_period")
                country = r.raw_data.get("country", "")
                if rate is not None:
                    parts.append(
                        f"The latest inflation rate for {country} is {rate}% "
                        f"(as of {period})."
                    )

            # For demographic, summarise key indicators
            if r.tool_name == "demographic":
                indicators = r.raw_data.get("indicators", {})
                gdp = indicators.get("gdp_per_capita_ppp", {}).get("value")
                if gdp:
                    parts.append(f"GDP per capita (PPP) in the area is ${gdp:,.0f}.")

    return " ".join(parts)[:3000] if parts else ""


async def filter_context(
    business: BusinessSnapshot,
    question: str,
    tool_results: list[ToolResult],
    on_progress: Optional[Callable[[str], None]] = None,
) -> tuple[str, list[ToolResult]]:
    """Filter raw tool results into a relevant narrative.

    Returns (narrative, updated_results_with_scores).
    If filtering fails, returns a simple fallback narrative.
    """
    successful = [r for r in tool_results if r.status == ToolStatus.COMPLETED]

    if not successful:
        return "", tool_results

    # For small result sets, skip the Claude call
    if len(successful) <= SIMPLE_THRESHOLD:
        logger.info("Small result set (%d tools) -- using simple narrative", len(successful))
        narrative = _build_simple_narrative(successful)
        for r in successful:
            r.relevance_score = 0.7  # Default score for unfiltered results
        return narrative, tool_results

    # Full Claude-powered filter for larger result sets
    if on_progress:
        on_progress("Filtering results for relevance...")

    try:
        settings = get_settings()
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        filter_prompt = _load_prompt("relevance_filter.txt")

        tool_data_text = _format_tool_data(successful)

        business_text = (
            f"Business: {business.name} ({business.type})\n"
            f"Location: {business.location or 'Not specified'}\n"
            f"Description: {business.description}\n"
            f"Customers: {business.customer_description or 'Not described'}"
        )

        response = await client.messages.create(
            model=settings.model_name,
            max_tokens=1200,
            system=filter_prompt,
            messages=[{
                "role": "user",
                "content": (
                    f"{business_text}\n\n"
                    f"QUESTION: {question}\n\n"
                    f"TOOL RESULTS:\n{tool_data_text}"
                ),
            }],
        )

        result = _parse_json(response.content[0].text)
        narrative = result.get("narrative", "")
        scores = result.get("scores", {})

        # Apply scores to tool results
        for r in tool_results:
            if r.tool_name in scores:
                r.relevance_score = float(scores[r.tool_name])

        # Cap narrative length
        if len(narrative.split()) > 800:
            words = narrative.split()[:800]
            narrative = " ".join(words)

        logger.info("Relevance filter produced %d-word narrative", len(narrative.split()))
        return narrative, tool_results

    except Exception as e:
        logger.error("Relevance filter failed: %s -- using simple fallback", e)
        narrative = _build_simple_narrative(successful)
        return narrative, tool_results
