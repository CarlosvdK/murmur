"""FastAPI dependency for extracting the authenticated Supabase user."""

from uuid import UUID
from fastapi import Depends, HTTPException, Request
from backend.db.client import get_supabase


async def get_current_user_id(request: Request) -> UUID:
    """Extract user_id from the Supabase JWT in the Authorization header.

    Uses the service-role client to verify the token via Supabase's
    auth.get_user() endpoint -- no local JWT secret needed.
    """
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
