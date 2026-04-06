from fastapi import APIRouter, HTTPException
from uuid import UUID, uuid4
from datetime import datetime, timezone

from backend.models.business import BusinessCreate, Business

router = APIRouter(prefix="/businesses", tags=["businesses"])

# In-memory store for development — replaced by Supabase in production
_businesses: dict[UUID, Business] = {}


@router.post("/", response_model=Business)
async def create_business(data: BusinessCreate):
    now = datetime.now(timezone.utc)
    business = Business(
        id=uuid4(),
        user_id=uuid4(),  # TODO: Extract from Supabase auth
        name=data.name,
        type=data.type,
        description=data.description,
        customer_description=data.customer_description,
        location=data.location,
        years_open=data.years_open,
        business_role=data.business_role,
        visit_frequency=data.visit_frequency,
        busy_days=data.busy_days,
        busy_times=data.busy_times,
        customer_value_drivers=data.customer_value_drivers,
        customer_social_context=data.customer_social_context,
        regular_proportion=data.regular_proportion,
        area_demographics=data.area_demographics,
        competitor_count=data.competitor_count,
        area_feel=data.area_feel,
        website_url=data.website_url,
        google_place_id=data.google_place_id,
        additional_customer_notes=data.additional_customer_notes,
        has_prior_change=data.has_prior_change,
        prior_change_description=data.prior_change_description,
        prior_change_outcome=data.prior_change_outcome,
        location_city=data.location_city,
        location_neighbourhood=data.location_neighbourhood,
        location_country=data.location_country,
        created_at=now,
        updated_at=now,
    )
    _businesses[business.id] = business
    return business


@router.get("/{business_id}", response_model=Business)
async def get_business(business_id: UUID):
    business = _businesses.get(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


@router.get("/", response_model=list[Business])
async def list_businesses():
    return list(_businesses.values())
