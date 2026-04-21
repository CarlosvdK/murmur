"""ContextTool wrapper around the raw MarketDataTool client (AlphaVantage)."""
from __future__ import annotations

import logging
import os
from typing import Optional

from backend.context.tools.base import ContextTool
from backend.context.tools.market_data import MarketDataTool

logger = logging.getLogger(__name__)


class MarketDataContextTool(ContextTool):
    name = "market_data"
    description = (
        "Get equity-market signals (S&P 500 level, sector performance, "
        "currency moves) relevant to discretionary-spend questions. "
        "Useful when the question is about premium positioning, "
        "large-ticket purchases, or macro-driven consumer mood. "
        "Requires ALPHA_VANTAGE_API_KEY."
    )
    required_config = ["alpha_vantage_api_key"]

    async def execute(
        self,
        business_name: str,
        business_type: str,
        location: Optional[str],
        question: str,
        hints: dict,
    ) -> dict:
        key = os.getenv("ALPHA_VANTAGE_API_KEY") or ""
        inner = MarketDataTool(alpha_vantage_api_key=key)
        try:
            narrative = await inner.execute(location or "")
        except Exception as exc:
            logger.warning("MarketDataTool failed: %s", exc)
            return {"narrative": "", "error": str(exc)[:200]}
        return {"narrative": narrative or ""}
