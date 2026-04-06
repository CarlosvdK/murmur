"""
CRM data models -- contacts, organisations, correspondence, activities, twin queries.

Privacy principle: no raw correspondence content is ever stored in these models.
Only anonymised communication patterns and extracted signals.
"""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime, date


# ============================================================
# CONTACTS
# ============================================================

class ContactCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    seniority_level: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    contact_type: str = "contact"
    organisation_id: Optional[UUID] = None
    role_label: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[list[str]] = None


class Contact(BaseModel):
    id: UUID
    first_name: str
    last_name: Optional[str] = None
    full_name: str
    job_title: Optional[str] = None
    department: Optional[str] = None
    seniority_level: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    contact_type: str = "contact"
    relationship_strength: int = 0
    communication_style: Optional[str] = None
    last_contact_date: Optional[datetime] = None
    days_since_contact: Optional[int] = None
    has_twin: bool = False
    twin_type: Optional[str] = None
    twin_confidence: Optional[str] = None
    twin_corpus_size: int = 0
    current_sentiment: Optional[str] = None
    sentiment_trend: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[list[str]] = None
    organisation_id: Optional[UUID] = None
    organisation_name: Optional[str] = None
    role_label: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ============================================================
# ORGANISATIONS
# ============================================================

class OrganisationCreate(BaseModel):
    name: str
    domain: Optional[str] = None
    organisation_type: str = "customer"
    industry: Optional[str] = None
    size_category: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    relationship_status: str = "active"
    relationship_since: Optional[date] = None
    contract_value_annual: Optional[float] = None
    currency: str = "EUR"
    website_url: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None


class Organisation(BaseModel):
    id: UUID
    name: str
    domain: Optional[str] = None
    organisation_type: str
    industry: Optional[str] = None
    size_category: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    relationship_status: str = "active"
    relationship_since: Optional[date] = None
    contract_value_annual: Optional[float] = None
    currency: str = "EUR"
    health_score: Optional[int] = None
    health_trend: Optional[str] = None
    last_contact_date: Optional[datetime] = None
    days_since_contact: Optional[int] = None
    has_twin: bool = False
    website_url: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    contacts_count: int = 0
    created_at: datetime
    updated_at: datetime


# ============================================================
# CORRESPONDENCE
# ============================================================

class CorrespondenceUpload(BaseModel):
    contact_id: UUID
    source_type: str  # email | whatsapp | transcript | meeting_notes | other
    # File is uploaded separately via multipart


class CorrespondenceRecord(BaseModel):
    id: UUID
    contact_id: UUID
    source_type: str
    message_count: Optional[int] = None
    processed: bool = False
    extracted_signals: Optional[dict] = None
    created_at: datetime


# ============================================================
# ACTIVITIES
# ============================================================

class ActivityCreate(BaseModel):
    contact_id: Optional[UUID] = None
    organisation_id: Optional[UUID] = None
    activity_type: str  # email_sent | call | meeting | note | twin_query | signal_flag
    title: str
    body: Optional[str] = None
    occurred_at: Optional[datetime] = None


class Activity(BaseModel):
    id: UUID
    contact_id: Optional[UUID] = None
    organisation_id: Optional[UUID] = None
    activity_type: str
    title: str
    body: Optional[str] = None
    occurred_at: datetime
    created_at: datetime


# ============================================================
# TWIN QUERIES
# ============================================================

class TwinQueryRequest(BaseModel):
    contact_id: Optional[UUID] = None
    organisation_id: Optional[UUID] = None
    question: str


class TwinQueryResponse(BaseModel):
    id: UUID
    contact_id: Optional[UUID] = None
    organisation_id: Optional[UUID] = None
    question: str
    answer: str
    confidence: str
    key_signals: list[str] = []
    preparation_tips: list[str] = []
    caveats: list[str] = []
    created_at: datetime
