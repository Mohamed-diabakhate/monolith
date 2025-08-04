"""
Health check endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
import structlog

from app.database import test_connection
from app.config import settings

logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "EstFor Asset Collection System",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness probe endpoint."""
    try:
        # Check database connection
        db_healthy = await test_connection()
        
        if db_healthy:
            return {
                "status": "ready",
                "database": "connected",
                "service": "ready"
            }
        else:
            return {
                "status": "not_ready",
                "database": "disconnected",
                "service": "not_ready"
            }
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return {
            "status": "not_ready",
            "database": "error",
            "service": "not_ready",
            "error": str(e)
        }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness probe endpoint."""
    return {
        "status": "alive",
        "service": "running"
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with all components."""
    health_status = {
        "status": "healthy",
        "service": "EstFor Asset Collection System",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "components": {}
    }
    
    # Check database
    try:
        db_healthy = await test_connection()
        health_status["components"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "type": "firestore",
            "project": settings.FIRESTORE_PROJECT_ID
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check configuration
    health_status["components"]["configuration"] = {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "log_level": settings.LOG_LEVEL
    }
    
    return health_status 