"""Structured JSON logging.

Stdlib-only (no extra dep): a custom Formatter that serialises each LogRecord
to JSON, injecting the current request_id from our context var.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from backend.observability.middleware import request_id_var


_RESERVED = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "message", "asctime", "taskName",
}


class _RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        rid = request_id_var.get()
        if rid is not None:
            record.request_id = rid  # type: ignore[attr-defined]
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": time.strftime(
                "%Y-%m-%dT%H:%M:%S",
                time.gmtime(record.created),
            ) + f".{int(record.msecs):03d}Z",
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
        }
        rid = getattr(record, "request_id", None) or request_id_var.get()
        if rid:
            payload["request_id"] = rid
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        for key, value in record.__dict__.items():
            if key in _RESERVED or key == "request_id":
                continue
            if key.startswith("_"):
                continue
            try:
                json.dumps(value)
            except (TypeError, ValueError):
                value = repr(value)
            payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(
    *,
    handler: logging.Handler | None = None,
    level: int = logging.INFO,
) -> None:
    """Install the JSON formatter + request-id filter on the root logger."""
    root = logging.getLogger()
    # Clear any handlers that basicConfig may have installed
    for existing in list(root.handlers):
        root.removeHandler(existing)

    h = handler if handler is not None else logging.StreamHandler()
    h.setFormatter(JsonFormatter())
    h.addFilter(_RequestIDFilter())
    root.addHandler(h)
    root.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    # Ensure our filter sees records even if a child logger was created
    # before configure_logging() ran.
    if not any(isinstance(f, _RequestIDFilter) for f in logger.filters):
        logger.addFilter(_RequestIDFilter())
    return logger
