"""
Pytest configuration and shared fixtures for Solana NFT Downloader tests.
"""
import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import responses
import requests


@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp(prefix="nft_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def mock_nft_data():
    """Sample NFT data for testing."""
    return {
        "assets": [
            {
                "contract": "test-contract-1",
                "tokenId": "1",
                "name": "Test NFT #1",
                "description": "A test NFT for testing",
                "imageUrl": "https://example.com/nft1.jpg",
                "externalUrl": "https://example.com/nft1",
                "attributes": [
                    {
                        "trait_type": "Rarity",
                        "value": "Common"
                    }
                ]
            },
            {
                "contract": "test-contract-2",
                "tokenId": "2",
                "name": "Test NFT #2",
                "description": "Another test NFT",
                "imageUrl": "https://example.com/nft2.png",
                "externalUrl": "https://example.com/nft2",
                "attributes": [
                    {
                        "trait_type": "Rarity",
                        "value": "Rare"
                    }
                ]
            }
        ],
        "nextToken": None
    }


@pytest.fixture(scope="session")
def test_wallet_address():
    """Test wallet address for NFT queries."""
    return "test-wallet-address"


@pytest.fixture(scope="session")
def mock_ankr_response(mock_nft_data):
    """Mock Ankr API response."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": mock_nft_data
    }


@pytest.fixture(scope="session")
def mock_secret_value():
    """Mock secret value from Google Secret Manager."""
    return "test-ankr-api-key"


@pytest.fixture(scope="function")
def mock_secret_manager(mock_secret_value):
    """Mock Google Secret Manager client."""
    with patch('google.cloud.secretmanager.SecretManagerServiceClient') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Mock secret access
        mock_secret = Mock()
        mock_secret.payload.data.decode.return_value = mock_secret_value
        mock_instance.access_secret_version.return_value = mock_secret
        
        yield mock_instance


@pytest.fixture(scope="function")
def mock_ankr_api(mock_ankr_response):
    """Mock Ankr API responses."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Mock successful NFT query
        rsps.add(
            responses.POST,
            "https://rpc.ankr.com/multichain",
            json=mock_ankr_response,
            status=200
        )
        
        # Mock rate limit response
        rsps.add(
            responses.POST,
            "https://rpc.ankr.com/multichain",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32000,
                    "message": "Rate limit exceeded"
                }
            },
            status=429,
            match=[responses.matchers.json_params_matcher({
                "jsonrpc": "2.0",
                "method": "ankr_getNFTsByOwner",
                "params": {"wallet": "rate-limited-wallet"}
            })]
        )
        
        yield rsps


@pytest.fixture(scope="function")
def temp_output_dir():
    """Create a temporary output directory for downloads."""
    temp_dir = tempfile.mkdtemp(prefix="nft_output_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def mock_image_response():
    """Mock image download response."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://example.com/nft1.jpg",
            body=b"fake-image-data",
            status=200,
            content_type="image/jpeg"
        )
        rsps.add(
            responses.GET,
            "https://example.com/nft2.png",
            body=b"fake-png-data",
            status=200,
            content_type="image/png"
        )
        yield rsps


@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment variables."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ.update({
        "GOOGLE_CLOUD_PROJECT": "test-project",
        "TEST_MODE": "true",
        "ANKR_API_URL": "http://localhost:8080",
        "SECRET_MANAGER_ENDPOINT": "http://localhost:8085"
    })
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(scope="function")
def mock_file_system():
    """Mock file system operations."""
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.mkdir') as mock_mkdir, \
         patch('builtins.open', create=True) as mock_open:
        
        mock_exists.return_value = False
        mock_mkdir.return_value = None
        mock_file = Mock()
        mock_file.write.return_value = None
        mock_file.close.return_value = None
        mock_open.return_value.__enter__.return_value = mock_file
        
        yield {
            'exists': mock_exists,
            'mkdir': mock_mkdir,
            'open': mock_open,
            'file': mock_file
        }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e) 