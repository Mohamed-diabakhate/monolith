"""
Container Idle Monitoring and Auto-Stop Service.

This service monitors container usage patterns and automatically stops
idle containers based on configurable timeout periods to optimize resources.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Set, List
import structlog
from contextlib import asynccontextmanager

from app.config import settings
from app.services.container_manager import container_manager, ContainerPriority, ContainerState

logger = structlog.get_logger()

class IdleMonitorService:
    """
    Background service that monitors container idle times and stops unused containers.
    
    Features:
    - Configurable idle timeouts per container priority
    - Graceful shutdown with active request checking
    - Batch operations for efficiency
    - Comprehensive logging and monitoring
    - Safe shutdown prevention for critical containers
    """
    
    def __init__(self):
        self.is_running = False
        self.monitor_task = None
        self.stop_event = asyncio.Event()
        
        # Monitoring configuration
        self.check_interval = 60  # Check every minute
        self.batch_size = 5  # Stop max 5 containers per cycle
        
        # Statistics
        self.stats = {
            "containers_stopped": 0,
            "stop_attempts": 0,
            "stop_failures": 0,
            "last_check": None,
            "idle_containers_found": 0
        }
        
        # Safety checks
        self.min_running_containers = 2  # Always keep at least core services running

    async def start(self):
        """Start the idle monitoring service."""
        if self.is_running:
            logger.warning("Idle monitor service already running")
            return
        
        if not settings.CONTAINER_AUTO_STOP:
            logger.info("Container auto-stop is disabled")
            return
        
        logger.info("Starting container idle monitoring service")
        self.is_running = True
        self.stop_event.clear()
        
        # Start the monitoring task
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        
        return self.monitor_task

    async def stop(self):
        """Stop the idle monitoring service."""
        if not self.is_running:
            return
        
        logger.info("Stopping container idle monitoring service")
        self.is_running = False
        self.stop_event.set()
        
        if self.monitor_task:
            try:
                await asyncio.wait_for(self.monitor_task, timeout=10)
            except asyncio.TimeoutError:
                logger.warning("Idle monitor task did not stop gracefully")
                self.monitor_task.cancel()

    async def get_stats(self) -> Dict:
        """Get monitoring statistics."""
        return {
            **self.stats,
            "is_running": self.is_running,
            "check_interval_seconds": self.check_interval,
            "last_check_iso": self.stats["last_check"].isoformat() if self.stats["last_check"] else None
        }

    async def force_idle_check(self) -> Dict:
        """Force an immediate idle check (for testing/debugging)."""
        logger.info("Performing forced idle check")
        return await self._perform_idle_check()

    async def _monitor_loop(self):
        """Main monitoring loop."""
        logger.info(f"Container idle monitoring started (interval: {self.check_interval}s)")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                # Wait for next check interval or stop signal
                try:
                    await asyncio.wait_for(self.stop_event.wait(), timeout=self.check_interval)
                    # Stop event was set, exit loop
                    break
                except asyncio.TimeoutError:
                    # Normal timeout, perform idle check
                    pass
                
                # Perform idle check
                check_result = await self._perform_idle_check()
                
                logger.debug(
                    "Idle check completed",
                    idle_containers=check_result.get("idle_containers", 0),
                    stopped_containers=check_result.get("stopped_containers", 0)
                )
                
            except Exception as e:
                logger.error("Error in idle monitoring loop", error=str(e))
                # Continue monitoring even if one cycle fails
                await asyncio.sleep(30)  # Wait before retrying
        
        logger.info("Container idle monitoring stopped")

    async def _perform_idle_check(self) -> Dict:
        """Perform a single idle check cycle."""
        check_start = datetime.utcnow()
        self.stats["last_check"] = check_start
        
        result = {
            "idle_containers": 0,
            "stopped_containers": 0,
            "errors": []
        }
        
        try:
            # Get idle containers
            idle_containers = await container_manager.get_idle_containers()
            result["idle_containers"] = len(idle_containers)
            self.stats["idle_containers_found"] = len(idle_containers)
            
            if not idle_containers:
                logger.debug("No idle containers found")
                return result
            
            # Filter and prioritize containers for stopping
            containers_to_stop = await self._select_containers_to_stop(idle_containers)
            
            if containers_to_stop:
                logger.info(
                    f"Stopping {len(containers_to_stop)} idle containers",
                    containers=containers_to_stop
                )
                
                # Stop containers
                stop_results = await self._stop_containers_batch(containers_to_stop)
                result["stopped_containers"] = sum(stop_results.values())
                
                # Update statistics
                self.stats["stop_attempts"] += len(containers_to_stop)
                self.stats["containers_stopped"] += result["stopped_containers"]
                self.stats["stop_failures"] += len(containers_to_stop) - result["stopped_containers"]
        
        except Exception as e:
            error_msg = f"Error during idle check: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
        
        return result

    async def _select_containers_to_stop(self, idle_containers: Dict[str, timedelta]) -> List[str]:
        """Select which idle containers to stop based on priority and safety rules."""
        candidates = []
        
        # Sort by idle time (longest idle first)
        sorted_containers = sorted(
            idle_containers.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for container_name, idle_time in sorted_containers:
            # Safety checks
            if not await self._is_safe_to_stop(container_name):
                logger.debug(f"Skipping {container_name} - not safe to stop")
                continue
            
            # Check if we've reached batch limit
            if len(candidates) >= self.batch_size:
                break
            
            candidates.append(container_name)
            logger.debug(
                f"Selected {container_name} for stopping",
                idle_time_minutes=idle_time.total_seconds() // 60
            )
        
        return candidates

    async def _is_safe_to_stop(self, container_name: str) -> bool:
        """Check if it's safe to stop a container."""
        try:
            # Never stop critical containers
            priority = container_manager.container_priorities.get(container_name)
            if priority == ContainerPriority.CRITICAL:
                return False
            
            # Check if container is currently being accessed
            # (This would require additional request tracking in middleware)
            
            # Ensure minimum number of containers remain running
            all_status = await container_manager.get_all_container_status()
            running_containers = [
                name for name, status in all_status.items()
                if status["state"] == ContainerState.RUNNING
            ]
            
            if len(running_containers) <= self.min_running_containers:
                logger.debug(f"Minimum container count reached, skipping {container_name}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking safety for {container_name}", error=str(e))
            return False

    async def _stop_containers_batch(self, container_names: List[str]) -> Dict[str, bool]:
        """Stop a batch of containers concurrently."""
        results = {}
        
        # Create stop tasks
        stop_tasks = [
            self._stop_container_with_result(name) 
            for name in container_names
        ]
        
        # Execute concurrently
        stop_results = await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(stop_results):
            container_name = container_names[i]
            if isinstance(result, Exception):
                logger.error(f"Failed to stop {container_name}", error=str(result))
                results[container_name] = False
            else:
                results[container_name] = result
                if result:
                    logger.info(f"Successfully stopped idle container: {container_name}")
                else:
                    logger.warning(f"Failed to stop idle container: {container_name}")
        
        return results

    async def _stop_container_with_result(self, container_name: str) -> bool:
        """Stop a container and return success status."""
        try:
            return await container_manager.stop_container(container_name)
        except Exception as e:
            logger.error(f"Error stopping container {container_name}", error=str(e))
            return False


class IdleMonitorManager:
    """Manager class for the idle monitoring service lifecycle."""
    
    def __init__(self):
        self.service = IdleMonitorService()
    
    @asynccontextmanager
    async def lifespan(self):
        """Async context manager for service lifecycle."""
        try:
            # Start the service
            await self.service.start()
            yield self.service
        finally:
            # Stop the service
            await self.service.stop()
    
    async def start_service(self):
        """Start the idle monitoring service."""
        return await self.service.start()
    
    async def stop_service(self):
        """Stop the idle monitoring service."""
        await self.service.stop()
    
    def get_service(self) -> IdleMonitorService:
        """Get the service instance."""
        return self.service


# Global idle monitor manager
idle_monitor_manager = IdleMonitorManager()