"""Phase 0 RED: secret hygiene tests.

These tests enforce that:
  1. .env files are gitignored (cannot be accidentally committed).
  2. No tracked file in the repo contains a real-looking secret.
  3. backend/.env.example has an entry for every field on Settings
     (so a new developer can copy it and boot the app).

They run entirely against the filesystem + `git ls-files`. No network.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from backend.config import Settings


REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _git_tracked_files() -> list[Path]:
    """Return every file currently tracked by git, as absolute Paths."""
    out = subprocess.check_output(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        text=True,
    )
    return [REPO_ROOT / line for line in out.splitlines() if line]


# Patterns that look like real secrets.
# The trailing character class requires at least one alphanumeric after the
# prefix, so obvious placeholders like "sk-ant-xxxxx" or "eyxxxxx" still don't
# match (they contain only 'x' after the prefix).
def _is_alpha_vantage_shaped(candidate: str) -> bool:
    """Match 16-char uppercase alnum with >=4 letters and >=1 digit."""
    if not re.fullmatch(r"[A-Z0-9]{16}", candidate):
        return False
    letters = sum(1 for c in candidate if c.isalpha())
    digits = sum(1 for c in candidate if c.isdigit())
    return letters >= 4 and digits >= 1


SECRET_PATTERNS: dict[str, tuple[re.Pattern[str], callable]] = {
    # Anthropic: sk-ant-api03-<base64-ish, 20+ chars after prefix>
    "anthropic_api_key": (
        re.compile(r"sk-ant-[a-zA-Z0-9_-]{20,}"),
        lambda s: True,
    ),
    # JWT (Supabase anon/service key shape): three dot-separated base64url parts
    "jwt": (
        re.compile(
            r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"
        ),
        lambda s: True,
    ),
    # FRED API keys are 32 hex chars. Exclude all-zero strings etc.
    "fred_hex32": (
        re.compile(r"\b[a-f0-9]{32}\b"),
        lambda s: len(set(s)) >= 4,  # enough entropy to look like a real key
    ),
    # Alpha Vantage: 16 char uppercase alnum with mixed letters + digits.
    "alpha_vantage": (
        re.compile(r"\b[A-Z0-9]{16}\b"),
        _is_alpha_vantage_shaped,
    ),
}


# Files/dirs where secret-shaped strings are expected and safe (commit hashes,
# generated fixtures, etc.) — explicit allowlist so future files do NOT
# automatically get an exemption.
ALLOWED_SECRET_SHAPED_PATHS: set[str] = {
    # migration hashes, git sha references etc. can be added here as needed
}


# ---------------------------------------------------------------------------
# 1. .env is gitignored
# ---------------------------------------------------------------------------


def test_env_is_gitignored():
    gitignore = (REPO_ROOT / ".gitignore").read_text()
    assert re.search(r"^\.env\b", gitignore, re.MULTILINE), (
        ".env must be listed in .gitignore so real secrets cannot be committed"
    )


def test_backend_env_not_tracked():
    """backend/.env and root .env must not be in git's index."""
    tracked = {p.relative_to(REPO_ROOT).as_posix() for p in _git_tracked_files()}
    forbidden = {".env", "backend/.env", "frontend/.env", "frontend/.env.local"}
    leaked = forbidden & tracked
    assert not leaked, f"These env files are tracked by git and must not be: {leaked}"


# ---------------------------------------------------------------------------
# 2. No real-looking secrets in tracked files
# ---------------------------------------------------------------------------


def _files_git_would_add() -> list[Path]:
    """Files that `git add .` would stage right now.

    Returns tracked + untracked files that are NOT ignored by .gitignore.
    This is the true commit-risk surface.
    """
    out = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=REPO_ROOT,
        text=True,
    )
    return [REPO_ROOT / line for line in out.splitlines() if line]


@pytest.mark.parametrize("pattern_name", list(SECRET_PATTERNS.keys()))
def test_no_real_secrets_in_commit_risk_files(pattern_name):
    """Scan all files that a `git add .` would stage (tracked + untracked,
    not gitignored). These are the files at real risk of leakage."""
    pattern, validator = SECRET_PATTERNS[pattern_name]
    offenders: list[tuple[str, str]] = []

    for path in _files_git_would_add():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in ALLOWED_SECRET_SHAPED_PATHS:
            continue
        if path.suffix.lower() in {
            ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".woff",
            ".woff2", ".ttf", ".otf", ".zip", ".gz", ".pkl", ".joblib",
            ".bin", ".so", ".dylib", ".mp4", ".mov", ".webp",
        }:
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if b"\x00" in raw[:8192]:
            continue
        try:
            text = raw.decode("utf-8", errors="ignore")
        except UnicodeDecodeError:
            continue
        for match in pattern.finditer(text):
            snippet = match.group(0)
            if not validator(snippet):
                continue
            if re.fullmatch(r"[x0]+", snippet, re.IGNORECASE):
                continue
            offenders.append((rel, snippet[:8] + "..."))

    assert not offenders, (
        f"Possible {pattern_name} secret(s) in files a bare `git add .` "
        f"would stage. Redact or gitignore: {offenders}"
    )


@pytest.mark.parametrize("pattern_name", list(SECRET_PATTERNS.keys()))
def test_no_real_secrets_in_tracked_files(pattern_name):
    """Scan every tracked text file for secret-shaped strings."""
    pattern, validator = SECRET_PATTERNS[pattern_name]
    offenders: list[tuple[str, str]] = []

    for path in _git_tracked_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in ALLOWED_SECRET_SHAPED_PATHS:
            continue
        # Skip known binary extensions fast
        if path.suffix.lower() in {
            ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".woff",
            ".woff2", ".ttf", ".otf", ".zip", ".gz", ".pkl", ".joblib",
            ".bin", ".so", ".dylib", ".mp4", ".mov", ".webp",
        }:
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        # Binary content detector: NULL byte in first 8KB
        if b"\x00" in raw[:8192]:
            continue
        try:
            text = raw.decode("utf-8", errors="ignore")
        except UnicodeDecodeError:
            continue

        for match in pattern.finditer(text):
            snippet = match.group(0)
            if not validator(snippet):
                continue
            # Skip obvious placeholders (all-x, all-zero, etc.)
            if re.fullmatch(r"[x0]+", snippet, re.IGNORECASE):
                continue
            offenders.append((rel, snippet[:8] + "..."))

    assert not offenders, (
        f"Possible {pattern_name} secret(s) found in tracked files: {offenders}"
    )


# ---------------------------------------------------------------------------
# 3. .env.example is complete
# ---------------------------------------------------------------------------


def _read_env_example_keys() -> set[str]:
    example = REPO_ROOT / "backend" / ".env.example"
    assert example.exists(), "backend/.env.example must exist"
    keys = set()
    for line in example.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            keys.add(line.split("=", 1)[0].strip().upper())
    return keys


def test_env_example_covers_every_settings_field():
    """Every field on Settings() must have a matching key in .env.example."""
    example_keys = _read_env_example_keys()
    missing: list[str] = []
    for field_name in Settings.model_fields:
        if field_name.startswith("model_"):  # pydantic internal
            continue
        if field_name.upper() not in example_keys:
            missing.append(field_name)

    assert not missing, (
        f"backend/.env.example is missing keys for Settings fields: {missing}"
    )
