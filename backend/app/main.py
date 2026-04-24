"""
IBS Wellness Companion - FastAPI Backend
Main application entry point with middleware, routes, and configuration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from pathlib import Path

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import engine, create_tables
from app.api.v1 import api_router
from app.api.v1 import real_time_predictions, firebase, oauth


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting IBS Wellness Companion API...")

    # Create database tables
    await create_tables()

    # Initialize ML models (if needed)
    # await load_ml_models()

    # Seed initial data
    try:
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.seed_data import seed
        await seed()
    except Exception as e:
        logger.warning(f"Seeding skipped: {e}")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down IBS Wellness Companion API...")

    # Cleanup resources
    await engine.dispose()

    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Security middleware — allow all hosts so Render/Vercel/custom domains work
# Specific host restriction can be re-enabled once a custom domain is set
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Global exception handler
# @app.exception_handler(IBSException)  # Comment out for now
# async def ibs_exception_handler(request: Request, exc: IBSException):
#     """Handle custom IBS exceptions."""
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "error": exc.error_code,
#             "message": exc.message,
#             "details": exc.details
#         }
#     )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)

    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "type": type(exc).__name__,
            },
        )

    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the IBS Wellness Companion API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(real_time_predictions.router, prefix="/api/v1")
app.include_router(firebase.router, prefix="/api/v1")
# Mount OAuth under /auth so frontend can call /api/v1/auth/oauth
app.include_router(oauth.router, prefix="/api/v1/auth")

# Static files (if needed)
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
        access_log=True,
    )
