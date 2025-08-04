"""
Assets API endpoints.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
import structlog

from app.database import (
    store_asset, get_asset, list_assets, update_asset, 
    delete_asset, get_asset_count
)
from app.services.estfor_client import EstForClient
from app.tasks import collect_assets_task

logger = structlog.get_logger()
router = APIRouter()


class AssetResponse(BaseModel):
    """Asset response model."""
    id: str
    name: str
    type: str
    rarity: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AssetCreate(BaseModel):
    """Asset creation model."""
    name: str
    type: str
    rarity: Optional[str] = None
    description: Optional[str] = None


@router.get("/", response_model=List[AssetResponse])
async def get_assets(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> List[AssetResponse]:
    """Get list of assets with pagination."""
    try:
        assets = await list_assets(limit=limit, offset=offset)
        return [AssetResponse(**asset) for asset in assets]
    except Exception as e:
        logger.error("Failed to get assets", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve assets")


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset_by_id(asset_id: str) -> AssetResponse:
    """Get a specific asset by ID."""
    try:
        asset = await get_asset(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return AssetResponse(**asset)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get asset", error=str(e), asset_id=asset_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve asset")


@router.post("/", response_model=AssetResponse)
async def create_asset(asset_data: AssetCreate) -> AssetResponse:
    """Create a new asset."""
    try:
        asset_id = await store_asset(asset_data.dict())
        asset = await get_asset(asset_id)
        return AssetResponse(**asset)
    except Exception as e:
        logger.error("Failed to create asset", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create asset")


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset_by_id(asset_id: str, asset_data: AssetCreate) -> AssetResponse:
    """Update an existing asset."""
    try:
        success = await update_asset(asset_id, asset_data.dict())
        if not success:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        asset = await get_asset(asset_id)
        return AssetResponse(**asset)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update asset", error=str(e), asset_id=asset_id)
        raise HTTPException(status_code=500, detail="Failed to update asset")


@router.delete("/{asset_id}")
async def delete_asset_by_id(asset_id: str) -> Dict[str, str]:
    """Delete an asset."""
    try:
        success = await delete_asset(asset_id)
        if not success:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        return {"message": "Asset deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete asset", error=str(e), asset_id=asset_id)
        raise HTTPException(status_code=500, detail="Failed to delete asset")


@router.post("/collect")
async def trigger_asset_collection() -> Dict[str, Any]:
    """Trigger asset collection from EstFor API."""
    try:
        # Start background task
        task = collect_assets_task.delay()
        
        logger.info("Asset collection task started", task_id=task.id)
        
        return {
            "message": "Asset collection started",
            "task_id": task.id,
            "status": "queued"
        }
    except Exception as e:
        logger.error("Failed to start asset collection", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to start asset collection")


@router.get("/stats/summary")
async def get_asset_stats() -> Dict[str, Any]:
    """Get asset collection statistics."""
    try:
        total_count = await get_asset_count()
        
        return {
            "total_assets": total_count,
            "collection_status": "active",
            "last_updated": "2024-01-01T00:00:00Z"  # TODO: Add actual last update time
        }
    except Exception as e:
        logger.error("Failed to get asset stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics") 