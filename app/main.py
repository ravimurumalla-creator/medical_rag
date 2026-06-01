from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(title="Medical Document Intelligence API")

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "API is running"}