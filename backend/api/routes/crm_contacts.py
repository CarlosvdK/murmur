"""CRM Contacts -- CRUD + twin operations."""

import logging
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from backend.models.crm import ContactCreate, Contact
from backend.auth.tiers import Tier, check_feature_access
from backend.auth.dependencies import get_current_user_id
from backend.db.client import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crm/contacts", tags=["crm-contacts"])


def _get_current_tier() -> Tier:
    # TODO: extract from user profile / subscription
    return Tier.CONNECT


def _contact_to_row(data: ContactCreate, user_id: UUID) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "user_id": str(user_id),
        "first_name": data.first_name,
        "last_name": data.last_name,
        "full_name": f"{data.first_name} {data.last_name or ''}".strip(),
        "job_title": data.job_title,
        "department": data.department,
        "seniority_level": data.seniority_level,
        "email": data.email,
        "phone": data.phone,
        "linkedin_url": data.linkedin_url,
        "city": data.city,
        "country": data.country,
        "contact_type": data.contact_type,
        "notes": data.notes,
        "tags": data.tags or [],
        "organisation_id": str(data.organisation_id) if data.organisation_id else None,
        "role_label": data.role_label,
        "created_at": now,
        "updated_at": now,
    }


def _row_to_contact(row: dict) -> Contact:
    return Contact(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row.get("last_name"),
        full_name=row["full_name"],
        job_title=row.get("job_title"),
        department=row.get("department"),
        seniority_level=row.get("seniority_level"),
        email=row.get("email"),
        phone=row.get("phone"),
        linkedin_url=row.get("linkedin_url"),
        city=row.get("city"),
        country=row.get("country"),
        contact_type=row.get("contact_type", "contact"),
        relationship_strength=row.get("relationship_strength", 0),
        communication_style=row.get("communication_style"),
        last_contact_date=row.get("last_contact_date"),
        has_twin=row.get("has_twin", False),
        twin_type=row.get("twin_type"),
        twin_confidence=row.get("twin_confidence"),
        twin_corpus_size=row.get("twin_corpus_size", 0),
        current_sentiment=row.get("current_sentiment"),
        sentiment_trend=row.get("sentiment_trend"),
        notes=row.get("notes"),
        tags=row.get("tags"),
        organisation_id=row.get("organisation_id"),
        organisation_name=row.get("organisation_name"),
        role_label=row.get("role_label"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.post("/", response_model=Contact)
async def create_contact(
    data: ContactCreate,
    user_id: UUID = Depends(get_current_user_id),
):
    tier = _get_current_tier()
    if not check_feature_access(tier, "crm_access"):
        raise HTTPException(status_code=403, detail="CRM requires Connect tier or higher")

    db = get_supabase()
    row = _contact_to_row(data, user_id)
    result = db.table("crm_contacts").insert(row).execute()
    return _row_to_contact(result.data[0])


@router.get("/", response_model=list[Contact])
async def list_contacts(
    contact_type: Optional[str] = None,
    has_twin: Optional[bool] = None,
    user_id: UUID = Depends(get_current_user_id),
):
    db = get_supabase()
    query = db.table("crm_contacts").select("*").eq("user_id", str(user_id))
    if contact_type:
        query = query.eq("contact_type", contact_type)
    if has_twin is not None:
        query = query.eq("has_twin", has_twin)
    result = query.order("updated_at", desc=True).execute()
    return [_row_to_contact(row) for row in result.data]


@router.get("/{contact_id}", response_model=Contact)
async def get_contact(
    contact_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
):
    db = get_supabase()
    result = (
        db.table("crm_contacts")
        .select("*")
        .eq("id", str(contact_id))
        .eq("user_id", str(user_id))
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Contact not found")
    return _row_to_contact(result.data)


@router.put("/{contact_id}", response_model=Contact)
async def update_contact(
    contact_id: UUID,
    data: ContactCreate,
    user_id: UUID = Depends(get_current_user_id),
):
    db = get_supabase()
    # Verify ownership
    existing = (
        db.table("crm_contacts")
        .select("id")
        .eq("id", str(contact_id))
        .eq("user_id", str(user_id))
        .maybe_single()
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Contact not found")

    updates = {
        "first_name": data.first_name,
        "last_name": data.last_name,
        "full_name": f"{data.first_name} {data.last_name or ''}".strip(),
        "job_title": data.job_title,
        "email": data.email,
        "phone": data.phone,
        "contact_type": data.contact_type,
        "notes": data.notes,
        "tags": data.tags or [],
        "organisation_id": str(data.organisation_id) if data.organisation_id else None,
        "role_label": data.role_label,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    result = (
        db.table("crm_contacts")
        .update(updates)
        .eq("id", str(contact_id))
        .execute()
    )
    return _row_to_contact(result.data[0])


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
):
    db = get_supabase()
    existing = (
        db.table("crm_contacts")
        .select("id")
        .eq("id", str(contact_id))
        .eq("user_id", str(user_id))
        .maybe_single()
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.table("crm_contacts").delete().eq("id", str(contact_id)).execute()
    return {"deleted": True}
