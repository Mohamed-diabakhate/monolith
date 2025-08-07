"""
Container Auto-Start Middleware for FastAPI.

This middleware automatically starts required containers when endpoints are accessed
and ensures services are available before processing requests.
"""

import time
import asyncio
from typing import Callable, Dict, Set
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.config import settings
from app.services.container_manager import container_manager, ContainerState

logger = structlog.get_logger()

class ContainerAutoStartMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically starts required containers for incoming requests.
    
    Features:
    - Analyzes request path to determine required containers
    - Starts containers if they're not running
    - Waits for containers to be healthy before proceeding
    - Handles startup failures gracefully
    - Updates container access timestamps
    """
    
    def __init__(self, app, enable_auto_start: bool = True):
        super().__init__(app)
        self.enable_auto_start = enable_auto_start
        self.startup_cache: Dict[str, float] = {}  # Cache recent startups
        self.cache_timeout = 300  # 5 minutes cache
        
        # Bypass paths that don't require container management
        self.bypass_paths = {
            "/health",
            "/health/",
            "/health/live",
            "/health/containers",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico"
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware dispatch method."""
        
        # Skip if auto-start is disabled
        if not self.enable_auto_start or not settings.CONTAINER_AUTO_START:
            return await call_next(request)
        
        # Skip bypass paths
        if request.url.path in self.bypass_paths:
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            # Get required containers for this endpoint
            required_containers = await container_manager.get_required_containers_for_endpoint(
                request.url.path
            )
            
            if not required_containers:
                # No specific container requirements, proceed
                return await call_next(request)
            
            # Check if we need to start any containers
            containers_to_start = await self._get_containers_to_start(required_containers)
            
            if containers_to_start:
                logger.info(
                    "Starting containers for request", 
                    path=request.url.path,
                    containers=list(containers_to_start)
                )
                
                # Start containers and wait for them to be ready
                startup_success = await self._ensure_containers_ready(
                    containers_to_start, 
                    request.url.path
                )
                
                if not startup_success:
                    return await self._return_service_unavailable_error(containers_to_start)
            
            # Mark all required containers as accessed
            for container in required_containers:
                await container_manager.mark_container_accessed(container)
            
            # Process the request
            response = await call_next(request)
            
            # Log successful request with container info
            processing_time = time.time() - start_time
            logger.info(
                "Request processed successfully",
                path=request.url.path,
                containers=list(required_containers),
                processing_time_ms=round(processing_time * 1000, 2)
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Container middleware error",
                path=request.url.path,
                error=str(e)
            )
            # Don't block request on middleware errors
            return await call_next(request)

    async def _get_containers_to_start(self, required_containers: Set[str]) -> Set[str]:
        """Determine which containers need to be started."""
        containers_to_start = set()
        
        for container_name in required_containers:
            # Check cache first to avoid redundant checks
            if self._is_recently_started(container_name):
                continue
                
            state = await container_manager.get_container_state(container_name)
            
            if state in [ContainerState.STOPPED, ContainerState.ERROR, ContainerState.UNKNOWN]:
                containers_to_start.add(container_name)
            elif state == ContainerState.STARTING:
                # Container is already starting, include in monitoring
                containers_to_start.add(container_name)
        
        return containers_to_start

    async def _ensure_containers_ready(self, containers: Set[str], request_path: str) -> bool:
        """Start containers and wait for them to be ready."""
        try:
            # Start all containers concurrently
            startup_results = await container_manager.ensure_containers_running(containers)
            
            # Check if all containers started successfully
            failed_containers = [
                container for container, success in startup_results.items() 
                if not success
            ]
            
            if failed_containers:
                logger.error(
                    "Failed to start required containers",
                    path=request_path,
                    failed_containers=failed_containers
                )
                return False
            
            # Cache successful startups
            current_time = time.time()
            for container in containers:
                self.startup_cache[container] = current_time
            
            logger.info(
                "All required containers started successfully",
                path=request_path,
                containers=list(containers)
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Error ensuring containers ready",
                path=request_path,
                containers=list(containers),
                error=str(e)
            )
            return False

    def _is_recently_started(self, container_name: str) -> bool:
        """Check if container was recently started (cached)."""
        if container_name not in self.startup_cache:
            return False
        
        start_time = self.startup_cache[container_name]
        current_time = time.time()
        
        # Remove expired cache entries
        if current_time - start_time > self.cache_timeout:
            del self.startup_cache[container_name]
            return False
        
        return True

    async def _return_service_unavailable_error(self, failed_containers: Set[str]) -> JSONResponse:
        """Return a 503 Service Unavailable response for container startup failures."""
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service Unavailable",
                "message": "Required services are starting up. Please try again in a moment.",
                "details": {
                    "failed_services": list(failed_containers),
                    "estimated_wait_time": "30-60 seconds"
                },
                "retry_after": 30
            },
            headers={"Retry-After": "30"}
        )


class ContainerHealthCheckMiddleware(BaseHTTPMiddleware):
    """
    Middleware that performs lightweight container health checks during requests.
    
    This middleware runs after the auto-start middleware to ensure containers
    remain healthy during request processing.
    """
    
    def __init__(self, app, enable_health_checks: bool = True):
        super().__init__(app)
        self.enable_health_checks = enable_health_checks
        self.last_health_check: Dict[str, float] = {}
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Perform health checks and process request."""
        
        if not self.enable_health_checks:
            return await call_next(request)
        
        try:
            # Get required containers for this request
            required_containers = await container_manager.get_required_containers_for_endpoint(
                request.url.path
            )
            
            # Perform periodic health checks (not on every request)
            await self._periodic_health_check(required_containers)
            
            # Process the request
            response = await call_next(request)
            
            return response
            
        except Exception as e:
            logger.error("Container health check middleware error", error=str(e))
            return await call_next(request)

    async def _periodic_health_check(self, containers: Set[str]):
        """Perform periodic health checks on containers."""
        current_time = time.time()
        check_interval = settings.CONTAINER_HEALTH_CHECK_INTERVAL
        
        for container_name in containers:
            last_check = self.last_health_check.get(container_name, 0)
            
            if current_time - last_check > check_interval:
                # Perform health check asynchronously (don't block request)
                asyncio.create_task(self._check_container_health(container_name))
                self.last_health_check[container_name] = current_time

    async def _check_container_health(self, container_name: str):
        """Check health of a specific container."""
        try:
            state = await container_manager.get_container_state(container_name)
            if state == ContainerState.ERROR:
                logger.warning(f"Container {container_name} is in error state")
            elif state == ContainerState.UNKNOWN:
                logger.warning(f"Container {container_name} state is unknown")
        except Exception as e:
            logger.error(f"Failed to check health of {container_name}", error=str(e))