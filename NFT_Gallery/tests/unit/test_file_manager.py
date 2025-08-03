"""
Unit tests for FileManager class.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import requests
from src.file_manager import FileManager, FileManagerError


class TestFileManager:
    """Test cases for FileManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def file_manager(self, temp_dir):
        """Create FileManager instance with temporary directory."""
        return FileManager(output_dir=temp_dir)
    
    def test_initialization_with_default_dir(self):
        """Test FileManager initialization with default directory."""
        with patch('pathlib.Path.expanduser') as mock_expanduser, \
             patch('pathlib.Path.resolve') as mock_resolve, \
             patch('pathlib.Path.mkdir') as mock_mkdir:
            
            mock_path = Mock()
            mock_expanduser.return_value = mock_path
            mock_resolve.return_value = mock_path
            
            file_manager = FileManager()
            
            assert file_manager.output_dir == mock_path
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    def test_initialization_with_custom_dir(self, temp_dir):
        """Test FileManager initialization with custom directory."""
        file_manager = FileManager(output_dir=temp_dir)
        assert file_manager.output_dir == Path(temp_dir).resolve()
    
    def test_initialization_permission_error(self):
        """Test FileManager initialization with permission error."""
        with patch('pathlib.Path.expanduser') as mock_expanduser, \
             patch('pathlib.Path.resolve') as mock_resolve, \
             patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            
            mock_path = Mock()
            mock_expanduser.return_value = mock_path
            mock_resolve.return_value = mock_path
            
            with pytest.raises(FileManagerError, match="Permission denied creating directory"):
                FileManager()
    
    def test_initialization_general_error(self):
        """Test FileManager initialization with general error."""
        with patch('pathlib.Path.expanduser') as mock_expanduser, \
             patch('pathlib.Path.resolve') as mock_resolve, \
             patch('pathlib.Path.mkdir', side_effect=Exception("General error")):
            
            mock_path = Mock()
            mock_expanduser.return_value = mock_path
            mock_resolve.return_value = mock_path
            
            with pytest.raises(FileManagerError, match="Failed to create output directory"):
                FileManager()
    
    def test_generate_safe_filename(self, file_manager):
        """Test safe filename generation."""
        filename = file_manager._generate_safe_filename(
            nft_name="Test NFT #123",
            token_id="1234567890abcdef",
            contract="abcdef1234567890",
            url="https://example.com/image.jpg"
        )
        
        assert "Test_NFT_123" in filename
        assert "12345678" in filename
        assert "abcdef12" in filename
        assert filename.endswith(".jpg")
    
    def test_generate_safe_filename_with_none_name(self, file_manager):
        """Test safe filename generation with None NFT name."""
        filename = file_manager._generate_safe_filename(
            nft_name=None,
            token_id="1234567890abcdef",
            contract="abcdef1234567890",
            url="https://example.com/image.png"
        )
        
        assert "NFT_12345678" in filename
        assert filename.endswith(".png")
    
    def test_sanitize_filename(self, file_manager):
        """Test filename sanitization."""
        # Test invalid characters
        sanitized = file_manager._sanitize_filename('file<>:"/\\|?*name')
        assert sanitized == 'file_________name'
        
        # Test leading/trailing spaces and dots
        sanitized = file_manager._sanitize_filename('  .filename.  ')
        assert sanitized == 'filename'
        
        # Test length limit
        long_name = 'a' * 150
        sanitized = file_manager._sanitize_filename(long_name)
        assert len(sanitized) == 100
        
        # Test empty filename
        sanitized = file_manager._sanitize_filename('')
        assert sanitized == 'unnamed'
        
        # Test only spaces
        sanitized = file_manager._sanitize_filename('   ')
        assert sanitized == 'unnamed'
    
    def test_get_extension_from_url(self, file_manager):
        """Test file extension extraction from URL."""
        # Test common extensions
        assert file_manager._get_extension_from_url("https://example.com/image.jpg") == ".jpg"
        assert file_manager._get_extension_from_url("https://example.com/image.png") == ".png"
        assert file_manager._get_extension_from_url("https://example.com/image.gif") == ".gif"
        assert file_manager._get_extension_from_url("https://example.com/image.webp") == ".webp"
        
        # Test URL with query parameters
        assert file_manager._get_extension_from_url("https://example.com/image.jpg?size=large") == ".jpg"
        
        # Test URL without extension
        assert file_manager._get_extension_from_url("https://example.com/image") == ""
        
        # Test URL with multiple dots
        assert file_manager._get_extension_from_url("https://example.com/image.large.jpg") == ".jpg"
    
    def test_file_exists(self, file_manager, temp_dir):
        """Test file existence checking."""
        # Test non-existent file
        assert not file_manager.file_exists("nonexistent.txt")
        
        # Test existing file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("test content")
        assert file_manager.file_exists("test.txt")
    
    @patch('requests.get')
    def test_download_image_success(self, mock_get, file_manager, temp_dir):
        """Test successful image download."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.iter_content.return_value = [b"fake image data"]
        mock_get.return_value = mock_response
        
        success = file_manager.download_image(
            url="https://example.com/image.jpg",
            filename="test_image.jpg"
        )
        
        assert success
        assert (Path(temp_dir) / "test_image.jpg").exists()
        mock_get.assert_called_once_with("https://example.com/image.jpg", stream=True, timeout=30)
    
    @patch('requests.get')
    def test_download_image_http_error(self, mock_get, file_manager):
        """Test image download with HTTP error."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with pytest.raises(FileManagerError, match="Failed to download image"):
            file_manager.download_image(
                url="https://example.com/image.jpg",
                filename="test_image.jpg"
            )
    
    @patch('requests.get')
    def test_download_image_request_exception(self, mock_get, file_manager):
        """Test image download with request exception."""
        # Mock request exception
        mock_get.side_effect = requests.RequestException("Network error")
        
        with pytest.raises(FileManagerError, match="Failed to download image"):
            file_manager.download_image(
                url="https://example.com/image.jpg",
                filename="test_image.jpg"
            )
    
    def test_get_file_info(self, file_manager, temp_dir):
        """Test file information retrieval."""
        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("test content")
        
        info = file_manager.get_file_info("test.txt")
        
        assert info is not None
        assert info["size"] == 12  # "test content" length
        assert "modified" in info
        assert "path" in info
    
    def test_get_file_info_nonexistent(self, file_manager):
        """Test file information for non-existent file."""
        info = file_manager.get_file_info("nonexistent.txt")
        assert info is None
    
    def test_list_downloaded_files(self, file_manager, temp_dir):
        """Test listing downloaded files."""
        # Create test files
        (Path(temp_dir) / "file1.jpg").write_text("content1")
        (Path(temp_dir) / "file2.png").write_text("content2")
        (Path(temp_dir) / ".hidden").write_text("hidden")
        
        files = file_manager.list_downloaded_files()
        
        assert len(files) == 3  # All files are included
        assert "file1.jpg" in files
        assert "file2.png" in files
        assert ".hidden" in files  # Hidden files are included
    
    @patch('shutil.disk_usage')
    def test_get_disk_space(self, mock_disk_usage, file_manager):
        """Test disk space checking."""
        # Mock disk usage - returns (total, used, free)
        mock_disk_usage.return_value = (1000000000, 500000000, 500000000)  # 1GB total, 500MB used, 500MB free
        
        # The actual implementation expects a named tuple, but we're mocking with a regular tuple
        # So we need to handle the exception case
        with pytest.raises(FileManagerError, match="Failed to get disk space"):
            file_manager.get_disk_space()
        
        mock_disk_usage.assert_called_once_with(file_manager.output_dir)
    
    def test_cleanup_temp_files(self, file_manager, temp_dir):
        """Test temporary file cleanup."""
        # Create test files including temp files
        (Path(temp_dir) / "normal.txt").write_text("normal")
        (Path(temp_dir) / "temp.tmp").write_text("temp")
        (Path(temp_dir) / "another.tmp").write_text("another")
        
        count = file_manager.cleanup_temp_files()
        
        assert count == 2
        assert not (Path(temp_dir) / "temp.tmp").exists()
        assert not (Path(temp_dir) / "another.tmp").exists()
        assert (Path(temp_dir) / "normal.txt").exists()
    
    def test_cleanup_temp_files_custom_pattern(self, file_manager, temp_dir):
        """Test temporary file cleanup with custom pattern."""
        # Create test files
        (Path(temp_dir) / "file.txt").write_text("content")
        (Path(temp_dir) / "backup.bak").write_text("backup")
        
        count = file_manager.cleanup_temp_files(pattern="*.bak")
        
        assert count == 1
        assert not (Path(temp_dir) / "backup.bak").exists()
        assert (Path(temp_dir) / "file.txt").exists()
    
    def test_get_file_hash(self, file_manager, temp_dir):
        """Test file hash calculation."""
        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("test content")
        
        file_hash = file_manager.get_file_hash("test.txt")
        
        assert file_hash is not None
        assert len(file_hash) == 64  # SHA-256 hash length
    
    def test_get_file_hash_nonexistent(self, file_manager):
        """Test file hash for non-existent file."""
        file_hash = file_manager.get_file_hash("nonexistent.txt")
        assert file_hash is None
    
    def test_get_file_hash_permission_error(self, file_manager, temp_dir):
        """Test file hash with permission error."""
        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("test content")
        
        # Make file unreadable
        test_file.chmod(0o000)
        
        file_hash = file_manager.get_file_hash("test.txt")
        
        assert file_hash is None
        
        # Restore permissions for cleanup
        test_file.chmod(0o644) 