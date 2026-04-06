"""CRM Organisations -- CRUD."""

import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional

from fastapi import APIRouter, HTTPException

from backend.models.crm import OrganisationCreate, Organisation
from backend.auth.tiers import Tier, check_feature_access

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crm/organisations", tags=["crm-organisations"])

_organisations: dict[UUID, Organisation] = {}


def _get_current_tier() -> Tier:
    return Tier.CONNECT


@router.post("/", response_model=Organisation)
async def create_organisation(data: OrganisationCreate):
    tier = _get_current_tier()
    if not check_feature_access(tier, "crm_access"):
        raise HTTPException(status_code=403, detail="CRM requires Connect tier or higher")

    now = datetime.now(timezone.utc)
    org = Organisation(
        id=uuid4(),
        name=data.name,
        domain=data.domain,
        organisation_type=data.organisation_type,
        industry=data.industry,
        size_category=data.size_category,
        country=data.country,
        city=data.city,
        relationship_status=data.relationship_status,
        relationship_since=data.relationship_since,
        contract_value_annual=data.contract_value_annual,
        currency=data.currency,
        website_url=data.website_url,
        description=data.description,
        tags=data.tags or [],
        created_at=now,
        updated_at=now,
    )
    _organisations[org.id] = org
    return org


@router.get("/", response_model=list[Organisation])
async def list_organisations(organisation_type: Optional[str] = None):
    results = list(_organisations.values())
    if organisation_type:
        results = [o for o in results if o.organisation_type == organisation_type]
    return sorted(results, key=lambda o: o.updated_at, reverse=True)


@router.get("/{org_id}", response_model=Organisation)
async def get_organisation(org_id: UUID):
    org = _organisations.get(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return org


@router.delete("/{org_id}")
async def delete_organisation(org_id: UUID):
    if org_id not in _organisations:
        raise HTTPException(status_code=404, detail="Organisation not found")
    del _organisations[org_id]
    return {"deleted": True}
