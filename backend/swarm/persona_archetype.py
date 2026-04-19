"""
Persona archetype cache layer with 1-month TTL.

Personas are expensive to generate (one API call per persona, ~15s per swarm).
For a given business, we reuse the same "archetype" (demographics, personality,
OCEAN traits) across multiple questions, as long as the archetype is fresh
(<30 days old). The responses (Turn 2, 2b, 3) are always generated fresh.

This keeps the swarm feeling consistent ("Maria from last week is still here")
while avoiding stale personas that have drifted from current customer behavior.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
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
        # Try to load from cache
        archetype = db.table("persona_archetypes").select("*").eq(
            "business_id", business_id
        ).execute()

        if archetype.data and len(archetype.data) > 0:
            row = archetype.data[0]
            expires_at = datetime.fromisoformat(row["expires_at"])
            now = datetime.now(timezone.utc)

            if expires_at > now:
                # Cache is valid
                profiles_data = row["profiles"]
                personas = [
                    PersonaProfile(**p) if isinstance(p, dict) else p
                    for p in profiles_data
                ]
                logger.info(
                    "Persona archetype cache HIT for business %s, %d personas, "
                    "expires in %.0f hours",
                    business_id, len(personas),
                    (expires_at - now).total_seconds() / 3600,
                )
                return personas, False
            else:
                # Cache is expired
                logger.info("Persona archetype cache EXPIRED for business %s", business_id)

    except Exception as e:
        logger.warning("Archetype cache lookup failed (non-fatal): %s", e)

    # Cache miss or error -- generate fresh
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
        expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

        db.table("persona_archetypes").upsert(
            {
                "business_id": business_id,
                "profiles": profiles_json,
                "persona_count": len(personas),
                "expires_at": expires_at,
            }
        ).execute()

        logger.info(
            "Stored persona archetype for business %s, %d personas, expires %s",
            business_id, len(personas), expires_at,
        )
    except Exception as e:
        logger.warning("Failed to store archetype (non-fatal): %s", e)

    return personas, True


async def delete_expired_archetypes(db) -> int:
    """Clean up expired archetypes. Call this as a daily cron job.

    Returns number of rows deleted.
    """
    if db is None:
        return 0

    try:
        now = datetime.now(timezone.utc).isoformat()
        result = db.table("persona_archetypes").delete().lt("expires_at", now).execute()
        deleted = len(result.data) if result.data else 0
        logger.info("Deleted %d expired persona archetypes", deleted)
        return deleted
    except Exception as e:
        logger.warning("Failed to delete expired archetypes: %s", e)
        return 0
