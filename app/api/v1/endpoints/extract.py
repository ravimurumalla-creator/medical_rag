from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.services.pdf_service import PDFService
from app.services.s3_service import S3Service
from app.services.textract_service import TextractService

router = APIRouter()

settings = get_settings()
pdf_service = PDFService()
s3_service = S3Service()
textract_service = TextractService()

RAW_DIR = Path("data/raw")
EXTRACTED_DIR = Path("data/extracted")
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/{document_id}/extract", status_code=status.HTTP_200_OK)
async def extract_document(document_id: str):
    matching_files = list(RAW_DIR.glob(f"{document_id}.*"))

    if not matching_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found for id: {document_id}"
        )

    source_file = matching_files[0]

    try:
        pdf_service.ensure_supported_file(source_file)
        suffix = source_file.suffix.lower()

        if suffix == ".pdf":
            s3_key = f"{settings.S3_RAW_PREFIX}{source_file.name}"
            s3_service.upload_file(source_file, object_name=s3_key)

            extracted_text = textract_service.extract_text_from_s3_pdf(
                s3_bucket=settings.S3_BUCKET_NAME,
                s3_key=s3_key,
            )

            extraction_mode = "async_pdf"
        else:
            extracted_text = textract_service.extract_text_from_file(source_file)
            extraction_mode = "sync_image"

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(e)
        ) from e
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

    output_path = EXTRACTED_DIR / f"{document_id}.txt"
    output_path.write_text(extracted_text, encoding="utf-8")

    return {
        "document_id": document_id,
        "source_file": source_file.name,
        "extracted_file": output_path.name,
        "extraction_mode": extraction_mode,
        "status": "extracted"
    }