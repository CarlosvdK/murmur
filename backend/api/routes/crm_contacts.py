"""CRM Contacts -- CRUD + twin operations."""

import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional

from fastapi import APIRouter, HTTPException

from backend.models.crm import ContactCreate, Contact
from backend.auth.tiers import Tier, check_feature_access

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crm/contacts", tags=["crm-contacts"])

# In-memory store (dev)
_contacts: dict[UUID, Contact] = {}


def _get_current_tier() -> Tier:
    # TODO: extract from auth
    return Tier.CONNECT


@router.post("/", response_model=Contact)
async def create_contact(data: ContactCreate):
    tier = _get_current_tier()
    if not check_feature_access(tier, "crm_access"):
        raise HTTPException(status_code=403, detail="CRM requires Connect tier or higher")

    now = datetime.now(timezone.utc)
    contact = Contact(
        id=uuid4(),
        first_name=data.first_name,
        last_name=data.last_name,
        full_name=f"{data.first_name} {data.last_name or ''}".strip(),
        job_title=data.job_title,
        department=data.department,
        seniority_level=data.seniority_level,
        email=data.email,
        phone=data.phone,
        linkedin_url=data.linkedin_url,
        city=data.city,
        country=data.country,
        contact_type=data.contact_type,
        notes=data.notes,
        tags=data.tags or [],
        organisation_id=data.organisation_id,
        role_label=data.role_label,
        created_at=now,
        updated_at=now,
    )
    _contacts[contact.id] = contact
    return contact


@router.get("/", response_model=list[Contact])
async def list_contacts(
    contact_type: Optional[str] = None,
    has_twin: Optional[bool] = None,
):
    results = list(_contacts.values())
    if contact_type:
        results = [c for c in results if c.contact_type == contact_type]
    if has_twin is not None:
        results = [c for c in results if c.has_twin == has_twin]
    return sorted(results, key=lambda c: c.updated_at, reverse=True)


@router.get("/{contact_id}", response_model=Contact)
async def get_contact(contact_id: UUID):
    contact = _contacts.get(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=Contact)
async def update_contact(contact_id: UUID, data: ContactCreate):
    contact = _contacts.get(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.first_name = data.first_name
    contact.last_name = data.last_name
    contact.full_name = f"{data.first_name} {data.last_name or ''}".strip()
    contact.job_title = data.job_title
    contact.email = data.email
    contact.phone = data.phone
    contact.contact_type = data.contact_type
    contact.notes = data.notes
    contact.tags = data.tags or []
    contact.organisation_id = data.organisation_id
    contact.role_label = data.role_label
    contact.updated_at = datetime.now(timezone.utc)
    return contact


@router.delete("/{contact_id}")
async def delete_contact(contact_id: UUID):
    if contact_id not in _contacts:
        raise HTTPException(status_code=404, detail="Contact not found")
    del _contacts[contact_id]
    return {"deleted": True}
