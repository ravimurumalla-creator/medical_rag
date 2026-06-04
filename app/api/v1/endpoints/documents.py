from fastapi import APIRouter, Path, HTTPException, File, UploadFile
from pydantic import BaseModel
import boto3
import io
import os

from pypdf import PdfReader

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


# In-memory store for extracted text (use Redis/DB in production)
EXTRACTED_TEXT_STORE = {}

s3_client = boto3.client("s3")
S3_BUCKET = os.getenv("medragbucket", "medical-docs-bucket")


def download_pdf_from_s3(document_id: str) -> bytes:
    """Download PDF from S3."""
    key = f"raw/{document_id}.pdf"
    try:
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
        return obj["Body"].read()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"PDF not found in S3: {document_id}")


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF."""
    pdf_file = io.BytesIO(pdf_bytes)
    reader = PdfReader(pdf_file)
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    return "\n\n".join(text_parts)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF and store it in S3 with a UUID document_id.
    Returns the document_id.
    """
    import uuid
    doc_id = str(uuid.uuid4())
    key = f"raw/{doc_id}.pdf"

    pdf_bytes = await file.read()

    s3_client.put_object(Bucket=S3_BUCKET, Key=key, Body=pdf_bytes, ContentType=file.content_type)

    return {
        "status": "ok",
        "document_id": doc_id,
        "message": "Document uploaded successfully",
    }


@router.post("/data/raw/{document_id}.pdf/extract")
async def extract_document(document_id: str = Path(...)):
    """
    Extract text from a PDF in S3 and store it for querying.
    Must be called before /query.
    """
    pdf_bytes = download_pdf_from_s3(document_id)
    text = extract_text_from_pdf(pdf_bytes)

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from PDF")

    EXTRACTED_TEXT_STORE[document_id] = text

    return {
        "status": "ok",
        "document_id": document_id,
        "text_length": len(text),
        "text_preview": text[:300],
    }


@router.post("/data/raw/{document_id}.pdf/query")
async def query_document(document_id: str = Path(...), request: QueryRequest = QueryRequest(question="")):
    """
    Query a document using Bedrock.
    Requires that extract was called first.
    """
    text = EXTRACTED_TEXT_STORE.get(document_id)
    if text is None:
        raise HTTPException(
            status_code=404,
            detail=f"Extracted text not found for document id: {document_id}. "
                   f"Please call /extract first."
        )

    from app.services.bedrock_service import BedrockService
    bedrock = BedrockService()
    answer = bedrock.ask_question(context=text, question=request.question)

    return {
        "status": "ok",
        "document_id": document_id,
        "question": request.question,
        "answer": answer,
    }