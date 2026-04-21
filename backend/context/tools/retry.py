"""Shared HTTP retry decorator for context tools.

Centralises the tenacity config so new tools don't each reinvent it.
Retries on transient failures (5xx, 429, network errors) with bounded
exponential backoff. Does NOT retry on other 4xx -- those represent
caller-side problems (bad API key, malformed request) where retrying
just wastes budget.
"""
from __future__ import annotations

from typing import Callable, TypeVar

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

F = TypeVar("F", bound=Callable)


def _is_transient(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        return code == 429 or 500 <= code < 600
    return isinstance(exc, (httpx.TimeoutException, httpx.TransportError))


async def retry_get_json(
    url: str,
    *,
    params: dict | None = None,
    timeout: float = 15.0,
    headers: dict | None = None,
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 8.0,
) -> dict | list:
    """GET `url`, raise_for_status, return JSON, with retry on transient errors.

    Drop-in replacement for the common tool pattern:

        async with httpx.AsyncClient(timeout=...) as client:
            resp = await client.get(url, params=...)
            resp.raise_for_status()
            data = resp.json()

    which had no retry. Now tools get retry for free.
    """

    @retry_http(max_attempts=max_attempts, min_wait=min_wait, max_wait=max_wait)
    async def _once():
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            return resp.json()

    return await _once()


def retry_http(
    *,
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 8.0,
):
    """Decorator that retries transient HTTP failures with exponential backoff.

    Usage:
        @retry_http()
        async def fetch(...):
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
    """

    def decorator(fn: F) -> F:
        wrapped = retry(
            retry=retry_if_exception(_is_transient),
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            reraise=True,
        )(fn)
        return wrapped  # type: ignore[return-value]

    return decorator
