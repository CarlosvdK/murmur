"""
SSE progress emitter for real-time frontend updates.

Uses an asyncio.Queue per simulation. The pipeline pushes events,
the SSE endpoint reads and streams them.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Optional


class ProgressEmitter:
    """Wraps an asyncio.Queue to emit structured progress events."""

    def __init__(self, simulation_id: str, queue: asyncio.Queue):
        self.simulation_id = simulation_id
        self.queue = queue

    async def emit(self, phase: str, step: str, metadata: Optional[dict] = None):
        payload = {
            "phase": phase,
            "step": step,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "simulation_id": self.simulation_id,
            "metadata": metadata or {},
        }
        await self.queue.put(payload)

    def emit_sync(self, phase: str, step: str, metadata: Optional[dict] = None):
        """Non-async version for use in sync callbacks."""
        payload = {
            "phase": phase,
            "step": step,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "simulation_id": self.simulation_id,
            "metadata": metadata or {},
        }
        self.queue.put_nowait(payload)

    async def complete(self):
        """Signal that the stream is done."""
        await self.queue.put(None)

    @staticmethod
    def format_sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"
