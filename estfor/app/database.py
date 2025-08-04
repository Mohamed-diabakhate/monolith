"""
Database configuration and operations for Firestore.
"""

import os
from typing import Optional, Dict, Any, List
import structlog

from google.cloud import firestore
from google.auth import default

from app.config import settings

logger = structlog.get_logger()

# Global Firestore client
db: Optional[firestore.Client] = None


async def init_firestore() -> None:
    """Initialize Firestore client."""
    global db
    
    try:
        # Check if we're using the emulator
        if settings.ENVIRONMENT in ["development", "test"]:
            os.environ["FIRESTORE_EMULATOR_HOST"] = f"{settings.FIRESTORE_EMULATOR_HOST}:{settings.FIRESTORE_EMULATOR_PORT}"
            logger.info("Using Firestore emulator", host=settings.FIRESTORE_EMULATOR_HOST)
        
        # Initialize Firestore client
        db = firestore.Client(project=settings.FIRESTORE_PROJECT_ID)
        
        # Test connection
        await test_connection()
        
        logger.info("Firestore initialized successfully", project=settings.FIRESTORE_PROJECT_ID)
        
    except Exception as e:
        logger.error("Failed to initialize Firestore", error=str(e))
        raise


async def test_connection() -> bool:
    """Test Firestore connection."""
    if not db:
        raise RuntimeError("Firestore not initialized")
    
    try:
        # Simple test query
        collection_ref = db.collection(settings.FIRESTORE_COLLECTION)
        docs = collection_ref.limit(1).stream()
        list(docs)  # Force execution
        return True
    except Exception as e:
        logger.error("Firestore connection test failed", error=str(e))
        return False


def get_collection() -> firestore.CollectionReference:
    """Get the assets collection reference."""
    if not db:
        raise RuntimeError("Firestore not initialized")
    
    return db.collection(settings.FIRESTORE_COLLECTION)


async def store_asset(asset_data: Dict[str, Any]) -> str:
    """Store an asset in Firestore."""
    try:
        collection_ref = get_collection()
        
        # Add timestamp
        asset_data["created_at"] = firestore.SERVER_TIMESTAMP
        asset_data["updated_at"] = firestore.SERVER_TIMESTAMP
        
        # Store document
        doc_ref = collection_ref.add(asset_data)[1]
        
        logger.info("Asset stored successfully", asset_id=doc_ref.id)
        return doc_ref.id
        
    except Exception as e:
        logger.error("Failed to store asset", error=str(e), asset_data=asset_data)
        raise


async def get_asset(asset_id: str) -> Optional[Dict[str, Any]]:
    """Get an asset by ID."""
    try:
        collection_ref = get_collection()
        doc_ref = collection_ref.document(asset_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return {"id": doc.id, **doc.to_dict()}
        return None
        
    except Exception as e:
        logger.error("Failed to get asset", error=str(e), asset_id=asset_id)
        raise


async def list_assets(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """List assets with pagination."""
    try:
        collection_ref = get_collection()
        query = collection_ref.order_by("created_at", direction=firestore.Query.DESCENDING)
        
        if offset > 0:
            query = query.offset(offset)
        
        docs = query.limit(limit).stream()
        
        assets = []
        for doc in docs:
            assets.append({"id": doc.id, **doc.to_dict()})
        
        return assets
        
    except Exception as e:
        logger.error("Failed to list assets", error=str(e))
        raise


async def update_asset(asset_id: str, asset_data: Dict[str, Any]) -> bool:
    """Update an asset."""
    try:
        collection_ref = get_collection()
        doc_ref = collection_ref.document(asset_id)
        
        # Add update timestamp
        asset_data["updated_at"] = firestore.SERVER_TIMESTAMP
        
        doc_ref.update(asset_data)
        
        logger.info("Asset updated successfully", asset_id=asset_id)
        return True
        
    except Exception as e:
        logger.error("Failed to update asset", error=str(e), asset_id=asset_id)
        raise


async def delete_asset(asset_id: str) -> bool:
    """Delete an asset."""
    try:
        collection_ref = get_collection()
        doc_ref = collection_ref.document(asset_id)
        doc_ref.delete()
        
        logger.info("Asset deleted successfully", asset_id=asset_id)
        return True
        
    except Exception as e:
        logger.error("Failed to delete asset", error=str(e), asset_id=asset_id)
        raise


async def get_asset_count() -> int:
    """Get total number of assets."""
    try:
        collection_ref = get_collection()
        docs = collection_ref.stream()
        return len(list(docs))
        
    except Exception as e:
        logger.error("Failed to get asset count", error=str(e))
        raise 