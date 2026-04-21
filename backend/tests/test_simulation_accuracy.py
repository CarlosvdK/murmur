"""Phase 2b RED: structured simulation accuracy storage.

When a user reports the real outcome of a past simulation, we need to
persist a structured accuracy record (not just a boolean on real_outcomes)
so we can track calibration over time per business type, confidence band,
scenario type etc.

Contract:
  1. A migration file exists creating a `simulation_accuracy` table.
  2. `backend.ml.accuracy.compute_simulation_accuracy(predicted, outcome)`
     returns a dict with accuracy_pct, predicted_winner, actual_matched.
  3. Submitting an outcome inserts one accuracy row alongside the
     existing real_outcomes row.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# 1. Migration file
# ---------------------------------------------------------------------------


def test_simulation_accuracy_migration_file_exists():
    candidates = list(
        (REPO_ROOT / "backend" / "db").glob("migration_*simulation_accuracy*.sql")
    ) + list(
        (REPO_ROOT / "backend" / "db" / "migrations").glob("*simulation_accuracy*.sql")
    )
    assert candidates, (
        "Expected a migration file defining the simulation_accuracy table "
        "under backend/db/ or backend/db/migrations/"
    )


def test_simulation_accuracy_migration_has_expected_columns():
    sql_files = list(
        (REPO_ROOT / "backend" / "db").glob("migration_*simulation_accuracy*.sql")
    ) + list(
        (REPO_ROOT / "backend" / "db" / "migrations").glob("*simulation_accuracy*.sql")
    )
    assert sql_files, "migration file missing"
    body = sql_files[0].read_text().lower()
    assert "create table" in body and "simulation_accuracy" in body
    # Required columns
    for col in ("simulation_id", "accuracy_pct", "predicted_winner", "actual_matched", "created_at"):
        assert col in body, f"migration is missing column `{col}`"


# ---------------------------------------------------------------------------
# 2. compute_simulation_accuracy helper
# ---------------------------------------------------------------------------


def test_compute_accuracy_matched_true_returns_100():
    from backend.ml.accuracy import compute_simulation_accuracy

    record = compute_simulation_accuracy(
        result={
            "confidence_score": "high",
            "winner": "A",
            "summary": "A wins decisively",
        },
        outcome={"outcome_matched": True, "what_actually_happened": "A won"},
    )
    assert record["accuracy_pct"] == 100.0
    assert record["actual_matched"] is True
    assert record["predicted_winner"] == "A"
    assert record["predicted_confidence"] == "high"


def test_compute_accuracy_matched_false_returns_0():
    from backend.ml.accuracy import compute_simulation_accuracy

    record = compute_simulation_accuracy(
        result={"confidence_score": "medium", "winner": "B"},
        outcome={"outcome_matched": False, "what_actually_happened": "A won"},
    )
    assert record["accuracy_pct"] == 0.0
    assert record["actual_matched"] is False


def test_compute_accuracy_unknown_match_defaults_to_null():
    from backend.ml.accuracy import compute_simulation_accuracy

    record = compute_simulation_accuracy(
        result={"confidence_score": "low", "winner": None},
        outcome={"outcome_matched": None, "what_actually_happened": "mixed results"},
    )
    # None -> we report unknown, not 0 (can't tell is NOT wrong)
    assert record["accuracy_pct"] is None
    assert record["actual_matched"] is None


def test_compute_accuracy_never_throws_on_sparse_input():
    """Real-world outcomes often arrive with missing fields."""
    from backend.ml.accuracy import compute_simulation_accuracy

    record = compute_simulation_accuracy(result={}, outcome={})
    assert isinstance(record, dict)
    assert "accuracy_pct" in record


# ---------------------------------------------------------------------------
# 3. Outcome submit writes one accuracy row
# ---------------------------------------------------------------------------


def test_submit_outcome_also_inserts_simulation_accuracy_row():
    """After POST /simulations/{id}/outcome we expect TWO DB inserts:
    real_outcomes AND simulation_accuracy."""
    from fastapi.testclient import TestClient
    from backend.api.main import app

    fake_db = MagicMock()

    # /simulations/{id}/outcome path reads:
    #   simulations -> business_id
    #   businesses  -> user ownership
    #   real_outcomes.insert(...)
    #   simulation_results -> latest result for this sim   <-- new
    #   simulation_accuracy.insert(...)                   <-- new
    sim_chain = fake_db.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute
    sim_chain.return_value = MagicMock(data={"business_id": "biz-uuid"})

    insert_calls: list[tuple[str, dict]] = []

    def table_router(name: str):
        m = MagicMock()
        # select().eq().maybe_single().execute() for sim + business ownership
        m.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
            data={"business_id": "biz-uuid", "id": "biz-uuid"}
        )
        # select().eq().order().limit().maybe_single().execute() for latest result
        m.select.return_value.eq.return_value.order.return_value.limit.return_value.maybe_single.return_value.execute.return_value = MagicMock(
            data={
                "id": "res-uuid",
                "confidence_score": "high",
                "winner": "A",
                "summary": "A wins",
            }
        )
        # Also support .single() variants
        m.select.return_value.eq.return_value.order.return_value.limit.return_value.single.return_value.execute.return_value = MagicMock(
            data={
                "id": "res-uuid",
                "confidence_score": "high",
                "winner": "A",
                "summary": "A wins",
            }
        )

        def _insert(row):
            insert_calls.append((name, row))
            i = MagicMock()
            i.execute.return_value = MagicMock(data=[row])
            return i

        m.insert.side_effect = _insert
        return m

    fake_db.table.side_effect = table_router

    with patch("backend.api.routes.simulations.get_supabase", return_value=fake_db):
        client = TestClient(app)
        resp = client.post(
            "/api/simulations/00000000-0000-0000-0000-000000000001/outcome",
            json={
                "what_actually_happened": "A won by 12%",
                "outcome_matched": True,
                "match_details": "matched high-confidence prediction",
            },
        )
    assert resp.status_code in (200, 201), resp.text
    tables_inserted = [name for name, _ in insert_calls]
    assert "real_outcomes" in tables_inserted
    assert "simulation_accuracy" in tables_inserted, (
        f"expected an insert into simulation_accuracy, saw: {tables_inserted}"
    )
