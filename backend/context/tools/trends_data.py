"""
Trends data tool: Google Trends (via pytrends)
Provides search interest, trending topics, keyword volume
"""

import asyncio
from typing import Optional


class GoogleTrendsTool:
    """Gather Google Trends data: search interest, emerging topics."""

    def __init__(self):
        self.tool_name = "Google Trends"

    async def get_trending_searches(self, country_code: str = "US") -> dict:
        """
        Get trending searches for a country.
        This requires pytrends library: pip install pytrends
        """
        try:
            from pytrends.request import TrendReq

            # Use async wrapper to prevent blocking
            def fetch_trends():
                pytrends = TrendReq(hl="en-US", tz=360)
                trending = pytrends.trending_searches(pn=country_code)
                return trending.values.tolist()

            loop = asyncio.get_event_loop()
            trends = await loop.run_in_executor(None, fetch_trends)
            return {"country": country_code, "trending": trends[:5]}
        except ImportError:
            return {"error": "pytrends library not installed"}
        except Exception as e:
            return {"error": str(e)}

    async def get_search_interest(self, keywords: list[str]) -> dict:
        """
        Get search interest over time for keywords.
        Returns trend data for the past year.
        """
        try:
            from pytrends.request import TrendReq

            def fetch_interest():
                pytrends = TrendReq(hl="en-US", tz=360)
                pytrends.build_payload(keywords, timeframe="today 12-m", geo="US")
                return pytrends.interest_over_time()

            loop = asyncio.get_event_loop()
            interest = await loop.run_in_executor(None, fetch_interest)

            # Extract last value and trend
            if not interest.empty:
                latest_value = interest.iloc[-1][keywords[0]]
                previous_value = interest.iloc[0][keywords[0]]
                trend_direction = "up" if latest_value > previous_value else "down"

                return {
                    "keywords": keywords,
                    "latest_interest": int(latest_value),
                    "trend": trend_direction,
                    "change": f"{((latest_value - previous_value) / max(previous_value, 1) * 100):.1f}%",
                }
        except ImportError:
            return {"error": "pytrends library not installed"}
        except Exception as e:
            return {"error": str(e)}

    async def get_related_topics(self, keyword: str) -> dict:
        """Get related topics and rising queries for a keyword."""
        try:
            from pytrends.request import TrendReq

            def fetch_related():
                pytrends = TrendReq(hl="en-US", tz=360)
                pytrends.build_payload([keyword], timeframe="today 12-m")
                related_topics = pytrends.related_topics()
                return related_topics.get(keyword, {})

            loop = asyncio.get_event_loop()
            related = await loop.run_in_executor(None, fetch_related)

            return {
                "keyword": keyword,
                "related_topics": related.get("top", [])[:5] if related.get("top") else [],
                "rising_queries": related.get("rising", [])[:5] if related.get("rising") else [],
            }
        except ImportError:
            return {"error": "pytrends library not installed"}
        except Exception as e:
            return {"error": str(e)}

    async def execute(self, business_type: str, location: str) -> str:
        """Execute: gather trends data and return as narrative."""
        narrative_parts = []

        # Extract country code from location
        country_map = {
            "US": "US",
            "Canada": "CA",
            "UK": "GB",
            "Germany": "DE",
            "France": "FR",
            "Japan": "JP",
            "Australia": "AU",
        }

        country_code = "US"
        for key, code in country_map.items():
            if key.lower() in location.lower():
                country_code = code
                break

        # Get trending searches
        trending = await self.get_trending_searches(country_code)
        if trending.get("trending"):
            top_trends = ", ".join(trending["trending"][:3])
            narrative_parts.append(f"Trending searches: {top_trends}")

        # Get search interest for business-related keywords
        business_keywords = self._get_business_keywords(business_type)
        if business_keywords:
            interest = await self.get_search_interest(business_keywords[:3])
            if interest.get("keywords") and not interest.get("error"):
                trend = interest.get("trend", "stable")
                change = interest.get("change", "0%")
                narrative_parts.append(
                    f"Interest in '{business_keywords[0]}' is {trend} ({change} over 12 months)"
                )

        # Get related topics
        if business_keywords:
            related = await self.get_related_topics(business_keywords[0])
            if related.get("related_topics"):
                related_list = [t["value"] for t in related["related_topics"][:2]]
                if related_list:
                    narrative_parts.append(f"Related searches: {', '.join(related_list)}")

        narrative = "Trends Context: " + ". ".join(narrative_parts) if narrative_parts else ""
        return narrative if narrative else "Trend data unavailable"

    def _get_business_keywords(self, business_type: str) -> list[str]:
        """Get relevant keywords based on business type."""
        keywords_map = {
            "restaurant": ["restaurant dining", "food delivery", "meal prep"],
            "retail": ["shopping", "online retail", "consumer trends"],
            "saas": ["software", "cloud services", "productivity tools"],
            "hospitality": ["hotel booking", "vacation", "travel"],
            "e-commerce": ["online shopping", "e-commerce", "product reviews"],
            "marketplace": ["marketplace", "peer to peer", "sharing economy"],
            "hair_salon": ["haircut", "salon", "beauty services"],
            "grocery": ["grocery shopping", "supermarket", "food shopping"],
            "gym": ["fitness", "gym membership", "workout"],
            "coffee_shop": ["coffee", "cafe", "coffee culture"],
        }

        for key, keywords in keywords_map.items():
            if key in business_type.lower():
                return keywords

        return [business_type]


if __name__ == "__main__":
    import asyncio

    tool = GoogleTrendsTool()

    async def test():
        trending = await tool.get_trending_searches()
        print("Trending:", trending)

        interest = await tool.get_search_interest(["restaurant"])
        print("Interest:", interest)

        related = await tool.get_related_topics("restaurant")
        print("Related:", related)

        result = await tool.execute("restaurant", "San Francisco, USA")
        print("Result:", result)

    asyncio.run(test())
