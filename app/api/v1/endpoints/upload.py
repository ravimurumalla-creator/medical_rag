from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
}

UPLOAD_DIR = Path("data/raw")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}"
        )

    document_id = str(uuid4())
    extension = Path(file.filename).suffix if file.filename else ""

    if not extension:
        if file.content_type == "application/pdf":
            extension = ".pdf"
        elif file.content_type == "image/png":
            extension = ".png"
        else:
            extension = ".jpg"

    safe_filename = f"{document_id}{extension}"
    file_path = UPLOAD_DIR / safe_filename

    contents = await file.read()
    file_path.write_bytes(contents)

    return {
        "document_id": document_id,
        "filename": file.filename,
        "stored_filename": safe_filename,
        "content_type": file.content_type,
        "size_bytes": len(contents),
        "path": str(file_path),
        "status": "uploaded"
    }