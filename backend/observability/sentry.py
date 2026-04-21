"""Sentry SDK initialisation.

No-op when SENTRY_DSN isn't set so local dev stays quiet.
Called once at app startup from backend/api/main.py.
"""
from __future__ import annotations

import os

import sentry_sdk


def init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return

    traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    profiles_sample_rate = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.0"))
    environment = os.getenv("ENVIRONMENT", "development")
    release = os.getenv("GIT_SHA")

    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        environment=environment,
        release=release,
        send_default_pii=False,
    )
