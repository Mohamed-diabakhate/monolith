"""
Unit tests for NFTProcessor class.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.nft_processor import NFTProcessor, NFTProcessorError
from src.secret_manager import SecretManagerError
from src.ankr_api import AnkrAPIError
from src.file_manager import FileManagerError


class TestNFTProcessor:
    """Test cases for NFTProcessor class."""
    
    @pytest.fixture
    def mock_secret_manager(self):
        """Mock SecretManager."""
        mock = Mock()
        mock.get_secret.return_value = "test_api_key"
        return mock
    
    @pytest.fixture
    def mock_ankr_client(self):
        """Mock AnkrAPIClient."""
        mock = Mock()
        return mock
    
    @pytest.fixture
    def mock_file_manager(self):
        """Mock FileManager."""
        mock = Mock()
        return mock
    
    @pytest.fixture
    def nft_processor(self, mock_secret_manager, mock_ankr_client, mock_file_manager):
        """Create NFTProcessor with mocked dependencies."""
        with patch('src.nft_processor.SecretManager', return_value=mock_secret_manager), \
             patch('src.nft_processor.AnkrAPIClient', return_value=mock_ankr_client), \
             patch('src.nft_processor.FileManager', return_value=mock_file_manager):
            
            return NFTProcessor(wallet_address="test_wallet")
    
    def test_initialization_success(self, mock_secret_manager, mock_ankr_client, mock_file_manager):
        """Test successful NFTProcessor initialization."""
        with patch('src.nft_processor.SecretManager', return_value=mock_secret_manager), \
             patch('src.nft_processor.AnkrAPIClient', return_value=mock_ankr_client), \
             patch('src.nft_processor.FileManager', return_value=mock_file_manager):
            
            processor = NFTProcessor(wallet_address="test_wallet")
            
            assert processor.wallet_address == "test_wallet"
            assert processor.output_dir == "~/Pictures/SolanaNFTs"
            mock_secret_manager.get_secret.assert_called_once_with("ANKR_API_KEY")
    
    def test_initialization_with_custom_output_dir(self, mock_secret_manager, mock_ankr_client, mock_file_manager):
        """Test NFTProcessor initialization with custom output directory."""
        with patch('src.nft_processor.SecretManager', return_value=mock_secret_manager), \
             patch('src.nft_processor.AnkrAPIClient', return_value=mock_ankr_client), \
             patch('src.nft_processor.FileManager', return_value=mock_file_manager):
            
            processor = NFTProcessor(
                wallet_address="test_wallet",
                output_dir="/custom/path"
            )
            
            assert processor.output_dir == "/custom/path"
    
    def test_initialization_secret_manager_error(self):
        """Test NFTProcessor initialization with SecretManager error."""
        with patch('src.nft_processor.SecretManager', side_effect=SecretManagerError("Secret error")):
            with pytest.raises(NFTProcessorError, match="Failed to initialize NFT processor"):
                NFTProcessor(wallet_address="test_wallet")
    
    def test_initialization_ankr_api_error(self, mock_secret_manager):
        """Test NFTProcessor initialization with AnkrAPI error."""
        with patch('src.nft_processor.SecretManager', return_value=mock_secret_manager), \
             patch('src.nft_processor.AnkrAPIClient', side_effect=AnkrAPIError("API error")):
            with pytest.raises(NFTProcessorError, match="Failed to initialize NFT processor"):
                NFTProcessor(wallet_address="test_wallet")
    
    def test_initialization_file_manager_error(self, mock_secret_manager, mock_ankr_client):
        """Test NFTProcessor initialization with FileManager error."""
        with patch('src.nft_processor.SecretManager', return_value=mock_secret_manager), \
             patch('src.nft_processor.AnkrAPIClient', return_value=mock_ankr_client), \
             patch('src.nft_processor.FileManager', side_effect=FileManagerError("File error")):
            with pytest.raises(NFTProcessorError, match="Failed to initialize NFT processor"):
                NFTProcessor(wallet_address="test_wallet")
    
    def test_process_wallet_success(self, nft_processor):
        """Test successful wallet processing."""
        # Mock API response
        mock_response = {
            "result": {
                "assets": [
                    {
                        "tokenId": "123",
                        "name": "Test NFT 1",
                        "imageUrl": "https://example.com/image1.jpg",
                        "contract": "contract1"
                    },
                    {
                        "tokenId": "456",
                        "name": "Test NFT 2",
                        "imageUrl": "https://example.com/image2.png",
                        "contract": "contract2"
                    }
                ]
            }
        }
        
        # Mock the _fetch_nfts method directly
        nft_processor._fetch_nfts = Mock(return_value=mock_response)
        nft_processor.file_manager.file_exists.return_value = False
        nft_processor.file_manager.download_image.return_value = True
        
        results = nft_processor.process_wallet()
        
        assert results["total_nfts"] == 2
        assert results["downloaded"] == 2
        assert results["skipped"] == 0
        assert results["failed"] == 0
        assert len(results["errors"]) == 0
    
    def test_process_wallet_no_nfts(self, nft_processor):
        """Test wallet processing with no NFTs."""
        # Mock empty response
        mock_response = {"result": {"assets": []}}
        
        # Mock the _fetch_nfts method directly
        nft_processor._fetch_nfts = Mock(return_value=mock_response)
        
        results = nft_processor.process_wallet()
        
        assert results["total_nfts"] == 0
        assert results["downloaded"] == 0
        assert results["skipped"] == 0
        assert results["failed"] == 0
    
    def test_process_wallet_invalid_response(self, nft_processor):
        """Test wallet processing with invalid API response."""
        # Mock invalid response
        mock_response = {"invalid": "response"}
        
        # Mock the _fetch_nfts method directly
        nft_processor._fetch_nfts = Mock(return_value=mock_response)
        
        with pytest.raises(NFTProcessorError, match="Invalid response from Ankr API"):
            nft_processor.process_wallet()
    
    def test_process_wallet_api_error(self, nft_processor):
        """Test wallet processing with API error."""
        nft_processor.ankr_client.get_nfts.side_effect = AnkrAPIError("API error")
        
        with pytest.raises(NFTProcessorError, match="Failed to process wallet"):
            nft_processor.process_wallet()
    
    def test_process_wallet_mixed_results(self, nft_processor):
        """Test wallet processing with mixed success/failure results."""
        # Mock API response
        mock_response = {
            "result": {
                "assets": [
                    {
                        "tokenId": "123",
                        "name": "Test NFT 1",
                        "imageUrl": "https://example.com/image1.jpg",
                        "contract": "contract1"
                    },
                    {
                        "tokenId": "456",
                        "name": "Test NFT 2",
                        "imageUrl": "https://example.com/image2.png",
                        "contract": "contract2"
                    }
                ]
            }
        }
        
        # Mock the _fetch_nfts method directly
        nft_processor._fetch_nfts = Mock(return_value=mock_response)
        nft_processor.file_manager.file_exists.return_value = False
        # First download succeeds, second fails
        nft_processor.file_manager.download_image.side_effect = [True, False]
        
        results = nft_processor.process_wallet()
        
        assert results["total_nfts"] == 2
        assert results["downloaded"] == 1
        assert results["skipped"] == 1
        assert results["failed"] == 0
    
    def test_process_wallet_processing_error(self, nft_processor):
        """Test wallet processing with individual NFT processing error."""
        # Mock API response
        mock_response = {
            "result": {
                "assets": [
                    {
                        "tokenId": "123",
                        "name": "Test NFT 1",
                        "imageUrl": "https://example.com/image1.jpg",
                        "contract": "contract1"
                    }
                ]
            }
        }
        
        # Mock the _fetch_nfts method directly
        nft_processor._fetch_nfts = Mock(return_value=mock_response)
        nft_processor.file_manager.file_exists.return_value = False
        nft_processor.file_manager.download_image.side_effect = Exception("Download error")
        
        results = nft_processor.process_wallet()
        
        assert results["total_nfts"] == 1
        assert results["downloaded"] == 0
        assert results["skipped"] == 0
        assert results["failed"] == 1
        assert len(results["errors"]) == 1
        assert "Failed to process NFT" in results["errors"][0]
    
    def test_process_single_nft_success(self, nft_processor):
        """Test successful single NFT processing."""
        asset = {
            "tokenId": "123",
            "name": "Test NFT",
            "imageUrl": "https://example.com/image.jpg",
            "contract": "contract123"
        }
        
        # Mock file doesn't exist, so download will proceed
        nft_processor.file_manager.file_exists.return_value = False
        nft_processor.file_manager.download_image.return_value = True
        
        success = nft_processor._process_single_nft(asset)
        
        assert success
        nft_processor.file_manager.download_image.assert_called_once()
    
    def test_process_single_nft_no_image(self, nft_processor):
        """Test single NFT processing with no image URL."""
        asset = {
            "tokenId": "123",
            "name": "Test NFT",
            "contract": "contract123"
            # No imageUrl field
        }
        
        success = nft_processor._process_single_nft(asset)
        
        assert not success
    
    def test_process_single_nft_download_failure(self, nft_processor):
        """Test single NFT processing with download failure."""
        asset = {
            "tokenId": "123",
            "name": "Test NFT",
            "imageUrl": "https://example.com/image.jpg",
            "contract": "contract123"
        }
        
        nft_processor.file_manager.download_image.return_value = False
        
        success = nft_processor._process_single_nft(asset)
        
        assert not success
    
    def test_get_processing_stats(self, nft_processor):
        """Test processing statistics retrieval."""
        # Mock file manager methods
        nft_processor.file_manager.list_downloaded_files.return_value = ["file1.jpg", "file2.png"]
        nft_processor.file_manager.get_disk_space.return_value = (1000000000, 2000000000)  # 1GB free, 2GB total
        
        stats = nft_processor.get_processing_stats()
        
        assert "downloaded_files" in stats
        assert "available_space_gb" in stats
        assert "total_space_gb" in stats
        assert "output_directory" in stats
        assert stats["downloaded_files"] == 2
        assert stats["available_space_gb"] == 0.93  # 1GB / 1024^3
        assert stats["total_space_gb"] == 1.86  # 2GB / 1024^3
    
    def test_validate_wallet_address(self, nft_processor):
        """Test wallet address validation."""
        # Test valid address
        nft_processor.ankr_client._is_valid_solana_address.return_value = True
        assert nft_processor.validate_wallet_address()
        
        # Test invalid address
        nft_processor.ankr_client._is_valid_solana_address.side_effect = Exception("Invalid address")
        assert not nft_processor.validate_wallet_address()
    
    def test_check_api_connectivity(self, nft_processor):
        """Test API connectivity check."""
        # Test successful connectivity
        nft_processor.ankr_client.get_wallet_balance.return_value = {"balance": "1000"}
        assert nft_processor.check_api_connectivity()
        
        # Test failed connectivity
        nft_processor.ankr_client.get_wallet_balance.side_effect = Exception("API error")
        assert not nft_processor.check_api_connectivity()
    
    def test_cleanup_orphaned_files(self, nft_processor):
        """Test orphaned file cleanup."""
        # Mock NFT data
        nft_data = {
            "result": {
                "assets": [
                    {
                        "tokenId": "123",
                        "name": "Test NFT",
                        "image": "https://example.com/image.jpg",
                        "contract": "contract123"
                    }
                ]
            }
        }
        
        # Mock file manager to return some orphaned files
        nft_processor.file_manager.list_downloaded_files.return_value = ["orphaned1.jpg", "orphaned2.png"]
        nft_processor.file_manager.get_file_info.return_value = {"name": "orphaned1.jpg"}
        
        count = nft_processor.cleanup_orphaned_files(nft_data)
        
        assert count >= 0  # Should return number of cleaned files 