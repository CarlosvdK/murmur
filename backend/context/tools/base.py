"""
Base class for all context enrichment tools.

Every tool must:
- Declare name, description, and required_config keys
- Implement execute() returning a raw data dict
- Implement available() to check API key presence
- Never raise from run() -- always return a ToolResult
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

from backend.models.context import ToolResult, ToolStatus

logger = logging.getLogger(__name__)

TOOL_TIMEOUT = 30  # seconds per tool, overridable via config


class ContextTool(ABC):

    name: str = ""
    description: str = ""
    required_config: list[str] = []

    @abstractmethod
    async def execute(
        self,
        business_name: str,
        business_type: str,
        location: Optional[str],
        question: str,
        hints: dict,
    ) -> dict:
        """Run the tool and return raw data. May raise on failure."""
        ...

    def available(self, settings) -> bool:
        """Check if all required API keys are present."""
        for key in self.required_config:
            if not getattr(settings, key, ""):
                return False
        return True

    async def run(
        self,
        timeout: int = TOOL_TIMEOUT,
        **kwargs,
    ) -> ToolResult:
        """Execute with timeout and error handling. Always returns ToolResult."""
        start = time.monotonic()
        try:
            raw = await asyncio.wait_for(
                self.execute(**kwargs),
                timeout=timeout,
            )
            elapsed = time.monotonic() - start
            logger.info("Tool %s completed in %.1fs", self.name, elapsed)
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.COMPLETED,
                raw_data=raw,
                elapsed_seconds=elapsed,
            )
        except asyncio.TimeoutError:
            elapsed = time.monotonic() - start
            logger.warning("Tool %s timed out after %.1fs", self.name, elapsed)
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                error=f"Timed out after {timeout}s",
                elapsed_seconds=elapsed,
            )
        except Exception as e:
            elapsed = time.monotonic() - start
            logger.error("Tool %s failed: %s", self.name, e)
            return ToolResult(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                error=str(e)[:500],
                elapsed_seconds=elapsed,
            )
