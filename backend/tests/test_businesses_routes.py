"""Tests for business CRUD API endpoints."""
import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock
from datetime import datetime

from fastapi.testclient import TestClient
from fastapi import HTTPException
from backend.api.main import app
from backend.models.business import BusinessCreate, Business
from backend.auth.dependencies import get_current_user_id


# Create test client
client = TestClient(app)


def _make_business_row(business_id: str, user_id: str, name: str = "Test Coffee Shop", **kwargs):
    """Create a complete business row with all required fields."""
    return {
        "id": business_id,
        "user_id": user_id,
        "name": name,
        "type": kwargs.get("type", "restaurant"),
        "description": kwargs.get("description", "A cozy coffee shop"),
        "customer_description": kwargs.get("customer_description", "Office workers and students"),
        "location": kwargs.get("location", "San Francisco, CA"),
        "metadata": kwargs.get("metadata", {}),
        "created_at": kwargs.get("created_at", "2024-01-01T00:00:00Z"),
        "updated_at": kwargs.get("updated_at", "2024-01-01T00:00:00Z"),
        "years_open": None,
        "business_role": None,
        "business_not_role": None,
        "visit_frequency": None,
        "busy_days": None,
        "busy_times": None,
        "customer_value_drivers": None,
        "customer_social_context": None,
        "regular_proportion": None,
        "area_demographics": None,
        "competitor_count": None,
        "area_feel": None,
        "website_url": None,
        "google_place_id": None,
        "additional_customer_notes": None,
        "has_prior_change": None,
        "prior_change_description": None,
        "prior_change_outcome": None,
        "location_street": None,
        "location_number": None,
        "location_postcode": None,
        "location_city": None,
        "location_neighbourhood": None,
        "location_country": None,
        "location_settings": None,
        "area_draws": None,
        "customer_transport": None,
        "has_parking": None,
        "first_visit_reasons": None,
        "seasonal_patterns": None,
        "customer_community": None,
        "opening_hours": None,
        "google_business_url": None,
        "tripadvisor_url": None,
        "instagram_url": None,
        "facebook_url": None,
        "prior_change_types": None,
        "prior_change_went": None,
        "anything_else": None,
    }


def _create_mock_supabase():
    """Create a fresh MagicMock for Supabase that properly chains."""
    return MagicMock()


def _setup_auth_override(user_id):
    """Create an async override for auth dependency."""
    async def override():
        return user_id
    app.dependency_overrides[get_current_user_id] = override


def teardown_overrides():
    """Clear dependency overrides after test."""
    app.dependency_overrides.clear()


class TestCreateBusiness:
    """Test POST /api/businesses endpoint."""

    def test_create_business_success(self):
        """POST /api/businesses with valid data should create business."""
        business_id = str(uuid4())
        user_id = str(uuid4())

        _setup_auth_override(user_id)
        try:
            with patch("backend.api.routes.businesses.get_supabase") as mock_get_supabase:
                mock_db = _create_mock_supabase()
                mock_get_supabase.return_value = mock_db

                # Mock the insert chain
                business_row = _make_business_row(business_id, user_id)
                mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock(
                    data=[business_row]
                )

                payload = {
                    "name": "Test Coffee Shop",
                    "type": "restaurant",
                    "description": "A cozy coffee shop",
                    "customer_description": "Office workers and students",
                    "location": "San Francisco, CA",
                }

                response = client.post("/api/businesses", json=payload)
                assert response.status_code in [200, 201], f"Got {response.status_code}: {response.text}"
                assert response.json()["name"] == "Test Coffee Shop"
        finally:
            teardown_overrides()

    def test_create_business_requires_auth(self):
        """POST /api/businesses without auth should return 401."""
        async def override_auth():
            raise HTTPException(status_code=401, detail="No auth")

        app.dependency_overrides[get_current_user_id] = override_auth
        try:
            payload = {
                "name": "Test Coffee Shop",
                "type": "restaurant",
                "description": "A cozy coffee shop",
                "customer_description": "Office workers and students",
                "location": "San Francisco, CA",
            }

            response = client.post("/api/businesses", json=payload)
            assert response.status_code == 401
        finally:
            teardown_overrides()


class TestGetBusiness:
    """Test GET /api/businesses/{id} endpoint."""

    def test_get_business_owned_by_user(self):
        """GET /api/businesses/{id} should return business if owned by user."""
        business_id = str(uuid4())
        user_id = str(uuid4())

        _setup_auth_override(user_id)
        try:
            with patch("backend.api.routes.businesses.get_supabase") as mock_get_supabase:
                mock_db = _create_mock_supabase()
                mock_get_supabase.return_value = mock_db

                business_row = _make_business_row(business_id, user_id)
                # The .execute() returns an object with .data attribute
                execute_result = MagicMock()
                execute_result.data = business_row
                mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = execute_result

                response = client.get(f"/api/businesses/{business_id}")
                assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
                assert response.json()["name"] == "Test Coffee Shop"
        finally:
            teardown_overrides()

    def test_get_business_not_found(self):
        """GET /api/businesses/{id} should return 404 if not found."""
        business_id = str(uuid4())
        user_id = str(uuid4())

        _setup_auth_override(user_id)
        try:
            with patch("backend.api.routes.businesses.get_supabase") as mock_get_supabase:
                mock_db = _create_mock_supabase()
                mock_get_supabase.return_value = mock_db

                # Simulate "not found" from Supabase (data is None)
                execute_result = MagicMock()
                execute_result.data = None
                mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = execute_result

                response = client.get(f"/api/businesses/{business_id}")
                assert response.status_code == 404
        finally:
            teardown_overrides()

    def test_get_business_wrong_owner(self):
        """GET /api/businesses/{id} should return 404 when user doesn't match."""
        business_id = str(uuid4())
        user_id = str(uuid4())

        _setup_auth_override(user_id)
        try:
            with patch("backend.api.routes.businesses.get_supabase") as mock_get_supabase:
                mock_db = _create_mock_supabase()
                mock_get_supabase.return_value = mock_db

                # Business owned by different user - query returns None due to eq filter
                execute_result = MagicMock()
                execute_result.data = None
                mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = execute_result

                response = client.get(f"/api/businesses/{business_id}")
                assert response.status_code == 404
        finally:
            teardown_overrides()


class TestUpdateBusiness:
    """Test PUT /api/businesses/{id} endpoint."""

    def test_update_business_success(self):
        """PUT /api/businesses/{id} should update fields."""
        business_id = str(uuid4())
        user_id = str(uuid4())

        _setup_auth_override(user_id)
        try:
            with patch("backend.api.routes.businesses.get_supabase") as mock_get_supabase:
                mock_db = _create_mock_supabase()
                mock_get_supabase.return_value = mock_db

                # Mock the ownership check (first select query)
                mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                    data={"id": business_id}
                )

                # Mock the update response
                updated_row = _make_business_row(
                    business_id,
                    user_id,
                    name="Updated Coffee Shop",
                    description="An updated cozy coffee shop"
                )
                mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[updated_row]
                )

                payload = {
                    "name": "Updated Coffee Shop",
                    "type": "restaurant",
                    "description": "An updated cozy coffee shop",
                    "customer_description": "Office workers",
                    "location": "San Francisco, CA",
                }
                response = client.put(f"/api/businesses/{business_id}", json=payload)
                assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
                assert response.json()["name"] == "Updated Coffee Shop"
        finally:
            teardown_overrides()

    def test_update_business_not_found(self):
        """PUT /api/businesses/{id} should return 404 if not owner."""
        business_id = str(uuid4())
        user_id = str(uuid4())

        _setup_auth_override(user_id)
        try:
            with patch("backend.api.routes.businesses.get_supabase") as mock_get_supabase:
                mock_db = _create_mock_supabase()
                mock_get_supabase.return_value = mock_db

                # Try to update business not owned by user (ownership check fails)
                mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MagicMock(
                    data=None
                )

                payload = {
                    "name": "Hacked Shop",
                    "type": "restaurant",
                    "description": "A hacked shop",
                    "customer_description": "Hackers",
                    "location": "Hacker Town",
                }
                response = client.put(f"/api/businesses/{business_id}", json=payload)
                assert response.status_code == 404
        finally:
            teardown_overrides()


class TestListBusinesses:
    """Test GET /api/businesses endpoint."""

    def test_list_businesses_returns_user_businesses(self):
        """GET /api/businesses should return only user's businesses."""
        user_id = str(uuid4())

        _setup_auth_override(user_id)
        try:
            with patch("backend.api.routes.businesses.get_supabase") as mock_get_supabase:
                mock_db = _create_mock_supabase()
                mock_get_supabase.return_value = mock_db

                business_id_1 = str(uuid4())
                business_id_2 = str(uuid4())

                businesses = [
                    _make_business_row(business_id_1, user_id, name="Coffee Shop", type="restaurant", description="Cozy", customer_description="Office workers", location="SF"),
                    _make_business_row(business_id_2, user_id, name="Barber Shop", type="service", description="Professional", customer_description="Professionals", location="SF"),
                ]

                mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=businesses
                )

                response = client.get("/api/businesses")
                assert response.status_code == 200
                assert len(response.json()) == 2
                assert response.json()[0]["name"] == "Coffee Shop"
                assert response.json()[1]["name"] == "Barber Shop"
        finally:
            teardown_overrides()

    def test_list_businesses_empty(self):
        """GET /api/businesses should return empty list if no businesses."""
        user_id = str(uuid4())

        _setup_auth_override(user_id)
        try:
            with patch("backend.api.routes.businesses.get_supabase") as mock_get_supabase:
                mock_db = _create_mock_supabase()
                mock_get_supabase.return_value = mock_db

                mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[]
                )

                response = client.get("/api/businesses")
                assert response.status_code == 200
                assert response.json() == []
        finally:
            teardown_overrides()
