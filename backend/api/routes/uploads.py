import csv
import io
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from backend.auth.dependencies import get_current_user_id
from backend.db.client import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".txt", ".pdf", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/{business_id}")
async def upload_file(
    business_id: UUID,
    file: UploadFile = File(...),
    user_id: UUID = Depends(get_current_user_id),
):
    """Upload a data file for a business. Stores in Supabase and creates a record."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum 10MB.")

    db = get_supabase()

    # Verify business ownership
    biz = (
        db.table("businesses")
        .select("id")
        .eq("id", str(business_id))
        .eq("user_id", str(user_id))
        .maybe_single()
        .execute()
    )
    if not biz.data:
        raise HTTPException(status_code=404, detail="Business not found")

    # Upload to Supabase Storage
    storage_path = f"{user_id}/{business_id}/{file.filename}"
    file_url = storage_path  # Will be the storage reference

    try:
        db.storage.from_("business-uploads").upload(
            storage_path, content,
            {"content-type": file.content_type or "application/octet-stream"},
        )
        # Get public URL
        url_resp = db.storage.from_("business-uploads").get_public_url(storage_path)
        if url_resp:
            file_url = url_resp
    except Exception as e:
        logger.warning("Storage upload failed (bucket may not exist): %s", e)
        # Continue without storage -- still save the record

    # Parse CSV if applicable
    parsed_data = None
    if ext == ".csv":
        try:
            text = content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(text))
            rows = [row for row in reader]
            parsed_data = {
                "row_count": len(rows),
                "columns": list(rows[0].keys()) if rows else [],
                "sample": rows[:5],
            }
        except Exception as e:
            logger.warning("CSV parsing failed: %s", e)
            parsed_data = {"error": str(e)}

    # Create DB record
    record = {
        "business_id": str(business_id),
        "file_url": file_url,
        "file_name": file.filename,
        "file_type": ext.lstrip("."),
        "parsed_data": parsed_data,
        "parse_status": "parsed" if parsed_data and "error" not in parsed_data else "pending",
    }
    result = db.table("business_uploads").insert(record).execute()

    return {
        "id": result.data[0]["id"] if result.data else None,
        "filename": file.filename,
        "size": len(content),
        "status": record["parse_status"],
        "parsed_data": parsed_data,
    }
