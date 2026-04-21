"""ContextTool wrapper around the raw EconomicDataTool client.

The raw client (backend.context.tools.economic_data.EconomicDataTool) takes
the FRED key in its constructor and has a custom `execute(location)` shape.
This wrapper conforms to the ContextTool ABC so the orchestrator can
discover and invoke it alongside the other registered tools.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

from backend.context.tools.base import ContextTool
from backend.context.tools.economic_data import EconomicDataTool

logger = logging.getLogger(__name__)


class EconomicDataContextTool(ContextTool):
    name = "economic_data"
    description = (
        "Get current macroeconomic indicators (inflation, unemployment, "
        "federal funds rate) for the business's country. Useful when the "
        "question involves pricing, spending power, or consumer confidence. "
        "Requires FRED_API_KEY."
    )
    required_config = ["fred_api_key"]

    async def execute(
        self,
        business_name: str,
        business_type: str,
        location: Optional[str],
        question: str,
        hints: dict,
    ) -> dict:
        fred_key = os.getenv("FRED_API_KEY") or ""
        inner = EconomicDataTool(fred_api_key=fred_key)
        try:
            narrative = await inner.execute(location or "")
        except Exception as exc:
            logger.warning("EconomicDataTool failed: %s", exc)
            return {"narrative": "", "error": str(exc)[:200]}
        return {"narrative": narrative or ""}
