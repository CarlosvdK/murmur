"""CRM Twin -- correspondence upload + twin query endpoints."""

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from backend.models.crm import TwinQueryRequest, TwinQueryResponse
from backend.crm.correspondence_processor import process_correspondence
from backend.crm.twin_engine import query_twin
from backend.crm.signal_detector import detect_signals
from backend.auth.tiers import Tier, check_feature_access
from backend.auth.dependencies import get_current_user_id
from backend.db.client import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crm/twin", tags=["crm-twin"])


def _get_current_tier() -> Tier:
    return Tier.CONNECT


def _verify_contact_ownership(db, contact_id: UUID, user_id: UUID) -> dict:
    """Fetch a contact row, raising 404 if not found or not owned by user."""
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
    return result.data


@router.post("/upload/{contact_id}")
async def upload_correspondence(
    contact_id: UUID,
    source_type: str = Form(...),
    file: UploadFile = File(...),
    confirm_rights: bool = Form(False),
    user_id: UUID = Depends(get_current_user_id),
):
    """Upload correspondence for twin processing.

    PRIVACY: Raw file is processed in memory and discarded.
    Only anonymised communication patterns are stored.
    """
    tier = _get_current_tier()
    if not check_feature_access(tier, "twin_access"):
        raise HTTPException(status_code=403, detail="Twin access requires Connect tier or higher")

    if not confirm_rights:
        raise HTTPException(
            status_code=400,
            detail="You must confirm you have the right to upload this correspondence",
        )

    db = get_supabase()
    contact_row = _verify_contact_ownership(db, contact_id, user_id)

    # Read file content into memory
    raw_bytes = await file.read()
    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raw_text = raw_bytes.decode("latin-1")

    # Process correspondence -- extract patterns, anonymise
    signals = await process_correspondence(
        raw_text=raw_text,
        contact_name=contact_row["full_name"],
        source_type=source_type,
    )

    # CRITICAL: Discard raw text immediately
    del raw_text
    del raw_bytes

    # Update contact with twin status
    twin_confidence = "medium" if signals.get("message_count", 0) < 50 else "high"
    sentiment = "positive"

    # Run signal detection
    detected = detect_signals(signals)

    # Store signal alerts in DB
    if detected:
        alert_rows = [
            {
                "contact_id": str(contact_id),
                "type": s.type,
                "severity": s.severity,
                "title": s.title,
                "message": s.message,
                "recommendation": s.recommendation,
            }
            for s in detected
        ]
        db.table("crm_signal_alerts").insert(alert_rows).execute()
        sentiment = "negative" if any(s.severity == "warning" for s in detected) else "neutral"

    # Update contact twin fields
    db.table("crm_contacts").update({
        "has_twin": True,
        "twin_type": "customer_twin",
        "twin_confidence": twin_confidence,
        "twin_corpus_size": signals.get("message_count", 0),
        "communication_style": signals.get("communication_style"),
        "current_sentiment": sentiment,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", str(contact_id)).execute()

    # Store correspondence record (no raw content)
    corr_row = {
        "contact_id": str(contact_id),
        "source_type": source_type,
        "message_count": signals.get("message_count"),
        "processed": True,
        "extracted_signals": signals,
    }
    db.table("crm_correspondence").insert(corr_row).execute()

    logger.info(
        "Correspondence processed for %s: %d messages, %d signals detected",
        contact_row["full_name"], signals.get("message_count", 0), len(detected),
    )

    # Fetch stored alerts for response
    alerts_result = (
        db.table("crm_signal_alerts")
        .select("*")
        .eq("contact_id", str(contact_id))
        .execute()
    )

    return {
        "processed": True,
        "message_count": signals.get("message_count", 0),
        "twin_confidence": twin_confidence,
        "signals_detected": len(detected),
        "signals": [
            {"type": a["type"], "severity": a["severity"], "title": a["title"],
             "message": a["message"], "recommendation": a.get("recommendation")}
            for a in alerts_result.data
        ],
    }


@router.post("/query", response_model=TwinQueryResponse)
async def ask_twin(
    data: TwinQueryRequest,
    user_id: UUID = Depends(get_current_user_id),
):
    """Ask a question about a contact based on their communication profile."""
    tier = _get_current_tier()
    if not check_feature_access(tier, "twin_access"):
        raise HTTPException(status_code=403, detail="Twin access requires Connect tier or higher")

    if not data.contact_id:
        raise HTTPException(status_code=400, detail="contact_id is required")

    db = get_supabase()
    contact_row = _verify_contact_ownership(db, data.contact_id, user_id)

    if not contact_row.get("has_twin"):
        raise HTTPException(
            status_code=400,
            detail="No twin available for this contact. Upload correspondence first.",
        )

    # Get the latest correspondence signals
    corr_result = (
        db.table("crm_correspondence")
        .select("extracted_signals")
        .eq("contact_id", str(data.contact_id))
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not corr_result.data or not corr_result.data[0].get("extracted_signals"):
        raise HTTPException(status_code=400, detail="No correspondence data processed for this contact")

    signals = corr_result.data[0]["extracted_signals"]

    result = await query_twin(
        question=data.question,
        contact_name=contact_row["full_name"],
        extracted_signals=signals,
    )

    # Store twin query in DB
    query_row = {
        "contact_id": str(data.contact_id),
        "organisation_id": str(data.organisation_id) if data.organisation_id else None,
        "question": data.question,
        "answer": result.get("answer", "Unable to generate response"),
        "confidence": result.get("confidence", "low"),
        "key_signals": result.get("key_signals", []),
        "preparation_tips": result.get("preparation_tips", []),
        "caveats": result.get("caveats", []),
    }
    insert_result = db.table("crm_twin_queries").insert(query_row).execute()
    saved = insert_result.data[0]

    return TwinQueryResponse(
        id=saved["id"],
        contact_id=data.contact_id,
        question=data.question,
        answer=saved["answer"],
        confidence=saved["confidence"],
        key_signals=saved.get("key_signals", []),
        preparation_tips=saved.get("preparation_tips", []),
        caveats=saved.get("caveats", []),
        created_at=saved["created_at"],
    )


@router.get("/signals/{contact_id}")
async def get_contact_signals(
    contact_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
):
    """Get detected relationship signals for a contact."""
    db = get_supabase()
    _verify_contact_ownership(db, contact_id, user_id)
    result = (
        db.table("crm_signal_alerts")
        .select("type, severity, title, message, recommendation")
        .eq("contact_id", str(contact_id))
        .execute()
    )
    return {"contact_id": str(contact_id), "signals": result.data}


@router.get("/queries/{contact_id}", response_model=list[TwinQueryResponse])
async def get_twin_queries(
    contact_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
):
    """Get previous twin queries for a contact."""
    db = get_supabase()
    _verify_contact_ownership(db, contact_id, user_id)
    result = (
        db.table("crm_twin_queries")
        .select("*")
        .eq("contact_id", str(contact_id))
        .order("created_at", desc=True)
        .execute()
    )
    return [
        TwinQueryResponse(
            id=r["id"],
            contact_id=r.get("contact_id"),
            organisation_id=r.get("organisation_id"),
            question=r["question"],
            answer=r["answer"],
            confidence=r["confidence"],
            key_signals=r.get("key_signals", []),
            preparation_tips=r.get("preparation_tips", []),
            caveats=r.get("caveats", []),
            created_at=r["created_at"],
        )
        for r in result.data
    ]
