"""
Unit tests for Google Secret Manager integration.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import os


class TestSecretManager:
    """Test cases for Google Secret Manager functionality."""
    
    @pytest.mark.unit
    def test_valid_secret_retrieval(self, mock_secret_manager, mock_secret_value):
        """Test successful secret retrieval."""
        from src.secret_manager import SecretManager
        
        secret_manager = SecretManager("test-project")
        secret = secret_manager.get_secret("ANKR_API_KEY")
        
        assert secret == mock_secret_value
        mock_secret_manager.access_secret_version.assert_called_once()
    
    @pytest.mark.unit
    def test_invalid_secret_version_handling(self, mock_secret_manager):
        """Test handling of invalid secret version."""
        from src.secret_manager import SecretManager, SecretManagerError
        
        # Mock secret manager to raise an exception
        mock_secret_manager.access_secret_version.side_effect = Exception("Secret version not found")
        
        secret_manager = SecretManager("test-project")
        
        with pytest.raises(SecretManagerError) as exc_info:
            secret_manager.get_secret("ANKR_API_KEY")
        
        assert "Secret version not found" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_authentication_failure_handling(self, mock_secret_manager):
        """Test handling of authentication failures."""
        from src.secret_manager import SecretManager, SecretManagerError
        
        # Mock authentication error
        mock_secret_manager.access_secret_version.side_effect = Exception("Authentication failed")
        
        secret_manager = SecretManager("test-project")
        
        with pytest.raises(SecretManagerError) as exc_info:
            secret_manager.get_secret("ANKR_API_KEY")
        
        assert "Authentication failed" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_project_id_validation(self):
        """Test project ID validation."""
        from src.secret_manager import SecretManager, SecretManagerError
        import os
        
        # Save original environment variable
        original_project = os.environ.get('GOOGLE_CLOUD_PROJECT')
        
        try:
            # Remove environment variable for testing
            if 'GOOGLE_CLOUD_PROJECT' in os.environ:
                del os.environ['GOOGLE_CLOUD_PROJECT']
            
            # Test empty project ID
            with pytest.raises(SecretManagerError) as exc_info:
                SecretManager("")
            
            assert "Project ID" in str(exc_info.value)
            
            # Test None project ID
            with pytest.raises(SecretManagerError) as exc_info:
                SecretManager(None)
            
            assert "Project ID" in str(exc_info.value)
            
            # Test invalid project ID format (doesn't start with test-)
            with pytest.raises(SecretManagerError) as exc_info:
                SecretManager("123invalid")
            
            assert "Invalid project ID format" in str(exc_info.value)
            
        finally:
            # Restore original environment variable
            if original_project:
                os.environ['GOOGLE_CLOUD_PROJECT'] = original_project
    
    @pytest.mark.unit
    def test_secret_format_validation(self, mock_secret_manager):
        """Test secret format validation."""
        from src.secret_manager import SecretManager, SecretManagerError
        
        # Mock empty secret
        mock_secret = Mock()
        mock_secret.payload.data.decode.return_value = ""
        mock_secret_manager.access_secret_version.return_value = mock_secret
        
        secret_manager = SecretManager("test-project")
        
        with pytest.raises(SecretManagerError) as exc_info:
            secret_manager.get_secret("ANKR_API_KEY")
        
        assert "empty" in str(exc_info.value).lower()
    
    @pytest.mark.unit
    def test_secret_name_validation(self, mock_secret_manager):
        """Test secret name validation."""
        from src.secret_manager import SecretManager, SecretManagerError
        
        secret_manager = SecretManager("test-project")
        
        # Test empty secret name
        with pytest.raises(SecretManagerError) as exc_info:
            secret_manager.get_secret("")
        
        assert "Secret name" in str(exc_info.value)
        
        # Test None secret name
        with pytest.raises(SecretManagerError) as exc_info:
            secret_manager.get_secret(None)
        
        assert "Secret name" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_client_initialization(self):
        """Test Secret Manager client initialization."""
        from src.secret_manager import SecretManager
        
        with patch('google.cloud.secretmanager.SecretManagerServiceClient') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            
            secret_manager = SecretManager("test-project")
            
            mock_client.assert_called_once()
            assert secret_manager.client == mock_instance
            assert secret_manager.project_id == "test-project"
    
    @pytest.mark.unit
    def test_secret_path_construction(self, mock_secret_manager):
        """Test correct secret path construction."""
        from src.secret_manager import SecretManager
        
        secret_manager = SecretManager("test-project")
        
        # Mock the internal method to capture the path
        with patch.object(secret_manager, '_get_secret_path') as mock_path:
            mock_path.return_value = "projects/test-project/secrets/ANKR_API_KEY/versions/latest"
            
            secret_manager.get_secret("ANKR_API_KEY")
            
            mock_path.assert_called_once_with("ANKR_API_KEY", "latest")
    
    @pytest.mark.unit
    def test_environment_variable_fallback(self, mock_secret_manager):
        """Test fallback to environment variables when Secret Manager fails."""
        from src.secret_manager import SecretManager
        
        # Mock Secret Manager failure
        mock_secret_manager.access_secret_version.side_effect = Exception("Service unavailable")
        
        # Set environment variable as fallback
        os.environ["ANKR_API_KEY"] = "env-api-key"
        
        secret_manager = SecretManager("test-project")
        secret = secret_manager.get_secret("ANKR_API_KEY", fallback_to_env=True)
        
        assert secret == "env-api-key"
        
        # Clean up
        del os.environ["ANKR_API_KEY"]
    
    @pytest.mark.unit
    def test_secret_caching(self, mock_secret_manager, mock_secret_value):
        """Test that secrets are cached after first retrieval."""
        from src.secret_manager import SecretManager
        
        secret_manager = SecretManager("test-project")
        
        # First call should hit the API
        secret1 = secret_manager.get_secret("ANKR_API_KEY")
        assert secret1 == mock_secret_value
        
        # Second call should use cache
        secret2 = secret_manager.get_secret("ANKR_API_KEY")
        assert secret2 == mock_secret_value
        
        # Verify API was only called once
        assert mock_secret_manager.access_secret_version.call_count == 1
    
    @pytest.mark.unit
    def test_cache_invalidation(self, mock_secret_manager, mock_secret_value):
        """Test cache invalidation functionality."""
        from src.secret_manager import SecretManager
        
        secret_manager = SecretManager("test-project")
        
        # First call
        secret1 = secret_manager.get_secret("ANKR_API_KEY")
        assert secret1 == mock_secret_value
        
        # Invalidate cache
        secret_manager.invalidate_cache("ANKR_API_KEY")
        
        # Second call should hit API again
        secret2 = secret_manager.get_secret("ANKR_API_KEY")
        assert secret2 == mock_secret_value
        
        # Verify API was called twice
        assert mock_secret_manager.access_secret_version.call_count == 2
    
    @pytest.mark.unit
    def test_multiple_secrets_handling(self, mock_secret_manager):
        """Test handling of multiple different secrets."""
        from src.secret_manager import SecretManager
        
        # Mock different secrets
        mock_secret1 = Mock()
        mock_secret1.payload.data.decode.return_value = "secret1"
        mock_secret2 = Mock()
        mock_secret2.payload.data.decode.return_value = "secret2"
        
        mock_secret_manager.access_secret_version.side_effect = [mock_secret1, mock_secret2]
        
        secret_manager = SecretManager("test-project")
        
        secret1 = secret_manager.get_secret("SECRET1")
        secret2 = secret_manager.get_secret("SECRET2")
        
        assert secret1 == "secret1"
        assert secret2 == "secret2"
        assert mock_secret_manager.access_secret_version.call_count == 2
    
    @pytest.mark.unit
    def test_error_logging(self, mock_secret_manager, caplog):
        """Test that errors are properly logged."""
        from src.secret_manager import SecretManager, SecretManagerError
        import logging
        
        # Mock logging
        caplog.set_level(logging.ERROR)
        
        # Mock secret manager to raise an exception
        mock_secret_manager.access_secret_version.side_effect = Exception("Test error")
        
        secret_manager = SecretManager("test-project")
        
        with pytest.raises(SecretManagerError):
            secret_manager.get_secret("ANKR_API_KEY")
        
        assert "Test error" in caplog.text
        assert "ERROR" in caplog.text 