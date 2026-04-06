"""
Main entry point for context enrichment.

gather_context() is the only function the simulation pipeline needs to call.
It orchestrates: plan -> execute tools -> filter -> return BusinessContext.

CRITICAL: This function NEVER raises. If anything fails at any level,
it returns an empty BusinessContext so the swarm can proceed without context.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Optional, Callable

from backend.config import get_settings
from backend.context.orchestrator import plan_research
from backend.context.agent_runner import run_all_tools
from backend.context.filter import filter_context
from backend.models.business import BusinessSnapshot
from backend.models.context import BusinessContext, ToolStatus

logger = logging.getLogger(__name__)


async def gather_context(
    business: BusinessSnapshot,
    question: str,
    on_progress: Optional[Callable[[str], None]] = None,
) -> BusinessContext:
    """Gather real-world context to enrich the persona swarm.

    Steps:
    1. Ask orchestrator which tools to run
    2. Run selected tools in parallel
    3. Filter results for relevance
    4. Return BusinessContext with filtered_narrative

    Always returns a BusinessContext. Never raises.
    """
    settings = get_settings()
    start = time.monotonic()

    if not settings.context_enabled:
        logger.info("Context engine disabled via config")
        return BusinessContext()

    try:
        ctx = await asyncio.wait_for(
            _gather_inner(business, question, on_progress),
            timeout=settings.context_timeout,
        )
        ctx.total_elapsed_seconds = time.monotonic() - start
        ctx.created_at = datetime.now(timezone.utc)
        return ctx

    except asyncio.TimeoutError:
        elapsed = time.monotonic() - start
        logger.error("Context engine hit %ds hard timeout", settings.context_timeout)
        if on_progress:
            on_progress("Context research timed out -- proceeding with business profile only")
        return BusinessContext(total_elapsed_seconds=elapsed)

    except Exception as e:
        elapsed = time.monotonic() - start
        logger.exception("Context engine failed: %s", e)
        if on_progress:
            on_progress("Context research failed -- proceeding with business profile only")
        return BusinessContext(total_elapsed_seconds=elapsed)


async def _gather_inner(
    business: BusinessSnapshot,
    question: str,
    on_progress: Optional[Callable[[str], None]],
) -> BusinessContext:
    """Inner implementation. May raise -- caught by gather_context()."""

    # Step 1: Orchestrator decides what to research
    plan = await plan_research(business, question, on_progress)

    if not plan.tool_calls:
        if on_progress:
            on_progress("No additional research needed for this question")
        return BusinessContext(
            orchestrator_reasoning=plan.reasoning,
        )

    # Step 2: Run tools in parallel
    tool_results = await run_all_tools(
        plan,
        business_name=business.name,
        business_type=business.type,
        location=business.location,
        question=question,
        on_progress=on_progress,
    )

    # Step 3: Filter for relevance
    narrative, scored_results = await filter_context(
        business, question, tool_results, on_progress,
    )

    succeeded = sum(1 for r in scored_results if r.status == ToolStatus.COMPLETED)
    failed = sum(1 for r in scored_results if r.status == ToolStatus.FAILED)

    if on_progress:
        if narrative:
            insight_count = len([r for r in scored_results if r.relevance_score > 0.5])
            on_progress(f"Context research complete -- found {insight_count} relevant insights")
        else:
            on_progress("No relevant context found -- proceeding with business profile only")

    return BusinessContext(
        tool_results=scored_results,
        filtered_narrative=narrative,
        tools_planned=[tc.name for tc in plan.tool_calls],
        tools_succeeded=succeeded,
        tools_failed=failed,
        orchestrator_reasoning=plan.reasoning,
    )
