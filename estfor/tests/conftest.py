"""
Pytest configuration and fixtures for comprehensive testing.
"""

import pytest
import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, patch

import httpx
from fastapi.testclient import TestClient
from google.cloud import firestore
from celery import Celery

from app.main import app
from app.config import settings
from app.database import init_firestore, db


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """Test settings with emulator configuration."""
    # Override settings for testing
    os.environ["ENVIRONMENT"] = "test"
    os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
    os.environ["ESTFOR_API_URL"] = "https://api.estfor.com"
    os.environ["ESTFOR_API_KEY"] = "test-api-key"
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    os.environ["CELERY_BROKER_URL"] = "redis://localhost:6379/1"
    os.environ["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/2"
    return settings


@pytest.fixture(scope="session")
async def firestore_client():
    """Firestore client for testing."""
    # Initialize Firestore emulator connection
    await init_firestore()
    yield db
    # Cleanup
    if db:
        # Clear test data
        collection_ref = db.collection(settings.FIRESTORE_COLLECTION)
        docs = collection_ref.stream()
        for doc in docs:
            doc.reference.delete()


@pytest.fixture
def test_client() -> Generator:
    """FastAPI test client."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_estfor_api():
    """Mock EstFor API responses."""
    mock_assets = [
        {
            "id": "asset_1",
            "name": "Test Sword",
            "type": "weapon",
            "rarity": "common",
            "description": "A basic test sword"
        },
        {
            "id": "asset_2", 
            "name": "Test Shield",
            "type": "armor",
            "rarity": "rare",
            "description": "A magical test shield"
        }
    ]
    
    with patch("app.services.estfor_client.EstForClient.get_assets") as mock_get_assets:
        mock_get_assets.return_value = mock_assets
        yield mock_get_assets


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for external API calls."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        yield mock_client


@pytest.fixture
def celery_app():
    """Celery app for testing."""
    test_celery = Celery(
        "test_estfor",
        broker="memory://",
        backend="rpc://"
    )
    test_celery.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    return test_celery


@pytest.fixture
def sample_asset_data():
    """Sample asset data for testing."""
    return {
        "name": "Test Asset",
        "type": "weapon",
        "rarity": "common",
        "description": "A test asset for unit testing"
    }


@pytest.fixture
def sample_asset_response():
    """Sample asset response data."""
    return {
        "id": "test_asset_id",
        "name": "Test Asset",
        "type": "weapon",
        "rarity": "common",
        "description": "A test asset for unit testing",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_prometheus_metrics():
    """Mock Prometheus metrics."""
    with patch("prometheus_client.Counter") as mock_counter, \
         patch("prometheus_client.Histogram") as mock_histogram:
        
        mock_counter.return_value.inc.return_value = None
        mock_histogram.return_value.observe.return_value = None
        
        yield {
            "counter": mock_counter,
            "histogram": mock_histogram
        }


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch("redis.Redis") as mock_redis_client:
        mock_redis_client.return_value.ping.return_value = True
        mock_redis_client.return_value.get.return_value = None
        mock_redis_client.return_value.set.return_value = True
        yield mock_redis_client


@pytest.fixture
def temp_dir():
    """Temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_logger():
    """Mock structured logger."""
    with patch("structlog.get_logger") as mock_logger:
        mock_logger.return_value.info.return_value = None
        mock_logger.return_value.error.return_value = None
        mock_logger.return_value.warning.return_value = None
        yield mock_logger


# Performance testing fixtures
@pytest.fixture
def performance_test_data():
    """Large dataset for performance testing."""
    return [
        {
            "id": f"asset_{i}",
            "name": f"Performance Test Asset {i}",
            "type": "weapon" if i % 2 == 0 else "armor",
            "rarity": "common" if i % 3 == 0 else "rare" if i % 3 == 1 else "epic",
            "description": f"Performance test asset number {i}"
        }
        for i in range(1000)
    ]


# Security testing fixtures
@pytest.fixture
def malicious_input_data():
    """Malicious input data for security testing."""
    return {
        "name": "<script>alert('xss')</script>",
        "type": "'; DROP TABLE assets; --",
        "rarity": "../../../etc/passwd",
        "description": "'; INSERT INTO users VALUES ('admin', 'password'); --"
    }


# Integration testing fixtures
@pytest.fixture
async def integration_test_client():
    """Integration test client with real database."""
    # Use real Firestore emulator
    await init_firestore()
    
    with TestClient(app) as client:
        yield client
    
    # Cleanup
    if db:
        collection_ref = db.collection(settings.FIRESTORE_COLLECTION)
        docs = collection_ref.stream()
        for doc in docs:
            doc.reference.delete()


# E2E testing fixtures
@pytest.fixture
def docker_compose_services():
    """Docker Compose services for E2E testing."""
    return {
        "app": {"port": 8000, "health_check": "/health"},
        "firestore": {"port": 8080, "health_check": "/"},
        "redis": {"port": 6379, "health_check": "ping"},
        "prometheus": {"port": 9090, "health_check": "/metrics"},
        "grafana": {"port": 3000, "health_check": "/api/health"}
    }


# Load testing fixtures
@pytest.fixture
def load_test_scenarios():
    """Load testing scenarios for K6."""
    return {
        "smoke": {"vus": 1, "duration": "30s"},
        "load": {"vus": 10, "duration": "2m"},
        "stress": {"vus": 50, "duration": "5m"},
        "spike": {"vus": 100, "duration": "1m"},
        "breakpoint": {"vus": 200, "duration": "10m"}
    } 