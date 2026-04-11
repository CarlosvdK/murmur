"""
Google Trends search interest via pytrends (unofficial API).

Shows how interest in relevant search terms has trended over time.
Useful for understanding whether demand is growing or shrinking
for the business type or specific products/services.

Free, no API key needed. Rate-limited by Google.
"""

import logging
from typing import Optional

from backend.context.tools.base import ContextTool

logger = logging.getLogger(__name__)


class GoogleTrendsTool(ContextTool):
    name = "google_trends"
    description = (
        "Check search interest trends for products, services, or topics over time. "
        "Shows whether customer interest is growing, stable, or declining. "
        "Provide search_terms in hints (comma-separated). No API key required."
    )
    required_config = []  # Free via pytrends

    async def execute(
        self,
        business_name: str,
        business_type: str,
        location: Optional[str],
        question: str,
        hints: dict,
    ) -> dict:
        search_terms_raw = hints.get("search_terms", business_type)
        if isinstance(search_terms_raw, list):
            search_terms = search_terms_raw[:5]
        else:
            search_terms = [t.strip() for t in search_terms_raw.split(",")][:5]

        try:
            from pytrends.request import TrendReq
        except ImportError:
            logger.warning("pytrends not installed -- Google Trends tool unavailable")
            return {
                "available": False,
                "reason": "pytrends library not installed",
                "search_terms": search_terms,
            }

        try:
            # Determine geo code from location
            geo = ""
            if location:
                loc = location.lower()
                # Simple country code extraction
                country_hints = {
                    "spain": "ES", "uk": "GB", "united kingdom": "GB",
                    "united states": "US", "usa": "US", "germany": "DE",
                    "france": "FR", "italy": "IT", "netherlands": "NL",
                    "portugal": "PT", "ireland": "IE", "australia": "AU",
                    "canada": "CA", "brazil": "BR", "mexico": "MX",
                    "japan": "JP", "india": "IN", "china": "CN",
                }
                for hint, code in country_hints.items():
                    if hint in loc:
                        geo = code
                        break

            pytrends = TrendReq(hl="en-US", tz=0, timeout=(10, 25))
            pytrends.build_payload(search_terms, cat=0, timeframe="today 12-m", geo=geo)
            interest = pytrends.interest_over_time()

            if interest.empty:
                return {
                    "available": True,
                    "search_terms": search_terms,
                    "geo": geo or "worldwide",
                    "trends": [],
                    "summary": "No trend data available for these terms",
                }

            # Extract trend summary for each term
            trends = []
            for term in search_terms:
                if term not in interest.columns:
                    continue
                series = interest[term]
                recent_avg = float(series.tail(4).mean())  # last month
                older_avg = float(series.head(13).mean())   # first quarter
                overall_avg = float(series.mean())

                if older_avg > 0:
                    change_pct = ((recent_avg - older_avg) / older_avg) * 100
                else:
                    change_pct = 0

                if change_pct > 15:
                    direction = "growing"
                elif change_pct < -15:
                    direction = "declining"
                else:
                    direction = "stable"

                trends.append({
                    "term": term,
                    "direction": direction,
                    "change_pct": round(change_pct, 1),
                    "recent_interest": round(recent_avg, 1),
                    "average_interest": round(overall_avg, 1),
                })

            # Build narrative summary
            summaries = []
            for t in trends:
                if t["direction"] == "growing":
                    summaries.append(f'Search interest in "{t["term"]}" is growing ({t["change_pct"]:+.0f}% over 12 months)')
                elif t["direction"] == "declining":
                    summaries.append(f'Search interest in "{t["term"]}" is declining ({t["change_pct"]:+.0f}% over 12 months)')
                else:
                    summaries.append(f'Search interest in "{t["term"]}" is stable')

            return {
                "available": True,
                "search_terms": search_terms,
                "geo": geo or "worldwide",
                "timeframe": "12 months",
                "trends": trends,
                "summary": ". ".join(summaries) if summaries else "No clear trends detected",
            }

        except Exception as e:
            logger.warning("Google Trends failed: %s", e)
            return {
                "available": False,
                "reason": str(e),
                "search_terms": search_terms,
            }
