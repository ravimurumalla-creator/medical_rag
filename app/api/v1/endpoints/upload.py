from fastapi import APIRouter, File, UploadFile
from pathlib import Path
from typing import Optional
router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    import uuid
    doc_id = str(uuid.uuid4())
    key = f"raw/{doc_id}.pdf"

    pdf_bytes = await file.read()

    from app.services.s3_service import S3Service
    s3_service = S3Service()

    # Use upload_bytes for in-memory bytes
    s3_service.upload_bytes(
        data=pdf_bytes,
        object_name=key,
        content_type=file.content_type,
    )

    return {
        "status": "ok",
        "document_id": doc_id,
        "message": "Document uploaded successfully",
    }