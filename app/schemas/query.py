from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.bedrock_service import BedrockService

router = APIRouter()

EXTRACTED_DIR = Path("data/extracted")
bedrock_service = BedrockService()


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)


@router.post("/{document_id}/query", status_code=status.HTTP_200_OK)
async def query_document(document_id: str, payload: QueryRequest):
    extracted_path = EXTRACTED_DIR / f"{document_id}.txt"

    if not extracted_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extracted text not found for document id: {document_id}"
        )

    context = extracted_path.read_text(encoding="utf-8")

    try:
        answer = bedrock_service.ask_question(context=context, question=payload.question)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return {
        "document_id": document_id,
        "question": payload.question,
        "answer": answer,
        "status": "answered"
    }