from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from datetime import datetime, timezone

from backend.models.business import BusinessCreate, Business
from backend.db.client import get_supabase
from backend.auth.dependencies import get_current_user_id

router = APIRouter(prefix="/businesses", tags=["businesses"])

# Fields that live as top-level columns in the businesses table.
# Everything else goes into the metadata JSONB column.
_TOP_LEVEL_FIELDS = {
    "id", "user_id", "name", "type", "description",
    "customer_description", "location", "metadata",
    "created_at", "updated_at",
}


def _business_to_row(data: BusinessCreate, user_id: UUID) -> dict:
    """Convert a BusinessCreate into a Supabase-ready row dict."""
    now = datetime.now(timezone.utc).isoformat()
    metadata = {}
    for field in data.model_fields:
        if field not in _TOP_LEVEL_FIELDS and getattr(data, field) is not None:
            metadata[field] = getattr(data, field)
    return {
        "user_id": str(user_id),
        "name": data.name,
        "type": data.type,
        "description": data.description,
        "customer_description": data.customer_description,
        "location": data.location,
        "metadata": metadata,
        "created_at": now,
        "updated_at": now,
    }


def _row_to_business(row: dict) -> Business:
    """Convert a Supabase row into a Business model, unpacking metadata."""
    meta = row.get("metadata") or {}
    return Business(
        id=row["id"],
        user_id=row["user_id"],
        name=row["name"],
        type=row["type"],
        description=row["description"],
        customer_description=row.get("customer_description"),
        location=row.get("location"),
        years_open=meta.get("years_open"),
        business_role=meta.get("business_role"),
        visit_frequency=meta.get("visit_frequency"),
        busy_days=meta.get("busy_days"),
        busy_times=meta.get("busy_times"),
        customer_value_drivers=meta.get("customer_value_drivers"),
        customer_social_context=meta.get("customer_social_context"),
        regular_proportion=meta.get("regular_proportion"),
        area_demographics=meta.get("area_demographics"),
        competitor_count=meta.get("competitor_count"),
        area_feel=meta.get("area_feel"),
        website_url=meta.get("website_url"),
        google_place_id=meta.get("google_place_id"),
        additional_customer_notes=meta.get("additional_customer_notes"),
        has_prior_change=meta.get("has_prior_change"),
        prior_change_description=meta.get("prior_change_description"),
        prior_change_outcome=meta.get("prior_change_outcome"),
        location_street=meta.get("location_street"),
        location_number=meta.get("location_number"),
        location_postcode=meta.get("location_postcode"),
        location_city=meta.get("location_city"),
        location_neighbourhood=meta.get("location_neighbourhood"),
        location_country=meta.get("location_country"),
        location_settings=meta.get("location_settings"),
        area_draws=meta.get("area_draws"),
        customer_transport=meta.get("customer_transport"),
        has_parking=meta.get("has_parking"),
        first_visit_reasons=meta.get("first_visit_reasons"),
        seasonal_patterns=meta.get("seasonal_patterns"),
        customer_community=meta.get("customer_community"),
        opening_hours=meta.get("opening_hours"),
        google_business_url=meta.get("google_business_url"),
        tripadvisor_url=meta.get("tripadvisor_url"),
        instagram_url=meta.get("instagram_url"),
        facebook_url=meta.get("facebook_url"),
        prior_change_types=meta.get("prior_change_types"),
        prior_change_went=meta.get("prior_change_went"),
        anything_else=meta.get("anything_else"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.post("/", response_model=Business)
async def create_business(
    data: BusinessCreate,
    user_id: UUID = Depends(get_current_user_id),
):
    db = get_supabase()
    row = _business_to_row(data, user_id)
    result = db.table("businesses").insert(row).execute()
    return _row_to_business(result.data[0])


@router.put("/{business_id}", response_model=Business)
async def update_business(
    business_id: UUID,
    data: BusinessCreate,
    user_id: UUID = Depends(get_current_user_id),
):
    db = get_supabase()
    # Verify ownership
    existing = (
        db.table("businesses")
        .select("id")
        .eq("id", str(business_id))
        .eq("user_id", str(user_id))
        .maybe_single()
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Business not found")

    metadata = {}
    for field in data.model_fields:
        if field not in _TOP_LEVEL_FIELDS and getattr(data, field) is not None:
            metadata[field] = getattr(data, field)

    updates = {
        "name": data.name,
        "type": data.type,
        "description": data.description,
        "customer_description": data.customer_description,
        "location": data.location,
        "metadata": metadata,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    result = (
        db.table("businesses")
        .update(updates)
        .eq("id", str(business_id))
        .execute()
    )
    return _row_to_business(result.data[0])


@router.get("/{business_id}", response_model=Business)
async def get_business(
    business_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
):
    db = get_supabase()
    result = (
        db.table("businesses")
        .select("*")
        .eq("id", str(business_id))
        .eq("user_id", str(user_id))
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Business not found")
    return _row_to_business(result.data)


@router.get("/", response_model=list[Business])
async def list_businesses(user_id: UUID = Depends(get_current_user_id)):
    db = get_supabase()
    result = (
        db.table("businesses")
        .select("*")
        .eq("user_id", str(user_id))
        .execute()
    )
    return [_row_to_business(row) for row in result.data]


@router.delete("/account")
async def delete_account(user_id: UUID = Depends(get_current_user_id)):
    """Delete all user data: businesses (cascades to simulations, personas, etc.), contacts, and auth account."""
    db = get_supabase()

    # Delete CRM data (contacts cascade to correspondence, signals, twin queries)
    db.table("crm_contacts").delete().eq("user_id", str(user_id)).execute()
    db.table("crm_organisations").delete().eq("user_id", str(user_id)).execute()

    # Delete businesses (cascades to simulations, personas, responses, results, uploads, outcomes)
    db.table("businesses").delete().eq("user_id", str(user_id)).execute()

    # Delete Supabase auth user
    try:
        db.auth.admin.delete_user(str(user_id))
    except Exception:
        pass  # Auth deletion may fail if using anon key -- user can still be cleaned up in dashboard

    return {"deleted": True}
