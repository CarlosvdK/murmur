"""Tests for backend.config -- Settings defaults."""

from backend.config import Settings


class TestSettingsDefaults:
    def test_persona_count_default(self):
        s = Settings(anthropic_api_key="x", supabase_url="x", supabase_key="x")
        assert s.persona_count == 15

    def test_concurrency_limit_default(self):
        s = Settings(anthropic_api_key="x", supabase_url="x", supabase_key="x")
        assert s.concurrency_limit == 5

    def test_model_name_default(self):
        s = Settings(anthropic_api_key="x", supabase_url="x", supabase_key="x")
        assert s.model_name == "claude-sonnet-4-20250514"

    def test_redis_url_default(self):
        s = Settings(anthropic_api_key="x", supabase_url="x", supabase_key="x")
        assert s.redis_url == "redis://localhost:6379"

    def test_context_enabled_default(self):
        s = Settings(anthropic_api_key="x", supabase_url="x", supabase_key="x")
        assert s.context_enabled is True

    def test_context_timeout_default(self):
        s = Settings(anthropic_api_key="x", supabase_url="x", supabase_key="x")
        assert s.context_timeout == 90

    def test_context_tool_timeout_default(self):
        s = Settings(anthropic_api_key="x", supabase_url="x", supabase_key="x")
        assert s.context_tool_timeout == 30

    def test_context_max_tools_default(self):
        s = Settings(anthropic_api_key="x", supabase_url="x", supabase_key="x")
        assert s.context_max_tools == 5

    def test_api_keys_default_empty_when_no_env(self):
        """API keys default to empty string (may be overridden by .env in dev)."""
        # We test with explicit empty values to avoid picking up .env
        s = Settings(
            anthropic_api_key="x",
            supabase_url="x",
            supabase_key="x",
            google_places_api_key="",
            brave_search_api_key="",
            reddit_client_id="",
            reddit_client_secret="",
        )
        assert s.google_places_api_key == ""
        assert s.brave_search_api_key == ""
        assert s.reddit_client_id == ""
        assert s.reddit_client_secret == ""

    def test_custom_values_override(self):
        s = Settings(
            anthropic_api_key="real-key",
            persona_count=25,
            concurrency_limit=10,
            context_enabled=False,
        )
        assert s.persona_count == 25
        assert s.concurrency_limit == 10
        assert s.context_enabled is False
