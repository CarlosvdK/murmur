"""
Real-outcome learning loop.

When users submit what actually happened via
``POST /simulations/{id}/outcome``, those rows should not just sit in a
table -- they should update the bias-correction priors so that the next
simulation is measurably better calibrated than the last.

This module is the SCAFFOLD. It is intentionally minimal and offline
-- it should run as a cron job, not inside a request. Wiring it to
Supabase happens when the migration and outcome-submission UI have
collected ~30+ rows.

What it does:
1. Pull all (simulation, outcome) pairs from Supabase.
2. Group by ``tactic`` (from the stored ``research_override.tactic_detected``).
3. For each tactic, fit the per-tactic sentiment shift that would have
   correctly flipped the wrong ones without flipping the right ones.
4. Produce a proposed updated ``TACTIC_CORRECTIONS`` table and write
   it to ``backend/ml/saved_models/tactic_corrections_fitted.json`` for
   review before hot-deploying.

This is deliberately NOT auto-deploying the new priors. The fit is
shown to the operator, who promotes it manually. This prevents a bad
fit from silently wrecking the live product.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


SAVED_MODELS_DIR = Path(__file__).parent / "saved_models"
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
FIT_OUTPUT_PATH = SAVED_MODELS_DIR / "tactic_corrections_fitted.json"


@dataclass
class OutcomeRow:
    """One (simulation, outcome) pair used for learning."""
    simulation_id: str
    tactic: Optional[str]
    our_winner: Optional[str]           # "A" | "B" | "tie" | "positive" | "negative"
    real_outcome: str                   # free-text description of what happened
    outcome_matched: Optional[bool]     # user-submitted label
    stated_sentiment: Optional[float]
    revealed_sentiment: Optional[float]
    decision: Optional[str]
    question: Optional[str]


def _fetch_outcome_rows() -> list[OutcomeRow]:
    """Pull rows from Supabase. Returns an empty list if the client is
    unavailable or the table is empty.

    We defer importing Supabase until call time so this module can be
    imported in environments where the client is not configured.
    """
    try:
        from backend.db.supabase_client import get_supabase_client  # type: ignore
    except ImportError:
        logger.warning(
            "No Supabase client available -- outcome learner cannot fetch rows"
        )
        return []

    try:
        db = get_supabase_client()
    except Exception:
        logger.exception("Supabase client init failed")
        return []

    try:
        outcomes = db.table("real_outcomes").select("*").execute()
        sims = {}
        if outcomes.data:
            sim_ids = list({o["simulation_id"] for o in outcomes.data if o.get("simulation_id")})
            if sim_ids:
                sim_rows = (
                    db.table("simulations").select("*").in_("id", sim_ids).execute()
                )
                sims = {s["id"]: s for s in (sim_rows.data or [])}
    except Exception:
        logger.exception("Failed to fetch outcome rows")
        return []

    rows: list[OutcomeRow] = []
    for o in outcomes.data or []:
        sim = sims.get(o.get("simulation_id"), {}) or {}
        result = sim.get("result") or {}
        override = result.get("research_override") or {}
        rows.append(OutcomeRow(
            simulation_id=o.get("simulation_id", ""),
            tactic=override.get("tactic_detected"),
            our_winner=result.get("winner"),
            real_outcome=o.get("real_outcome", "") or "",
            outcome_matched=o.get("outcome_matched"),
            stated_sentiment=_avg_sentiment_from_sim(sim, key="sentiment"),
            revealed_sentiment=_avg_sentiment_from_sim(sim, key="actual_sentiment"),
            decision=result.get("decision"),
            question=sim.get("question"),
        ))
    return rows


def _avg_sentiment_from_sim(sim: dict, key: str) -> Optional[float]:
    responses = sim.get("responses") or []
    vals: list[float] = []
    for r in responses:
        v = (r.get("core") or {}).get(key)
        if v is None:
            v = r.get(key)
        try:
            if v is not None:
                vals.append(float(v))
        except (TypeError, ValueError):
            pass
    return sum(vals) / len(vals) if vals else None


def fit_corrections(
    rows: list[OutcomeRow], min_rows_per_tactic: int = 5,
) -> dict[str, dict]:
    """Propose an updated per-tactic stated-to-revealed shift.

    The fit is deliberately simple:
      - For each tactic, gather rows where ``outcome_matched`` is not None.
      - Count how often we were wrong.
      - If ``wrong_rate > 0.5`` AND stated_sentiment is available, propose
        a shift toward the direction that would have flipped wrongs without
        flipping rights.
      - Keep the existing prior if fewer than ``min_rows_per_tactic`` rows.

    Returns a mapping tactic -> proposed correction dict with keys:
      stated_to_revealed_shift, n_rows, wrong_rate, confidence.
    """
    by_tactic: dict[str, list[OutcomeRow]] = {}
    for r in rows:
        if not r.tactic:
            continue
        by_tactic.setdefault(r.tactic, []).append(r)

    proposals: dict[str, dict] = {}
    for tactic, trows in by_tactic.items():
        labelled = [t for t in trows if t.outcome_matched is not None]
        n = len(labelled)
        if n < min_rows_per_tactic:
            proposals[tactic] = {
                "n_rows": n,
                "status": "insufficient_data",
                "min_required": min_rows_per_tactic,
            }
            continue

        wrong = sum(1 for t in labelled if t.outcome_matched is False)
        wrong_rate = wrong / n

        # Direction of the proposed shift: if most wrongs are cases where
        # we predicted the tactic would hurt (negative winner / avoid) but
        # the reality was positive, the shift should be positive. We proxy
        # this with stated_sentiment: if the average stated sentiment on
        # the wrong cases is noticeably negative, push the correction up.
        wrong_rows = [t for t in labelled if t.outcome_matched is False]
        if wrong_rows:
            stated_avg = sum(
                (t.stated_sentiment or 0.0) for t in wrong_rows
            ) / len(wrong_rows)
        else:
            stated_avg = 0.0

        # Simple rule: a strong proposal is triggered only when the product
        # is clearly miscalibrated (>50% wrong) AND the wrongs share a
        # directional bias. Proposed magnitude is bounded to [-0.35, +0.35].
        proposed_shift = 0.0
        status = "no_change"
        if wrong_rate > 0.5 and stated_avg < -0.1:
            proposed_shift = min(0.35, 0.1 + wrong_rate * 0.3)
            status = "propose_increase"
        elif wrong_rate > 0.5 and stated_avg > 0.1:
            proposed_shift = max(-0.35, -0.1 - wrong_rate * 0.3)
            status = "propose_decrease"

        proposals[tactic] = {
            "n_rows": n,
            "wrong_rate": round(wrong_rate, 3),
            "stated_avg_on_wrongs": round(stated_avg, 3),
            "proposed_shift_delta": round(proposed_shift, 3),
            "status": status,
        }

    return proposals


def run_learning_cycle() -> dict:
    """Pull outcomes, fit a proposal, write it to disk for review.

    This is the entry point for a scheduled job. It NEVER mutates the
    live correction table -- promotion is a manual step after reviewing
    the fitted JSON.
    """
    rows = _fetch_outcome_rows()
    logger.info("outcome_learner: loaded %d rows", len(rows))

    proposals = fit_corrections(rows)

    payload = {
        "n_rows_total": len(rows),
        "proposals": proposals,
    }
    FIT_OUTPUT_PATH.write_text(json.dumps(payload, indent=2))
    logger.info("outcome_learner: wrote proposals to %s", FIT_OUTPUT_PATH)
    return payload


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(run_learning_cycle(), indent=2))
