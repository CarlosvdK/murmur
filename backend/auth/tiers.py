"""
Tier system for Murmur.

Three tiers:
- SIMULATE (free): swarm simulations only, 5/month
- CONNECT (49 EUR/month): CRM + twins + correspondence
- INTELLIGENCE (199 EUR/month): org intelligence + vendor twin + portfolio
"""

from enum import Enum
from typing import Optional


class Tier(str, Enum):
    SIMULATE = "simulate"
    CONNECT = "connect"
    INTELLIGENCE = "intelligence"


TIER_LIMITS = {
    Tier.SIMULATE: {
        "simulations_per_month": 5,
        "crm_access": False,
        "contacts_limit": 0,
        "organisations_limit": 0,
        "twin_access": False,
        "vendor_twin": False,
        "org_intelligence": False,
        "portfolio_signals": False,
        "team_seats": 1,
    },
    Tier.CONNECT: {
        "simulations_per_month": None,
        "crm_access": True,
        "contacts_limit": 50,
        "organisations_limit": 20,
        "twin_access": True,
        "vendor_twin": False,
        "org_intelligence": False,
        "portfolio_signals": False,
        "team_seats": 1,
    },
    Tier.INTELLIGENCE: {
        "simulations_per_month": None,
        "crm_access": True,
        "contacts_limit": None,
        "organisations_limit": None,
        "twin_access": True,
        "vendor_twin": True,
        "org_intelligence": True,
        "portfolio_signals": True,
        "team_seats": 10,
    },
}


def check_feature_access(user_tier: Tier, feature: str) -> bool:
    limits = TIER_LIMITS.get(user_tier, TIER_LIMITS[Tier.SIMULATE])
    return bool(limits.get(feature, False))


def get_limit(user_tier: Tier, limit_key: str) -> Optional[int]:
    limits = TIER_LIMITS.get(user_tier, TIER_LIMITS[Tier.SIMULATE])
    return limits.get(limit_key)


def get_tier_name(tier: Tier) -> str:
    names = {
        Tier.SIMULATE: "Simulate (Free)",
        Tier.CONNECT: "Connect (49 EUR/month)",
        Tier.INTELLIGENCE: "Intelligence (199 EUR/month)",
    }
    return names.get(tier, "Free")
