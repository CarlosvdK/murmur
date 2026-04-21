"""Phase 6 RED: migration runner.

The Postgres schema is currently applied by hand-copying SQL files into
Supabase's SQL editor. For production we need an idempotent runner that:
  1. Creates a `schema_migrations` table to track which files ran.
  2. Applies pending migrations in filename order.
  3. Refuses to re-run already-applied migrations.

Tests run the runner against a fake Supabase client so they don't hit a
real database.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


class FakeSupabase:
    """Minimal in-memory Supabase stand-in for the runner."""

    def __init__(self):
        self.applied: list[str] = []  # versions recorded in schema_migrations
        self.sql_executed: list[str] = []
        self.table_exists = False

    def rpc(self, fn: str, params: dict):
        # The runner uses rpc("exec_sql", {"sql": "..."}) to run arbitrary SQL.
        sql = params.get("sql", "")
        self.sql_executed.append(sql)
        if "schema_migrations" in sql and "CREATE TABLE" in sql.upper():
            self.table_exists = True
        result = MagicMock()
        result.execute.return_value = MagicMock(data=[])
        return result

    def table(self, name: str):
        assert name == "schema_migrations"
        t = MagicMock()

        def select(*_a, **_kw):
            s = MagicMock()
            rows = [{"version": v} for v in self.applied]
            s.execute.return_value = MagicMock(data=rows)
            return s

        def insert(row):
            self.applied.append(row["version"])
            i = MagicMock()
            i.execute.return_value = MagicMock(data=[row])
            return i

        t.select.side_effect = select
        t.insert.side_effect = insert
        return t


# ---------------------------------------------------------------------------
# 1. schema_migrations table is created on first run
# ---------------------------------------------------------------------------


def test_runner_creates_schema_migrations_table_on_first_run():
    from backend.db.migrate import run_migrations

    fake = FakeSupabase()
    run_migrations(db=fake, migrations_dir=REPO_ROOT / "backend" / "db", dry_run=True)
    # The runner must emit a CREATE TABLE IF NOT EXISTS schema_migrations on first use.
    combined = "\n".join(fake.sql_executed)
    assert "schema_migrations" in combined.lower()
    assert "create table" in combined.lower()


# ---------------------------------------------------------------------------
# 2. Pending migrations are discovered in order
# ---------------------------------------------------------------------------


def test_runner_lists_pending_migrations_in_filename_order(tmp_path):
    from backend.db.migrate import list_pending_migrations

    # Create synthetic SQL files out of order
    (tmp_path / "migration_005_thing.sql").write_text("-- 5")
    (tmp_path / "migration_002_other.sql").write_text("-- 2")
    (tmp_path / "migration_007_simulation_accuracy.sql").write_text("-- 7")
    (tmp_path / "README.md").write_text("not-sql")

    pending = list_pending_migrations(tmp_path, applied=set())
    names = [p.name for p in pending]
    assert names == [
        "migration_002_other.sql",
        "migration_005_thing.sql",
        "migration_007_simulation_accuracy.sql",
    ]


def test_runner_excludes_already_applied_migrations(tmp_path):
    from backend.db.migrate import list_pending_migrations

    (tmp_path / "migration_002_other.sql").write_text("-- 2")
    (tmp_path / "migration_005_thing.sql").write_text("-- 5")

    pending = list_pending_migrations(
        tmp_path, applied={"migration_002_other"}
    )
    assert [p.name for p in pending] == ["migration_005_thing.sql"]


# ---------------------------------------------------------------------------
# 3. Running twice is a no-op
# ---------------------------------------------------------------------------


def test_runner_is_idempotent(tmp_path):
    from backend.db.migrate import run_migrations

    (tmp_path / "migration_002_other.sql").write_text("SELECT 1;")
    (tmp_path / "migration_005_thing.sql").write_text("SELECT 2;")

    fake = FakeSupabase()

    run_migrations(db=fake, migrations_dir=tmp_path)
    first_run = list(fake.applied)
    first_sql_count = len(fake.sql_executed)

    run_migrations(db=fake, migrations_dir=tmp_path)
    second_run = list(fake.applied)

    # Same versions, and no new migration SQL between the two runs
    # (the bootstrap CREATE TABLE may fire both times but that's fine).
    assert first_run == second_run == ["migration_002_other", "migration_005_thing"]
    # No new user-migration SQL files executed on the second run.
    new_sql = fake.sql_executed[first_sql_count:]
    for sql in new_sql:
        assert "SELECT 1" not in sql
        assert "SELECT 2" not in sql
