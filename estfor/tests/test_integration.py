"""
Integration tests for EstFor Asset Collection System.

Tests service-to-service communication and real database operations.
"""

import pytest
import asyncio
from unittest.mock import patch, Mock
import httpx

from app.main import app
from app.database import init_firestore, store_asset, get_asset, list_assets
from app.services.estfor_client import EstForClient


class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_endpoints_integration(self, integration_test_client):
        """Test health endpoints with real application."""
        # Test basic health check
        response = integration_test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        
        # Test readiness check
        response = integration_test_client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        
        # Test liveness check
        response = integration_test_client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        
        # Test detailed health check
        response = integration_test_client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "components" in data
        assert "database" in data["components"]
    
    @pytest.mark.asyncio
    async def test_assets_crud_integration(self, integration_test_client, firestore_client):
        """Test complete CRUD operations for assets."""
        # Create asset
        asset_data = {
            "name": "Integration Test Asset",
            "type": "weapon",
            "rarity": "common",
            "description": "Asset created during integration test"
        }
        
        response = integration_test_client.post("/assets/", json=asset_data)
        assert response.status_code == 200
        created_asset = response.json()
        assert created_asset["name"] == asset_data["name"]
        assert created_asset["type"] == asset_data["type"]
        asset_id = created_asset["id"]
        
        # Read asset
        response = integration_test_client.get(f"/assets/{asset_id}")
        assert response.status_code == 200
        retrieved_asset = response.json()
        assert retrieved_asset["id"] == asset_id
        assert retrieved_asset["name"] == asset_data["name"]
        
        # Update asset
        update_data = {
            "name": "Updated Integration Test Asset",
            "type": "armor",
            "rarity": "rare",
            "description": "Updated asset description"
        }
        
        response = integration_test_client.put(f"/assets/{asset_id}", json=update_data)
        assert response.status_code == 200
        updated_asset = response.json()
        assert updated_asset["name"] == update_data["name"]
        assert updated_asset["type"] == update_data["type"]
        
        # List assets
        response = integration_test_client.get("/assets/")
        assert response.status_code == 200
        assets_list = response.json()
        assert isinstance(assets_list, list)
        assert len(assets_list) > 0
        
        # Delete asset
        response = integration_test_client.delete(f"/assets/{asset_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Asset deleted successfully"
        
        # Verify deletion
        response = integration_test_client.get(f"/assets/{asset_id}")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_asset_collection_integration(self, integration_test_client):
        """Test asset collection endpoint integration."""
        with patch('app.tasks.collect_assets_task') as mock_task:
            mock_task.delay.return_value = Mock(id="test_task_id")
            
            response = integration_test_client.post("/assets/collect")
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Asset collection started"
            assert data["task_id"] == "test_task_id"
            assert data["status"] == "queued"
    
    @pytest.mark.asyncio
    async def test_asset_stats_integration(self, integration_test_client, firestore_client):
        """Test asset statistics endpoint integration."""
        # Create some test assets first
        test_assets = [
            {"name": "Test Asset 1", "type": "weapon", "rarity": "common"},
            {"name": "Test Asset 2", "type": "armor", "rarity": "rare"},
            {"name": "Test Asset 3", "type": "consumable", "rarity": "epic"}
        ]
        
        for asset_data in test_assets:
            await store_asset(asset_data)
        
        # Test stats endpoint
        response = integration_test_client.get("/assets/stats/summary")
        assert response.status_code == 200
        stats = response.json()
        assert "total_assets" in stats
        assert "collection_status" in stats
        assert stats["total_assets"] >= 3  # At least our test assets


class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    @pytest.mark.asyncio
    async def test_firestore_connection_integration(self, firestore_client):
        """Test real Firestore connection and operations."""
        # Test connection
        connection_healthy = await init_firestore()
        assert connection_healthy is None  # init_firestore doesn't return anything on success
        
        # Test storing and retrieving data
        test_asset = {
            "name": "Database Integration Test Asset",
            "type": "weapon",
            "rarity": "legendary",
            "description": "Asset for database integration testing"
        }
        
        # Store asset
        asset_id = await store_asset(test_asset)
        assert asset_id is not None
        assert isinstance(asset_id, str)
        
        # Retrieve asset
        retrieved_asset = await get_asset(asset_id)
        assert retrieved_asset is not None
        assert retrieved_asset["name"] == test_asset["name"]
        assert retrieved_asset["type"] == test_asset["type"]
        assert retrieved_asset["id"] == asset_id
        
        # List assets
        assets_list = await list_assets(limit=10)
        assert isinstance(assets_list, list)
        assert len(assets_list) > 0
        
        # Verify our test asset is in the list
        asset_ids = [asset["id"] for asset in assets_list]
        assert asset_id in asset_ids
    
    @pytest.mark.asyncio
    async def test_bulk_operations_integration(self, firestore_client):
        """Test bulk database operations."""
        # Create multiple assets
        test_assets = []
        for i in range(10):
            asset_data = {
                "name": f"Bulk Test Asset {i}",
                "type": "weapon" if i % 2 == 0 else "armor",
                "rarity": "common" if i % 3 == 0 else "rare" if i % 3 == 1 else "epic",
                "description": f"Bulk test asset number {i}"
            }
            test_assets.append(asset_data)
        
        # Store all assets
        stored_ids = []
        for asset_data in test_assets:
            asset_id = await store_asset(asset_data)
            stored_ids.append(asset_id)
        
        assert len(stored_ids) == 10
        assert all(isinstance(asset_id, str) for asset_id in stored_ids)
        
        # Retrieve all assets
        retrieved_assets = await list_assets(limit=20)
        assert len(retrieved_assets) >= 10
        
        # Verify all our test assets are present
        retrieved_names = [asset["name"] for asset in retrieved_assets]
        for asset_data in test_assets:
            assert asset_data["name"] in retrieved_names


class TestEstForAPIIntegration:
    """Integration tests for EstFor API client."""
    
    @pytest.mark.asyncio
    async def test_estfor_client_integration(self):
        """Test EstFor API client with real HTTP calls."""
        client = EstForClient()
        
        # Test with mock responses since we can't call real API in tests
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = [
                {
                    "id": "estfor_asset_1",
                    "name": "EstFor Test Sword",
                    "type": "weapon",
                    "rarity": "common",
                    "description": "Test asset from EstFor API"
                }
            ]
            mock_response.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Test get_assets
            assets = await client.get_assets(limit=10, offset=0)
            assert len(assets) == 1
            assert assets[0]["id"] == "estfor_asset_1"
            assert assets[0]["name"] == "EstFor Test Sword"
            
            # Test get_asset_by_id
            mock_response.json.return_value = {
                "id": "estfor_asset_1",
                "name": "EstFor Test Sword",
                "type": "weapon",
                "rarity": "common"
            }
            
            asset = await client.get_asset_by_id("estfor_asset_1")
            assert asset["id"] == "estfor_asset_1"
            assert asset["name"] == "EstFor Test Sword"
    
    @pytest.mark.asyncio
    async def test_estfor_error_handling_integration(self):
        """Test EstFor API error handling."""
        client = EstForClient()
        
        with patch('httpx.AsyncClient') as mock_client:
            # Test HTTP error
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=Mock(), response=Mock()
            )
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(httpx.HTTPStatusError):
                await client.get_assets()
            
            # Test network error
            mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.ConnectError(
                "Connection failed"
            )
            
            with pytest.raises(httpx.ConnectError):
                await client.get_assets()


class TestServiceCommunication:
    """Integration tests for service-to-service communication."""
    
    @pytest.mark.asyncio
    async def test_app_worker_communication(self, integration_test_client):
        """Test communication between app and worker services."""
        # Test that app can trigger worker tasks
        with patch('app.tasks.collect_assets_task') as mock_task:
            mock_task.delay.return_value = Mock(id="test_task_id")
            
            response = integration_test_client.post("/assets/collect")
            assert response.status_code == 200
            
            # Verify task was called
            mock_task.delay.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_database_app_communication(self, integration_test_client, firestore_client):
        """Test communication between app and database."""
        # Test that app can store and retrieve data through database
        asset_data = {
            "name": "Service Communication Test Asset",
            "type": "weapon",
            "rarity": "common"
        }
        
        # Store through API
        response = integration_test_client.post("/assets/", json=asset_data)
        assert response.status_code == 200
        created_asset = response.json()
        asset_id = created_asset["id"]
        
        # Retrieve through database directly
        retrieved_asset = await get_asset(asset_id)
        assert retrieved_asset is not None
        assert retrieved_asset["name"] == asset_data["name"]
        
        # Verify through API
        response = integration_test_client.get(f"/assets/{asset_id}")
        assert response.status_code == 200
        api_asset = response.json()
        assert api_asset["name"] == asset_data["name"]


class TestErrorHandlingIntegration:
    """Integration tests for error handling."""
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, integration_test_client):
        """Test database error handling in integration."""
        # Test with invalid asset ID
        response = integration_test_client.get("/assets/nonexistent_id")
        assert response.status_code == 404
        assert "Asset not found" in response.json()["detail"]
        
        # Test with invalid data
        invalid_asset = {
            "name": "",  # Empty name should be invalid
            "type": "invalid_type"
        }
        
        response = integration_test_client.post("/assets/", json=invalid_asset)
        # Should either return 422 (validation error) or 500 (server error)
        assert response.status_code in [422, 500]
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, integration_test_client):
        """Test API error handling."""
        # Test invalid endpoint
        response = integration_test_client.get("/nonexistent")
        assert response.status_code == 404
        
        # Test invalid method
        response = integration_test_client.post("/health")
        assert response.status_code == 405  # Method not allowed
        
        # Test malformed JSON
        response = integration_test_client.post(
            "/assets/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Unprocessable entity


class TestPerformanceIntegration:
    """Integration tests for performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_api_response_time_integration(self, integration_test_client):
        """Test API response times in integration."""
        import time
        
        # Test health endpoint response time
        start_time = time.time()
        response = integration_test_client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
        
        # Test assets endpoint response time
        start_time = time.time()
        response = integration_test_client.get("/assets/")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 2.0  # Should respond within 2 seconds
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_integration(self, integration_test_client):
        """Test handling of concurrent requests."""
        import asyncio
        import httpx
        
        async def make_request():
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/health")
                return response.status_code
        
        # Make multiple concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(status_code == 200 for status_code in results) 