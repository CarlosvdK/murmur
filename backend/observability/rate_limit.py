"""Shared slowapi Limiter.

Exposing this from its own module avoids circular imports between
backend.api.main and the route modules that decorate endpoints.
"""
from __future__ import annotations

import os

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request


def _rate_limit_key(request: Request) -> str:
    # Health is exempt so uptime probes don't trip limits.
    if request.url.path.endswith("/api/health"):
        return "__exempt__"
    return get_remote_address(request)


DEFAULT_LIMIT = os.getenv("RATE_LIMIT_DEFAULT", "120/minute")

limiter = Limiter(key_func=_rate_limit_key, default_limits=[DEFAULT_LIMIT])
