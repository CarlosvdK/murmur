"""Compute a structured accuracy record for a simulation given the
real outcome the user reported.

Kept deliberately small and pure so it's trivially reusable from:
  - POST /simulations/{id}/outcome (live user report)
  - backtest_runner.py (historical A/B cases)

The shape returned matches the simulation_accuracy table's columns so a
caller can insert it directly.
"""
from __future__ import annotations

from typing import Any


def compute_simulation_accuracy(
    *,
    result: dict[str, Any],
    outcome: dict[str, Any],
) -> dict[str, Any]:
    """Compare a SimulationResult-shaped dict with a real_outcomes-shaped dict.

    Returns a dict with:
      - accuracy_pct:       100.0 | 0.0 | None  (None = we can't tell yet)
      - actual_matched:     True | False | None
      - predicted_winner:   echoed from result
      - predicted_confidence: echoed from result
      - predicted_summary:  echoed (trimmed) from result
      - match_details:      echoed from outcome
    """
    matched = outcome.get("outcome_matched")
    if matched is True:
        accuracy_pct: float | None = 100.0
    elif matched is False:
        accuracy_pct = 0.0
    else:
        accuracy_pct = None

    summary = (result.get("summary") or "")[:500] or None

    return {
        "accuracy_pct": accuracy_pct,
        "actual_matched": matched if isinstance(matched, bool) else None,
        "predicted_winner": result.get("winner"),
        "predicted_confidence": result.get("confidence_score"),
        "predicted_summary": summary,
        "match_details": outcome.get("match_details"),
    }
