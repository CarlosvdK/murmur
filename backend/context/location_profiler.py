"""
Location profiler: Build rich demographic/economic/cultural profiles for locations.

Caches quarterly to avoid redundant API calls while staying fresh.
Used by context engine to ground persona generation in real-world constraints.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib

logger = logging.getLogger(__name__)

# Hofstede cultural dimensions (lookup table, one-time data)
HOFSTEDE_DIMENSIONS = {
    "IR": {"pdist": 58, "idv": 41, "mas": 43, "uai": 59, "ltowvs": 30, "ind": 40},
    "US": {"pdist": 40, "idv": 91, "mas": 62, "uai": 46, "ltowvs": 26, "ind": 68},
    "CN": {"pdist": 80, "idv": 20, "mas": 66, "uai": 30, "ltowvs": 87, "ind": 24},
    "BR": {"pdist": 69, "idv": 38, "mas": 49, "uai": 76, "ltowvs": 44, "ind": 59},
    "NG": {"pdist": 80, "idv": 30, "mas": 60, "uai": 55, "ltowvs": 13, "ind": 84},
    "DE": {"pdist": 35, "idv": 67, "mas": 66, "uai": 65, "ltowvs": 83, "ind": 40},
    "IN": {"pdist": 77, "idv": 48, "mas": 56, "uai": 40, "ltowvs": 51, "ind": 26},
    "JP": {"pdist": 54, "idv": 46, "mas": 95, "uai": 92, "ltowvs": 88, "ind": 42},
    "MX": {"pdist": 81, "idv": 30, "mas": 69, "uai": 86, "ltowvs": 24, "ind": 97},
    "GB": {"pdist": 35, "idv": 89, "mas": 66, "uai": 35, "ltowvs": 51, "ind": 69},
}

# Context culture: high-context vs low-context
CONTEXT_CULTURE = {
    "IR": "high", "CN": "high", "JP": "high", "IN": "high",
    "BR": "high", "MX": "high",
    "US": "low", "GB": "low", "DE": "low", "NG": "low",
}

# Primary payment method by region (inferred)
PRIMARY_PAYMENT = {
    "IR": "cash", "NG": "cash", "IN": "cash/mobile",
    "BR": "card", "MX": "cash/card",
    "US": "card", "GB": "card", "DE": "card",
    "CN": "mobile/alipay", "JP": "card/cash",
}


class LocationProfile:
    """Rich profile of a location (country, region, city)."""

    def __init__(self, location: str):
        self.location = location  # e.g., "Tehran, Iran" or "San Francisco, USA"
        self.country_code = self._extract_country_code(location)
        self.timezone = self._get_timezone(self.country_code)

        # Culture
        self.hofstede = HOFSTEDE_DIMENSIONS.get(self.country_code, {})
        self.context_culture = CONTEXT_CULTURE.get(self.country_code, "neutral")

        # Economics (would be fetched from World Bank API)
        self.inflation_rate = 0.0  # Updated daily
        self.unemployment_rate = 0.0  # Updated weekly
        self.gdp_growth_rate = 0.0  # Updated quarterly
        self.interest_rate = 0.0  # Updated as announced

        # Business
        self.primary_payment = PRIMARY_PAYMENT.get(self.country_code, "card")
        self.digital_adoption = self._infer_digital_adoption(self.country_code)
        self.trust_in_institutions = self._infer_trust(self.country_code)

        # Metadata
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.expires_at = datetime.now(timezone.utc) + timedelta(days=90)

    @staticmethod
    def _extract_country_code(location: str) -> str:
        """Extract country code from location string.

        Examples: "Tehran, Iran" -> "IR", "San Francisco, USA" -> "US"
        """
        # Simple mapping for common countries
        country_map = {
            "iran": "IR", "us": "US", "usa": "US", "united states": "US",
            "china": "CN", "brazil": "BR", "nigeria": "NG", "india": "IN",
            "germany": "DE", "japan": "JP", "mexico": "MX", "uk": "GB",
            "united kingdom": "GB", "england": "GB",
        }

        location_lower = location.lower()
        for country_name, code in country_map.items():
            if country_name in location_lower:
                return code

        # Fallback: return last 2 chars (very crude)
        parts = location.split(",")
        if len(parts) > 1:
            return parts[-1].strip()[-2:].upper()
        return "XX"

    @staticmethod
    def _get_timezone(country_code: str) -> str:
        """Get primary timezone for country."""
        timezones = {
            "IR": "Asia/Tehran",
            "US": "America/New_York",  # Default to ET
            "CN": "Asia/Shanghai",
            "BR": "America/Sao_Paulo",
            "NG": "Africa/Lagos",
            "IN": "Asia/Kolkata",
            "DE": "Europe/Berlin",
            "JP": "Asia/Tokyo",
            "MX": "America/Mexico_City",
            "GB": "Europe/London",
        }
        return timezones.get(country_code, "UTC")

    @staticmethod
    def _infer_digital_adoption(country_code: str) -> str:
        """Infer digital adoption level from country."""
        adoption = {
            "US": "very_high", "GB": "very_high", "DE": "very_high", "JP": "very_high",
            "CN": "high", "BR": "medium", "IN": "medium",
            "IR": "low", "NG": "low", "MX": "medium",
        }
        return adoption.get(country_code, "medium")

    @staticmethod
    def _infer_trust(country_code: str) -> str:
        """Infer trust in institutions from country."""
        trust = {
            "US": "medium", "GB": "medium", "DE": "high", "JP": "high",
            "CN": "low", "BR": "low", "IN": "low",
            "IR": "very_low", "NG": "low", "MX": "low",
        }
        return trust.get(country_code, "medium")

    def model_dump(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "location": self.location,
            "country_code": self.country_code,
            "timezone": self.timezone,
            "hofstede": self.hofstede,
            "context_culture": self.context_culture,
            "inflation_rate": self.inflation_rate,
            "unemployment_rate": self.unemployment_rate,
            "gdp_growth_rate": self.gdp_growth_rate,
            "interest_rate": self.interest_rate,
            "primary_payment": self.primary_payment,
            "digital_adoption": self.digital_adoption,
            "trust_in_institutions": self.trust_in_institutions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }


class LocationProfiler:
    """Manages location profile caching and generation."""

    def __init__(self, db=None, cache=None):
        self.db = db
        self.cache = cache

    async def get_or_create(self, location: str) -> LocationProfile:
        """Get cached profile or generate fresh.

        Caches quarterly (90 days) since macro data updates slowly.
        """
        profile = LocationProfile(location)

        # Check cache (Redis or in-memory)
        if self.cache:
            cached = await self.cache.get(f"location_profile:{location}")
            if cached:
                logger.info(f"Location profile cache HIT: {location}")
                return self._deserialize_profile(cached)

        # Check database
        if self.db:
            try:
                result = await self._fetch_from_db(location)
                if result and not self._is_expired(result):
                    logger.info(f"Location profile DB HIT: {location}")
                    return self._row_to_profile(result)
            except Exception as e:
                logger.warning(f"DB lookup failed: {e}")

        # Generate fresh (would call World Bank API here)
        await self._enrich_from_world_bank(profile)

        # Cache it
        if self.cache:
            await self.cache.set(
                f"location_profile:{location}",
                profile.model_dump(),
                ttl=86400 * 90,  # 90 days
            )

        if self.db:
            await self._store_to_db(profile)

        logger.info(f"Location profile generated: {location}")
        return profile

    async def _enrich_from_world_bank(self, profile: LocationProfile):
        """Fetch live economic data from World Bank API.

        This would call actual World Bank API in production.
        For now, using stub values.
        """
        try:
            # In production:
            # async with httpx.AsyncClient() as client:
            #     resp = await client.get(
            #         f"https://api.worldbank.org/v2/country/{profile.country_code}",
            #         params={"format": "json"}
            #     )
            #     data = resp.json()
            #     profile.gdp_growth_rate = data[1][0]["NY.GDP.MKTP.KD.ZG.AD.SU.ZS"]

            # Stub data for now
            stub_data = {
                "IR": {"inflation": 42.0, "unemployment": 8.2, "gdp_growth": -6.8, "interest_rate": 30.0},
                "US": {"inflation": 3.2, "unemployment": 3.9, "gdp_growth": 2.5, "interest_rate": 5.25},
                "CN": {"inflation": 1.8, "unemployment": 4.0, "gdp_growth": 5.0, "interest_rate": 3.65},
                "BR": {"inflation": 4.5, "unemployment": 7.8, "gdp_growth": 2.9, "interest_rate": 10.5},
            }

            if profile.country_code in stub_data:
                data = stub_data[profile.country_code]
                profile.inflation_rate = data["inflation"]
                profile.unemployment_rate = data["unemployment"]
                profile.gdp_growth_rate = data["gdp_growth"]
                profile.interest_rate = data["interest_rate"]
                profile.updated_at = datetime.now(timezone.utc)

        except Exception as e:
            logger.warning(f"World Bank enrichment failed: {e}")

    async def _fetch_from_db(self, location: str):
        """Fetch cached profile from database."""
        result = self.db.table("location_profiles").select("*").eq(
            "location", location
        ).maybe_single().execute()
        return result.data if result.data else None

    async def _store_to_db(self, profile: LocationProfile):
        """Store profile to database."""
        try:
            self.db.table("location_profiles").upsert({
                "location": profile.location,
                "country_code": profile.country_code,
                "timezone": profile.timezone,
                "data": profile.model_dump(),
                "expires_at": profile.expires_at.isoformat(),
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to store profile: {e}")

    @staticmethod
    def _is_expired(row: dict) -> bool:
        """Check if profile is expired."""
        expires_at = datetime.fromisoformat(row.get("expires_at", ""))
        return expires_at < datetime.now(timezone.utc)

    @staticmethod
    def _row_to_profile(row: dict) -> LocationProfile:
        """Reconstruct profile from DB row."""
        profile = LocationProfile(row["location"])
        data = row.get("data", {})
        profile.inflation_rate = data.get("inflation_rate", 0)
        profile.unemployment_rate = data.get("unemployment_rate", 0)
        profile.gdp_growth_rate = data.get("gdp_growth_rate", 0)
        profile.interest_rate = data.get("interest_rate", 0)
        return profile

    @staticmethod
    def _deserialize_profile(data: dict) -> LocationProfile:
        """Reconstruct profile from cached data."""
        profile = LocationProfile(data["location"])
        profile.inflation_rate = data.get("inflation_rate", 0)
        profile.unemployment_rate = data.get("unemployment_rate", 0)
        profile.gdp_growth_rate = data.get("gdp_growth_rate", 0)
        profile.interest_rate = data.get("interest_rate", 0)
        return profile
