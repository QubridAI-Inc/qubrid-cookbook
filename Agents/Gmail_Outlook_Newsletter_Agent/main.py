"""
main.py

FastAPI entry point for NewsletterAgent.
Initialises the SQLite database on startup and mounts the API router.

Run with:
    uvicorn main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from api.routes import router
from database.db import init_db

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialise the SQLite database on startup."""
    init_db()
    yield


app = FastAPI(
    title="NewsletterAgent API",
    description="6-Agent Newsletter Generator powered by Google ADK × Qubrid AI × Composio",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow Streamlit (running on 8501) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root() -> dict:
    """Health-check root endpoint."""
    return {"message": "NewsletterAgent API is running. See /docs for endpoints."}
