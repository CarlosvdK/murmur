"""CRM Organisations -- CRUD."""

import logging
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from backend.models.crm import OrganisationCreate, Organisation
from backend.auth.tiers import Tier, check_feature_access
from backend.auth.dependencies import get_current_user_id, get_current_user_tier
from backend.db.client import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crm/organisations", tags=["crm-organisations"])


def _org_to_row(data: OrganisationCreate, user_id: UUID) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "user_id": str(user_id),
        "name": data.name,
        "domain": data.domain,
        "organisation_type": data.organisation_type,
        "industry": data.industry,
        "size_category": data.size_category,
        "country": data.country,
        "city": data.city,
        "relationship_status": data.relationship_status,
        "relationship_since": data.relationship_since.isoformat() if data.relationship_since else None,
        "contract_value_annual": float(data.contract_value_annual) if data.contract_value_annual else None,
        "currency": data.currency,
        "website_url": data.website_url,
        "description": data.description,
        "tags": data.tags or [],
        "created_at": now,
        "updated_at": now,
    }


def _row_to_org(row: dict) -> Organisation:
    return Organisation(
        id=row["id"],
        name=row["name"],
        domain=row.get("domain"),
        organisation_type=row.get("organisation_type", "customer"),
        industry=row.get("industry"),
        size_category=row.get("size_category"),
        country=row.get("country"),
        city=row.get("city"),
        relationship_status=row.get("relationship_status", "active"),
        relationship_since=row.get("relationship_since"),
        contract_value_annual=row.get("contract_value_annual"),
        currency=row.get("currency", "EUR"),
        health_score=row.get("health_score"),
        health_trend=row.get("health_trend"),
        last_contact_date=row.get("last_contact_date"),
        has_twin=row.get("has_twin", False),
        website_url=row.get("website_url"),
        description=row.get("description"),
        tags=row.get("tags"),
        contacts_count=row.get("contacts_count", 0),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.post("/", response_model=Organisation)
async def create_organisation(
    data: OrganisationCreate,
    user_id: UUID = Depends(get_current_user_id),
    tier: Tier = Depends(get_current_user_tier),
):
    if not check_feature_access(tier, "crm_access"):
        raise HTTPException(status_code=403, detail="CRM requires Connect tier or higher")

    db = get_supabase()
    row = _org_to_row(data, user_id)
    result = db.table("crm_organisations").insert(row).execute()
    return _row_to_org(result.data[0])


@router.get("/", response_model=list[Organisation])
async def list_organisations(
    organisation_type: Optional[str] = None,
    user_id: UUID = Depends(get_current_user_id),
):
    db = get_supabase()
    query = db.table("crm_organisations").select("*").eq("user_id", str(user_id))
    if organisation_type:
        query = query.eq("organisation_type", organisation_type)
    result = query.order("updated_at", desc=True).execute()
    return [_row_to_org(row) for row in result.data]


@router.get("/{org_id}", response_model=Organisation)
async def get_organisation(
    org_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
):
    db = get_supabase()
    result = (
        db.table("crm_organisations")
        .select("*")
        .eq("id", str(org_id))
        .eq("user_id", str(user_id))
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return _row_to_org(result.data)


@router.delete("/{org_id}")
async def delete_organisation(
    org_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
):
    db = get_supabase()
    existing = (
        db.table("crm_organisations")
        .select("id")
        .eq("id", str(org_id))
        .eq("user_id", str(user_id))
        .maybe_single()
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Organisation not found")
    db.table("crm_organisations").delete().eq("id", str(org_id)).execute()
    return {"deleted": True}
