"""
Health check endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
import structlog

from app.database import test_connection
from app.config import settings
from app.services.container_manager import container_manager
from app.services.idle_monitor import idle_monitor_manager

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


@router.get("/containers")
async def container_status() -> Dict[str, Any]:
    """Container management status endpoint."""
    try:
        # Get all container statuses
        container_statuses = await container_manager.get_all_container_status()
        
        # Get idle monitoring stats
        idle_stats = await idle_monitor_manager.get_service().get_stats()
        
        # Count containers by state
        state_counts = {}
        for status_info in container_statuses.values():
            state = status_info["state"]
            state_counts[state] = state_counts.get(state, 0) + 1
        
        return {
            "status": "healthy",
            "container_management": {
                "auto_start_enabled": settings.CONTAINER_AUTO_START,
                "auto_stop_enabled": settings.CONTAINER_AUTO_STOP,
                "idle_timeout_minutes": settings.CONTAINER_IDLE_TIMEOUT
            },
            "container_summary": {
                "total_containers": len(container_statuses),
                "state_counts": state_counts
            },
            "containers": container_statuses,
            "idle_monitor": idle_stats
        }
    except Exception as e:
        logger.error("Container status check failed", error=str(e))
        return {
            "status": "error",
            "error": str(e),
            "container_management": {
                "auto_start_enabled": settings.CONTAINER_AUTO_START,
                "auto_stop_enabled": settings.CONTAINER_AUTO_STOP
            }
        }


@router.get("/services")
async def service_dependencies() -> Dict[str, Any]:
    """Show endpoint-to-container service mappings."""
    return {
        "status": "healthy",
        "service_mappings": {
            "endpoint_dependencies": container_manager.endpoint_dependencies,
            "service_containers": container_manager.service_containers,
            "container_priorities": {
                name: priority.value 
                for name, priority in container_manager.container_priorities.items()
            }
        },
        "configuration": {
            "auto_start_enabled": settings.CONTAINER_AUTO_START,
            "auto_stop_enabled": settings.CONTAINER_AUTO_STOP,
            "idle_timeouts": {
                "normal": settings.CONTAINER_IDLE_TIMEOUT,
                "high": settings.CONTAINER_HIGH_IDLE_TIMEOUT,
                "low": settings.CONTAINER_LOW_IDLE_TIMEOUT
            }
        }
    }


@router.get("/automation")
async def automation_status() -> Dict[str, Any]:
    """Container automation system status."""
    try:
        # Get idle containers
        idle_containers = await container_manager.get_idle_containers()
        
        # Get monitoring stats
        idle_stats = await idle_monitor_manager.get_service().get_stats()
        
        # Get recent container access times
        container_access = {}
        for container_name in container_manager.container_priorities.keys():
            access_data = await container_manager.redis_client.hget(
                "container_last_access", container_name
            )
            container_access[container_name] = access_data
        
        return {
            "status": "healthy",
            "automation": {
                "auto_start": {
                    "enabled": settings.CONTAINER_AUTO_START,
                    "startup_timeout": settings.CONTAINER_STARTUP_TIMEOUT
                },
                "auto_stop": {
                    "enabled": settings.CONTAINER_AUTO_STOP,
                    "idle_monitor_running": idle_stats["is_running"],
                    "check_interval": idle_stats["check_interval_seconds"],
                    "last_check": idle_stats["last_check_iso"]
                }
            },
            "idle_analysis": {
                "idle_containers_count": len(idle_containers),
                "idle_containers": {
                    name: f"{idle_time.total_seconds()//60:.0f} minutes"
                    for name, idle_time in idle_containers.items()
                }
            },
            "statistics": {
                "containers_stopped_total": idle_stats["containers_stopped"],
                "stop_attempts_total": idle_stats["stop_attempts"],
                "stop_failures_total": idle_stats["stop_failures"],
                "idle_containers_found_last_check": idle_stats["idle_containers_found"]
            }
        }
    except Exception as e:
        logger.error("Automation status check failed", error=str(e))
        return {
            "status": "error",
            "error": str(e)
        }


@router.post("/containers/{container_name}/start")
async def start_container_endpoint(container_name: str) -> Dict[str, Any]:
    """Manually start a container."""
    try:
        success = await container_manager.start_container(container_name)
        if success:
            return {
                "status": "success",
                "message": f"Container {container_name} started successfully"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to start container {container_name}"
            }
    except Exception as e:
        logger.error(f"Manual container start failed for {container_name}", error=str(e))
        return {
            "status": "error",
            "message": str(e)
        }


@router.post("/containers/{container_name}/stop")
async def stop_container_endpoint(container_name: str) -> Dict[str, Any]:
    """Manually stop a container."""
    try:
        success = await container_manager.stop_container(container_name, force=True)
        if success:
            return {
                "status": "success", 
                "message": f"Container {container_name} stopped successfully"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to stop container {container_name}"
            }
    except Exception as e:
        logger.error(f"Manual container stop failed for {container_name}", error=str(e))
        return {
            "status": "error",
            "message": str(e)
        }


@router.post("/automation/idle-check")
async def trigger_idle_check() -> Dict[str, Any]:
    """Manually trigger an idle container check."""
    try:
        result = await idle_monitor_manager.get_service().force_idle_check()
        return {
            "status": "success",
            "message": "Idle check completed",
            "result": result
        }
    except Exception as e:
        logger.error("Manual idle check failed", error=str(e))
        return {
            "status": "error",
            "message": str(e)
        }