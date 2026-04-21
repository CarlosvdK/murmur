"""Minimal idempotent migration runner.

Applies `migration_*.sql` files under backend/db/ (or an explicit directory)
in lexical order, recording each applied filename in a `schema_migrations`
table so re-runs are a no-op.

Supabase's Python SDK does not expose arbitrary SQL by default; production
setups enable an `exec_sql` RPC. Tests substitute a fake client.

Usage:
    python -m backend.db.migrate                # apply pending
    python -m backend.db.migrate --dry-run      # list pending only
"""
from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path
from typing import Iterable, Protocol

logger = logging.getLogger(__name__)

_DEFAULT_DIR = Path(__file__).resolve().parent
_MIGRATION_RE = re.compile(r"^migration_\d+.*\.sql$")

_BOOTSTRAP_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
""".strip()


class _DBLike(Protocol):
    def rpc(self, fn: str, params: dict): ...
    def table(self, name: str): ...


def _migration_version(path: Path) -> str:
    return path.stem  # e.g. "migration_007_simulation_accuracy"


def list_pending_migrations(
    migrations_dir: Path,
    applied: Iterable[str],
) -> list[Path]:
    """Return migration files (sorted) that are not in `applied`."""
    applied_set = set(applied)
    all_files = [
        p for p in migrations_dir.iterdir()
        if p.is_file() and _MIGRATION_RE.match(p.name)
    ]
    pending = [p for p in all_files if _migration_version(p) not in applied_set]
    return sorted(pending, key=lambda p: p.name)


def _ensure_bootstrap(db: _DBLike) -> None:
    db.rpc("exec_sql", {"sql": _BOOTSTRAP_SQL}).execute()


def _applied_versions(db: _DBLike) -> set[str]:
    try:
        res = db.table("schema_migrations").select("version").execute()
    except Exception as exc:  # pragma: no cover
        logger.warning("schema_migrations read failed (treating as empty): %s", exc)
        return set()
    rows = getattr(res, "data", None) or []
    return {row["version"] for row in rows if row.get("version")}


def run_migrations(
    *,
    db: _DBLike,
    migrations_dir: Path | None = None,
    dry_run: bool = False,
) -> list[str]:
    """Apply every pending migration once. Returns versions that ran."""
    migrations_dir = migrations_dir or _DEFAULT_DIR
    _ensure_bootstrap(db)
    applied = _applied_versions(db)
    pending = list_pending_migrations(migrations_dir, applied)

    ran: list[str] = []
    for path in pending:
        version = _migration_version(path)
        if dry_run:
            logger.info("DRY-RUN pending: %s", version)
            ran.append(version)
            continue
        sql = path.read_text()
        logger.info("Applying migration %s (%d bytes)", version, len(sql))
        db.rpc("exec_sql", {"sql": sql}).execute()
        db.table("schema_migrations").insert({"version": version}).execute()
        ran.append(version)
    return ran


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--dir", type=Path, default=_DEFAULT_DIR)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    from backend.db.client import get_supabase

    ran = run_migrations(db=get_supabase(), migrations_dir=args.dir, dry_run=args.dry_run)
    if not ran:
        logger.info("No pending migrations.")
    else:
        action = "Would apply" if args.dry_run else "Applied"
        for v in ran:
            logger.info("%s: %s", action, v)


if __name__ == "__main__":
    main()
