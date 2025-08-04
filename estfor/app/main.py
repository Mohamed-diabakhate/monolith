"""
Main FastAPI application for EstFor Asset Collection System.
"""

import structlog
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import assets, health
from app.database import init_mongodb, close_mongodb

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting EstFor Asset Collection System")
    
    try:
        # Initialize MongoDB
        await init_mongodb()
        logger.info("MongoDB initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize MongoDB", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down EstFor Asset Collection System")
    await close_mongodb()


# Create FastAPI application
app = FastAPI(
    title="EstFor Asset Collection System - Sonic",
    description="A system for collecting and storing EstFor Kingdom assets",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(assets.router, prefix="/assets", tags=["assets"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "EstFor Asset Collection System",
        "version": "1.0.0",
        "status": "running"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    ) 