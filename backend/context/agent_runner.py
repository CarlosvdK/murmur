"""
Parallel tool execution with per-tool and global timeouts.

Rules:
- Hard timeout of 90s total -- swarm starts regardless
- Each tool has its own 30s timeout
- A failing tool never blocks others
- Results returned as they complete
"""

import asyncio
import logging
from typing import Optional, Callable

from backend.config import get_settings
from backend.context.orchestrator import ResearchPlan, ToolCall
from backend.context.tools import get_tool_by_name
from backend.models.context import ToolResult, ToolStatus

logger = logging.getLogger(__name__)

FRIENDLY_NAMES = {
    "google_places": "Searching for competitors nearby...",
    "review_analyzer": "Reading customer reviews...",
    "web_search": "Searching the web...",
    "news_search": "Checking recent local news...",
    "price_index": "Checking local economic indicators...",
    "weather_trends": "Checking seasonal patterns...",
    "demographic": "Analysing the local area...",
    "social_sentiment": "Searching for public sentiment...",
}


async def _run_single_tool(
    tool_call: ToolCall,
    business_name: str,
    business_type: str,
    location: Optional[str],
    question: str,
    tool_timeout: int,
    on_progress: Optional[Callable[[str], None]],
) -> ToolResult:
    """Run a single tool with progress reporting."""
    friendly = FRIENDLY_NAMES.get(tool_call.name, f"Running {tool_call.name}...")
    if on_progress:
        on_progress(friendly)

    try:
        tool = get_tool_by_name(tool_call.name)
    except ValueError:
        logger.error("Unknown tool requested: %s", tool_call.name)
        return ToolResult(
            tool_name=tool_call.name,
            status=ToolStatus.FAILED,
            error=f"Unknown tool: {tool_call.name}",
        )

    result = await tool.run(
        timeout=tool_timeout,
        business_name=business_name,
        business_type=business_type,
        location=location,
        question=question,
        hints=tool_call.hints,
    )

    if result.status == ToolStatus.COMPLETED:
        if on_progress:
            on_progress(f"{tool_call.name.replace('_', ' ').title()} complete")
    elif result.status == ToolStatus.FAILED:
        if on_progress:
            on_progress(f"{tool_call.name.replace('_', ' ').title()} unavailable -- continuing without it")

    return result


async def run_all_tools(
    plan: ResearchPlan,
    business_name: str,
    business_type: str,
    location: Optional[str],
    question: str,
    on_progress: Optional[Callable[[str], None]] = None,
) -> list[ToolResult]:
    """Run all planned tools in parallel with a global timeout.

    Returns list of ToolResults (some may have FAILED status).
    Never raises -- always returns.
    """
    if not plan.tool_calls:
        return []

    settings = get_settings()
    tool_timeout = settings.context_tool_timeout
    total_timeout = settings.context_timeout

    if on_progress:
        on_progress(f"Gathering context from {len(plan.tool_calls)} sources...")

    try:
        results = await asyncio.wait_for(
            asyncio.gather(
                *[
                    _run_single_tool(
                        tc, business_name, business_type, location,
                        question, tool_timeout, on_progress,
                    )
                    for tc in plan.tool_calls
                ],
                return_exceptions=True,
            ),
            timeout=total_timeout,
        )
    except asyncio.TimeoutError:
        logger.warning("Global context timeout (%ds) reached", total_timeout)
        if on_progress:
            on_progress("Research phase timed out -- proceeding with what we have")
        results = []

    # Convert exceptions to failed ToolResults
    clean_results = []
    for r in results:
        if isinstance(r, Exception):
            clean_results.append(ToolResult(
                tool_name="unknown",
                status=ToolStatus.FAILED,
                error=str(r)[:500],
            ))
        elif isinstance(r, ToolResult):
            clean_results.append(r)

    succeeded = sum(1 for r in clean_results if r.status == ToolStatus.COMPLETED)
    failed = sum(1 for r in clean_results if r.status == ToolStatus.FAILED)

    if on_progress:
        on_progress(f"Context gathered from {succeeded}/{len(plan.tool_calls)} sources")

    logger.info("Tool execution: %d succeeded, %d failed", succeeded, failed)
    return clean_results
