"""
Enhanced asset-related API endpoints with EstFor game integration.
"""

import structlog
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Union, Dict
from datetime import datetime
from pydantic import BaseModel

from app.database import get_collection, store_asset, init_mongodb
from app.database.enhanced import enhanced_asset_db
from app.services.estfor_client import estfor_client
from app.services.asset_enrichment import asset_enrichment_service
from app.models.enhanced_asset import (
    EstForAsset,
    EnhancedAssetResponse,
    AssetFilter,
    AssetStatsSummary,
    AssetCategory,
    RarityTier,
)
from app.game_constants import EquipPosition, Skill, BoostType

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


@router.get("/", response_model=List[EnhancedAssetResponse])
async def get_assets(
    # Filtering parameters
    category: Optional[AssetCategory] = Query(None, description="Filter by asset category"),
    equip_position: Optional[EquipPosition] = Query(None, description="Filter by equipment position"),
    min_rarity: Optional[RarityTier] = Query(None, description="Minimum rarity tier"),
    max_rarity: Optional[RarityTier] = Query(None, description="Maximum rarity tier"),
    required_skill: Optional[str] = Query(None, description="Filter by required skill"),
    max_skill_level: Optional[int] = Query(None, description="Maximum skill level requirement"),
    has_boost: Optional[BoostType] = Query(None, description="Filter by boost type"),
    tradeable_only: Optional[bool] = Query(None, description="Only tradeable items"),
    equipment_only: Optional[bool] = Query(None, description="Only equipable items"),
    consumable_only: Optional[bool] = Query(None, description="Only consumable items"),
    
    # Pagination and sorting
    limit: int = Query(100, ge=1, le=1000, description="Number of assets to return"),
    offset: int = Query(0, ge=0, description="Number of assets to skip"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: int = Query(-1, description="Sort order (1 for ascending, -1 for descending)"),
):
    """Get enhanced assets with filtering and pagination."""
    try:
        # Create filter from query parameters
        asset_filter = AssetFilter(
            category=category,
            equip_position=equip_position,
            min_rarity=min_rarity,
            max_rarity=max_rarity,
            required_skill=required_skill,
            max_skill_level=max_skill_level,
            has_boost=has_boost,
            tradeable_only=tradeable_only,
            equipment_only=equipment_only,
            consumable_only=consumable_only,
        )
        
        # Get enhanced assets from database
        assets = await enhanced_asset_db.list_enhanced_assets(
            asset_filter=asset_filter,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Convert to response format
        return [EnhancedAssetResponse.from_asset(asset) for asset in assets]
        
    except Exception as e:
        logger.error("Failed to retrieve enhanced assets", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve assets")


@router.get("/{asset_id}", response_model=EnhancedAssetResponse)
async def get_asset(asset_id: str):
    """Get a specific enhanced asset by ID."""
    try:
        # Get enhanced asset from database
        asset = await enhanced_asset_db.get_enhanced_asset(asset_id)
        
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        return EnhancedAssetResponse.from_asset(asset)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve enhanced asset", error=str(e), asset_id=asset_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve asset")


@router.post("/collect")
async def collect_assets():
    """Collect and enrich assets from the EstFor API."""
    try:
        logger.info("Starting enhanced asset collection from EstFor API")
        
        # Fetch assets from the real EstFor API
        raw_assets = await estfor_client.get_assets(limit=100, offset=0)
        
        if not raw_assets:
            logger.warning("No assets returned from EstFor API")
            return {
                "message": "No assets found in EstFor API",
                "total_assets": 0,
                "enriched_count": 0,
                "stored_count": 0,
                "status": "completed"
            }
        
        # Enrich and store all assets
        enriched_count = 0
        stored_count = 0
        failed_count = 0
        
        for raw_asset in raw_assets:
            try:
                # Enrich asset with game metadata
                enhanced_asset = asset_enrichment_service.enrich_asset(raw_asset)
                enriched_count += 1
                
                # Store enhanced asset
                await enhanced_asset_db.store_enhanced_asset(enhanced_asset)
                stored_count += 1
                
            except Exception as e:
                logger.error("Failed to enrich and store asset", error=str(e), asset=raw_asset.get("name"))
                failed_count += 1
        
        logger.info("Enhanced asset collection completed", 
                   total_assets=len(raw_assets), 
                   enriched_count=enriched_count,
                   stored_count=stored_count,
                   failed_count=failed_count)
        
        return {
            "message": "Enhanced asset collection from EstFor API completed",
            "total_assets": len(raw_assets),
            "enriched_count": enriched_count,
            "stored_count": stored_count,
            "failed_count": failed_count,
            "status": "completed",
            "source": "api.estfor.com",
            "enhancement": "estfor_game_constants"
        }
        
    except Exception as e:
        logger.error("Failed to collect and enrich assets from EstFor API", error=str(e))
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


@router.get("/stats/summary", response_model=AssetStatsSummary)
async def get_asset_stats():
    """Get comprehensive asset statistics."""
    try:
        # Get enhanced stats from database
        stats = await enhanced_asset_db.get_asset_stats()
        return stats
        
    except Exception as e:
        logger.error("Failed to get enhanced asset stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get asset stats")


# New specialized endpoints

@router.get("/search", response_model=List[EnhancedAssetResponse])
async def search_assets(
    q: str = Query(..., description="Search query"),
    category: Optional[AssetCategory] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=200, description="Number of results to return")
):
    """Search assets by name and description."""
    try:
        # Create filter for search
        asset_filter = AssetFilter(category=category) if category else None
        
        # Search assets
        assets = await enhanced_asset_db.search_enhanced_assets(
            search_query=q,
            asset_filter=asset_filter,
            limit=limit
        )
        
        return [EnhancedAssetResponse.from_asset(asset) for asset in assets]
        
    except Exception as e:
        logger.error("Failed to search assets", error=str(e), query=q)
        raise HTTPException(status_code=500, detail="Failed to search assets")


@router.get("/equipment/{position}", response_model=List[EnhancedAssetResponse])
async def get_equipment_by_position(
    position: EquipPosition,
    min_rarity: Optional[RarityTier] = Query(None, description="Minimum rarity"),
    max_skill_level: Optional[int] = Query(None, description="Maximum skill requirement"),
    limit: int = Query(100, ge=1, le=500, description="Number of items to return")
):
    """Get equipment items by position (HEAD, BODY, etc.)."""
    try:
        # Create filter for equipment position
        asset_filter = AssetFilter(
            equip_position=position,
            min_rarity=min_rarity,
            equipment_only=True
        )
        
        assets = await enhanced_asset_db.list_enhanced_assets(
            asset_filter=asset_filter,
            limit=limit,
            sort_by="rarity_tier",
            sort_order=1
        )
        
        # Filter by skill level if specified
        if max_skill_level:
            assets = [
                asset for asset in assets 
                if not asset.skill_requirements or max(asset.skill_requirements.values()) <= max_skill_level
            ]
        
        return [EnhancedAssetResponse.from_asset(asset) for asset in assets]
        
    except Exception as e:
        logger.error("Failed to get equipment by position", error=str(e), position=position.name)
        raise HTTPException(status_code=500, detail="Failed to get equipment")


@router.get("/by-skill/{skill_name}", response_model=List[EnhancedAssetResponse])
async def get_assets_by_skill(
    skill_name: str,
    max_level: Optional[int] = Query(None, description="Maximum skill level requirement"),
    category: Optional[AssetCategory] = Query(None, description="Filter by category"),
    limit: int = Query(100, ge=1, le=500, description="Number of items to return")
):
    """Get assets that require a specific skill."""
    try:
        # Validate skill name
        skill_name = skill_name.upper()
        valid_skills = [skill.name for skill in Skill]
        if skill_name not in valid_skills:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid skill name. Valid skills: {', '.join(valid_skills)}"
            )
        
        assets = await enhanced_asset_db.get_assets_by_skill(
            skill_name=skill_name,
            max_level=max_level,
            limit=limit
        )
        
        # Filter by category if specified
        if category:
            assets = [asset for asset in assets if asset.category == category]
        
        return [EnhancedAssetResponse.from_asset(asset) for asset in assets]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get assets by skill", error=str(e), skill=skill_name)
        raise HTTPException(status_code=500, detail="Failed to get assets by skill")


@router.get("/categories", response_model=Dict[str, int])
async def get_asset_categories():
    """Get all asset categories with counts."""
    try:
        stats = await enhanced_asset_db.get_asset_stats()
        return stats.by_category
        
    except Exception as e:
        logger.error("Failed to get asset categories", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get asset categories")


@router.get("/boosts", response_model=List[EnhancedAssetResponse])
async def get_assets_with_boosts(
    boost_type: Optional[BoostType] = Query(None, description="Filter by boost type"),
    category: Optional[AssetCategory] = Query(None, description="Filter by category"),
    limit: int = Query(100, ge=1, le=500, description="Number of items to return")
):
    """Get assets that have boost effects."""
    try:
        assets = await enhanced_asset_db.get_assets_with_boosts(
            boost_type=boost_type,
            limit=limit
        )
        
        # Filter by category if specified
        if category:
            assets = [asset for asset in assets if asset.category == category]
        
        return [EnhancedAssetResponse.from_asset(asset) for asset in assets]
        
    except Exception as e:
        logger.error("Failed to get assets with boosts", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get assets with boosts")


@router.post("/compatible")
async def check_asset_compatibility(
    asset_id: str,
    player_skills: Dict[str, int]
):
    """Check if a player can use/equip a specific asset."""
    try:
        # Get the asset
        asset = await enhanced_asset_db.get_enhanced_asset(asset_id)
        
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Check compatibility
        can_equip = asset.can_equip_with_skills(player_skills)
        
        # Get relevant boosts for player's skills
        relevant_boosts = []
        for skill_name in player_skills.keys():
            try:
                skill = Skill[skill_name.upper()]
                boosts = asset.get_relevant_boosts(skill)
                relevant_boosts.extend([
                    {
                        "skill": skill.name,
                        "boost_type": boost.boost_type.name,
                        "value": boost.value,
                        "duration": boost.duration
                    }
                    for boost in boosts
                ])
            except (KeyError, AttributeError):
                pass
        
        return {
            "asset_id": asset_id,
            "asset_name": asset.name,
            "compatible": can_equip,
            "requirements": asset.skill_requirements,
            "player_skills": player_skills,
            "missing_requirements": {
                skill: level - player_skills.get(skill, 0)
                for skill, level in asset.skill_requirements.items()
                if player_skills.get(skill, 0) < level
            },
            "relevant_boosts": relevant_boosts,
            "is_equipment": asset.is_equipment(),
            "is_consumable": asset.is_consumable(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to check asset compatibility", error=str(e), asset_id=asset_id)
        raise HTTPException(status_code=500, detail="Failed to check compatibility")


@router.post("/migrate")
async def migrate_legacy_assets(
    limit: int = Query(1000, ge=1, le=5000, description="Number of assets to migrate")
):
    """Migrate legacy assets to enhanced format."""
    try:
        logger.info("Starting legacy asset migration", limit=limit)
        
        # Perform bulk migration
        result = await enhanced_asset_db.bulk_migrate_legacy_assets(limit=limit)
        
        logger.info("Legacy asset migration completed", result=result)
        
        return {
            "message": "Legacy asset migration completed",
            "migrated_count": result["migrated"],
            "failed_count": result["failed"],
            "total_processed": result["migrated"] + result["failed"],
            "status": "completed"
        }
        
    except Exception as e:
        logger.error("Failed to migrate legacy assets", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to migrate legacy assets") 