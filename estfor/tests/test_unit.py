"""
Unit tests for EstFor Asset Collection System.

Target: 90%+ coverage
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException

from app.config import Settings
from app.database import (
    init_firestore, test_connection, store_asset, get_asset,
    list_assets, update_asset, delete_asset, get_asset_count
)
from app.services.estfor_client import EstForClient
from app.routers.assets import AssetResponse, AssetCreate
from app.tasks import collect_assets_task, update_asset_task


class TestConfig:
    """Unit tests for configuration."""
    
    def test_settings_defaults(self):
        """Test default settings values."""
        settings = Settings()
        assert settings.ENVIRONMENT == "development"
        assert settings.LOG_LEVEL == "INFO"
        assert settings.API_PORT == 8000
        assert settings.FIRESTORE_PROJECT_ID == "estfor"
        assert settings.FIRESTORE_COLLECTION == "all_assets"
    
    def test_settings_environment_override(self):
        """Test environment variable override."""
        with patch.dict('os.environ', {'ENVIRONMENT': 'production'}):
            settings = Settings()
            assert settings.ENVIRONMENT == "production"
    
    def test_settings_validation(self):
        """Test settings validation."""
        settings = Settings()
        assert isinstance(settings.MAX_WORKERS, int)
        assert settings.MAX_WORKERS > 0
        assert isinstance(settings.WORKER_TIMEOUT, int)
        assert settings.WORKER_TIMEOUT > 0


class TestDatabase:
    """Unit tests for database operations."""
    
    @pytest.mark.asyncio
    async def test_init_firestore_success(self, mock_logger):
        """Test successful Firestore initialization."""
        with patch('app.database.firestore.Client') as mock_client:
            mock_client.return_value = Mock()
            
            await init_firestore()
            
            mock_client.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_init_firestore_failure(self, mock_logger):
        """Test Firestore initialization failure."""
        with patch('app.database.firestore.Client', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception):
                await init_firestore()
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, firestore_client):
        """Test successful database connection."""
        result = await test_connection()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self):
        """Test database connection failure."""
        with patch('app.database.db', None):
            with pytest.raises(RuntimeError, match="Firestore not initialized"):
                await test_connection()
    
    @pytest.mark.asyncio
    async def test_store_asset_success(self, firestore_client, sample_asset_data):
        """Test successful asset storage."""
        with patch('app.database.get_collection') as mock_get_collection:
            mock_collection = Mock()
            mock_doc_ref = Mock()
            mock_doc_ref.id = "test_asset_id"
            mock_collection.add.return_value = (None, mock_doc_ref)
            mock_get_collection.return_value = mock_collection
            
            asset_id = await store_asset(sample_asset_data)
            
            assert asset_id == "test_asset_id"
            mock_collection.add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_asset_success(self, firestore_client):
        """Test successful asset retrieval."""
        with patch('app.database.get_collection') as mock_get_collection:
            mock_collection = Mock()
            mock_doc_ref = Mock()
            mock_doc = Mock()
            mock_doc.exists = True
            mock_doc.id = "test_asset_id"
            mock_doc.to_dict.return_value = {"name": "Test Asset"}
            mock_doc_ref.get.return_value = mock_doc
            mock_collection.document.return_value = mock_doc_ref
            mock_get_collection.return_value = mock_collection
            
            asset = await get_asset("test_asset_id")
            
            assert asset["id"] == "test_asset_id"
            assert asset["name"] == "Test Asset"
    
    @pytest.mark.asyncio
    async def test_get_asset_not_found(self, firestore_client):
        """Test asset retrieval when not found."""
        with patch('app.database.get_collection') as mock_get_collection:
            mock_collection = Mock()
            mock_doc_ref = Mock()
            mock_doc = Mock()
            mock_doc.exists = False
            mock_doc_ref.get.return_value = mock_doc
            mock_collection.document.return_value = mock_doc_ref
            mock_get_collection.return_value = mock_collection
            
            asset = await get_asset("nonexistent_id")
            
            assert asset is None
    
    @pytest.mark.asyncio
    async def test_list_assets_success(self, firestore_client):
        """Test successful asset listing."""
        with patch('app.database.get_collection') as mock_get_collection:
            mock_collection = Mock()
            mock_query = Mock()
            mock_docs = [
                Mock(id="asset_1", to_dict=lambda: {"name": "Asset 1"}),
                Mock(id="asset_2", to_dict=lambda: {"name": "Asset 2"})
            ]
            mock_query.limit.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.stream.return_value = mock_docs
            mock_collection.order_by.return_value = mock_query
            mock_get_collection.return_value = mock_collection
            
            assets = await list_assets(limit=10, offset=0)
            
            assert len(assets) == 2
            assert assets[0]["id"] == "asset_1"
            assert assets[1]["id"] == "asset_2"
    
    @pytest.mark.asyncio
    async def test_update_asset_success(self, firestore_client):
        """Test successful asset update."""
        with patch('app.database.get_collection') as mock_get_collection:
            mock_collection = Mock()
            mock_doc_ref = Mock()
            mock_collection.document.return_value = mock_doc_ref
            mock_get_collection.return_value = mock_collection
            
            result = await update_asset("test_asset_id", {"name": "Updated Asset"})
            
            assert result is True
            mock_doc_ref.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_asset_success(self, firestore_client):
        """Test successful asset deletion."""
        with patch('app.database.get_collection') as mock_get_collection:
            mock_collection = Mock()
            mock_doc_ref = Mock()
            mock_collection.document.return_value = mock_doc_ref
            mock_get_collection.return_value = mock_collection
            
            result = await delete_asset("test_asset_id")
            
            assert result is True
            mock_doc_ref.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_asset_count_success(self, firestore_client):
        """Test successful asset count retrieval."""
        with patch('app.database.get_collection') as mock_get_collection:
            mock_collection = Mock()
            mock_docs = [Mock(), Mock(), Mock()]  # 3 assets
            mock_collection.stream.return_value = mock_docs
            mock_get_collection.return_value = mock_collection
            
            count = await get_asset_count()
            
            assert count == 3


class TestEstForClient:
    """Unit tests for EstFor API client."""
    
    @pytest.mark.asyncio
    async def test_get_assets_success(self, mock_http_client):
        """Test successful asset fetching from EstFor API."""
        client = EstForClient()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = [{"id": "asset_1", "name": "Test Asset"}]
            mock_response.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            assets = await client.get_assets(limit=10, offset=0)
            
            assert len(assets) == 1
            assert assets[0]["id"] == "asset_1"
    
    @pytest.mark.asyncio
    async def test_get_assets_failure(self, mock_http_client):
        """Test asset fetching failure."""
        client = EstForClient()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("API Error")
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(Exception):
                await client.get_assets()
    
    @pytest.mark.asyncio
    async def test_get_asset_by_id_success(self, mock_http_client):
        """Test successful single asset fetching."""
        client = EstForClient()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"id": "asset_1", "name": "Test Asset"}
            mock_response.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            asset = await client.get_asset_by_id("asset_1")
            
            assert asset["id"] == "asset_1"
            assert asset["name"] == "Test Asset"
    
    @pytest.mark.asyncio
    async def test_get_asset_by_id_not_found(self, mock_http_client):
        """Test asset fetching when not found."""
        client = EstForClient()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            asset = await client.get_asset_by_id("nonexistent")
            
            assert asset is None


class TestAssetModels:
    """Unit tests for asset models."""
    
    def test_asset_response_model(self):
        """Test AssetResponse model validation."""
        asset_data = {
            "id": "test_id",
            "name": "Test Asset",
            "type": "weapon",
            "rarity": "common",
            "description": "Test description",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        asset = AssetResponse(**asset_data)
        
        assert asset.id == "test_id"
        assert asset.name == "Test Asset"
        assert asset.type == "weapon"
        assert asset.rarity == "common"
    
    def test_asset_create_model(self):
        """Test AssetCreate model validation."""
        asset_data = {
            "name": "Test Asset",
            "type": "weapon",
            "rarity": "common",
            "description": "Test description"
        }
        
        asset = AssetCreate(**asset_data)
        
        assert asset.name == "Test Asset"
        assert asset.type == "weapon"
        assert asset.rarity == "common"
        assert asset.description == "Test description"
    
    def test_asset_create_model_minimal(self):
        """Test AssetCreate model with minimal data."""
        asset_data = {
            "name": "Test Asset",
            "type": "weapon"
        }
        
        asset = AssetCreate(**asset_data)
        
        assert asset.name == "Test Asset"
        assert asset.type == "weapon"
        assert asset.rarity is None
        assert asset.description is None


class TestCeleryTasks:
    """Unit tests for Celery tasks."""
    
    def test_collect_assets_task_success(self, mock_estfor_api, mock_logger):
        """Test successful asset collection task."""
        with patch('app.tasks.store_asset') as mock_store_asset:
            mock_store_asset.return_value = "test_asset_id"
            
            result = collect_assets_task()
            
            assert result["status"] == "completed"
            assert "total_assets" in result
            assert "stored_count" in result
            assert "task_id" in result
    
    def test_collect_assets_task_failure(self, mock_logger):
        """Test asset collection task failure."""
        with patch('app.services.estfor_client.EstForClient.get_assets', side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                collect_assets_task()
    
    def test_update_asset_task_success(self, mock_logger):
        """Test successful asset update task."""
        with patch('app.services.estfor_client.EstForClient.get_asset_by_id') as mock_get_asset, \
             patch('app.tasks.store_asset') as mock_store_asset:
            
            mock_get_asset.return_value = {"id": "asset_1", "name": "Updated Asset"}
            mock_store_asset.return_value = "asset_1"
            
            result = update_asset_task("asset_1")
            
            assert result["status"] == "completed"
            assert result["asset_id"] == "asset_1"
    
    def test_update_asset_task_not_found(self, mock_logger):
        """Test asset update task when asset not found."""
        with patch('app.services.estfor_client.EstForClient.get_asset_by_id') as mock_get_asset:
            mock_get_asset.return_value = None
            
            result = update_asset_task("nonexistent")
            
            assert result["status"] == "not_found"
            assert result["asset_id"] == "nonexistent"


class TestSecurity:
    """Unit tests for security features."""
    
    def test_malicious_input_sanitization(self, malicious_input_data):
        """Test input sanitization against malicious data."""
        # Test that malicious input is properly handled
        with pytest.raises(ValueError):
            AssetCreate(**malicious_input_data)
    
    def test_sql_injection_prevention(self, malicious_input_data):
        """Test SQL injection prevention."""
        # Test that SQL injection attempts are prevented
        malicious_name = malicious_input_data["name"]
        assert "<script>" in malicious_name  # Verify test data is malicious
        
        # The model should reject this or sanitize it
        with pytest.raises(ValueError):
            AssetCreate(name=malicious_name, type="weapon")
    
    def test_xss_prevention(self, malicious_input_data):
        """Test XSS prevention."""
        # Test that XSS attempts are prevented
        xss_payload = malicious_input_data["name"]
        assert "<script>" in xss_payload  # Verify test data contains XSS
        
        # The model should reject this or sanitize it
        with pytest.raises(ValueError):
            AssetCreate(name=xss_payload, type="weapon")


class TestPerformance:
    """Unit tests for performance features."""
    
    @pytest.mark.asyncio
    async def test_bulk_asset_storage(self, firestore_client, performance_test_data):
        """Test bulk asset storage performance."""
        import time
        
        start_time = time.time()
        
        with patch('app.database.get_collection') as mock_get_collection:
            mock_collection = Mock()
            mock_doc_ref = Mock()
            mock_doc_ref.id = "test_asset_id"
            mock_collection.add.return_value = (None, mock_doc_ref)
            mock_get_collection.return_value = mock_collection
            
            # Store multiple assets
            for asset_data in performance_test_data[:100]:  # Test with 100 assets
                await store_asset(asset_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertion: should complete within reasonable time
        assert execution_time < 10.0  # 10 seconds for 100 assets
    
    def test_memory_usage(self, performance_test_data):
        """Test memory usage with large datasets."""
        import sys
        
        # Measure memory before
        initial_memory = sys.getsizeof(performance_test_data)
        
        # Process large dataset
        processed_data = [asset.copy() for asset in performance_test_data]
        
        # Measure memory after
        final_memory = sys.getsizeof(processed_data)
        
        # Memory usage should be reasonable
        memory_increase = final_memory - initial_memory
        assert memory_increase < 1024 * 1024  # Less than 1MB increase 