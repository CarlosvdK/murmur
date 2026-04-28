"""
Real-time intelligence gatherer: Weather, news, economic APIs.

Collects data in parallel, caches aggressively, never blocks simulation.
Separate from location profiler (which is quarterly) — this is hourly/daily.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
import json
import holidays

logger = logging.getLogger(__name__)


class RealtimeContext:
    """Real-time context snapshot for a specific moment."""

    def __init__(self, timestamp: datetime, location: str):
        self.timestamp = timestamp
        self.location = location

        # Weather
        self.weather_temp = 20.0
        self.weather_condition = "partly_cloudy"
        self.weather_forecast_7d = "warming"

        # Economic
        self.economic_news = []  # Recent news about inflation, rates, etc.
        self.stock_market_sentiment = "neutral"  # up, down, neutral
        self.commodity_price_change = 0.0  # % change today

        # News/Events
        self.trending_topics = []
        self.industry_news = []
        self.local_news = []
        self.upcoming_events = []  # e.g., "Ramadan starts in 3 days"

        # Temporal
        self.day_of_week = ""  # Monday, etc.
        self.time_of_day = ""  # morning, afternoon, evening, night
        self.is_holiday = False
        self.is_payday_week = False  # Inferred from country

        # Social sentiment
        self.social_sentiment_score = 0.0  # -1 to 1
        self.trending_topics_sentiment = {}  # topic -> sentiment

    def model_dump(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "location": self.location,
            "weather": {
                "temp": self.weather_temp,
                "condition": self.weather_condition,
                "forecast_7d": self.weather_forecast_7d,
            },
            "economic": {
                "news": self.economic_news,
                "stock_sentiment": self.stock_market_sentiment,
                "commodity_change_pct": self.commodity_price_change,
            },
            "news": {
                "trending_topics": self.trending_topics,
                "industry_news": self.industry_news,
                "local_news": self.local_news,
                "upcoming_events": self.upcoming_events,
            },
            "temporal": {
                "day_of_week": self.day_of_week,
                "time_of_day": self.time_of_day,
                "is_holiday": self.is_holiday,
                "is_payday_week": self.is_payday_week,
            },
            "social": {
                "sentiment_score": self.social_sentiment_score,
                "trending_sentiment": self.trending_topics_sentiment,
            },
        }


class RealtimeIntelligence:
    """Gathers real-time context from multiple APIs in parallel."""

    def __init__(self, cache=None):
        self.cache = cache

    async def gather_all(
        self,
        location: str,
        simulation_date: Optional[datetime] = None,
    ) -> RealtimeContext:
        """Gather all real-time context in parallel.

        Args:
            location: e.g., "Tehran, Iran"
            simulation_date: When to gather context for (defaults to now)

        Returns:
            RealtimeContext with all data that could be gathered
        """
        if simulation_date is None:
            simulation_date = datetime.now(timezone.utc)

        context = RealtimeContext(simulation_date, location)

        # Kick off 5 parallel gatherers (non-blocking, 5s timeout each)
        tasks = [
            self._gather_weather(location, simulation_date),
            self._gather_economic(location, simulation_date),
            self._gather_news(location, simulation_date),
            self._gather_temporal(simulation_date, location),
            self._gather_social_sentiment(location, simulation_date),
        ]

        try:
            results = await asyncio.gather(
                *tasks,
                return_exceptions=True,
                timeout=5.0,
            )

            # Merge results
            if isinstance(results[0], dict):
                context.weather_temp = results[0].get("temp", 20.0)
                context.weather_condition = results[0].get("condition", "unknown")
                context.weather_forecast_7d = results[0].get("forecast", "unknown")

            if isinstance(results[1], dict):
                context.economic_news = results[1].get("news", [])
                context.stock_market_sentiment = results[1].get("sentiment", "neutral")
                context.commodity_price_change = results[1].get("commodity_change", 0.0)

            if isinstance(results[2], dict):
                context.trending_topics = results[2].get("trending", [])
                context.industry_news = results[2].get("industry", [])
                context.local_news = results[2].get("local", [])
                context.upcoming_events = results[2].get("events", [])

            if isinstance(results[3], dict):
                context.day_of_week = results[3].get("day_of_week", "")
                context.time_of_day = results[3].get("time_of_day", "")
                context.is_holiday = results[3].get("is_holiday", False)
                context.is_payday_week = results[3].get("is_payday_week", False)

            if isinstance(results[4], dict):
                context.social_sentiment_score = results[4].get("sentiment", 0.0)
                context.trending_topics_sentiment = results[4].get("topics", {})

        except asyncio.TimeoutError:
            logger.warning("Real-time context gathering timed out, returning partial")
        except Exception as e:
            logger.warning(f"Real-time gathering error: {e}, continuing with defaults")

        return context

    async def _gather_weather(self, location: str, date: datetime) -> dict:
        """Gather weather from Open-Meteo API (free, no auth)."""
        try:
            # In production: call Open-Meteo API
            # async with httpx.AsyncClient() as client:
            #     resp = await client.get(...)

            # Stub data for Tehran
            if "Tehran" in location or "Iran" in location:
                temp_map = {
                    "spring": 18.0,  # April ~18°C in Tehran
                    "summer": 35.0,  # July ~35°C
                    "fall": 22.0,
                    "winter": 8.0,
                }
                month = date.month
                season = "spring" if month in [3, 4, 5] else (
                    "summer" if month in [6, 7, 8] else (
                        "fall" if month in [9, 10, 11] else "winter"
                    )
                )

            else:
                temp_map = {"spring": 15.0, "summer": 25.0, "fall": 18.0, "winter": 5.0}

            return {
                "temp": temp_map.get(season, 20.0),
                "condition": "partly_cloudy",
                "forecast": f"{season} pattern continues",
            }

        except Exception as e:
            logger.debug(f"Weather gathering failed: {e}")
            return {"temp": 20.0, "condition": "unknown", "forecast": "unknown"}

    async def _gather_economic(self, location: str, date: datetime) -> dict:
        """Gather economic news and sentiment."""
        try:
            # In production: call NewsAPI or Bloomberg for economic news
            # async with httpx.AsyncClient() as client:
            #     resp = await client.get(...)

            # Stub data for Iran
            if "Tehran" in location or "Iran" in location:
                return {
                    "news": [
                        "Iran inflation at 42% annually (Central Bank statement)",
                        "Currency depreciation continues amid sanctions",
                        "Central Bank raises interest rates to 30%",
                    ],
                    "sentiment": "negative",
                    "commodity_change": -2.5,  # Oil down 2.5% today
                }

            # Stub data for US
            return {
                "news": [
                    "Fed holds rates steady at 5.25%",
                    "CPI inflation at 3.2% YoY",
                    "S&P 500 up 1.2% today",
                ],
                "sentiment": "neutral",
                "commodity_change": 0.8,
            }

        except Exception as e:
            logger.debug(f"Economic gathering failed: {e}")
            return {"news": [], "sentiment": "unknown", "commodity_change": 0.0}

    async def _gather_news(self, location: str, date: datetime) -> dict:
        """Gather trending topics and local news."""
        try:
            # In production: call NewsAPI, Google Trends, Reddit API
            # async with httpx.AsyncClient() as client:
            #     resp = await client.get(...)

            # Stub data
            return {
                "trending": ["inflation crisis", "cost of living", "business optimism"],
                "industry": ["retail sales down 2%", "coffee industry trending up"],
                "local": ["local coffee shop raises prices"],
                "events": ["Ramadan starts in 3 days", "Weekend coming up"],
            }

        except Exception as e:
            logger.debug(f"News gathering failed: {e}")
            return {"trending": [], "industry": [], "local": [], "events": []}

    async def _gather_temporal(self, date: datetime, location: str) -> dict:
        """Gather temporal context (day of week, time of day, holidays, etc.)."""
        try:
            day_of_week = date.strftime("%A")
            hour = date.hour

            # Time of day
            if hour < 6:
                time_of_day = "night"
            elif hour < 12:
                time_of_day = "morning"
            elif hour < 17:
                time_of_day = "afternoon"
            else:
                time_of_day = "evening"

            # Is holiday - extract country code from location and check holidays package
            is_holiday = self._is_holiday(date, location)

            # Is payday week (stub: assume mid-month and end-of-month)
            day = date.day
            is_payday_week = (10 <= day <= 15) or (25 <= day <= 31)

            return {
                "day_of_week": day_of_week,
                "time_of_day": time_of_day,
                "is_holiday": is_holiday,
                "is_payday_week": is_payday_week,
                "season": self._get_season(date),
            }

        except Exception as e:
            logger.debug(f"Temporal gathering failed: {e}")
            return {
                "day_of_week": "unknown",
                "time_of_day": "unknown",
                "is_holiday": False,
                "is_payday_week": False,
            }

    async def _gather_social_sentiment(self, location: str, date: datetime) -> dict:
        """Gather social media sentiment (Twitter, Reddit, TikTok)."""
        try:
            # In production: call Twitter API v2, Reddit API, etc.
            # async with httpx.AsyncClient() as client:
            #     resp = await client.get(...)

            # Stub data
            return {
                "sentiment": -0.3,  # Slightly negative
                "topics": {
                    "inflation": -0.8,  # Very negative
                    "business": -0.2,  # Slightly negative
                    "lifestyle": 0.1,  # Slightly positive
                },
            }

        except Exception as e:
            logger.debug(f"Social sentiment gathering failed: {e}")
            return {"sentiment": 0.0, "topics": {}}

    @staticmethod
    def _get_season(date: datetime) -> str:
        """Get season from date."""
        month = date.month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "fall"
        else:
            return "winter"

    @staticmethod
    def _extract_country_code(location: str) -> str:
        """Extract ISO country code from location string or return if already a code."""
        # If already a 2-char country code, return it
        if len(location) == 2 and location.isupper():
            return location

        country_map = {
            "iran": "IR", "us": "US", "usa": "US", "united states": "US",
            "china": "CN", "brazil": "BR", "nigeria": "NG", "india": "IN",
            "germany": "DE", "japan": "JP", "mexico": "MX", "uk": "GB",
            "united kingdom": "GB", "england": "GB", "united states of america": "US",
        }
        location_lower = location.lower()
        for country_name, code in country_map.items():
            if country_name in location_lower:
                return code
        return None

    @staticmethod
    def _is_holiday(date: datetime, location: str) -> bool:
        """Check if date is a holiday in the location's country."""
        try:
            country_code = RealtimeIntelligence._extract_country_code(location)
            if not country_code:
                return False

            # Get holidays for the country and year
            country_holidays = holidays.country_holidays(country_code, years=date.year)
            return date.date() in country_holidays
        except Exception:
            return False
