from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.services.pdf_service import PDFService
from app.services.textract_service import TextractService

router = APIRouter()

RAW_DIR = Path("data/raw")
EXTRACTED_DIR = Path("data/extracted")
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

pdf_service = PDFService()
textract_service = TextractService()


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
        extracted_text = textract_service.extract_text_from_file(source_file)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    output_path = EXTRACTED_DIR / f"{document_id}.txt"
    output_path.write_text(extracted_text, encoding="utf-8")

    return {
        "document_id": document_id,
        "source_file": source_file.name,
        "extracted_file": output_path.name,
        "status": "extracted"
    }