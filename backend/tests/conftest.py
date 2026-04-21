"""Pytest configuration and shared fixtures."""
import pytest
from uuid import uuid4
from backend.api.main import app
from backend.auth.dependencies import get_current_user_id
from backend.observability.rate_limit import limiter


# Set up auth override globally for all tests
test_user_id = str(uuid4())


def mock_get_current_user_id():
    return test_user_id


app.dependency_overrides[get_current_user_id] = mock_get_current_user_id


@pytest.fixture(autouse=True)
def restore_auth_override():
    """Ensure auth override is restored after each test."""
    yield
    # Restore the auth override in case a test cleared it
    if get_current_user_id not in app.dependency_overrides:
        app.dependency_overrides[get_current_user_id] = mock_get_current_user_id


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """slowapi's in-memory storage persists across TestClient calls within a
    pytest process -- clear it before each test so limits don't leak."""
    limiter.reset()
    yield
    limiter.reset()
