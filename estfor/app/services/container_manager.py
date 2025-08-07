"""
Container Management Service for Auto Start/Stop functionality.

This service manages Docker container lifecycle based on endpoint access patterns
and configurable idle timeouts.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum
import structlog
import docker
from docker.errors import DockerException, NotFound, APIError
import redis.asyncio as redis

from app.config import settings

logger = structlog.get_logger()

class ContainerState(str, Enum):
    """Container states."""
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"

class ContainerPriority(str, Enum):
    """Container priority levels."""
    CRITICAL = "critical"  # Never auto-stop
    HIGH = "high"         # Long idle timeout
    NORMAL = "normal"     # Standard idle timeout
    LOW = "low"          # Short idle timeout

class ContainerManager:
    """Manages Docker container lifecycle for auto start/stop functionality."""
    
    def __init__(self):
        self.docker_client = None
        self.redis_client = None
        self._container_states: Dict[str, ContainerState] = {}
        self._last_access: Dict[str, datetime] = {}
        self._startup_locks: Dict[str, asyncio.Lock] = {}
        
        # Service-to-container mapping
        self.service_containers = {
            "core": {"app", "mongodb", "redis"},
            "monitoring": {"prometheus", "grafana", "alertmanager"},
            "logging": {"elasticsearch", "logstash", "kibana", "filebeat"},
            "processing": {"worker"},
            "metrics": {"cadvisor"}
        }
        
        # Container priorities
        self.container_priorities = {
            # Critical - never auto-stop
            "app": ContainerPriority.CRITICAL,
            "mongodb": ContainerPriority.CRITICAL, 
            "redis": ContainerPriority.CRITICAL,
            
            # High priority - long timeout (2 hours)
            "worker": ContainerPriority.HIGH,
            "prometheus": ContainerPriority.HIGH,
            
            # Normal priority - standard timeout (30 minutes)
            "grafana": ContainerPriority.NORMAL,
            "alertmanager": ContainerPriority.NORMAL,
            
            # Low priority - short timeout (10 minutes)
            "elasticsearch": ContainerPriority.LOW,
            "logstash": ContainerPriority.LOW,
            "kibana": ContainerPriority.LOW,
            "filebeat": ContainerPriority.LOW,
            "cadvisor": ContainerPriority.LOW
        }
        
        # Endpoint-to-containers mapping
        self.endpoint_dependencies = {
            "/assets": {"app", "mongodb", "redis"},
            "/health": {"app"},
            "/metrics": {"app", "prometheus"},
            "/logs": {"kibana", "elasticsearch"},
            "/dashboards": {"grafana"},
            "/tasks": {"worker", "redis"},
            "/admin": {"grafana", "kibana", "prometheus"}
        }

    async def initialize(self):
        """Initialize Docker and Redis connections."""
        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
            
            # Initialize Redis client
            self.redis_client = redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
            logger.info("Redis client initialized")
            
            # Load existing container states
            await self._load_container_states()
            
            return True
        except Exception as e:
            logger.error("Failed to initialize ContainerManager", error=str(e))
            return False

    async def close(self):
        """Close connections."""
        if self.redis_client:
            await self.redis_client.close()
        if self.docker_client:
            self.docker_client.close()

    async def get_container_state(self, container_name: str) -> ContainerState:
        """Get current state of a container."""
        try:
            container = self.docker_client.containers.get(f"estfor-{container_name}-1")
            status = container.status
            
            state_mapping = {
                "running": ContainerState.RUNNING,
                "exited": ContainerState.STOPPED,
                "paused": ContainerState.STOPPED,
                "restarting": ContainerState.STARTING,
                "removing": ContainerState.STOPPING,
                "dead": ContainerState.ERROR
            }
            
            state = state_mapping.get(status, ContainerState.UNKNOWN)
            self._container_states[container_name] = state
            
            # Update state in Redis
            await self._save_container_state(container_name, state)
            
            return state
            
        except NotFound:
            logger.warning(f"Container {container_name} not found")
            return ContainerState.UNKNOWN
        except Exception as e:
            logger.error(f"Error getting container state for {container_name}", error=str(e))
            return ContainerState.ERROR

    async def start_container(self, container_name: str, wait_for_health: bool = True) -> bool:
        """Start a container and optionally wait for it to be healthy."""
        if container_name not in self._startup_locks:
            self._startup_locks[container_name] = asyncio.Lock()
            
        async with self._startup_locks[container_name]:
            try:
                # Check current state
                current_state = await self.get_container_state(container_name)
                if current_state == ContainerState.RUNNING:
                    logger.info(f"Container {container_name} already running")
                    return True
                
                # Mark as starting
                self._container_states[container_name] = ContainerState.STARTING
                await self._save_container_state(container_name, ContainerState.STARTING)
                
                logger.info(f"Starting container {container_name}")
                
                # Start the container
                container = self.docker_client.containers.get(f"estfor-{container_name}-1")
                container.start()
                
                # Wait for container to be running
                if wait_for_health:
                    return await self._wait_for_container_health(container_name)
                else:
                    self._container_states[container_name] = ContainerState.RUNNING
                    await self._save_container_state(container_name, ContainerState.RUNNING)
                    return True
                    
            except NotFound:
                logger.error(f"Container {container_name} not found")
                return False
            except Exception as e:
                logger.error(f"Failed to start container {container_name}", error=str(e))
                self._container_states[container_name] = ContainerState.ERROR
                await self._save_container_state(container_name, ContainerState.ERROR)
                return False

    async def stop_container(self, container_name: str, force: bool = False) -> bool:
        """Stop a container gracefully or forcefully."""
        try:
            # Check if container is critical
            if self.container_priorities.get(container_name) == ContainerPriority.CRITICAL and not force:
                logger.warning(f"Skipping stop of critical container {container_name}")
                return False
            
            # Mark as stopping
            self._container_states[container_name] = ContainerState.STOPPING
            await self._save_container_state(container_name, ContainerState.STOPPING)
            
            logger.info(f"Stopping container {container_name}")
            
            container = self.docker_client.containers.get(f"estfor-{container_name}-1")
            container.stop(timeout=10 if not force else 0)
            
            # Update state
            self._container_states[container_name] = ContainerState.STOPPED
            await self._save_container_state(container_name, ContainerState.STOPPED)
            
            return True
            
        except NotFound:
            logger.warning(f"Container {container_name} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to stop container {container_name}", error=str(e))
            return False

    async def get_required_containers_for_endpoint(self, endpoint_path: str) -> Set[str]:
        """Get list of containers required for an endpoint."""
        required = set()
        
        # Check exact matches first
        if endpoint_path in self.endpoint_dependencies:
            required.update(self.endpoint_dependencies[endpoint_path])
        
        # Check prefix matches
        for endpoint_pattern, containers in self.endpoint_dependencies.items():
            if endpoint_path.startswith(endpoint_pattern):
                required.update(containers)
        
        # Always include core containers
        required.update(self.service_containers["core"])
        
        return required

    async def ensure_containers_running(self, container_names: Set[str]) -> Dict[str, bool]:
        """Ensure specified containers are running."""
        results = {}
        start_tasks = []
        
        for container_name in container_names:
            state = await self.get_container_state(container_name)
            if state != ContainerState.RUNNING:
                start_tasks.append(self._start_with_result(container_name))
            else:
                results[container_name] = True
                # Update last access time
                await self.mark_container_accessed(container_name)
        
        # Start containers concurrently
        if start_tasks:
            start_results = await asyncio.gather(*start_tasks, return_exceptions=True)
            for i, result in enumerate(start_results):
                container_name = list(container_names)[i]
                if isinstance(result, Exception):
                    logger.error(f"Failed to start {container_name}", error=str(result))
                    results[container_name] = False
                else:
                    results[container_name] = result
        
        return results

    async def mark_container_accessed(self, container_name: str):
        """Mark a container as recently accessed."""
        self._last_access[container_name] = datetime.utcnow()
        await self.redis_client.hset(
            "container_last_access", 
            container_name, 
            int(time.time())
        )

    async def get_idle_containers(self) -> Dict[str, timedelta]:
        """Get containers that have been idle beyond their timeout."""
        idle_containers = {}
        current_time = datetime.utcnow()
        
        # Load last access times from Redis
        access_times = await self.redis_client.hgetall("container_last_access")
        
        for container_name, priority in self.container_priorities.items():
            if priority == ContainerPriority.CRITICAL:
                continue
                
            # Get timeout based on priority
            timeout_minutes = self._get_timeout_for_priority(priority)
            timeout_delta = timedelta(minutes=timeout_minutes)
            
            # Get last access time
            last_access_timestamp = access_times.get(container_name)
            if last_access_timestamp:
                last_access = datetime.fromtimestamp(int(last_access_timestamp))
            else:
                # If no access time recorded, use current time - timeout (immediate candidate)
                last_access = current_time - timeout_delta - timedelta(minutes=1)
            
            idle_time = current_time - last_access
            
            if idle_time > timeout_delta:
                # Check if container is actually running
                state = await self.get_container_state(container_name)
                if state == ContainerState.RUNNING:
                    idle_containers[container_name] = idle_time
        
        return idle_containers

    async def get_all_container_status(self) -> Dict[str, Dict]:
        """Get status of all managed containers."""
        status = {}
        
        for container_name in self.container_priorities.keys():
            state = await self.get_container_state(container_name)
            last_access_timestamp = await self.redis_client.hget("container_last_access", container_name)
            
            last_access = None
            if last_access_timestamp:
                last_access = datetime.fromtimestamp(int(last_access_timestamp))
            
            status[container_name] = {
                "state": state,
                "priority": self.container_priorities[container_name],
                "last_access": last_access.isoformat() if last_access else None,
                "idle_timeout_minutes": self._get_timeout_for_priority(
                    self.container_priorities[container_name]
                )
            }
        
        return status

    async def _wait_for_container_health(self, container_name: str, timeout: int = 60) -> bool:
        """Wait for a container to be healthy."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                container = self.docker_client.containers.get(f"estfor-{container_name}-1")
                
                # Check if container has health check
                health = container.attrs.get("State", {}).get("Health")
                if health:
                    health_status = health.get("Status")
                    if health_status == "healthy":
                        self._container_states[container_name] = ContainerState.RUNNING
                        await self._save_container_state(container_name, ContainerState.RUNNING)
                        await self.mark_container_accessed(container_name)
                        return True
                    elif health_status == "unhealthy":
                        logger.error(f"Container {container_name} is unhealthy")
                        return False
                else:
                    # No health check, just check if running
                    if container.status == "running":
                        self._container_states[container_name] = ContainerState.RUNNING
                        await self._save_container_state(container_name, ContainerState.RUNNING)
                        await self.mark_container_accessed(container_name)
                        return True
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error checking health for {container_name}", error=str(e))
                await asyncio.sleep(2)
        
        logger.error(f"Container {container_name} failed to become healthy within {timeout}s")
        return False

    async def _start_with_result(self, container_name: str) -> bool:
        """Start container and return result."""
        return await self.start_container(container_name)

    async def _save_container_state(self, container_name: str, state: ContainerState):
        """Save container state to Redis."""
        await self.redis_client.hset("container_states", container_name, state.value)

    async def _load_container_states(self):
        """Load container states from Redis."""
        try:
            states = await self.redis_client.hgetall("container_states")
            for container_name, state_value in states.items():
                self._container_states[container_name] = ContainerState(state_value)
        except Exception as e:
            logger.warning("Failed to load container states from Redis", error=str(e))

    def _get_timeout_for_priority(self, priority: ContainerPriority) -> int:
        """Get idle timeout in minutes for a priority level."""
        timeouts = {
            ContainerPriority.CRITICAL: 0,  # Never timeout
            ContainerPriority.HIGH: settings.CONTAINER_HIGH_IDLE_TIMEOUT,
            ContainerPriority.NORMAL: settings.CONTAINER_IDLE_TIMEOUT,
            ContainerPriority.LOW: settings.CONTAINER_LOW_IDLE_TIMEOUT
        }
        return timeouts.get(priority, settings.CONTAINER_IDLE_TIMEOUT)


# Global container manager instance
container_manager = ContainerManager()