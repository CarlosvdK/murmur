import asyncio
import json
import logging
import random
import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel

from backend.config import get_settings
from backend.models.business import BusinessSnapshot
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
from backend.db.client import get_supabase
from backend.auth.dependencies import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simulations", tags=["simulations"])

# Ephemeral in-memory stores -- runtime-only state for live SSE streaming.
_simulation_progress: dict[UUID, SimulationProgress] = {}
_simulation_queues: dict[UUID, asyncio.Queue] = {}

# Progress message libraries
_progress_verbs = [
    "Interviewing", "Listening to", "Talking with", "Hearing from",
    "Consulting", "Checking in with", "Getting insights from",
    "Having a chat with", "Understanding", "Learning from",
]
_thinking_messages = [
    "Analysing your business profile...",
    "Reading through your survey responses...",
    "Building a picture of your customer base...",
    "Cross-referencing with published research...",
    "Studying your competitive landscape...",
    "Reviewing behavioral science literature...",
    "Calibrating for your market context...",
    "Loading cultural and demographic data...",
    "Preparing the simulation environment...",
    "Setting up customer archetypes...",
]


# ---------------------------------------------------------------------------
# Helpers: convert between Pydantic models and Supabase rows
# ---------------------------------------------------------------------------

def _sim_to_row(sim: Simulation) -> dict:
    return {
        "id": str(sim.id),
        "business_id": str(sim.business_id),
        "question": sim.question,
        "variant_a": sim.variant_a,
        "variant_b": sim.variant_b,
        "status": sim.status.value if isinstance(sim.status, SimulationStatus) else sim.status,
        "persona_count": sim.persona_count,
        "prompt_version": sim.prompt_version,
        "business_snapshot": sim.business_snapshot,
        "error_message": sim.error_message,
        "created_at": sim.created_at.isoformat(),
        "completed_at": sim.completed_at.isoformat() if sim.completed_at else None,
    }


def _row_to_sim(row: dict) -> Simulation:
    return Simulation(
        id=row["id"],
        business_id=row["business_id"],
        question=row["question"],
        variant_a=row.get("variant_a"),
        variant_b=row.get("variant_b"),
        status=row["status"],
        persona_count=row["persona_count"],
        prompt_version=row["prompt_version"],
        business_snapshot=row.get("business_snapshot"),
        error_message=row.get("error_message"),
        created_at=row["created_at"],
        completed_at=row.get("completed_at"),
    )


def _persona_to_row(persona: PersonaProfile, sim_id: UUID) -> dict:
    return {
        "simulation_id": str(sim_id),
        "name": persona.name,
        "age": persona.age,
        "occupation": persona.occupation,
        "visit_frequency": persona.engagement_pattern,  # DB column is still visit_frequency
        "avg_spend": persona.avg_spend,  # extracts number from spend_model
        "personality": persona.personality,
        "relationship_to_business": persona.relationship_to_business,
        "quirk": persona.quirk,
        "profile": persona.model_dump(),  # stores ALL fields including new ones
    }


def _row_to_persona(row: dict) -> PersonaProfile:
    profile = row.get("profile") or {}
    # Support both old format (visit_frequency/avg_spend) and new (engagement_pattern/spend_model)
    engagement = (
        profile.get("engagement_pattern")
        or row.get("visit_frequency")
        or ""
    )
    spend = (
        profile.get("spend_model")
        or (f"${row['avg_spend']}" if row.get("avg_spend") else "")
        or ""
    )
    return PersonaProfile(
        name=row["name"],
        age=row["age"],
        occupation=row.get("occupation", ""),
        engagement_pattern=engagement,
        spend_model=spend,
        personality=row.get("personality", ""),
        relationship_to_business=row.get("relationship_to_business", ""),
        quirk=row.get("quirk", ""),
        segment=profile.get("segment"),
        income_tier=profile.get("income_tier"),
        price_sensitivity=profile.get("price_sensitivity"),
        is_silent_majority=profile.get("is_silent_majority"),
        digital_behavior=profile.get("digital_behavior"),
        decision_style=profile.get("decision_style"),
        openness=profile.get("openness"),
        conscientiousness=profile.get("conscientiousness"),
        extraversion=profile.get("extraversion"),
        agreeableness=profile.get("agreeableness"),
        neuroticism=profile.get("neuroticism"),
    )


def _response_to_row(resp: dict, sim_id: UUID, persona_db_id: str) -> dict:
    return {
        "persona_id": persona_db_id,
        "simulation_id": str(sim_id),
        "response": resp.get("response", ""),
        "reasoning": resp.get("reasoning"),
        "sentiment": resp.get("sentiment"),
        "preference": resp.get("preference"),
        "preference_strength": resp.get("preference_strength"),
        "raw_output": resp,
    }


def _result_to_row(result: SimulationResult) -> dict:
    return {
        "id": str(result.id),
        "simulation_id": str(result.simulation_id),
        "summary": result.summary,
        "recommendation": result.recommendation,
        "confidence_score": result.confidence_score,
        "confidence_reasoning": result.confidence_reasoning,
        "winner": result.winner,
        "winner_reasoning": result.winner_reasoning,
        "themes": [t.model_dump() if hasattr(t, "model_dump") else t for t in (result.themes or [])],
        "standout_voices": [v.model_dump() if hasattr(v, "model_dump") else v for v in (result.standout_voices or [])],
        "raw_output": result.raw_output,
        "created_at": result.created_at.isoformat(),
    }


def _row_to_result(row: dict) -> SimulationResult:
    raw = row.get("raw_output") or {}
    return SimulationResult(
        id=row["id"],
        simulation_id=row["simulation_id"],
        summary=row["summary"],
        recommendation=row.get("recommendation"),
        confidence_score=row["confidence_score"],
        confidence_reasoning=row.get("confidence_reasoning"),
        winner=row.get("winner"),
        winner_reasoning=row.get("winner_reasoning"),
        themes=row.get("themes"),
        standout_voices=row.get("standout_voices"),
        baseline_summary=raw.get("baseline_summary"),
        behavioral_prediction=raw.get("behavioral_prediction"),
        stated_vs_actual_gap=raw.get("stated_vs_actual_gap"),
        raw_output=raw,
        created_at=row["created_at"],
    )


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _update_sim(sim_id: UUID, **fields):
    """Update arbitrary fields on a simulation row."""
    db = get_supabase()
    db.table("simulations").update(fields).eq("id", str(sim_id)).execute()


def _store_personas(personas: list[PersonaProfile], sim_id: UUID) -> list[str]:
    """Insert persona rows and return their DB-generated UUIDs."""
    db = get_supabase()
    rows = [_persona_to_row(p, sim_id) for p in personas]
    result = db.table("personas").insert(rows).execute()
    return [r["id"] for r in result.data]


def _store_responses(responses: list[dict], sim_id: UUID, persona_db_ids: list[str]):
    """Insert persona response rows. Maps responses to persona IDs by index."""
    db = get_supabase()
    rows = []
    for i, resp in enumerate(responses):
        persona_db_id = persona_db_ids[i] if i < len(persona_db_ids) else persona_db_ids[-1]
        rows.append(_response_to_row(resp, sim_id, persona_db_id))
    if rows:
        db.table("persona_responses").insert(rows).execute()


def _store_result(result: SimulationResult):
    db = get_supabase()
    db.table("simulation_results").insert(_result_to_row(result)).execute()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

class ClarifyingQuestionsRequest(BaseModel):
    business_id: str
    question: str


@router.post("/clarifying-questions")
async def generate_clarifying_questions(
    data: ClarifyingQuestionsRequest,
    user_id: UUID = Depends(get_current_user_id),
):
    """Generate smart clarifying questions using Claude + business profile."""
    db = get_supabase()

    # Get business profile
    biz = (
        db.table("businesses")
        .select("*")
        .eq("id", data.business_id)
        .eq("user_id", str(user_id))
        .maybe_single()
        .execute()
    )
    if not biz.data:
        return {"questions": []}

    row = biz.data
    metadata = row.get("metadata") or {}
    merged = {**row, **metadata}

    # Build the FULL survey context -- same as what the simulation uses
    try:
        from backend.survey.rag_builder import build_rag_context
        profile_text = build_rag_context(merged)
    except Exception:
        profile_text = f"Business: {merged.get('name', 'Unknown')} ({merged.get('type', 'unknown')})\nDescription: {merged.get('description', 'Not provided')}"

    try:
        from anthropic import AsyncAnthropic
        settings = get_settings()
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)

        response = await client.messages.create(
            model=settings.model_name,
            max_tokens=600,
            messages=[{
                "role": "user",
                "content": (
                    f"You are preparing to simulate customer reactions to a business decision. "
                    f"Before running the simulation, generate 3 clarifying questions that would "
                    f"make the simulation more accurate.\n\n"
                    f"BUSINESS PROFILE:\n{profile_text}\n\n"
                    f"USER'S QUESTION:\n{data.question}\n\n"
                    f"RULES:\n"
                    f"- Reference specific details from the business profile (their competitors, "
                    f"their customer demographics, their past changes, etc.)\n"
                    f"- Do NOT ask for information already provided in the question\n"
                    f"- Ask for concrete numbers, past outcomes, and competitor data\n"
                    f"- Each question should be 1 sentence, with a short hint in italics\n"
                    f"- Focus on information that would change the simulation outcome\n\n"
                    f"Return ONLY valid JSON:\n"
                    f'[{{"question": "...", "hint": "..."}}, ...]'
                ),
            }],
        )

        import json
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        questions = json.loads(raw)
        return {"questions": questions[:3]}

    except Exception as e:
        logger.warning("Clarifying question generation failed: %s", e)
        return {"questions": [
            {"question": "Can you describe the specific change you are considering?", "hint": "The more detail, the better the simulation"},
            {"question": "What triggered this idea?", "hint": "Understanding the motivation helps frame the simulation"},
            {"question": "Do you have any relevant data -- sales numbers, customer feedback, competitor info?", "hint": "Even rough numbers improve accuracy"},
        ]}


@router.post("/", response_model=Simulation)
async def create_simulation(
    data: SimulationCreate,
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a simulation and start running it in the background."""
    db = get_supabase()

    # Verify business exists and belongs to this user
    biz = (
        db.table("businesses")
        .select("*")
        .eq("id", str(data.business_id))
        .eq("user_id", str(user_id))
        .maybe_single()
        .execute()
    )
    if not biz.data:
        raise HTTPException(status_code=404, detail="Business not found")

    business_row = biz.data
    metadata = business_row.get("metadata") or {}
    # Merge metadata into row for snapshot -- fields may be in columns or JSONB
    merged = {**business_row, **metadata}
    snapshot = BusinessSnapshot(
        name=merged["name"],
        type=merged["type"],
        description=merged["description"],
        customer_description=merged.get("customer_description"),
        location=merged.get("location"),
        years_open=merged.get("years_open"),
        business_role=merged.get("business_role"),
        visit_frequency=merged.get("visit_frequency"),
        customer_value_drivers=merged.get("customer_value_drivers"),
        customer_social_context=merged.get("customer_social_context"),
        regular_proportion=merged.get("regular_proportion"),
        area_demographics=merged.get("area_demographics"),
        competitor_count=merged.get("competitor_count"),
        area_feel=merged.get("area_feel"),
        additional_customer_notes=merged.get("additional_customer_notes"),
        customer_age_distribution=merged.get("customer_age_distribution"),
        customer_income_bracket=merged.get("customer_income_bracket"),
        average_transaction_value=merged.get("average_transaction_value"),
        customer_gender_split=merged.get("customer_gender_split"),
        local_vs_visitor_ratio=merged.get("local_vs_visitor_ratio"),
        digital_savviness=merged.get("digital_savviness"),
        price_range=merged.get("price_range"),
    )

    # Build full workspace data for RAG context (already merged above)
    workspace_data = merged

    sim_id = uuid4()
    simulation = Simulation(
        id=sim_id,
        business_id=data.business_id,
        question=data.question,
        variant_a=data.variant_a,
        variant_b=data.variant_b,
        status=SimulationStatus.PENDING,
        persona_count=data.persona_count,
        prompt_version="v0.2",
        business_snapshot=snapshot.model_dump(),
        created_at=datetime.now(timezone.utc),
    )

    db.table("simulations").insert(_sim_to_row(simulation)).execute()

    _simulation_progress[sim_id] = SimulationProgress(
        simulation_id=sim_id,
        status=SimulationStatus.PENDING,
        step="Queued",
        personas_total=data.persona_count,
    )
    _simulation_queues[sim_id] = asyncio.Queue()

    asyncio.create_task(
        _run_pipeline(sim_id, snapshot, data.question, data.variant_a,
                      data.variant_b, data.persona_count, workspace_data)
    )

    return simulation


async def _run_pipeline(
    sim_id: UUID,
    business: BusinessSnapshot,
    question: str,
    variant_a: Optional[str],
    variant_b: Optional[str],
    persona_count: int,
    workspace_data: dict = None,
):
    """Full simulation pipeline: context -> generate -> interview -> aggregate -> caveats."""
    start = time.monotonic()
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
        # Step -1: Build enriched context from survey data + research library
        survey_context = ""
        research_context = ""
        try:
            from backend.survey.rag_builder import build_rag_context
            if workspace_data:
                survey_context = build_rag_context(workspace_data)
                logger.info("Survey RAG context: %d chars from workspace data", len(survey_context))
        except Exception as e:
            logger.warning("Survey RAG builder failed (non-fatal): %s", e)

        # Step 0.2: Interpret the question in business context
        interpretation = None
        interpreted_question = question  # fallback to raw question
        try:
            from backend.swarm.question_interpreter import interpret_question
            emit_sse("context", random.choice([
                "Understanding your question...",
                "Analysing what you are really asking...",
                "Interpreting your question in context...",
            ]))
            interpretation = await interpret_question(
                question=question,
                business_name=business.name,
                business_type=business.type,
                survey_context=survey_context,
            )
            if interpretation:
                interpreted_question = interpretation.interpreted_question
                logger.info(
                    "Question interpreted: '%s' -> '%s' (type=%s, affected=%s, %d%% customers)",
                    question[:50], interpreted_question[:50],
                    interpretation.question_type,
                    interpretation.affected_product,
                    interpretation.estimated_affected_customers_pct,
                )
                _update_sim(sim_id, question_interpretation={
                    "interpreted": interpretation.interpreted_question,
                    "type": interpretation.question_type,
                    "affected_product": interpretation.affected_product,
                    "is_core": interpretation.is_core_product,
                    "affected_pct": interpretation.estimated_affected_customers_pct,
                    "framing": interpretation.framing_instruction,
                })
        except Exception as e:
            logger.warning("Question interpretation failed (non-fatal): %s", e)

        try:
            country = (workspace_data or {}).get("location_country", "")
            # Use INTERPRETED question for better semantic search
            from backend.context.vector_rag import search_research_with_fallback
            rag_result = await search_research_with_fallback(
                question=interpreted_question,  # interpreted, not raw
                business_type=business.type,
                country_code=country,
                max_chars=6000,
            )
            research_context = rag_result.get("context", "")
            logger.info("Research context (%s): %d chars for type=%s",
                        rag_result.get("method", "unknown"), len(research_context), business.type)
            # Store RAG metadata for frontend
            _update_sim(sim_id, rag_selection={
                "sections": rag_result.get("sections_used", []),
                "method": rag_result.get("method", "unknown"),
            })
        except Exception as e:
            logger.warning("Research library failed (non-fatal): %s", e)

        # Step 0: Gather context (external APIs)
        context_narrative = None
        settings = get_settings()

        if settings.context_enabled:
            _update_sim(sim_id, status=SimulationStatus.GATHERING_CONTEXT.value)
            progress.status = SimulationStatus.GATHERING_CONTEXT
            ctx_msg = random.choice(_thinking_messages)
            progress.step = ctx_msg
            emit_sse("context", ctx_msg)

            def on_context_progress(msg: str):
                progress.step = msg
                progress.elapsed_seconds = time.monotonic() - start
                emit_sse("context", msg)

            context = await gather_context(business, question, on_progress=on_context_progress)
            context_narrative = context.filtered_narrative or None

            # Persist context data
            _update_sim(sim_id, context_data=context.model_dump(mode="json"))

            logger.info(
                "Context gathered: %d/%d tools succeeded, %.1fs, narrative=%d chars",
                context.tools_succeeded,
                context.tools_succeeded + context.tools_failed,
                context.total_elapsed_seconds,
                len(context.filtered_narrative),
            )

        # Step 0.1: Build psychological profile
        profile_context = ""
        try:
            from backend.context.profile_builder import build_profile
            country = (workspace_data or {}).get("location_country", "")
            psych_profile = build_profile(business, country_code=country)
            if psych_profile.summary:
                profile_context = psych_profile.summary
                logger.info("Psychological profile: %d chars, confidence=%s",
                            len(profile_context), psych_profile.confidence)
        except Exception as e:
            logger.warning("Profile builder failed (non-fatal): %s", e)

        # Combine all context sources: survey + profile + research + live agents
        enriched_parts = []
        if survey_context:
            enriched_parts.append(survey_context)
        if profile_context:
            enriched_parts.append(profile_context)
        if research_context:
            enriched_parts.append(research_context[:6000])
        if context_narrative:
            enriched_parts.append(context_narrative)
        # Inject question interpretation context so personas understand the framing
        if interpretation and interpretation.key_context_for_personas:
            enriched_parts.append(
                f"QUESTION CONTEXT:\n{interpretation.key_context_for_personas}\n"
                f"Framing: {interpretation.framing_instruction}"
            )
        if enriched_parts:
            context_narrative = "\n\n---\n\n".join(enriched_parts)
            logger.info("Enriched context: %d chars total (survey=%d, profile=%d, research=%d, agents=%d)",
                        len(context_narrative), len(survey_context), len(profile_context),
                        min(len(research_context), 4000),
                        len(context_narrative) - len(survey_context) - len(profile_context) - min(len(research_context), 4000))

        # Step 0.5: Reviewer Intelligence
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
            try:
                review_signals = await extract_review_signals(
                    business.name, business.location,
                )
            except Exception:
                review_signals = None
            if manifest:
                reviewer_intel = {
                    "total_personas": manifest.total_count,
                    "distribution": manifest.distribution_summary,
                    "confidence": manifest.confidence,
                    "based_on": manifest.based_on,
                    "caveats": manifest.key_caveats,
                }
                _update_sim(sim_id, reviewer_intel=reviewer_intel)
                logger.info("Reviewer intelligence: manifest with %d specs", manifest.total_count)
            else:
                logger.info("Reviewer intelligence returned no manifest -- using freeform generation")

        # Step 1: Generate personas
        _update_sim(sim_id, status=SimulationStatus.GENERATING_PERSONAS.value)
        progress.status = SimulationStatus.GENERATING_PERSONAS
        msg = random.choice([
            "Building your customer profiles...",
            "Creating realistic customer personas...",
            "Assembling a diverse customer panel...",
            "Recruiting simulated customers for your business...",
        ])
        progress.step = msg
        emit_sse("personas", msg)

        personas = await generate_personas(
            business, persona_count, context_narrative=context_narrative,
            manifest=manifest,
        )

        persona_db_ids = _store_personas(personas, sim_id)

        progress.personas_generated = len(personas)
        progress.personas_total = len(personas)
        emit_sse("personas", f"{len(personas)} customer personas ready")

        # Step 2: Interview all personas
        _update_sim(sim_id, status=SimulationStatus.SIMULATING.value)
        progress.status = SimulationStatus.SIMULATING
        sim_msg = random.choice([
            "Starting customer interviews...",
            "Beginning focus group sessions...",
            "Gathering customer perspectives...",
            "Running customer simulation...",
        ])
        progress.step = sim_msg
        emit_sse("simulation", sim_msg)

        def on_progress(persona_name: str, count: int):
            progress.current_persona = persona_name
            progress.personas_interviewed = count
            # If the simulator already sends a full message (contains turn info), use it directly
            if "(" in persona_name:
                progress.step = persona_name
                emit_sse("simulation", persona_name)
            else:
                verb = random.choice(_progress_verbs)
                progress.step = f"{verb} {persona_name}..."
                emit_sse("simulation", f"{verb} {persona_name}...")
            progress.elapsed_seconds = time.monotonic() - start

        responses = await run_simulation(
            personas, business, interpreted_question, variant_a, variant_b,
            on_progress=on_progress, context_narrative=context_narrative,
        )

        _store_responses(responses, sim_id, persona_db_ids)
        emit_sse("simulation", f"Interviewed {len(responses)} customers")

        # Step 3: Aggregate
        _update_sim(sim_id, status=SimulationStatus.AGGREGATING.value)
        progress.status = SimulationStatus.AGGREGATING
        agg_msg = random.choice([
            "Synthesising customer feedback...",
            "Analysing patterns across all interviews...",
            "Identifying themes and consensus...",
            "Comparing stated vs actual behaviour predictions...",
            "Building the final report...",
        ])
        progress.step = agg_msg
        emit_sse("aggregation", agg_msg)

        result_data = await aggregate_responses(
            business, interpreted_question, responses, variant_a, variant_b,
            context_narrative=context_narrative,
        )

        # Step 3.5: Research override check
        research_override = None
        try:
            from backend.swarm.research_override import apply_research_override
            research_override = await apply_research_override(
                question=interpreted_question,
                aggregation_result=result_data,
                persona_responses=responses,
                business_type=business.type,
            )
            if research_override and research_override.get("override_applied"):
                result_data["research_override"] = research_override
                logger.info(
                    "Research override applied: tactic=%s, conflict=%s",
                    research_override.get("tactic_detected"),
                    research_override.get("conflict_level"),
                )
                emit_sse("research", "Checking published research against customer feedback...")
        except Exception as e:
            logger.warning("Research override failed (non-fatal): %s", e)

        # Step 4.5: Impact estimation
        impact = estimate_impact(responses, interpreted_question, business_type=business.type)
        impact_data = {
            "revenue": {
                "point_estimate_pct": impact.revenue.point_estimate_pct,
                "ci_low_pct": impact.revenue.ci_low_pct,
                "ci_high_pct": impact.revenue.ci_high_pct,
                "confidence_level": impact.revenue.confidence_level,
                "impact_type": getattr(impact.revenue, "impact_type", "revenue"),
                "impact_label": getattr(impact.revenue, "impact_label", "Estimated revenue change"),
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
            "null_hypothesis": impact.null_hypothesis,
            "alternative_hypothesis": impact.alternative_hypothesis,
            "reject_null": impact.reject_null,
            "effect_size": impact.effect_size,
            "p_positive": impact.p_positive,
            "p_negative": impact.p_negative,
            "p_negligible": impact.p_negligible,
            "upside_vs_downside": impact.upside_vs_downside,
        }

        # Step 5: Generate caveats
        caveats_list = generate_caveats(
            business, question, persona_count, len(responses),
            variant_a, variant_b, review_signals=review_signals,
        )
        caveats_data = [
            {"type": c.type, "title": c.title, "message": c.message,
             "severity": c.severity, "source": c.source}
            for c in caveats_list
        ]

        # Persist impact + caveats
        _update_sim(sim_id, impact_data=impact_data, caveats=caveats_data)

        # Normalize themes and standout_voices
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
                    or v.get("stated_reaction")
                    or v.get("what_they_said")
                    or v.get("core_reaction")
                    or v.get("summary")
                    or v.get("insight")
                    or str(v.get("contrast", ""))
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
            baseline_summary=result_data.get("baseline_summary"),
            behavioral_prediction=result_data.get("behavioral_prediction"),
            stated_vs_actual_gap=result_data.get("stated_vs_actual_gap"),
            raw_output=result_data.get("raw_output", {}),
            created_at=datetime.now(timezone.utc),
        )

        _store_result(result)

        # Mark simulation as completed
        _update_sim(
            sim_id,
            status=SimulationStatus.COMPLETED.value,
            completed_at=datetime.now(timezone.utc).isoformat(),
        )
        progress.status = SimulationStatus.COMPLETED
        progress.step = "Complete"
        progress.elapsed_seconds = time.monotonic() - start
        emit_sse("complete", "Your results are ready")

        logger.info("Simulation %s completed in %.1fs", sim_id, progress.elapsed_seconds)

    except Exception as e:
        logger.exception("Simulation %s failed: %s", sim_id, e)
        _update_sim(
            sim_id,
            status=SimulationStatus.FAILED.value,
            error_message=str(e),
        )
        progress.status = SimulationStatus.FAILED
        progress.step = f"Failed: {str(e)[:100]}"
        emit_sse("failed", f"Simulation failed: {str(e)[:100]}")

    finally:
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


# --- Read endpoints ---

@router.get("/{sim_id}", response_model=Simulation)
async def get_simulation(sim_id: UUID):
    db = get_supabase()
    result = (
        db.table("simulations")
        .select("*")
        .eq("id", str(sim_id))
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return _row_to_sim(result.data)


@router.get("/{sim_id}/progress", response_model=SimulationProgress)
async def get_simulation_progress(sim_id: UUID):
    """Poll this endpoint for live progress updates (fallback for SSE)."""
    progress = _simulation_progress.get(sim_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return progress


@router.get("/{sim_id}/context")
async def get_simulation_context(sim_id: UUID):
    """Return the BusinessContext gathered for this simulation."""
    db = get_supabase()
    result = (
        db.table("simulations")
        .select("context_data")
        .eq("id", str(sim_id))
        .maybe_single()
        .execute()
    )
    if not result.data or not result.data.get("context_data"):
        raise HTTPException(status_code=404, detail="Context not found")
    return result.data["context_data"]


@router.get("/{sim_id}/caveats")
async def get_simulation_caveats(sim_id: UUID):
    """Return caveats generated for this simulation."""
    db = get_supabase()
    result = (
        db.table("simulations")
        .select("caveats")
        .eq("id", str(sim_id))
        .maybe_single()
        .execute()
    )
    if not result.data or result.data.get("caveats") is None:
        raise HTTPException(status_code=404, detail="Caveats not found")
    return result.data["caveats"]


@router.get("/{sim_id}/reviewer-intelligence")
async def get_simulation_reviewer_intel(sim_id: UUID):
    """Return the reviewer intelligence analysis for this simulation."""
    db = get_supabase()
    result = (
        db.table("simulations")
        .select("reviewer_intel")
        .eq("id", str(sim_id))
        .maybe_single()
        .execute()
    )
    if not result.data or not result.data.get("reviewer_intel"):
        raise HTTPException(status_code=404, detail="No reviewer intelligence for this simulation")
    return result.data["reviewer_intel"]


@router.get("/{sim_id}/impact")
async def get_simulation_impact(sim_id: UUID):
    """Return quantitative impact estimates with confidence intervals."""
    db = get_supabase()
    result = (
        db.table("simulations")
        .select("impact_data")
        .eq("id", str(sim_id))
        .maybe_single()
        .execute()
    )
    if not result.data or not result.data.get("impact_data"):
        raise HTTPException(status_code=404, detail="No impact estimate for this simulation")
    return result.data["impact_data"]


@router.get("/{sim_id}/demographics")
async def get_simulation_demographics(sim_id: UUID):
    """Return persona responses grouped by demographic segment."""
    db = get_supabase()

    # Get personas with their profiles
    personas_result = (
        db.table("personas")
        .select("*")
        .eq("simulation_id", str(sim_id))
        .execute()
    )
    if not personas_result.data:
        raise HTTPException(status_code=404, detail="No personas found")

    # Get responses
    responses_result = (
        db.table("persona_responses")
        .select("*")
        .eq("simulation_id", str(sim_id))
        .execute()
    )

    # Build persona lookup
    persona_map = {}
    for row in personas_result.data:
        profile = row.get("profile") or {}
        persona_map[row["id"]] = {
            "name": row["name"],
            "age": row["age"],
            "segment": profile.get("segment", "Unknown"),
            "income_tier": profile.get("income_tier"),
            "price_sensitivity": profile.get("price_sensitivity"),
        }

    # Group responses by segment
    groups: dict[str, list] = {}
    for resp in (responses_result.data or []):
        persona_info = persona_map.get(resp.get("persona_id"), {})
        segment = persona_info.get("segment", "Unknown")
        if segment not in groups:
            groups[segment] = []
        sentiment = resp.get("sentiment") or 0
        groups[segment].append({
            "persona_name": persona_info.get("name", "Unknown"),
            "age": persona_info.get("age"),
            "sentiment": float(sentiment),
            "raw_output": resp.get("raw_output"),
        })

    # Build summary
    result = []
    for segment, members in groups.items():
        avg_sent = sum(m["sentiment"] for m in members) / max(len(members), 1)
        result.append({
            "group": segment,
            "count": len(members),
            "avg_sentiment": round(avg_sent, 2),
            "personas": [m["persona_name"] for m in members],
            "members": members,
        })

    result.sort(key=lambda g: g["count"], reverse=True)
    return result


@router.get("/{sim_id}/personas", response_model=list[PersonaProfile])
async def get_simulation_personas(sim_id: UUID):
    db = get_supabase()
    result = (
        db.table("personas")
        .select("*")
        .eq("simulation_id", str(sim_id))
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Personas not found")
    return [_row_to_persona(row) for row in result.data]


@router.get("/{sim_id}/responses")
async def get_simulation_responses(sim_id: UUID):
    db = get_supabase()
    result = (
        db.table("persona_responses")
        .select("*")
        .eq("simulation_id", str(sim_id))
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Responses not found")
    return result.data


@router.get("/{sim_id}/result", response_model=SimulationResult)
async def get_simulation_result(sim_id: UUID):
    db = get_supabase()
    result = (
        db.table("simulation_results")
        .select("*")
        .eq("simulation_id", str(sim_id))
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Result not found")
    return _row_to_result(result.data)


@router.get("/", response_model=list[Simulation])
async def list_simulations(user_id: UUID = Depends(get_current_user_id)):
    db = get_supabase()
    # Get simulations for businesses owned by this user
    biz_result = (
        db.table("businesses")
        .select("id")
        .eq("user_id", str(user_id))
        .execute()
    )
    biz_ids = [b["id"] for b in biz_result.data]
    if not biz_ids:
        return []
    result = (
        db.table("simulations")
        .select("*")
        .in_("business_id", biz_ids)
        .execute()
    )
    return [_row_to_sim(row) for row in result.data]


@router.get("/accuracy-stats")
async def get_accuracy_stats(user_id: UUID = Depends(get_current_user_id)):
    """Return accuracy stats from real_outcomes table."""
    db = get_supabase()
    # Get user's business IDs
    biz_result = db.table("businesses").select("id").eq("user_id", str(user_id)).execute()
    biz_ids = [b["id"] for b in biz_result.data]
    if not biz_ids:
        return {"total_outcomes": 0, "matched": 0, "accuracy_pct": None}

    # Get simulation IDs for those businesses
    sim_result = db.table("simulations").select("id").in_("business_id", biz_ids).execute()
    sim_ids = [s["id"] for s in sim_result.data]
    if not sim_ids:
        return {"total_outcomes": 0, "matched": 0, "accuracy_pct": None}

    # Get real outcomes
    outcomes = db.table("real_outcomes").select("*").in_("simulation_id", sim_ids).execute()
    total = len(outcomes.data)
    matched = len([o for o in outcomes.data if o.get("outcome_matched")])

    return {
        "total_outcomes": total,
        "matched": matched,
        "accuracy_pct": round((matched / total) * 100) if total > 0 else None,
    }


class RealOutcomeCreate(BaseModel):
    simulation_id: str
    what_actually_happened: str
    outcome_matched: Optional[bool] = None
    match_details: Optional[str] = None
    notes: Optional[str] = None


@router.post("/{sim_id}/outcome")
async def submit_real_outcome(
    sim_id: UUID,
    data: RealOutcomeCreate,
    user_id: UUID = Depends(get_current_user_id),
):
    """Submit what actually happened after a simulation prediction."""
    db = get_supabase()

    # Verify simulation belongs to user's business
    sim = db.table("simulations").select("business_id").eq("id", str(sim_id)).maybe_single().execute()
    if not sim.data:
        raise HTTPException(status_code=404, detail="Simulation not found")

    biz = db.table("businesses").select("id").eq("id", sim.data["business_id"]).eq("user_id", str(user_id)).maybe_single().execute()
    if not biz.data:
        raise HTTPException(status_code=404, detail="Business not found")

    outcome = {
        "simulation_id": str(sim_id),
        "what_actually_happened": data.what_actually_happened,
        "outcome_matched": data.outcome_matched,
        "match_details": data.match_details,
        "notes": data.notes,
    }
    result = db.table("real_outcomes").insert(outcome).execute()
    return result.data[0] if result.data else {"status": "saved"}
