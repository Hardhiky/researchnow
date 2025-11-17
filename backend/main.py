"""
ResearchNow Backend - Main Application Entry Point
FastAPI application for research paper summarization and management
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from api.routes import health, papers, search, sources, summaries
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting ResearchNow Backend with BART AI Summarization...")
    yield
    # Shutdown
    logger.info("Shutting down ResearchNow Backend...")


# Create FastAPI application
app = FastAPI(
    title="ResearchNow API",
    description="AI-powered research paper summarization platform using BART (Local, Unlimited, Free)",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ResearchNow API",
        "version": "1.0.0",
        "status": "operational",
        "ai_model": "BART (facebook/bart-large-cnn) - Local & Unlimited",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_provider": "Hugging Face Transformers (Local)",
        "model": "facebook/bart-large-cnn",
        "limits": "Unlimited - No API limits, runs locally",
    }


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(papers.router, prefix="/api/v1/papers", tags=["Papers"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(summaries.router, prefix="/api/v1/summaries", tags=["Summaries"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["Sources"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
