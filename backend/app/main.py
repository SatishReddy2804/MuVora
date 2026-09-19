import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure root path is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, logger
from backend.app.api.routes import router as api_router
from backend.ml.predictor import predictor


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: configure logging and verify predictor
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} API backend...")
    logger.info(f"Model status: {'Fallback' if predictor.is_fallback else 'Loaded'}")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME} API backend.")


app = FastAPI(
    title=f"{settings.PROJECT_NAME} Sentiment Analysis API",
    description="Production-grade multilingual AI movie review sentiment analysis backend.",
    version="1.0.0",
    lifespan=lifespan
)

# Global CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev / preview
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers to avoid leaking stack traces
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred."}
    )

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} AI Sentiment Analysis API",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }
