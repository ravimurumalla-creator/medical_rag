import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

AMPLIFY_URL = os.getenv("AMPLIFY_URL", "").rstrip("/")

ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

if AMPLIFY_URL:
    ALLOWED_ORIGINS.append(AMPLIFY_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)