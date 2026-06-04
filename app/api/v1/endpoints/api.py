from fastapi import APIRouter
from .endpoints import documents

api_router = APIRouter()

api_router.include_router(
    documents.router,
    prefix="/api/v1/documents",
    tags=["documents"],
)