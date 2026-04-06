from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_role_key: str = ""
    redis_url: str = "redis://localhost:6379"
    persona_count: int = 15
    concurrency_limit: int = 5
    model_name: str = "claude-sonnet-4-20250514"

    # Context enrichment API keys (all optional -- tools degrade gracefully)
    google_places_api_key: str = ""
    brave_search_api_key: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""

    # Context engine tuning
    context_enabled: bool = True
    context_timeout: int = 90
    context_tool_timeout: int = 30
    context_max_tools: int = 5

    model_config = {"env_file": ".env", "protected_namespaces": ("settings_",)}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
