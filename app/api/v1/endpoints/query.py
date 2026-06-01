from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.bedrock_service import BedrockService

router = APIRouter()

EXTRACTED_DIR = Path("data/extracted")
bedrock_service = BedrockService()


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    include_context_preview: bool = False


class QueryResponse(BaseModel):
    document_id: str
    question: str
    answer: str
    status: str
    context_chars: int
    context_preview: str | None = None


@router.post(
    "/{document_id}/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
)
async def query_document(document_id: str, payload: QueryRequest):
    extracted_path = EXTRACTED_DIR / f"{document_id}.txt"

    if not extracted_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extracted text not found for document id: {document_id}"
        )

    context = extracted_path.read_text(encoding="utf-8").strip()

    if not context:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extracted text is empty for document id: {document_id}"
        )

    try:
        answer = bedrock_service.ask_question(
            context=context,
            question=payload.question,
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

    preview = context[:500] if payload.include_context_preview else None

    return QueryResponse(
        document_id=document_id,
        question=payload.question,
        answer=answer,
        status="answered",
        context_chars=len(context),
        context_preview=preview,
    )
    