"""
Celery tasks for background processing.
"""

from celery import Celery
from typing import Dict, Any, List
import structlog

from app.config import settings
from app.services.estfor_client import estfor_client
from app.database import store_asset

logger = structlog.get_logger()

# Initialize Celery
celery_app = Celery(
    "estfor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.WORKER_TIMEOUT,
    task_soft_time_limit=settings.WORKER_TIMEOUT - 30,
)


@celery_app.task(bind=True)
def collect_assets_task(self) -> Dict[str, Any]:
    """Background task to collect assets from EstFor API."""
    try:
        logger.info("Starting asset collection task", task_id=self.request.id)
        
        # Fetch assets from EstFor API
        assets = estfor_client.get_assets(limit=1000)
        
        stored_count = 0
        for asset in assets:
            try:
                # Store asset in Firestore
                store_asset(asset)
                stored_count += 1
            except Exception as e:
                logger.error("Failed to store asset", error=str(e), asset=asset)
        
        logger.info("Asset collection completed", 
                   task_id=self.request.id, 
                   total_assets=len(assets), 
                   stored_count=stored_count)
        
        return {
            "status": "completed",
            "total_assets": len(assets),
            "stored_count": stored_count,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error("Asset collection task failed", error=str(e), task_id=self.request.id)
        raise


@celery_app.task(bind=True)
def update_asset_task(self, asset_id: str) -> Dict[str, Any]:
    """Background task to update a specific asset."""
    try:
        logger.info("Starting asset update task", task_id=self.request.id, asset_id=asset_id)
        
        # Fetch updated asset from EstFor API
        asset = estfor_client.get_asset_by_id(asset_id)
        
        if asset:
            # Update asset in Firestore
            store_asset(asset)
            
            logger.info("Asset update completed", task_id=self.request.id, asset_id=asset_id)
            
            return {
                "status": "completed",
                "asset_id": asset_id,
                "task_id": self.request.id
            }
        else:
            logger.warning("Asset not found", task_id=self.request.id, asset_id=asset_id)
            
            return {
                "status": "not_found",
                "asset_id": asset_id,
                "task_id": self.request.id
            }
            
    except Exception as e:
        logger.error("Asset update task failed", error=str(e), task_id=self.request.id, asset_id=asset_id)
        raise 