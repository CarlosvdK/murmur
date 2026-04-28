"""Tests for authentication and authorization dependencies."""
import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock
from fastapi import HTTPException, Request

from backend.auth.dependencies import get_current_user_id, get_current_user_tier
from backend.auth.tiers import Tier


def _make_request(auth_header: str = "") -> Request:
    """Create a mock Request with Authorization header."""
    request = MagicMock(spec=Request)
    request.headers = MagicMock()
    request.headers.get = MagicMock(return_value=auth_header)
    return request


class TestGetCurrentUserIdValidToken:
    """Test valid token extraction via Supabase."""

    @pytest.mark.asyncio
    async def test_valid_token_extracts_user_id(self):
        """Valid token should extract user_id from Supabase response."""
        user_id = str(uuid4())
        request = _make_request(f"Bearer valid_token")

        with patch("backend.auth.dependencies.get_supabase") as mock_db:
            mock_user = MagicMock()
            mock_user.id = user_id
            mock_response = MagicMock()
            mock_response.user = mock_user
            mock_db.return_value.auth.get_user.return_value = mock_response

            result = await get_current_user_id(request)
            assert str(result) == user_id

    @pytest.mark.asyncio
    async def test_valid_token_returns_uuid(self):
        """Result should be a valid UUID."""
        user_id = str(uuid4())
        request = _make_request(f"Bearer token123")

        with patch("backend.auth.dependencies.get_supabase") as mock_db:
            mock_user = MagicMock()
            mock_user.id = user_id
            mock_response = MagicMock()
            mock_response.user = mock_user
            mock_db.return_value.auth.get_user.return_value = mock_response

            result = await get_current_user_id(request)
            assert isinstance(result, type(uuid4()))


class TestGetCurrentUserIdInvalidToken:
    """Test invalid/missing token handling."""

    @pytest.mark.asyncio
    async def test_missing_auth_header_raises_401(self):
        """Missing Authorization header should raise 401."""
        request = _make_request("")  # Empty auth header

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_id(request)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_malformed_auth_header_raises_401(self):
        """Malformed Authorization header should raise 401."""
        request = _make_request("InvalidBearer token")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_id(request)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_bearer_prefix_raises_401(self):
        """Authorization header without 'Bearer' prefix should raise 401."""
        request = _make_request("token_without_bearer")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_id(request)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_supabase_returns_no_user_raises_401(self):
        """When Supabase auth returns no user, should raise 401."""
        request = _make_request("Bearer expired_token")

        with patch("backend.auth.dependencies.get_supabase") as mock_db:
            mock_response = MagicMock()
            mock_response.user = None
            mock_db.return_value.auth.get_user.return_value = mock_response

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_id(request)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_supabase_auth_exception_raises_401(self):
        """When Supabase auth raises exception, should raise 401."""
        request = _make_request("Bearer bad_token")

        with patch("backend.auth.dependencies.get_supabase") as mock_db:
            mock_db.return_value.auth.get_user.side_effect = Exception("Invalid token")

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_id(request)
            assert exc_info.value.status_code == 401


class TestGetCurrentUserTier:
    """Test user tier extraction from Supabase user metadata."""

    @pytest.mark.asyncio
    async def test_connect_tier_from_metadata(self):
        """Tier 'connect' should be extracted from user metadata."""
        user_id = str(uuid4())
        request = _make_request("Bearer token123")

        with patch("backend.auth.dependencies.get_supabase") as mock_db:
            mock_user = MagicMock()
            mock_user.id = user_id
            mock_user.user_metadata = {"tier": "connect"}
            mock_response = MagicMock()
            mock_response.user = mock_user
            mock_db.return_value.auth.get_user.return_value = mock_response

            result = await get_current_user_tier(request)
            assert result == Tier.CONNECT

    @pytest.mark.asyncio
    async def test_intelligence_tier_from_metadata(self):
        """Tier 'intelligence' should be extracted from user metadata."""
        user_id = str(uuid4())
        request = _make_request("Bearer token123")

        with patch("backend.auth.dependencies.get_supabase") as mock_db:
            mock_user = MagicMock()
            mock_user.id = user_id
            mock_user.user_metadata = {"tier": "intelligence"}
            mock_response = MagicMock()
            mock_response.user = mock_user
            mock_db.return_value.auth.get_user.return_value = mock_response

            result = await get_current_user_tier(request)
            assert result == Tier.INTELLIGENCE

    @pytest.mark.asyncio
    async def test_missing_tier_defaults_to_simulate(self):
        """Missing tier should default to SIMULATE tier."""
        user_id = str(uuid4())
        request = _make_request("Bearer token123")

        with patch("backend.auth.dependencies.get_supabase") as mock_db:
            mock_user = MagicMock()
            mock_user.id = user_id
            mock_user.user_metadata = {}  # No tier
            mock_response = MagicMock()
            mock_response.user = mock_user
            mock_db.return_value.auth.get_user.return_value = mock_response

            result = await get_current_user_tier(request)
            assert result == Tier.SIMULATE

    @pytest.mark.asyncio
    async def test_missing_auth_header_defaults_to_simulate(self):
        """Missing Authorization header should default to SIMULATE tier."""
        request = _make_request("")

        result = await get_current_user_tier(request)
        assert result == Tier.SIMULATE

    @pytest.mark.asyncio
    async def test_invalid_tier_value_defaults_to_simulate(self):
        """Invalid tier value should default to SIMULATE tier."""
        user_id = str(uuid4())
        request = _make_request("Bearer token123")

        with patch("backend.auth.dependencies.get_supabase") as mock_db:
            mock_user = MagicMock()
            mock_user.id = user_id
            mock_user.user_metadata = {"tier": "invalid_tier"}
            mock_response = MagicMock()
            mock_response.user = mock_user
            mock_db.return_value.auth.get_user.return_value = mock_response

            result = await get_current_user_tier(request)
            assert result == Tier.SIMULATE

    @pytest.mark.asyncio
    async def test_supabase_error_defaults_to_simulate(self):
        """Supabase auth error should default to SIMULATE tier."""
        request = _make_request("Bearer bad_token")

        with patch("backend.auth.dependencies.get_supabase") as mock_db:
            mock_db.return_value.auth.get_user.side_effect = Exception("Auth error")

            result = await get_current_user_tier(request)
            assert result == Tier.SIMULATE
