"""
Unit tests for Helius API client.
"""
import pytest
import responses
from unittest.mock import patch, MagicMock
from src.helius_api import HeliusAPIClient, HeliusAPIError


class TestHeliusAPIClient:
    """Test cases for HeliusAPIClient."""
    
    def test_init_valid_api_key(self):
        """Test initialization with valid API key."""
        client = HeliusAPIClient("test-api-key")
        assert client.api_key == "test-api-key"
        assert client.timeout == 30
    
    def test_init_invalid_api_key(self):
        """Test initialization with invalid API key."""
        with pytest.raises(HeliusAPIError, match="API key must be a non-empty string"):
            HeliusAPIClient("")
        
        with pytest.raises(HeliusAPIError, match="API key must be a non-empty string"):
            HeliusAPIClient(None)
    
    def test_is_valid_solana_address(self):
        """Test Solana address validation."""
        client = HeliusAPIClient("test-api-key")
        
        # Valid addresses
        assert client._is_valid_solana_address("9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM")
        assert client._is_valid_solana_address("test-wallet-123")
        
        # Invalid addresses
        assert not client._is_valid_solana_address("")
        assert not client._is_valid_solana_address("invalid-address!")
        assert not client._is_valid_solana_address("0x1234567890abcdef")
    
    @responses.activate
    def test_get_nfts_by_owner_success(self):
        """Test successful NFT fetch by owner."""
        client = HeliusAPIClient("test-api-key")
        wallet_address = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
        
        # Mock response
        mock_response = [
            {
                "id": "test-nft-1",
                "content": {
                    "metadata": {
                        "name": "Test NFT 1"
                    },
                    "files": [
                        {
                            "type": "image/png",
                            "uri": "https://example.com/image1.png"
                        }
                    ]
                }
            }
        ]
        
        responses.add(
            responses.GET,
            f"https://api.helius.xyz/v0/addresses/{wallet_address}/nfts?api-key=test-api-key",
            json=mock_response,
            status=200
        )
        
        result = client.get_nfts_by_owner(wallet_address)
        assert result == mock_response
    
    def test_get_nfts_by_owner_invalid_address(self):
        """Test NFT fetch with invalid wallet address."""
        client = HeliusAPIClient("test-api-key")
        
        with pytest.raises(HeliusAPIError, match="Invalid Solana wallet address format"):
            client.get_nfts_by_owner("invalid-address")
    
    def test_get_nfts_by_owner_empty_address(self):
        """Test NFT fetch with empty wallet address."""
        client = HeliusAPIClient("test-api-key")
        
        with pytest.raises(HeliusAPIError, match="Wallet address must be a non-empty string"):
            client.get_nfts_by_owner("")
    
    @responses.activate
    def test_get_nft_metadata_success(self):
        """Test successful NFT metadata fetch."""
        client = HeliusAPIClient("test-api-key")
        asset_id = "test-asset-123"
        
        mock_response = {
            "id": asset_id,
            "content": {
                "metadata": {
                    "name": "Test NFT",
                    "description": "A test NFT"
                }
            }
        }
        
        responses.add(
            responses.GET,
            f"https://api.helius.xyz/v0/assets/{asset_id}?api-key=test-api-key",
            json=mock_response,
            status=200
        )
        
        result = client.get_nft_metadata(asset_id)
        assert result == mock_response
    
    @responses.activate
    def test_search_assets_success(self):
        """Test successful asset search."""
        client = HeliusAPIClient("test-api-key")
        owner_address = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
        
        mock_response = {
            "result": [
                {
                    "id": "test-asset-1",
                    "content": {
                        "metadata": {
                            "name": "Test Asset 1"
                        }
                    }
                }
            ]
        }
        
        responses.add(
            responses.POST,
            f"https://api.helius.xyz/v0/asset/search?api-key=test-api-key",
            json=mock_response,
            status=200
        )
        
        result = client.search_assets(owner_address)
        assert result == mock_response
    
    @responses.activate
    def test_get_wallet_balance_success(self):
        """Test successful wallet balance fetch."""
        client = HeliusAPIClient("test-api-key")
        wallet_address = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
        
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "value": 1000000000
            }
        }
        
        responses.add(
            responses.POST,
            f"https://api.helius.xyz/v0/rpc?api-key=test-api-key",
            json=mock_response,
            status=200
        )
        
        result = client.get_wallet_balance(wallet_address)
        assert result == mock_response
    
    @responses.activate
    def test_check_api_connectivity_success(self):
        """Test successful API connectivity check."""
        client = HeliusAPIClient("test-api-key")
        
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": "ok"
        }
        
        responses.add(
            responses.POST,
            f"https://api.helius.xyz/v0/rpc?api-key=test-api-key",
            json=mock_response,
            status=200
        )
        
        assert client.check_api_connectivity() is True
    
    @responses.activate
    def test_check_api_connectivity_failure(self):
        """Test API connectivity check failure."""
        client = HeliusAPIClient("test-api-key")
        
        responses.add(
            responses.POST,
            f"https://api.helius.xyz/v0/rpc?api-key=test-api-key",
            status=500
        )
        
        assert client.check_api_connectivity() is False
    
    @responses.activate
    def test_make_request_http_error(self):
        """Test HTTP error handling."""
        client = HeliusAPIClient("test-api-key")
        
        responses.add(
            responses.GET,
            f"https://api.helius.xyz/v0/addresses/test/nfts?api-key=test-api-key",
            status=401
        )
        
        with pytest.raises(HeliusAPIError, match="Authentication failed"):
            client.get_nfts_by_owner("test-wallet-123")
    
    @responses.activate
    def test_make_request_rate_limit(self):
        """Test rate limit error handling."""
        client = HeliusAPIClient("test-api-key")
        
        responses.add(
            responses.GET,
            f"https://api.helius.xyz/v0/addresses/test/nfts?api-key=test-api-key",
            status=429
        )
        
        with pytest.raises(HeliusAPIError, match="Rate limit exceeded"):
            client.get_nfts_by_owner("test-wallet-123")
    
    @responses.activate
    def test_make_request_timeout(self):
        """Test timeout error handling."""
        client = HeliusAPIClient("test-api-key", timeout=1)
        
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("timeout")
            
            with pytest.raises(HeliusAPIError, match="Unexpected error"):
                client.get_nfts_by_owner("test-wallet-123") 