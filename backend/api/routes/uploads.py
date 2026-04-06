from fastapi import APIRouter, UploadFile, File, HTTPException
from uuid import UUID

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/{business_id}")
async def upload_file(business_id: UUID, file: UploadFile = File(...)):
    """Upload a CSV or data file for a business.

    TODO: Implement Supabase Storage upload + CSV parsing.
    For now, returns a stub response.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    allowed_types = {".csv", ".xlsx", ".xls", ".txt"}
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not supported. Allowed: {', '.join(allowed_types)}",
        )

    content = await file.read()

    return {
        "filename": file.filename,
        "size": len(content),
        "status": "uploaded",
        "message": "File received. Parsing not yet implemented.",
    }
