"""
Enhanced database operations for EstFor assets with game metadata.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import structlog
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError, DuplicateKeyError
from bson import ObjectId

from app.database.base import get_collection
from app.models.enhanced_asset import (
    EstForAsset,
    AssetFilter,
    AssetStatsSummary,
    AssetCategory,
    RarityTier,
)
from app.game_constants import EquipPosition, BoostType
from app.services.asset_enrichment import asset_enrichment_service

logger = structlog.get_logger()


class EnhancedAssetDatabase:
    """Enhanced database operations for EstFor assets."""
    
    def __init__(self):
        """Initialize enhanced database operations."""
        self.collection_name = "enhanced_assets"
    
    def get_enhanced_collection(self) -> AsyncIOMotorCollection:
        """Get the enhanced assets collection."""
        # For now, use the same collection but with enhanced schema
        return get_collection()
    
    async def create_indexes(self):
        """Create indexes for enhanced asset queries."""
        try:
            collection = self.get_enhanced_collection()
            
            # Create indexes for common query patterns
            indexes = [
                # Basic queries
                ("item_id", 1),
                ("category", 1),
                ("equip_position", 1),
                ("rarity_tier", 1),
                
                # Skill requirements
                ("skill_requirements", 1),
                
                # Composite indexes for filtering
                [("category", 1), ("rarity_tier", 1)],
                [("equip_position", 1), ("skill_requirements", 1)],
                [("category", 1), ("equip_position", 1)],
                
                # Search and sorting
                [("name", "text"), ("description", "text")],
                ("created_at", -1),
                ("updated_at", -1),
            ]
            
            for index in indexes:
                try:
                    await collection.create_index(index)
                except Exception as e:
                    logger.warning("Failed to create index", index=index, error=str(e))
            
            logger.info("Enhanced asset indexes created successfully")
            
        except Exception as e:
            logger.error("Failed to create enhanced asset indexes", error=str(e))
            raise
    
    async def store_enhanced_asset(self, asset: EstForAsset) -> str:
        """Store an enhanced asset in the database."""
        try:
            collection = self.get_enhanced_collection()
            
            # Convert asset to dictionary
            asset_data = asset.dict()
            
            # Handle datetime serialization
            asset_data["created_at"] = asset.created_at
            asset_data["updated_at"] = asset.updated_at
            
            # Convert enums to values
            if asset.category:
                asset_data["category"] = asset.category.value
            if asset.equip_position:
                asset_data["equip_position"] = asset.equip_position.value
            if asset.rarity_tier:
                asset_data["rarity_tier"] = asset.rarity_tier.value
            
            # Convert boost effects
            asset_data["boost_effects"] = [
                {
                    "boost_type": boost.boost_type.value,
                    "value": boost.value,
                    "duration": boost.duration
                }
                for boost in asset.boost_effects
            ]
            
            # Use item_id as unique identifier if available
            if asset.item_id:
                # Try to update existing asset with same item_id
                result = await collection.replace_one(
                    {"item_id": asset.item_id},
                    asset_data,
                    upsert=True
                )
                
                if result.upserted_id:
                    asset_id = str(result.upserted_id)
                    logger.info("New enhanced asset stored", item_id=asset.item_id, asset_id=asset_id)
                else:
                    asset_id = asset.id
                    logger.info("Enhanced asset updated", item_id=asset.item_id, asset_id=asset_id)
            else:
                # Insert new asset without item_id
                result = await collection.insert_one(asset_data)
                asset_id = str(result.inserted_id)
                logger.info("Enhanced asset stored without item_id", asset_id=asset_id)
            
            return asset_id
            
        except PyMongoError as e:
            logger.error("Failed to store enhanced asset", error=str(e), asset=asset.name)
            raise
    
    async def get_enhanced_asset(self, asset_id: str) -> Optional[EstForAsset]:
        """Get an enhanced asset by ID."""
        try:
            collection = self.get_enhanced_collection()
            
            # Try ObjectId first, then string ID
            query = {}
            if ObjectId.is_valid(asset_id):
                query["_id"] = ObjectId(asset_id)
            else:
                query["$or"] = [
                    {"id": asset_id},
                    {"asset_id": asset_id},
                    {"item_id": int(asset_id) if asset_id.isdigit() else None}
                ]
            
            doc = await collection.find_one(query)
            
            if doc:
                return self._document_to_asset(doc)
            return None
            
        except Exception as e:
            logger.error("Failed to get enhanced asset", error=str(e), asset_id=asset_id)
            return None
    
    async def list_enhanced_assets(
        self, 
        asset_filter: Optional[AssetFilter] = None,
        limit: int = 100, 
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> List[EstForAsset]:
        """List enhanced assets with filtering and pagination."""
        try:
            collection = self.get_enhanced_collection()
            
            # Build query from filter
            query = asset_filter.build_query() if asset_filter else {}
            
            # Create cursor with sorting and pagination
            cursor = collection.find(query).sort(sort_by, sort_order).skip(offset).limit(limit)
            
            assets = []
            async for doc in cursor:
                asset = self._document_to_asset(doc)
                if asset:
                    assets.append(asset)
            
            logger.info("Enhanced assets listed", 
                       count=len(assets), 
                       limit=limit, 
                       offset=offset, 
                       filter_applied=asset_filter is not None)
            
            return assets
            
        except Exception as e:
            logger.error("Failed to list enhanced assets", error=str(e))
            return []
    
    async def search_enhanced_assets(
        self,
        search_query: str,
        asset_filter: Optional[AssetFilter] = None,
        limit: int = 50
    ) -> List[EstForAsset]:
        """Search enhanced assets by text."""
        try:
            collection = self.get_enhanced_collection()
            
            # Build base query from filter
            query = asset_filter.build_query() if asset_filter else {}
            
            # Add text search
            query["$text"] = {"$search": search_query}
            
            # Search with text score sorting
            cursor = collection.find(
                query,
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)
            
            assets = []
            async for doc in cursor:
                asset = self._document_to_asset(doc)
                if asset:
                    assets.append(asset)
            
            logger.info("Enhanced assets searched", 
                       query=search_query, 
                       results=len(assets))
            
            return assets
            
        except Exception as e:
            logger.error("Failed to search enhanced assets", error=str(e), query=search_query)
            return []
    
    async def get_assets_by_category(self, category: AssetCategory, limit: int = 100) -> List[EstForAsset]:
        """Get assets by category."""
        asset_filter = AssetFilter(category=category)
        return await self.list_enhanced_assets(asset_filter=asset_filter, limit=limit)
    
    async def get_assets_by_equip_position(self, position: EquipPosition, limit: int = 100) -> List[EstForAsset]:
        """Get assets by equipment position."""
        asset_filter = AssetFilter(equip_position=position)
        return await self.list_enhanced_assets(asset_filter=asset_filter, limit=limit)
    
    async def get_assets_by_skill(self, skill_name: str, max_level: Optional[int] = None, limit: int = 100) -> List[EstForAsset]:
        """Get assets that require a specific skill."""
        asset_filter = AssetFilter(required_skill=skill_name, max_skill_level=max_level)
        return await self.list_enhanced_assets(asset_filter=asset_filter, limit=limit)
    
    async def get_tradeable_assets(self, limit: int = 100) -> List[EstForAsset]:
        """Get all tradeable assets."""
        asset_filter = AssetFilter(tradeable_only=True)
        return await self.list_enhanced_assets(asset_filter=asset_filter, limit=limit)
    
    async def get_equipment_assets(self, limit: int = 100) -> List[EstForAsset]:
        """Get all equipable assets."""
        asset_filter = AssetFilter(equipment_only=True)
        return await self.list_enhanced_assets(asset_filter=asset_filter, limit=limit)
    
    async def get_consumable_assets(self, limit: int = 100) -> List[EstForAsset]:
        """Get all consumable assets."""
        asset_filter = AssetFilter(consumable_only=True)
        return await self.list_enhanced_assets(asset_filter=asset_filter, limit=limit)
    
    async def get_assets_with_boosts(self, boost_type: Optional[BoostType] = None, limit: int = 100) -> List[EstForAsset]:
        """Get assets that have boost effects."""
        asset_filter = AssetFilter(has_boost=boost_type)
        return await self.list_enhanced_assets(asset_filter=asset_filter, limit=limit)
    
    async def get_asset_stats(self) -> AssetStatsSummary:
        """Get comprehensive asset statistics."""
        try:
            collection = self.get_enhanced_collection()
            
            # Count total assets
            total_assets = await collection.count_documents({})
            
            # Count by category
            category_pipeline = [
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            category_counts = {}
            async for doc in collection.aggregate(category_pipeline):
                category_counts[doc["_id"]] = doc["count"]
            
            # Count by rarity
            rarity_pipeline = [
                {"$group": {"_id": "$rarity_tier", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
            rarity_counts = {}
            async for doc in collection.aggregate(rarity_pipeline):
                rarity_counts[str(doc["_id"])] = doc["count"]
            
            # Count by equipment position
            equip_pipeline = [
                {"$match": {"equip_position": {"$ne": None}}},
                {"$group": {"_id": "$equip_position", "count": {"$sum": 1}}}
            ]
            equip_counts = {}
            async for doc in collection.aggregate(equip_pipeline):
                equip_counts[str(doc["_id"])] = doc["count"]
            
            # Special counts
            equipment_count = await collection.count_documents({"equip_position": {"$ne": None}})
            consumable_count = await collection.count_documents({
                "category": {"$in": ["consumable", "food", "boost_vial"]}
            })
            material_count = await collection.count_documents({
                "category": {"$in": ["material", "log", "ore", "seed"]}
            })
            with_boosts = await collection.count_documents({"boost_effects.0": {"$exists": True}})
            tradeable_count = await collection.count_documents({"tradeable": True})
            
            return AssetStatsSummary(
                total_assets=total_assets,
                by_category=category_counts,
                by_rarity=rarity_counts,
                by_equip_position=equip_counts,
                equipment_count=equipment_count,
                consumable_count=consumable_count,
                material_count=material_count,
                with_boosts=with_boosts,
                tradeable_count=tradeable_count,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Failed to get asset stats", error=str(e))
            # Return empty stats on error
            return AssetStatsSummary(total_assets=0)
    
    async def migrate_legacy_asset(self, legacy_asset: Dict[str, Any]) -> Optional[EstForAsset]:
        """Migrate a legacy asset to enhanced format."""
        try:
            # Use enrichment service to enhance legacy data
            enhanced_asset = asset_enrichment_service.enrich_asset(legacy_asset)
            
            # Store the enhanced asset
            await self.store_enhanced_asset(enhanced_asset)
            
            logger.info("Legacy asset migrated", 
                       asset_id=enhanced_asset.id, 
                       category=enhanced_asset.category.value)
            
            return enhanced_asset
            
        except Exception as e:
            logger.error("Failed to migrate legacy asset", error=str(e), asset=legacy_asset.get("name"))
            return None
    
    async def bulk_migrate_legacy_assets(self, limit: int = 1000) -> Dict[str, int]:
        """Migrate legacy assets in bulk."""
        try:
            collection = self.get_enhanced_collection()
            
            # Find assets that don't have enhanced fields
            query = {
                "$or": [
                    {"category": {"$exists": False}},
                    {"equip_position": {"$exists": False}},
                    {"skill_requirements": {"$exists": False}}
                ]
            }
            
            cursor = collection.find(query).limit(limit)
            
            migrated = 0
            failed = 0
            
            async for doc in cursor:
                try:
                    enhanced_asset = await self.migrate_legacy_asset(doc)
                    if enhanced_asset:
                        migrated += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.error("Failed to migrate individual asset", error=str(e), asset_id=doc.get("_id"))
                    failed += 1
            
            logger.info("Bulk migration completed", migrated=migrated, failed=failed)
            
            return {"migrated": migrated, "failed": failed}
            
        except Exception as e:
            logger.error("Failed to bulk migrate legacy assets", error=str(e))
            return {"migrated": 0, "failed": 0}
    
    def _document_to_asset(self, doc: Dict[str, Any]) -> Optional[EstForAsset]:
        """Convert MongoDB document to EstForAsset."""
        try:
            # Set document ID
            doc["id"] = str(doc.get("_id", doc.get("id", "")))
            
            # Handle enum conversions
            if "category" in doc and isinstance(doc["category"], str):
                try:
                    doc["category"] = AssetCategory(doc["category"])
                except ValueError:
                    doc["category"] = AssetCategory.UNKNOWN
            
            if "equip_position" in doc and isinstance(doc["equip_position"], int):
                try:
                    doc["equip_position"] = EquipPosition(doc["equip_position"])
                except ValueError:
                    doc["equip_position"] = None
            
            if "rarity_tier" in doc and isinstance(doc["rarity_tier"], int):
                try:
                    doc["rarity_tier"] = RarityTier(doc["rarity_tier"])
                except ValueError:
                    doc["rarity_tier"] = RarityTier.COMMON
            
            # Handle boost effects
            if "boost_effects" in doc and isinstance(doc["boost_effects"], list):
                boost_effects = []
                for boost_data in doc["boost_effects"]:
                    if isinstance(boost_data, dict):
                        try:
                            boost_type = BoostType(boost_data["boost_type"])
                            boost_effects.append({
                                "boost_type": boost_type,
                                "value": boost_data.get("value", 0),
                                "duration": boost_data.get("duration")
                            })
                        except (ValueError, KeyError):
                            pass
                doc["boost_effects"] = boost_effects
            
            # Remove MongoDB-specific fields
            doc.pop("_id", None)
            
            return EstForAsset(**doc)
            
        except Exception as e:
            logger.error("Failed to convert document to asset", error=str(e), doc_id=doc.get("_id"))
            return None


# Global database instance
enhanced_asset_db = EnhancedAssetDatabase()