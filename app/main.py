from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

from app.api.v1.router import api_router

app = FastAPI(title="Medical Document Intelligence API")

# Enable CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount api_router at /api/v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "API is running"}