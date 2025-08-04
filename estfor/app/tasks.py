"""
Celery tasks for background processing.
"""

from celery import Celery
from typing import Dict, Any, List
import structlog

from app.config import settings
from app.services.estfor_client import estfor_client
from app.database import store_asset, init_mongodb

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
        
        # For now, create mock data since we don't have real API access
        mock_assets = [
            {
                "asset_id": f"weapon_{i:03d}",
                "name": f"Weapon {i}",
                "type": "weapon",
                "description": f"This is weapon number {i}",
                "metadata": {"rarity": "common", "level": i % 10 + 1}
            }
            for i in range(1, 51)  # Create 50 weapons
        ]
        
        # Add some armor items
        mock_assets.extend([
            {
                "asset_id": f"armor_{i:03d}",
                "name": f"Armor {i}",
                "type": "armor",
                "description": f"This is armor number {i}",
                "metadata": {"rarity": "uncommon", "level": i % 8 + 1}
            }
            for i in range(1, 31)  # Create 30 armor items
        ])
        
        # Add some consumables
        mock_assets.extend([
            {
                "asset_id": f"potion_{i:03d}",
                "name": f"Potion {i}",
                "type": "consumable",
                "description": f"This is potion number {i}",
                "metadata": {"rarity": "rare", "level": i % 5 + 1}
            }
            for i in range(1, 21)  # Create 20 potions
        ])
        
        # Initialize MongoDB connection and store all assets in a single event loop
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(init_mongodb())
            
            stored_count = 0
            for asset in mock_assets:
                try:
                    asset_id = loop.run_until_complete(store_asset(asset))
                    stored_count += 1
                except Exception as e:
                    logger.error("Failed to store asset", error=str(e), asset=asset)
        finally:
            loop.close()
        
        logger.info("Asset collection completed", 
                   task_id=self.request.id, 
                   total_assets=len(mock_assets), 
                   stored_count=stored_count)
        
        return {
            "status": "completed",
            "total_assets": len(mock_assets),
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
        
        # For now, create a mock updated asset
        mock_asset = {
            "asset_id": asset_id,
            "name": f"Updated {asset_id}",
            "type": "weapon",
            "description": f"This is an updated asset: {asset_id}",
            "metadata": {"rarity": "epic", "level": 99}
        }
        
        # Update asset in MongoDB
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(store_asset(mock_asset))
        finally:
            loop.close()
        
        logger.info("Asset update completed", task_id=self.request.id, asset_id=asset_id)
        
        return {
            "status": "completed",
            "asset_id": asset_id,
            "task_id": self.request.id
        }
            
    except Exception as e:
        logger.error("Asset update task failed", error=str(e), task_id=self.request.id, asset_id=asset_id)
        raise 