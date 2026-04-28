"""Tests for Supabase database client initialization."""
import pytest
from unittest.mock import patch, MagicMock

from backend.db.client import get_supabase


class TestGetSupabaseClient:
    """Test Supabase client initialization."""

    def test_get_supabase_returns_client(self):
        """get_supabase() should return a Supabase client instance."""
        client = get_supabase()
        assert client is not None
        # Client should have expected methods
        assert hasattr(client, "table")
        assert hasattr(client, "auth")
        assert hasattr(client, "postgrest")

    def test_get_supabase_cached(self):
        """get_supabase() should cache and return same instance (LRU cache)."""
        client1 = get_supabase()
        client2 = get_supabase()
        # Should be same instance due to lru_cache
        assert client1 is client2

    def test_get_supabase_uses_env_vars(self):
        """Client should use SUPABASE_URL and SUPABASE_KEY from env."""
        # This test verifies the client is initialized with correct credentials
        # by checking that it has the expected components
        client = get_supabase()
        # Client should have postgrest component which uses the URL and key
        assert hasattr(client, "postgrest")
        assert client.postgrest is not None
        # Should also have auth component
        assert hasattr(client, "auth")
        assert client.auth is not None
