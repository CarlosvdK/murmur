"""Supabase client singleton for backend database access."""

from functools import lru_cache
from supabase import create_client, Client
from backend.config import get_settings


@lru_cache()
def get_supabase() -> Client:
    """Return a Supabase client using the service-role key (bypasses RLS).

    Once Supabase Auth is wired in, routes that need user-scoped access
    should create per-request clients with the user's JWT instead.
    """
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env"
        )
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
