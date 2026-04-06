"""CRM Twin -- correspondence upload + twin query endpoints."""

import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from backend.models.crm import CorrespondenceRecord, TwinQueryRequest, TwinQueryResponse
from backend.crm.correspondence_processor import process_correspondence
from backend.crm.twin_engine import query_twin
from backend.crm.signal_detector import detect_signals
from backend.auth.tiers import Tier, check_feature_access
from backend.api.routes.crm_contacts import _contacts

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crm/twin", tags=["crm-twin"])

# In-memory stores
_correspondence: dict[UUID, CorrespondenceRecord] = {}
_contact_signals: dict[UUID, dict] = {}  # contact_id -> extracted_signals
_twin_queries: dict[UUID, TwinQueryResponse] = {}
_contact_signal_alerts: dict[UUID, list] = {}  # contact_id -> list of Signal dicts


def _get_current_tier() -> Tier:
    return Tier.CONNECT


@router.post("/upload/{contact_id}")
async def upload_correspondence(
    contact_id: UUID,
    source_type: str = Form(...),
    file: UploadFile = File(...),
    confirm_rights: bool = Form(False),
):
    """Upload correspondence for twin processing.

    PRIVACY: Raw file is processed in memory and discarded.
    Only anonymised communication patterns are stored.
    User must confirm they have the right to upload this correspondence.
    """
    tier = _get_current_tier()
    if not check_feature_access(tier, "twin_access"):
        raise HTTPException(status_code=403, detail="Twin access requires Connect tier or higher")

    if not confirm_rights:
        raise HTTPException(
            status_code=400,
            detail="You must confirm you have the right to upload this correspondence",
        )

    contact = _contacts.get(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Read file content into memory
    raw_bytes = await file.read()
    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raw_text = raw_bytes.decode("latin-1")

    # Process correspondence -- extract patterns, anonymise
    signals = await process_correspondence(
        raw_text=raw_text,
        contact_name=contact.full_name,
        source_type=source_type,
    )

    # CRITICAL: Discard raw text immediately
    del raw_text
    del raw_bytes

    # Store only extracted signals
    _contact_signals[contact_id] = signals

    # Update contact with twin status
    contact.has_twin = True
    contact.twin_type = "customer_twin"
    contact.twin_confidence = "medium" if signals.get("message_count", 0) < 50 else "high"
    contact.twin_corpus_size = signals.get("message_count", 0)
    contact.communication_style = signals.get("communication_style")
    contact.updated_at = datetime.now(timezone.utc)

    # Run signal detection
    detected = detect_signals(signals)
    _contact_signal_alerts[contact_id] = [
        {"type": s.type, "severity": s.severity, "title": s.title,
         "message": s.message, "recommendation": s.recommendation}
        for s in detected
    ]

    if detected:
        contact.current_sentiment = "negative" if any(s.severity == "warning" for s in detected) else "neutral"
    else:
        contact.current_sentiment = "positive"

    # Create correspondence record (no raw content)
    record = CorrespondenceRecord(
        id=uuid4(),
        contact_id=contact_id,
        source_type=source_type,
        message_count=signals.get("message_count"),
        processed=True,
        extracted_signals=signals,
        created_at=datetime.now(timezone.utc),
    )
    _correspondence[record.id] = record

    logger.info(
        "Correspondence processed for %s: %d messages, %d signals detected",
        contact.full_name, signals.get("message_count", 0), len(detected),
    )

    return {
        "processed": True,
        "message_count": signals.get("message_count", 0),
        "twin_confidence": contact.twin_confidence,
        "signals_detected": len(detected),
        "signals": _contact_signal_alerts.get(contact_id, []),
    }


@router.post("/query", response_model=TwinQueryResponse)
async def ask_twin(data: TwinQueryRequest):
    """Ask a question about a contact based on their communication profile."""
    tier = _get_current_tier()
    if not check_feature_access(tier, "twin_access"):
        raise HTTPException(status_code=403, detail="Twin access requires Connect tier or higher")

    if not data.contact_id:
        raise HTTPException(status_code=400, detail="contact_id is required")

    contact = _contacts.get(data.contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if not contact.has_twin:
        raise HTTPException(
            status_code=400,
            detail="No twin available for this contact. Upload correspondence first.",
        )

    signals = _contact_signals.get(data.contact_id, {})
    if not signals:
        raise HTTPException(status_code=400, detail="No correspondence data processed for this contact")

    result = await query_twin(
        question=data.question,
        contact_name=contact.full_name,
        extracted_signals=signals,
    )

    response = TwinQueryResponse(
        id=uuid4(),
        contact_id=data.contact_id,
        question=data.question,
        answer=result.get("answer", "Unable to generate response"),
        confidence=result.get("confidence", "low"),
        key_signals=result.get("key_signals", []),
        preparation_tips=result.get("preparation_tips", []),
        caveats=result.get("caveats", []),
        created_at=datetime.now(timezone.utc),
    )
    _twin_queries[response.id] = response

    return response


@router.get("/signals/{contact_id}")
async def get_contact_signals(contact_id: UUID):
    """Get detected relationship signals for a contact."""
    signals = _contact_signal_alerts.get(contact_id, [])
    return {"contact_id": str(contact_id), "signals": signals}


@router.get("/queries/{contact_id}", response_model=list[TwinQueryResponse])
async def get_twin_queries(contact_id: UUID):
    """Get previous twin queries for a contact."""
    queries = [q for q in _twin_queries.values() if q.contact_id == contact_id]
    return sorted(queries, key=lambda q: q.created_at, reverse=True)
