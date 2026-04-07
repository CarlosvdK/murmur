from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class BusinessCreate(BaseModel):
    # Step 1: Business basics
    name: str
    type: str
    description: str
    location: Optional[str] = None
    years_open: Optional[str] = None

    # Step 2: Customer relationship signals
    customer_description: Optional[str] = None
    business_role: Optional[str] = None  # habit|daily_need|treat|social|convenience|destination
    visit_frequency: Optional[str] = None  # daily|weekly|monthly|occasional|mixed
    busy_days: Optional[list[str]] = None
    busy_times: Optional[list[str]] = None
    customer_value_drivers: Optional[list[str]] = None
    customer_social_context: Optional[list[str]] = None
    regular_proportion: Optional[str] = None  # almost_none|handful|solid_base|mostly_regulars

    # Step 3: Local area
    area_demographics: Optional[list[str]] = None
    competitor_count: Optional[str] = None  # only_one|one_two|three_five|six_plus
    area_feel: Optional[str] = None  # community|transactional|destination|passing_trade

    # Step 4: Optional enrichment
    website_url: Optional[str] = None
    google_business_url: Optional[str] = None
    google_place_id: Optional[str] = None
    additional_customer_notes: Optional[str] = None
    has_prior_change: Optional[bool] = None
    prior_change_description: Optional[str] = None
    prior_change_outcome: Optional[str] = None

    # Structured location
    location_street: Optional[str] = None
    location_number: Optional[str] = None
    location_postcode: Optional[str] = None
    location_city: Optional[str] = None
    location_neighbourhood: Optional[str] = None
    location_country: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    # Extended fields
    location_settings: Optional[list[str]] = None
    area_draws: Optional[list[str]] = None
    customer_transport: Optional[list[str]] = None
    has_parking: Optional[str] = None
    first_visit_reasons: Optional[list[str]] = None
    seasonal_patterns: Optional[list[str]] = None
    customer_community: Optional[str] = None
    opening_hours: Optional[dict] = None
    google_business_url: Optional[str] = None
    tripadvisor_url: Optional[str] = None
    instagram_url: Optional[str] = None
    facebook_url: Optional[str] = None
    prior_change_types: Optional[list[str]] = None
    prior_change_went: Optional[str] = None
    anything_else: Optional[str] = None


class Business(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    type: str
    description: str
    customer_description: Optional[str] = None
    location: Optional[str] = None
    years_open: Optional[str] = None
    business_role: Optional[str] = None
    visit_frequency: Optional[str] = None
    busy_days: Optional[list[str]] = None
    busy_times: Optional[list[str]] = None
    customer_value_drivers: Optional[list[str]] = None
    customer_social_context: Optional[list[str]] = None
    regular_proportion: Optional[str] = None
    area_demographics: Optional[list[str]] = None
    competitor_count: Optional[str] = None
    area_feel: Optional[str] = None
    website_url: Optional[str] = None
    google_place_id: Optional[str] = None
    additional_customer_notes: Optional[str] = None
    has_prior_change: Optional[bool] = None
    prior_change_description: Optional[str] = None
    prior_change_outcome: Optional[str] = None
    location_street: Optional[str] = None
    location_number: Optional[str] = None
    location_postcode: Optional[str] = None
    location_city: Optional[str] = None
    location_neighbourhood: Optional[str] = None
    location_country: Optional[str] = None
    # Extended fields
    location_settings: Optional[list[str]] = None
    area_draws: Optional[list[str]] = None
    customer_transport: Optional[list[str]] = None
    has_parking: Optional[str] = None
    first_visit_reasons: Optional[list[str]] = None
    seasonal_patterns: Optional[list[str]] = None
    customer_community: Optional[str] = None
    opening_hours: Optional[dict] = None
    google_business_url: Optional[str] = None
    tripadvisor_url: Optional[str] = None
    instagram_url: Optional[str] = None
    facebook_url: Optional[str] = None
    prior_change_types: Optional[list[str]] = None
    prior_change_went: Optional[str] = None
    anything_else: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BusinessSnapshot(BaseModel):
    """Frozen copy of business profile at simulation time."""
    name: str
    type: str
    description: str
    customer_description: Optional[str] = None
    location: Optional[str] = None
    years_open: Optional[str] = None
    business_role: Optional[str] = None
    visit_frequency: Optional[str] = None
    customer_value_drivers: Optional[list[str]] = None
    customer_social_context: Optional[list[str]] = None
    regular_proportion: Optional[str] = None
    area_demographics: Optional[list[str]] = None
    competitor_count: Optional[str] = None
    area_feel: Optional[str] = None
    additional_customer_notes: Optional[str] = None
