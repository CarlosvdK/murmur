"""
Persona archetype cache layer (indefinite, not TTL-based).

KEY INSIGHT: Personas represent CUSTOMER DEMOGRAPHICS (static), not responses.
They should be cached INDEFINITELY for the same business, but regenerated
if the business profile changes significantly.

CONTEXT and RESPONSES are always generated fresh per question/date.

Caching strategy:
- Personas: Cached indefinitely until business profile changes
- Context: Always refreshed from APIs based on current date/question
- Responses: Always generated fresh per question
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Optional

from backend.models.persona import PersonaProfile
from backend.swarm.persona_generator import generate_personas
from backend.models.business import BusinessSnapshot

logger = logging.getLogger(__name__)


async def get_or_create_archetype(
    db,
    business_id: str,
    business: BusinessSnapshot,
    persona_count: int,
    context_narrative: Optional[str] = None,
    manifest=None,
) -> tuple[list[PersonaProfile], bool]:
    """Get cached persona archetype or generate fresh.

    Personas are cached INDEFINITELY. Context and responses are always fresh.

    Returns (personas, was_generated).
    was_generated=False means we reused a cached archetype.
    was_generated=True means we generated fresh and cached it.
    """
    if db is None:
        # Backtest or offline mode: no caching
        personas = await generate_personas(
            business, persona_count,
            context_narrative=context_narrative,
            manifest=manifest,
        )
        return personas, True

    try:
        # Try to load from cache (no expiration check)
        archetype = db.table("persona_archetypes").select("*").eq(
            "business_id", business_id
        ).execute()

        if archetype.data and len(archetype.data) > 0:
            row = archetype.data[0]
            profiles_data = row["profiles"]
            personas = [
                PersonaProfile(**p) if isinstance(p, dict) else p
                for p in profiles_data
            ]
            logger.info(
                "Persona archetype cache HIT for business %s, %d personas reused",
                business_id, len(personas),
            )
            return personas, False

    except Exception as e:
        logger.warning("Archetype cache lookup failed (non-fatal): %s", e)

    # Cache miss -- generate fresh
    personas = await generate_personas(
        business, persona_count,
        context_narrative=context_narrative,
        manifest=manifest,
    )

    # Store in cache
    try:
        profiles_json = [
            json.loads(p.model_dump_json()) if hasattr(p, "model_dump_json")
            else p.dict() if hasattr(p, "dict")
            else p
            for p in personas
        ]

        db.table("persona_archetypes").upsert(
            {
                "business_id": business_id,
                "profiles": profiles_json,
                "persona_count": len(personas),
                "business_snapshot_hash": _hash_business_snapshot(business),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()

        logger.info(
            "Stored persona archetype for business %s, %d personas",
            business_id, len(personas),
        )
    except Exception as e:
        logger.warning("Failed to store archetype (non-fatal): %s", e)

    return personas, True


async def delete_archetype_on_profile_change(db, business_id: str) -> bool:
    """Delete cached personas if business profile changed significantly.

    Returns True if deleted, False otherwise.
    """
    if db is None:
        return False

    try:
        result = db.table("persona_archetypes").delete().eq(
            "business_id", business_id
        ).execute()
        deleted = len(result.data) > 0 if result.data else False
        if deleted:
            logger.info("Deleted persona archetype for business %s due to profile change", business_id)
        return deleted
    except Exception as e:
        logger.warning("Failed to delete archetype: %s", e)
        return False


def is_profile_changed(
    old_profile: BusinessSnapshot,
    new_profile: BusinessSnapshot,
    threshold: float = 0.3,
) -> bool:
    """Detect significant changes in business profile.

    Compares: name, industry, description.
    Returns True if similarity < threshold.

    Args:
        old_profile: Previous business snapshot
        new_profile: New business snapshot
        threshold: Similarity threshold (0-1). Default 0.3 means >30% change triggers regen.

    Returns:
        True if profile changed significantly, False otherwise.
    """
    old_text = f"{old_profile.name} {old_profile.industry} {old_profile.description}".lower()
    new_text = f"{new_profile.name} {new_profile.industry} {new_profile.description}".lower()

    similarity = SequenceMatcher(None, old_text, new_text).ratio()
    changed = similarity < (1 - threshold)

    if changed:
        logger.info(
            "Profile change detected: similarity %.2f < threshold %.2f",
            similarity, 1 - threshold,
        )

    return changed


def _hash_business_snapshot(business: BusinessSnapshot) -> str:
    """Create a hash of the business profile for change detection."""
    text = f"{business.name}|{business.industry}|{business.description}"
    import hashlib
    return hashlib.md5(text.encode()).hexdigest()
