"""
Test configuration and fixtures for EstFor Asset Collection System.
"""

import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import structlog

from app.config import settings
from app.database import init_mongodb, close_mongodb, get_collection

# Configure test logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Test database configuration
TEST_DATABASE = "estfor_test"
TEST_COLLECTION = "all_assets_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def mongodb_client():
    """MongoDB client for testing."""
    # Override settings for testing
    original_uri = settings.MONGODB_URI
    original_db = settings.MONGODB_DATABASE
    original_collection = settings.MONGODB_COLLECTION
    
    # Use test database
    test_uri = original_uri.replace("/estfor?", "/estfor_test?")
    settings.MONGODB_URI = test_uri
    settings.MONGODB_DATABASE = TEST_DATABASE
    settings.MONGODB_COLLECTION = TEST_COLLECTION
    
    # Initialize MongoDB connection
    await init_mongodb()
    
    yield
    
    # Cleanup
    await close_mongodb()
    
    # Restore original settings
    settings.MONGODB_URI = original_uri
    settings.MONGODB_DATABASE = original_db
    settings.MONGODB_COLLECTION = original_collection


@pytest.fixture
async def clean_database(mongodb_client):
    """Clean the test database before each test."""
    collection_ref = get_collection()
    
    # Clear all documents
    await collection_ref.delete_many({})
    
    yield
    
    # Clean up after test
    await collection_ref.delete_many({})


@pytest.fixture
def sample_asset_data():
    """Sample asset data for testing."""
    return {
        "asset_id": "test_asset_001",
        "name": "Test Weapon",
        "type": "weapon",
        "description": "A test weapon for unit testing",
        "metadata": {
            "rarity": "rare",
            "level": 5,
            "damage": 100
        }
    }


@pytest.fixture
def multiple_assets_data():
    """Multiple sample assets for testing."""
    return [
        {
            "asset_id": "test_asset_001",
            "name": "Test Weapon 1",
            "type": "weapon",
            "description": "First test weapon",
            "metadata": {"rarity": "common", "level": 1}
        },
        {
            "asset_id": "test_asset_002",
            "name": "Test Armor 1",
            "type": "armor",
            "description": "First test armor",
            "metadata": {"rarity": "uncommon", "level": 2}
        },
        {
            "asset_id": "test_asset_003",
            "name": "Test Potion 1",
            "type": "consumable",
            "description": "First test potion",
            "metadata": {"rarity": "common", "level": 1}
        }
    ]


@pytest.fixture
async def populated_database(clean_database, multiple_assets_data):
    """Database populated with test assets."""
    collection_ref = get_collection()
    
    # Insert test assets
    for asset_data in multiple_assets_data:
        await collection_ref.insert_one(asset_data)
    
    return multiple_assets_data


@pytest.fixture
def integration_test_client():
    """Integration test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def performance_test_data():
    """Large dataset for performance testing."""
    assets = []
    for i in range(100):
        assets.append({
            "asset_id": f"perf_asset_{i:03d}",
            "name": f"Performance Asset {i}",
            "type": "weapon" if i % 3 == 0 else "armor" if i % 3 == 1 else "consumable",
            "description": f"Performance test asset number {i}",
            "metadata": {
                "rarity": ["common", "uncommon", "rare", "epic"][i % 4],
                "level": (i % 20) + 1,
                "value": i * 100
            }
        })
    return assets


# Service health check configuration for integration tests
SERVICE_HEALTH_CHECKS = {
    "app": {"port": 8000, "health_check": "/health"},
    "worker": {"port": 8000, "health_check": "/health"},
    "mongodb": {"port": 27017, "health_check": "ping"},
    "redis": {"port": 6379, "health_check": "ping"},
    "prometheus": {"port": 9090, "health_check": "/-/healthy"},
    "grafana": {"port": 3000, "health_check": "/api/health"},
}


@pytest.fixture(scope="session")
def docker_services():
    """Docker services for integration testing."""
    import subprocess
    import time
    
    # Start services
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    
    # Wait for services to be ready
    time.sleep(30)
    
    yield
    
    # Stop services
    subprocess.run(["docker-compose", "down"], check=True)


@pytest.fixture
async def mongodb_connection_test(mongodb_client):
    """Test MongoDB connection and basic operations."""
    collection_ref = get_collection()
    
    # Test basic operations
    test_doc = {"test": "connection", "timestamp": "now"}
    result = await collection_ref.insert_one(test_doc)
    assert result.inserted_id
    
    # Verify document was inserted
    doc = await collection_ref.find_one({"_id": result.inserted_id})
    assert doc is not None
    assert doc["test"] == "connection"
    
    # Clean up
    await collection_ref.delete_one({"_id": result.inserted_id})
    
    return True 