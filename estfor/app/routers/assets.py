"""
Asset-related API endpoints.
"""

import structlog
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database import get_collection, store_asset, init_mongodb
from app.services.estfor_client import estfor_client

logger = structlog.get_logger()
router = APIRouter()


class AssetResponse(BaseModel):
    """Asset response model."""
    id: str
    name: str
    type: str
    rarity: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AssetStats(BaseModel):
    """Asset statistics model."""
    total_assets: int
    collection_status: str
    last_updated: str


@router.get("/", response_model=List[AssetResponse])
async def get_assets():
    """Get all assets."""
    try:
        collection = get_collection()
        cursor = collection.find({})
        assets = []
        
        async for doc in cursor:
            assets.append(AssetResponse(
                id=str(doc["_id"]),
                name=doc.get("name", ""),
                type=doc.get("type", ""),
                rarity=doc.get("metadata", {}).get("rarity"),
                description=doc.get("description"),
                created_at=doc.get("created_at"),
                updated_at=doc.get("updated_at")
            ))
        
        return assets
    except Exception as e:
        logger.error("Failed to retrieve assets", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve assets")


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str):
    """Get a specific asset by ID."""
    try:
        collection = get_collection()
        doc = await collection.find_one({"_id": asset_id})
        
        if not doc:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        return AssetResponse(
            id=str(doc["_id"]),
            name=doc.get("name", ""),
            type=doc.get("type", ""),
            rarity=doc.get("metadata", {}).get("rarity"),
            description=doc.get("description"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve asset", error=str(e), asset_id=asset_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve asset")


@router.post("/collect")
async def collect_assets():
    """Collect assets from the real EstFor API."""
    try:
        logger.info("Starting asset collection from EstFor API")
        
        # Fetch assets from the real EstFor API
        assets = await estfor_client.get_assets(limit=100, offset=0)
        
        if not assets:
            logger.warning("No assets returned from EstFor API")
            return {
                "message": "No assets found in EstFor API",
                "total_assets": 0,
                "stored_count": 0,
                "status": "completed"
            }
        
        # Store all assets directly
        stored_count = 0
        for asset in assets:
            try:
                await store_asset(asset)
                stored_count += 1
            except Exception as e:
                logger.error("Failed to store asset", error=str(e), asset=asset)
        
        logger.info("Asset collection from EstFor API completed", 
                   total_assets=len(assets), 
                   stored_count=stored_count)
        
        return {
            "message": "Asset collection from EstFor API completed",
            "total_assets": len(assets),
            "stored_count": stored_count,
            "status": "completed",
            "source": "api.estfor.com"
        }
        
    except Exception as e:
        logger.error("Failed to collect assets from EstFor API", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to collect assets from EstFor API")


@router.post("/collect/{asset_type}")
async def collect_assets_by_type(asset_type: str):
    """Collect assets of a specific type from the EstFor API."""
    try:
        logger.info(f"Starting asset collection for type: {asset_type}")
        
        # Fetch assets of specific type from the real EstFor API
        assets = await estfor_client.get_assets(limit=100, offset=0, asset_type=asset_type)
        
        if not assets:
            logger.warning(f"No {asset_type} assets returned from EstFor API")
            return {
                "message": f"No {asset_type} assets found in EstFor API",
                "total_assets": 0,
                "stored_count": 0,
                "status": "completed",
                "asset_type": asset_type
            }
        
        # Store all assets directly
        stored_count = 0
        for asset in assets:
            try:
                await store_asset(asset)
                stored_count += 1
            except Exception as e:
                logger.error("Failed to store asset", error=str(e), asset=asset)
        
        logger.info(f"Asset collection for {asset_type} from EstFor API completed", 
                   total_assets=len(assets), 
                   stored_count=stored_count)
        
        return {
            "message": f"Asset collection for {asset_type} from EstFor API completed",
            "total_assets": len(assets),
            "stored_count": stored_count,
            "status": "completed",
            "asset_type": asset_type,
            "source": "api.estfor.com"
        }
        
    except Exception as e:
        logger.error(f"Failed to collect {asset_type} assets from EstFor API", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to collect {asset_type} assets from EstFor API")


@router.get("/stats/summary", response_model=AssetStats)
async def get_asset_stats():
    """Get asset collection statistics from EstFor API."""
    try:
        # Try to get stats from EstFor API first
        try:
            api_stats = await estfor_client.get_asset_stats()
            return AssetStats(
                total_assets=api_stats.get("total_assets", 0),
                collection_status="active",
                last_updated=api_stats.get("last_updated", "2024-01-01T00:00:00Z")
            )
        except Exception as api_error:
            logger.warning("Failed to get stats from EstFor API, using local database", error=str(api_error))
            # Fallback to local database stats
            collection = get_collection()
            total_assets = await collection.count_documents({})
            
            return AssetStats(
                total_assets=total_assets,
                collection_status="active",
                last_updated="2024-01-01T00:00:00Z"
            )
    except Exception as e:
        logger.error("Failed to get asset stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get asset stats") 