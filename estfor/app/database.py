"""
Database configuration and operations for MongoDB.
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import structlog
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError, DuplicateKeyError
from bson import ObjectId

from app.config import settings

logger = structlog.get_logger()

# Global MongoDB client
client: Optional[AsyncIOMotorClient] = None
db = None
collection = None


async def init_mongodb() -> None:
    """Initialize MongoDB client."""
    global client, db, collection
    
    try:
        # Initialize MongoDB client
        client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
            serverSelectionTimeoutMS=5000
        )
        
        # Get database and collection
        db = client[settings.MONGODB_DATABASE]
        collection = db[settings.MONGODB_COLLECTION]
        
        # Test connection
        await test_connection()
        
        logger.info("MongoDB initialized successfully", 
                   database=settings.MONGODB_DATABASE,
                   collection=settings.MONGODB_COLLECTION)
        
    except Exception as e:
        logger.error("Failed to initialize MongoDB", error=str(e))
        raise


async def test_connection() -> bool:
    """Test MongoDB connection."""
    if not client:
        raise RuntimeError("MongoDB not initialized")
    
    try:
        # Simple test query
        await client.admin.command('ping')
        return True
    except Exception as e:
        logger.error("MongoDB connection test failed", error=str(e))
        return False


def get_collection():
    """Get the assets collection reference."""
    if collection is None:
        raise RuntimeError("MongoDB not initialized")
    
    return collection


async def store_asset(asset_data: Dict[str, Any]) -> str:
    """Store an asset in MongoDB."""
    try:
        collection_ref = get_collection()
        
        # Transform API data to match database schema
        # API returns 'id' but database expects 'asset_id'
        if 'id' in asset_data and 'asset_id' not in asset_data:
            asset_data['asset_id'] = asset_data['id']
        
        # Add timestamps
        asset_data["created_at"] = datetime.utcnow()
        asset_data["updated_at"] = datetime.utcnow()
        
        # Store document
        result = await collection_ref.insert_one(asset_data)
        
        logger.info("Asset stored successfully", asset_id=str(result.inserted_id))
        return str(result.inserted_id)
        
    except DuplicateKeyError as e:
        logger.error("Duplicate asset key", error=str(e), asset_data=asset_data)
        raise
    except PyMongoError as e:
        logger.error("Failed to store asset", error=str(e), asset_data=asset_data)
        raise


async def get_asset(asset_id: str) -> Optional[Dict[str, Any]]:
    """Get an asset by ID."""
    try:
        collection_ref = get_collection()
        
        # Validate ObjectId format
        if not ObjectId.is_valid(asset_id):
            logger.warning("Invalid ObjectId format", asset_id=asset_id)
            return None
        
        doc = await collection_ref.find_one({"_id": ObjectId(asset_id)})
        
        if doc:
            # Convert ObjectId to string for JSON serialization
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            return doc
        return None
        
    except PyMongoError as e:
        logger.error("Failed to get asset", error=str(e), asset_id=asset_id)
        raise


async def list_assets(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """List assets with pagination."""
    try:
        collection_ref = get_collection()
        
        # Use skip and limit for pagination
        cursor = collection_ref.find().sort("created_at", -1).skip(offset).limit(limit)
        
        assets = []
        async for doc in cursor:
            # Convert ObjectId to string for JSON serialization
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            assets.append(doc)
        
        return assets
        
    except PyMongoError as e:
        logger.error("Failed to list assets", error=str(e))
        raise


async def update_asset(asset_id: str, asset_data: Dict[str, Any]) -> bool:
    """Update an asset."""
    try:
        collection_ref = get_collection()
        
        # Validate ObjectId format
        if not ObjectId.is_valid(asset_id):
            logger.warning("Invalid ObjectId format", asset_id=asset_id)
            return False
        
        # Add update timestamp
        asset_data["updated_at"] = datetime.utcnow()
        
        result = await collection_ref.update_one(
            {"_id": ObjectId(asset_id)},
            {"$set": asset_data}
        )
        
        if result.matched_count > 0:
            logger.info("Asset updated successfully", asset_id=asset_id)
            return True
        else:
            logger.warning("Asset not found for update", asset_id=asset_id)
            return False
        
    except PyMongoError as e:
        logger.error("Failed to update asset", error=str(e), asset_id=asset_id)
        raise


async def delete_asset(asset_id: str) -> bool:
    """Delete an asset."""
    try:
        collection_ref = get_collection()
        
        # Validate ObjectId format
        if not ObjectId.is_valid(asset_id):
            logger.warning("Invalid ObjectId format", asset_id=asset_id)
            return False
        
        result = await collection_ref.delete_one({"_id": ObjectId(asset_id)})
        
        if result.deleted_count > 0:
            logger.info("Asset deleted successfully", asset_id=asset_id)
            return True
        else:
            logger.warning("Asset not found for deletion", asset_id=asset_id)
            return False
        
    except PyMongoError as e:
        logger.error("Failed to delete asset", error=str(e), asset_id=asset_id)
        raise


async def get_asset_count() -> int:
    """Get total number of assets."""
    try:
        collection_ref = get_collection()
        count = await collection_ref.count_documents({})
        return count
        
    except PyMongoError as e:
        logger.error("Failed to get asset count", error=str(e))
        raise


async def close_mongodb() -> None:
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed") 