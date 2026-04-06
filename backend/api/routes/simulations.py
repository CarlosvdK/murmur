import asyncio
import json
import logging
import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional

from backend.config import get_settings
from backend.models.business import BusinessSnapshot
from backend.models.context import BusinessContext
from backend.models.simulation import (
    SimulationCreate,
    Simulation,
    SimulationStatus,
    SimulationProgress,
    SimulationResult,
)
from backend.models.persona import PersonaProfile
from backend.swarm import generate_personas, run_simulation, aggregate_responses
from backend.swarm.caveats import generate_caveats
from backend.context.engine import gather_context
from backend.reviewer_intelligence import build_reviewer_intelligence
from backend.reviewer_intelligence.review_signal_extractor import extract_review_signals
from backend.impact import estimate_impact
from backend.api.routes.businesses import _businesses

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simulations", tags=["simulations"])

# In-memory stores for development
_simulations: dict[UUID, Simulation] = {}
_simulation_personas: dict[UUID, list[PersonaProfile]] = {}
_simulation_responses: dict[UUID, list[dict]] = {}
_simulation_results: dict[UUID, SimulationResult] = {}
_simulation_progress: dict[UUID, SimulationProgress] = {}
_simulation_context: dict[UUID, BusinessContext] = {}
_simulation_caveats: dict[UUID, list] = {}
_simulation_reviewer_intel: dict[UUID, dict] = {}
_simulation_impact: dict[UUID, dict] = {}
_simulation_queues: dict[UUID, asyncio.Queue] = {}


@router.post("/", response_model=Simulation)
async def create_simulation(data: SimulationCreate):
    """Create a simulation and start running it in the background."""
    business = _businesses.get(data.business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    sim_id = uuid4()
    snapshot = BusinessSnapshot(
        name=business.name,
        type=business.type,
        description=business.description,
        customer_description=business.customer_description,
        location=business.location,
    )

    simulation = Simulation(
        id=sim_id,
        business_id=data.business_id,
        question=data.question,
        variant_a=data.variant_a,
        variant_b=data.variant_b,
        status=SimulationStatus.PENDING,
        persona_count=data.persona_count,
        prompt_version="v0.1",
        business_snapshot=snapshot.model_dump(),
        created_at=datetime.now(timezone.utc),
    )
    _simulations[sim_id] = simulation

    _simulation_progress[sim_id] = SimulationProgress(
        simulation_id=sim_id,
        status=SimulationStatus.PENDING,
        step="Queued",
        personas_total=data.persona_count,
    )

    # Create SSE queue for this simulation
    _simulation_queues[sim_id] = asyncio.Queue()

    # Run the simulation pipeline in the background
    asyncio.create_task(
        _run_pipeline(sim_id, snapshot, data.question, data.variant_a,
                      data.variant_b, data.persona_count)
    )

    return simulation


async def _run_pipeline(
    sim_id: UUID,
    business: BusinessSnapshot,
    question: str,
    variant_a: Optional[str],
    variant_b: Optional[str],
    persona_count: int,
):
    """Full simulation pipeline: context -> generate -> interview -> aggregate -> caveats."""
    start = time.monotonic()
    sim = _simulations[sim_id]
    progress = _simulation_progress[sim_id]
    queue = _simulation_queues.get(sim_id)

    def emit_sse(phase: str, step: str):
        if queue:
            queue.put_nowait({
                "phase": phase,
                "step": step,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "simulation_id": str(sim_id),
            })

    try:
        # Step 0: Gather context (NEW)
        context_narrative = None
        settings = get_settings()

        if settings.context_enabled:
            sim.status = SimulationStatus.GATHERING_CONTEXT
            progress.status = SimulationStatus.GATHERING_CONTEXT
            progress.step = "Researching market context..."
            emit_sse("context", "Researching market context...")

            def on_context_progress(msg: str):
                progress.step = msg
                progress.elapsed_seconds = time.monotonic() - start
                emit_sse("context", msg)

            context = await gather_context(business, question, on_progress=on_context_progress)
            _simulation_context[sim_id] = context
            context_narrative = context.filtered_narrative or None

            logger.info(
                "Context gathered: %d/%d tools succeeded, %.1fs, narrative=%d chars",
                context.tools_succeeded,
                context.tools_succeeded + context.tools_failed,
                context.total_elapsed_seconds,
                len(context.filtered_narrative),
            )

        # Step 0.5: Reviewer Intelligence (builds calibrated persona manifest)
        manifest = None
        review_signals = None
        if settings.google_places_api_key:
            progress.step = "Analysing your customer base..."
            emit_sse("reviewer_intel", "Analysing your customer base from review patterns...")

            def on_ri_progress(msg: str):
                progress.step = msg
                progress.elapsed_seconds = time.monotonic() - start
                emit_sse("reviewer_intel", msg)

            manifest = await build_reviewer_intelligence(
                business, persona_count, on_progress=on_ri_progress,
            )
            # Also grab raw signals for caveat generation (separate from manifest)
            try:
                review_signals = await extract_review_signals(
                    business.name, business.location,
                )
            except Exception:
                review_signals = None
            if manifest:
                _simulation_reviewer_intel[sim_id] = {
                    "total_personas": manifest.total_count,
                    "distribution": manifest.distribution_summary,
                    "confidence": manifest.confidence,
                    "based_on": manifest.based_on,
                    "caveats": manifest.key_caveats,
                }
                # Extract review signals for caveats (stored on the manifest)
                # We don't store the raw signals object -- just pass to caveats
                logger.info("Reviewer intelligence: manifest with %d specs", manifest.total_count)
            else:
                logger.info("Reviewer intelligence returned no manifest -- using freeform generation")

        # Step 1: Generate personas
        sim.status = SimulationStatus.GENERATING_PERSONAS
        progress.status = SimulationStatus.GENERATING_PERSONAS
        progress.step = "Generating customer personas..."
        emit_sse("personas", "Generating customer personas...")

        personas = await generate_personas(
            business, persona_count, context_narrative=context_narrative,
            manifest=manifest,
        )
        _simulation_personas[sim_id] = personas
        progress.personas_generated = len(personas)
        progress.personas_total = len(personas)
        emit_sse("personas", f"{len(personas)} customer personas ready")

        # Step 2: Interview all personas
        sim.status = SimulationStatus.SIMULATING
        progress.status = SimulationStatus.SIMULATING
        progress.step = "Interviewing customers..."
        emit_sse("simulation", "Interviewing customers...")

        def on_progress(persona_name: str, count: int):
            progress.current_persona = persona_name
            progress.personas_interviewed = count
            progress.step = f"Talking to {persona_name}..."
            progress.elapsed_seconds = time.monotonic() - start
            emit_sse("simulation", f"Talking to {persona_name}...")

        responses = await run_simulation(
            personas, business, question, variant_a, variant_b,
            on_progress=on_progress, context_narrative=context_narrative,
        )
        _simulation_responses[sim_id] = responses
        emit_sse("simulation", f"Interviewed {len(responses)} customers")

        # Step 3: Aggregate
        sim.status = SimulationStatus.AGGREGATING
        progress.status = SimulationStatus.AGGREGATING
        progress.step = "Synthesising customer feedback..."
        emit_sse("aggregation", "Synthesising customer feedback...")

        result_data = await aggregate_responses(
            business, question, responses, variant_a, variant_b,
            context_narrative=context_narrative,
        )

        # Step 4.5: Impact estimation (quantitative)
        impact = estimate_impact(responses, question)
        _simulation_impact[sim_id] = {
            "revenue": {
                "point_estimate_pct": impact.revenue.point_estimate_pct,
                "ci_low_pct": impact.revenue.ci_low_pct,
                "ci_high_pct": impact.revenue.ci_high_pct,
                "confidence_level": impact.revenue.confidence_level,
            },
            "customers_likely_stay": impact.customers_likely_stay,
            "customers_likely_reduce": impact.customers_likely_reduce,
            "customers_likely_leave": impact.customers_likely_leave,
            "total_customers_modelled": impact.total_customers_modelled,
            "retention_rate_pct": impact.retention_rate_pct,
            "decision": impact.decision,
            "decision_reasoning": impact.decision_reasoning,
            "decision_framework": impact.decision_framework,
            "worst_case_summary": impact.worst_case_summary,
            "best_case_summary": impact.best_case_summary,
            "most_likely_summary": impact.most_likely_summary,
        }

        # Step 5: Generate caveats
        caveats = generate_caveats(
            business, question, persona_count, len(responses),
            variant_a, variant_b, review_signals=review_signals,
        )
        _simulation_caveats[sim_id] = [
            {"type": c.type, "title": c.title, "message": c.message,
             "severity": c.severity, "source": c.source}
            for c in caveats
        ]

        # Normalize themes and standout_voices -- Claude may use varying field names
        raw_themes = result_data.get("themes") or []
        themes = []
        for t in raw_themes:
            if isinstance(t, dict):
                themes.append({
                    "label": t.get("label", t.get("name", "")),
                    "summary": t.get("summary", t.get("description", "")),
                    "count": t.get("count", t.get("persona_count", 0)),
                })

        raw_voices = result_data.get("standout_voices") or []
        voices = []
        for v in raw_voices:
            if isinstance(v, dict):
                # Claude uses many field name variants -- try them all
                pname = (
                    v.get("persona_name")
                    or v.get("name")
                    or v.get("persona")
                    or v.get("customer")
                    or v.get("voice")
                    or ""
                )
                quote = (
                    v.get("quote")
                    or v.get("excerpt")
                    or v.get("text")
                    or v.get("response")
                    or v.get("reaction")
                    or ""
                )
                if pname or quote:
                    voices.append({"persona_name": pname, "quote": quote})

        result = SimulationResult(
            id=uuid4(),
            simulation_id=sim_id,
            summary=result_data["summary"],
            recommendation=result_data["recommendation"],
            confidence_score=result_data["confidence_score"],
            confidence_reasoning=result_data.get("confidence_reasoning"),
            winner=result_data.get("winner"),
            winner_reasoning=result_data.get("winner_reasoning"),
            themes=themes or None,
            standout_voices=voices or None,
            raw_output=result_data.get("raw_output", {}),
            created_at=datetime.now(timezone.utc),
        )
        _simulation_results[sim_id] = result

        # Done
        sim.status = SimulationStatus.COMPLETED
        sim.completed_at = datetime.now(timezone.utc)
        progress.status = SimulationStatus.COMPLETED
        progress.step = "Complete"
        progress.elapsed_seconds = time.monotonic() - start
        emit_sse("complete", "Your results are ready")

        logger.info("Simulation %s completed in %.1fs", sim_id, progress.elapsed_seconds)

    except Exception as e:
        logger.exception("Simulation %s failed: %s", sim_id, e)
        sim.status = SimulationStatus.FAILED
        sim.error_message = str(e)
        progress.status = SimulationStatus.FAILED
        progress.step = f"Failed: {str(e)[:100]}"
        emit_sse("failed", f"Simulation failed: {str(e)[:100]}")

    finally:
        # Signal SSE stream is done
        if queue:
            await queue.put(None)


# --- SSE streaming endpoint ---

@router.get("/{sim_id}/stream")
async def stream_simulation_progress(sim_id: UUID):
    """Server-Sent Events endpoint for real-time simulation progress."""
    queue = _simulation_queues.get(sim_id)
    if not queue:
        raise HTTPException(status_code=404, detail="No active stream for this simulation")

    async def event_generator():
        try:
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=600)
                if event is None:
                    yield "event: done\ndata: {}\n\n"
                    break
                yield f"event: progress\ndata: {json.dumps(event)}\n\n"
        except asyncio.TimeoutError:
            yield "event: timeout\ndata: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# --- Existing endpoints ---

@router.get("/{sim_id}", response_model=Simulation)
async def get_simulation(sim_id: UUID):
    sim = _simulations.get(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim


@router.get("/{sim_id}/progress", response_model=SimulationProgress)
async def get_simulation_progress(sim_id: UUID):
    """Poll this endpoint for live progress updates (fallback for SSE)."""
    progress = _simulation_progress.get(sim_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return progress


@router.get("/{sim_id}/context")
async def get_simulation_context(sim_id: UUID):
    """Return the BusinessContext gathered for this simulation (audit trail)."""
    context = _simulation_context.get(sim_id)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    return context.model_dump()


@router.get("/{sim_id}/caveats")
async def get_simulation_caveats(sim_id: UUID):
    """Return caveats generated for this simulation."""
    caveats = _simulation_caveats.get(sim_id)
    if caveats is None:
        raise HTTPException(status_code=404, detail="Caveats not found")
    return caveats


@router.get("/{sim_id}/reviewer-intelligence")
async def get_simulation_reviewer_intel(sim_id: UUID):
    """Return the reviewer intelligence analysis for this simulation."""
    intel = _simulation_reviewer_intel.get(sim_id)
    if not intel:
        raise HTTPException(status_code=404, detail="No reviewer intelligence for this simulation")
    return intel


@router.get("/{sim_id}/impact")
async def get_simulation_impact(sim_id: UUID):
    """Return quantitative impact estimates with confidence intervals."""
    impact = _simulation_impact.get(sim_id)
    if not impact:
        raise HTTPException(status_code=404, detail="No impact estimate for this simulation")
    return impact


@router.get("/{sim_id}/personas", response_model=list[PersonaProfile])
async def get_simulation_personas(sim_id: UUID):
    personas = _simulation_personas.get(sim_id)
    if personas is None:
        raise HTTPException(status_code=404, detail="Personas not found")
    return personas


@router.get("/{sim_id}/responses")
async def get_simulation_responses(sim_id: UUID):
    responses = _simulation_responses.get(sim_id)
    if responses is None:
        raise HTTPException(status_code=404, detail="Responses not found")
    return responses


@router.get("/{sim_id}/result", response_model=SimulationResult)
async def get_simulation_result(sim_id: UUID):
    result = _simulation_results.get(sim_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.get("/", response_model=list[Simulation])
async def list_simulations():
    return list(_simulations.values())
