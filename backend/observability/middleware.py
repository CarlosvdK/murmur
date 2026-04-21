"""Request-ID middleware.

Generates (or echoes) an X-Request-ID for every request, binds it to a
ContextVar so log filters can pick it up, and writes it back on the
response headers so clients can correlate logs/tickets to server logs.
"""
from __future__ import annotations

import logging
import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

_access_log = logging.getLogger("murmur.access")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        incoming = request.headers.get(REQUEST_ID_HEADER)
        rid = incoming if incoming else uuid.uuid4().hex
        token = request_id_var.set(rid)
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        finally:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            request_id_var.reset(token)

        response.headers[REQUEST_ID_HEADER] = rid
        _access_log.info(
            "request complete",
            extra={
                "request_id": rid,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "elapsed_ms": elapsed_ms,
            },
        )
        return response
