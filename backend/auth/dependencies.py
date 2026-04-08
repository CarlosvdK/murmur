"""FastAPI dependency for extracting the authenticated Supabase user."""

from uuid import UUID
from fastapi import HTTPException, Request
from backend.db.client import get_supabase
from backend.auth.tiers import Tier


async def get_current_user_id(request: Request) -> UUID:
    """Extract user_id from the Supabase JWT in the Authorization header."""
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = auth_header.removeprefix("Bearer ")
    db = get_supabase()
    try:
        user_response = db.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return UUID(user_response.user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {e}")


async def get_current_user_tier(request: Request) -> Tier:
    """Extract the user's tier from Supabase user metadata.

    Reads raw_user_meta_data.tier from the JWT. Defaults to SIMULATE (free).
    To upgrade a user: update their metadata in Supabase dashboard or via API.
    """
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return Tier.SIMULATE

    token = auth_header.removeprefix("Bearer ")
    db = get_supabase()
    try:
        user_response = db.auth.get_user(token)
        if not user_response or not user_response.user:
            return Tier.SIMULATE
        meta = user_response.user.user_metadata or {}
        tier_str = meta.get("tier", "simulate")
        try:
            return Tier(tier_str)
        except ValueError:
            return Tier.SIMULATE
    except Exception:
        return Tier.SIMULATE
