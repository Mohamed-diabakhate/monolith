"""
End-to-End Smoke Tests for Solana NFT Downloader.
Tests complete workflow scenarios via Docker Compose.
"""
import pytest
import requests
import time
import os
from pathlib import Path
import subprocess
import json


class TestSmokeScenarios:
    """End-to-end smoke test scenarios."""
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_fresh_wallet_download(self, docker_compose_test):
        """Test complete workflow for fresh wallet download."""
        # Start test environment
        docker_compose_test.up(detached=True)
        
        try:
            # Wait for services to be ready
            self._wait_for_services_ready()
            
            # Execute NFT download for fresh wallet
            result = docker_compose_test.run(
                "nft-downloader-test",
                "python -m src.main --wallet test-wallet-address --output /app/test-data"
            )
            
            # Verify successful execution
            assert result.returncode == 0
            
            # Check that files were downloaded
            output_dir = Path("test-data")
            assert output_dir.exists()
            
            # Verify specific files exist
            expected_files = [
                "test-nft-1.jpg",
                "test-nft-2.png"
            ]
            
            for filename in expected_files:
                file_path = output_dir / filename
                assert file_path.exists(), f"Expected file {filename} not found"
                assert file_path.stat().st_size > 0, f"File {filename} is empty"
            
            # Verify test coverage report was generated
            coverage_dir = Path("test-data/htmlcov")
            assert coverage_dir.exists()
            assert (coverage_dir / "index.html").exists()
            
        finally:
            # Cleanup
            docker_compose_test.down()
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_incremental_download(self, docker_compose_test):
        """Test incremental download with existing files."""
        # Start test environment
        docker_compose_test.up(detached=True)
        
        try:
            # Wait for services to be ready
            self._wait_for_services_ready()
            
            # Create existing file to simulate incremental scenario
            output_dir = Path("test-data")
            output_dir.mkdir(exist_ok=True)
            existing_file = output_dir / "existing-nft.jpg"
            existing_file.write_bytes(b"existing-file-content")
            
            # Execute NFT download
            result = docker_compose_test.run(
                "nft-downloader-test",
                "python -m src.main --wallet test-wallet-address --output /app/test-data"
            )
            
            # Verify successful execution
            assert result.returncode == 0
            
            # Verify existing file was preserved
            assert existing_file.exists()
            assert existing_file.read_bytes() == b"existing-file-content"
            
            # Verify new files were downloaded
            expected_files = [
                "test-nft-1.jpg",
                "test-nft-2.png"
            ]
            
            for filename in expected_files:
                file_path = output_dir / filename
                assert file_path.exists(), f"Expected file {filename} not found"
            
        finally:
            # Cleanup
            docker_compose_test.down()
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_large_collection_processing(self, docker_compose_test):
        """Test processing of large NFT collection (1000+ NFTs)."""
        # Start test environment with large dataset
        docker_compose_test.up(detached=True)
        
        try:
            # Wait for services to be ready
            self._wait_for_services_ready()
            
            # Execute download for large wallet
            result = docker_compose_test.run(
                "nft-downloader-test",
                "python -m src.main --wallet large-wallet-address --output /app/test-data"
            )
            
            # Verify successful execution
            assert result.returncode == 0
            
            # Check performance metrics
            output_dir = Path("test-data")
            downloaded_files = list(output_dir.glob("*.jpg")) + list(output_dir.glob("*.png"))
            
            # Should have processed many files
            assert len(downloaded_files) >= 100
            
            # Verify all files are valid
            for file_path in downloaded_files:
                assert file_path.stat().st_size > 0, f"File {file_path} is empty"
            
        finally:
            # Cleanup
            docker_compose_test.down()
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_mixed_media_types_handling(self, docker_compose_test):
        """Test handling of mixed media types (images, videos, etc.)."""
        # Start test environment
        docker_compose_test.up(detached=True)
        
        try:
            # Wait for services to be ready
            self._wait_for_services_ready()
            
            # Execute download for wallet with mixed media
            result = docker_compose_test.run(
                "nft-downloader-test",
                "python -m src.main --wallet mixed-media-wallet --output /app/test-data"
            )
            
            # Verify successful execution
            assert result.returncode == 0
            
            # Check for different file types
            output_dir = Path("test-data")
            jpg_files = list(output_dir.glob("*.jpg"))
            png_files = list(output_dir.glob("*.png"))
            gif_files = list(output_dir.glob("*.gif"))
            mp4_files = list(output_dir.glob("*.mp4"))
            
            # Should have multiple file types
            assert len(jpg_files) > 0, "No JPG files found"
            assert len(png_files) > 0, "No PNG files found"
            
            # Verify file integrity
            all_files = jpg_files + png_files + gif_files + mp4_files
            for file_path in all_files:
                assert file_path.stat().st_size > 0, f"File {file_path} is empty"
            
        finally:
            # Cleanup
            docker_compose_test.down()
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_error_recovery_scenarios(self, docker_compose_test):
        """Test error recovery and resilience scenarios."""
        # Start test environment
        docker_compose_test.up(detached=True)
        
        try:
            # Wait for services to be ready
            self._wait_for_services_ready()
            
            # Test with invalid wallet (should handle gracefully)
            result = docker_compose_test.run(
                "nft-downloader-test",
                "python -m src.main --wallet invalid-wallet --output /app/test-data"
            )
            
            # Should handle error gracefully (non-zero exit but no crash)
            assert result.returncode != 0
            
            # Test with rate-limited wallet
            result = docker_compose_test.run(
                "nft-downloader-test",
                "python -m src.main --wallet rate-limited-wallet --output /app/test-data"
            )
            
            # Should handle rate limiting gracefully
            assert result.returncode != 0
            
            # Verify error logs were generated
            log_dir = Path("test-data/logs")
            if log_dir.exists():
                log_files = list(log_dir.glob("*.log"))
                assert len(log_files) > 0, "No error logs generated"
            
        finally:
            # Cleanup
            docker_compose_test.down()
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_cleanup_and_teardown(self, docker_compose_test):
        """Test proper cleanup and environment teardown."""
        # Start test environment
        docker_compose_test.up(detached=True)
        
        try:
            # Wait for services to be ready
            self._wait_for_services_ready()
            
            # Execute some operations
            result = docker_compose_test.run(
                "nft-downloader-test",
                "python -m src.main --wallet test-wallet-address --output /app/test-data"
            )
            
            # Verify successful execution
            assert result.returncode == 0
            
        finally:
            # Test cleanup
            docker_compose_test.down()
            
            # Verify containers are stopped
            containers = docker_compose_test.ps()
            assert len(containers) == 0, "Containers not properly stopped"
            
            # Verify test data cleanup (if configured)
            if os.getenv("CLEANUP_TEST_DATA", "true").lower() == "true":
                test_data_dir = Path("test-data")
                if test_data_dir.exists():
                    # Should only contain coverage reports, not downloaded files
                    downloaded_files = list(test_data_dir.glob("*.jpg")) + list(test_data_dir.glob("*.png"))
                    assert len(downloaded_files) == 0, "Downloaded files not cleaned up"
    
    def _wait_for_services_ready(self, timeout=60):
        """Wait for all services to be ready."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check mock Ankr API
                response = requests.get("http://localhost:8080/status", timeout=5)
                if response.status_code == 200:
                    # Check mock Secret Manager
                    response = requests.get("http://localhost:8085", timeout=5)
                    if response.status_code == 200:
                        return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        raise TimeoutError("Services not ready within timeout period")


@pytest.fixture(scope="class")
def docker_compose_test():
    """Docker Compose test fixture."""
    import docker
    
    client = docker.from_env()
    
    class DockerComposeTest:
        def __init__(self, client):
            self.client = client
            self.project_name = "nft-downloader-test"
        
        def up(self, detached=False):
            """Start test environment."""
            subprocess.run([
                "docker-compose", "-f", "docker-compose.test.yml",
                "-p", self.project_name, "up", "-d" if detached else ""
            ], check=True)
        
        def down(self):
            """Stop test environment."""
            subprocess.run([
                "docker-compose", "-f", "docker-compose.test.yml",
                "-p", self.project_name, "down", "-v"
            ], check=True)
        
        def run(self, service, command):
            """Run command in service."""
            return subprocess.run([
                "docker-compose", "-f", "docker-compose.test.yml",
                "-p", self.project_name, "run", "--rm", service
            ] + command.split(), capture_output=True, text=True)
        
        def ps(self):
            """List running containers."""
            return self.client.containers.list(
                filters={"label": f"com.docker.compose.project={self.project_name}"}
            )
    
    return DockerComposeTest(client) 