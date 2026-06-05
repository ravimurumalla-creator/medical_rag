from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.api.v1.router import api_router

app = FastAPI(title="Medical Document Intelligence API")

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://main.d32r8pqx8hfmkp.amplifyapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "API is running"}