"""
Unit tests for Firestore manager.
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from src.firestore_manager import FirestoreManager, FirestoreManagerError


class TestFirestoreManager:
    """Test cases for FirestoreManager class."""
    
    @pytest.fixture
    def mock_firestore_client(self):
        """Mock Firestore client."""
        with patch('src.firestore_manager.firestore.Client') as mock_client:
            mock_db = Mock()
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_client.return_value = mock_db
            yield mock_client
    
    @pytest.fixture
    def firestore_manager(self, mock_firestore_client):
        """Create FirestoreManager instance with mocked client."""
        return FirestoreManager(project_id="test-project")
    
    @pytest.fixture
    def sample_nft_data(self):
        """Sample NFT data from Helius API."""
        return {
            "id": "test-asset-id-123",
            "content": {
                "metadata": {
                    "name": "Test NFT",
                    "symbol": "TEST",
                    "description": "A test NFT",
                    "uri": "ipfs://test-metadata-uri",
                    "attributes": [
                        {"trait_type": "Background", "value": "Blue"},
                        {"trait_type": "Eyes", "value": "Green"}
                    ],
                    "collection": {
                        "name": "Test Collection",
                        "family": "Test Family"
                    },
                    "royalties": [
                        {"recipient": "creator-address", "percentage": 5.0}
                    ],
                    "creators": [
                        {"address": "creator-address", "share": 100}
                    ],
                    "supply": 1,
                    "decimals": 0,
                    "tokenStandard": "NonFungible"
                },
                "files": [
                    {
                        "uri": "https://example.com/image.png",
                        "mime": "image/png"
                    }
                ],
                "links": {
                    "image": "https://example.com/image.png"
                }
            },
            "compression": {
                "compressed": False
            }
        }
    
    def test_init_success(self, mock_firestore_client):
        """Test successful initialization."""
        manager = FirestoreManager(project_id="test-project")
        assert manager.collection_name == "nfts"
        mock_firestore_client.assert_called_once_with(project="test-project")
    
    def test_init_without_project_id(self, mock_firestore_client):
        """Test initialization without project ID."""
        manager = FirestoreManager()
        mock_firestore_client.assert_called_once_with()
    
    def test_init_failure(self):
        """Test initialization failure."""
        with patch('src.firestore_manager.firestore.Client', side_effect=Exception("Connection failed")):
            with pytest.raises(FirestoreManagerError, match="Failed to initialize Firestore client"):
                FirestoreManager()
    
    def test_store_nft_data_success(self, firestore_manager, sample_nft_data, mock_firestore_client):
        """Test successful NFT data storage."""
        mock_db = mock_firestore_client.return_value
        mock_collection = mock_db.collection.return_value
        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        
        result = firestore_manager.store_nft_data("test-wallet", sample_nft_data)
        
        assert result == "test-asset-id-123"
        mock_collection.document.assert_called_once_with("test-asset-id-123")
        mock_doc_ref.set.assert_called_once()
        
        # Verify the stored data structure
        call_args = mock_doc_ref.set.call_args[0][0]
        assert call_args["asset_id"] == "test-asset-id-123"
        assert call_args["wallet_address"] == "test-wallet"
        assert call_args["name"] == "Test NFT"
        assert call_args["symbol"] == "TEST"
        assert call_args["description"] == "A test NFT"
        assert call_args["image_url"] == "https://example.com/image.png"
        assert call_args["compressed"] == False
        assert len(call_args["attributes"]) == 2
        assert call_args["collection"]["name"] == "Test Collection"
    
    def test_store_nft_data_missing_id(self, firestore_manager):
        """Test NFT data storage with missing ID."""
        nft_data = {"content": {"metadata": {"name": "Test"}}}
        
        with pytest.raises(FirestoreManagerError, match="NFT data missing required 'id' field"):
            firestore_manager.store_nft_data("test-wallet", nft_data)
    
    def test_store_nft_data_storage_failure(self, firestore_manager, sample_nft_data, mock_firestore_client):
        """Test NFT data storage failure."""
        mock_db = mock_firestore_client.return_value
        mock_collection = mock_db.collection.return_value
        mock_collection.document.side_effect = Exception("Storage failed")
        
        with pytest.raises(FirestoreManagerError, match="Failed to store NFT data"):
            firestore_manager.store_nft_data("test-wallet", sample_nft_data)
    
    def test_store_wallet_nfts_success(self, firestore_manager, sample_nft_data, mock_firestore_client):
        """Test successful wallet NFTs storage."""
        mock_db = mock_firestore_client.return_value
        mock_collection = mock_db.collection.return_value
        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        
        nfts_data = [sample_nft_data]
        results = firestore_manager.store_wallet_nfts("test-wallet", nfts_data)
        
        assert results["total_nfts"] == 1
        assert results["stored"] == 1
        assert results["failed"] == 0
        assert len(results["errors"]) == 0
    
    def test_store_wallet_nfts_partial_failure(self, firestore_manager, sample_nft_data, mock_firestore_client):
        """Test wallet NFTs storage with partial failures."""
        mock_db = mock_firestore_client.return_value
        mock_collection = mock_db.collection.return_value
        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        
        # Make the second NFT fail
        def side_effect(asset_id):
            if asset_id == "test-asset-id-456":
                raise Exception("Storage failed")
            return mock_doc_ref
        
        mock_collection.document.side_effect = side_effect
        
        nfts_data = [
            sample_nft_data,
            {"id": "test-asset-id-456", "content": {"metadata": {"name": "Failed NFT"}}}
        ]
        
        results = firestore_manager.store_wallet_nfts("test-wallet", nfts_data)
        
        assert results["total_nfts"] == 2
        assert results["stored"] == 1
        assert results["failed"] == 1
        assert len(results["errors"]) == 1
    
    def test_get_nft_by_asset_id_success(self, firestore_manager, mock_firestore_client):
        """Test successful NFT retrieval by asset ID."""
        mock_db = mock_firestore_client.return_value
        mock_collection = mock_db.collection.return_value
        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"asset_id": "test-123", "name": "Test NFT"}
        mock_doc_ref.get.return_value = mock_doc
        
        result = firestore_manager.get_nft_by_asset_id("test-123")
        
        assert result == {"asset_id": "test-123", "name": "Test NFT"}
        mock_collection.document.assert_called_once_with("test-123")
    
    def test_get_nft_by_asset_id_not_found(self, firestore_manager, mock_firestore_client):
        """Test NFT retrieval when not found."""
        mock_db = mock_firestore_client.return_value
        mock_collection = mock_db.collection.return_value
        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        
        mock_doc = Mock()
        mock_doc.exists = False
        mock_doc_ref.get.return_value = mock_doc
        
        result = firestore_manager.get_nft_by_asset_id("test-123")
        
        assert result is None
    
    def test_get_nfts_by_wallet_success(self, firestore_manager, mock_firestore_client):
        """Test successful NFTs retrieval by wallet."""
        mock_db = mock_firestore_client.return_value
        mock_collection = mock_db.collection.return_value
        
        # Mock query and stream
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        mock_docs = [
            Mock(to_dict=lambda: {"asset_id": "test-1", "name": "NFT 1"}),
            Mock(to_dict=lambda: {"asset_id": "test-2", "name": "NFT 2"})
        ]
        mock_query.stream.return_value = mock_docs
        
        results = firestore_manager.get_nfts_by_wallet("test-wallet", limit=1000)
        
        assert len(results) == 2
        assert results[0]["asset_id"] == "test-1"
        assert results[1]["asset_id"] == "test-2"
    
    def test_search_nfts_with_filters(self, firestore_manager, mock_firestore_client):
        """Test NFT search with filters."""
        mock_db = mock_firestore_client.return_value
        mock_collection = mock_db.collection.return_value
        
        # Mock query chain
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        mock_docs = [
            Mock(to_dict=lambda: {"asset_id": "test-1", "name": "NFT 1"})
        ]
        mock_query.stream.return_value = mock_docs
        
        results = firestore_manager.search_nfts(
            wallet_address="test-wallet",
            collection_name="Test Collection",
            compressed=False,
            limit=100
        )
        
        assert len(results) == 1
        assert results[0]["asset_id"] == "test-1"
    
    def test_update_nft_sync_status_success(self, firestore_manager, mock_firestore_client):
        """Test successful sync status update."""
        mock_db = mock_firestore_client.return_value
        mock_collection = mock_db.collection.return_value
        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        
        result = firestore_manager.update_nft_sync_status("test-123", "synced")
        
        assert result is True
        mock_doc_ref.update.assert_called_once()
        
        # Verify update data
        call_args = mock_doc_ref.update.call_args[0][0]
        assert call_args["sync_status"] == "synced"
        assert "last_synced" in call_args
        assert "updated_at" in call_args
    
    def test_delete_nft_success(self, firestore_manager, mock_firestore_client):
        """Test successful NFT deletion."""
        mock_db = mock_firestore_client.return_value
        mock_collection = mock_db.collection.return_value
        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        
        result = firestore_manager.delete_nft("test-123")
        
        assert result is True
        mock_doc_ref.delete.assert_called_once()
    
    def test_get_collection_stats_success(self, firestore_manager, mock_firestore_client):
        """Test successful collection statistics retrieval."""
        mock_db = mock_firestore_client.return_value
        mock_collection = mock_db.collection.return_value
        
        # Mock query and stream
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        
        mock_docs = [
            Mock(to_dict=lambda: {
                "asset_id": "test-1",
                "name": "NFT 1",
                "collection": {"name": "Collection A"},
                "compressed": False,
                "sync_status": "synced",
                "created_at": datetime.now(timezone.utc)
            }),
            Mock(to_dict=lambda: {
                "asset_id": "test-2",
                "name": "NFT 2",
                "collection": {"name": "Collection A"},
                "compressed": True,
                "sync_status": "synced",
                "created_at": datetime.now(timezone.utc)
            })
        ]
        mock_query.stream.return_value = mock_docs
        
        stats = firestore_manager.get_collection_stats("test-wallet")
        
        assert stats["total_nfts"] == 2
        assert stats["collections"]["Collection A"] == 2
        assert stats["compressed_count"] == 1
        assert stats["sync_status_counts"]["synced"] == 2
        assert len(stats["recent_additions"]) == 2
    
    def test_extract_image_url_from_files(self, firestore_manager, sample_nft_data):
        """Test image URL extraction from files array."""
        image_url = firestore_manager._extract_image_url(sample_nft_data)
        assert image_url == "https://example.com/image.png"
    
    def test_extract_image_url_from_links(self, firestore_manager):
        """Test image URL extraction from links."""
        nft_data = {
            "content": {
                "links": {
                    "image": "https://example.com/image.jpg"
                }
            }
        }
        image_url = firestore_manager._extract_image_url(nft_data)
        assert image_url == "https://example.com/image.jpg"
    
    def test_extract_image_url_from_metadata(self, firestore_manager):
        """Test image URL extraction from metadata."""
        nft_data = {
            "content": {
                "metadata": {
                    "image": "https://example.com/image.png"
                }
            }
        }
        image_url = firestore_manager._extract_image_url(nft_data)
        assert image_url == "https://example.com/image.png"
    
    def test_extract_image_url_not_found(self, firestore_manager):
        """Test image URL extraction when not found."""
        nft_data = {
            "content": {
                "metadata": {
                    "name": "Test NFT"
                }
            }
        }
        image_url = firestore_manager._extract_image_url(nft_data)
        assert image_url == "" 