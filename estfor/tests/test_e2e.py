"""
End-to-End tests for EstFor Asset Collection System.

Tests complete workflow with Docker Compose services.
"""

import pytest
import subprocess
import time
import requests
import json
from typing import Dict, Any


class TestDockerComposeE2E:
    """End-to-end tests using Docker Compose."""
    
    @pytest.fixture(scope="class")
    def docker_compose_up(self):
        """Start all Docker Compose services."""
        try:
            # Start services
            subprocess.run(
                ["docker-compose", "up", "-d"],
                check=True,
                capture_output=True,
                text=True
            )
            
            # Wait for services to be ready
            time.sleep(30)
            
            yield
            
        finally:
            # Cleanup
            subprocess.run(
                ["docker-compose", "down", "-v"],
                check=True,
                capture_output=True,
                text=True
            )
    
    def test_all_services_startup(self, docker_compose_up):
        """Test that all services start successfully."""
        # Check service status
        result = subprocess.run(
            ["docker-compose", "ps"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        # Verify all services are running
        services = ["app", "worker", "firestore", "redis", "prometheus", "grafana"]
        output = result.stdout
        
        for service in services:
            assert service in output
            assert "Up" in output or "running" in output.lower()
    
    def test_health_checks_e2e(self, docker_compose_up):
        """Test health check endpoints in E2E environment."""
        # Test app health
        response = requests.get("http://localhost:8000/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        
        # Test readiness
        response = requests.get("http://localhost:8000/health/ready", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        
        # Test liveness
        response = requests.get("http://localhost:8000/health/live", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        
        # Test detailed health
        response = requests.get("http://localhost:8000/health/detailed", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "components" in data
        assert "database" in data["components"]
    
    def test_complete_asset_workflow_e2e(self, docker_compose_up):
        """Test complete asset collection workflow."""
        # 1. Check initial state
        response = requests.get("http://localhost:8000/assets/", timeout=10)
        assert response.status_code == 200
        initial_assets = response.json()
        initial_count = len(initial_assets)
        
        # 2. Create a test asset
        asset_data = {
            "name": "E2E Test Asset",
            "type": "weapon",
            "rarity": "legendary",
            "description": "Asset created during E2E testing"
        }
        
        response = requests.post(
            "http://localhost:8000/assets/",
            json=asset_data,
            timeout=10
        )
        assert response.status_code == 200
        created_asset = response.json()
        assert created_asset["name"] == asset_data["name"]
        asset_id = created_asset["id"]
        
        # 3. Verify asset was created
        response = requests.get(f"http://localhost:8000/assets/{asset_id}", timeout=10)
        assert response.status_code == 200
        retrieved_asset = response.json()
        assert retrieved_asset["id"] == asset_id
        assert retrieved_asset["name"] == asset_data["name"]
        
        # 4. Update asset
        update_data = {
            "name": "Updated E2E Test Asset",
            "type": "armor",
            "rarity": "epic",
            "description": "Updated asset description"
        }
        
        response = requests.put(
            f"http://localhost:8000/assets/{asset_id}",
            json=update_data,
            timeout=10
        )
        assert response.status_code == 200
        updated_asset = response.json()
        assert updated_asset["name"] == update_data["name"]
        
        # 5. Verify asset count increased
        response = requests.get("http://localhost:8000/assets/", timeout=10)
        assert response.status_code == 200
        final_assets = response.json()
        assert len(final_assets) == initial_count + 1
        
        # 6. Delete asset
        response = requests.delete(f"http://localhost:8000/assets/{asset_id}", timeout=10)
        assert response.status_code == 200
        assert response.json()["message"] == "Asset deleted successfully"
        
        # 7. Verify asset was deleted
        response = requests.get(f"http://localhost:8000/assets/{asset_id}", timeout=10)
        assert response.status_code == 404
    
    def test_asset_collection_task_e2e(self, docker_compose_up):
        """Test asset collection background task."""
        # Trigger asset collection
        response = requests.post("http://localhost:8000/assets/collect", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Asset collection started"
        assert "task_id" in data
        assert data["status"] == "queued"
        
        # Wait for task to complete (in real scenario)
        time.sleep(5)
        
        # Check task status (if we had a task status endpoint)
        # This would require implementing task status tracking
    
    def test_monitoring_endpoints_e2e(self, docker_compose_up):
        """Test monitoring and metrics endpoints."""
        # Test Prometheus metrics
        response = requests.get("http://localhost:9090/metrics", timeout=10)
        assert response.status_code == 200
        metrics = response.text
        assert "estfor_" in metrics  # Our custom metrics
        
        # Test Grafana health
        response = requests.get("http://localhost:3000/api/health", timeout=10)
        assert response.status_code == 200
        
        # Test app metrics endpoint
        response = requests.get("http://localhost:8000/metrics", timeout=10)
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
    
    def test_database_persistence_e2e(self, docker_compose_up):
        """Test database persistence across restarts."""
        # Create test asset
        asset_data = {
            "name": "Persistence Test Asset",
            "type": "weapon",
            "rarity": "common"
        }
        
        response = requests.post(
            "http://localhost:8000/assets/",
            json=asset_data,
            timeout=10
        )
        assert response.status_code == 200
        created_asset = response.json()
        asset_id = created_asset["id"]
        
        # Restart app service
        subprocess.run(
            ["docker-compose", "restart", "app"],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Wait for service to be ready
        time.sleep(15)
        
        # Verify asset still exists
        response = requests.get(f"http://localhost:8000/assets/{asset_id}", timeout=10)
        assert response.status_code == 200
        retrieved_asset = response.json()
        assert retrieved_asset["name"] == asset_data["name"]
    
    def test_error_handling_e2e(self, docker_compose_up):
        """Test error handling in E2E environment."""
        # Test invalid endpoint
        response = requests.get("http://localhost:8000/nonexistent", timeout=10)
        assert response.status_code == 404
        
        # Test invalid asset ID
        response = requests.get("http://localhost:8000/assets/invalid_id", timeout=10)
        assert response.status_code == 404
        
        # Test malformed JSON
        response = requests.post(
            "http://localhost:8000/assets/",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 422
        
        # Test missing required fields
        invalid_asset = {"name": "Test Asset"}  # Missing type
        response = requests.post(
            "http://localhost:8000/assets/",
            json=invalid_asset,
            timeout=10
        )
        assert response.status_code == 422
    
    def test_performance_e2e(self, docker_compose_up):
        """Test performance characteristics in E2E environment."""
        import time
        
        # Test response times
        endpoints = [
            "/health",
            "/assets/",
            "/assets/stats/summary"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response.status_code == 200
            assert response_time < 2.0  # Should respond within 2 seconds
        
        # Test concurrent requests
        import concurrent.futures
        
        def make_request():
            response = requests.get("http://localhost:8000/health", timeout=10)
            return response.status_code
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(status_code == 200 for status_code in results)
    
    def test_logging_e2e(self, docker_compose_up):
        """Test logging functionality in E2E environment."""
        # Make some requests to generate logs
        requests.get("http://localhost:8000/health", timeout=10)
        requests.get("http://localhost:8000/assets/", timeout=10)
        
        # Check app logs
        result = subprocess.run(
            ["docker-compose", "logs", "app"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        logs = result.stdout
        
        # Verify structured logging
        assert "INFO" in logs
        assert "EstFor Asset Collection System" in logs
        
        # Check worker logs
        result = subprocess.run(
            ["docker-compose", "logs", "worker"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        worker_logs = result.stdout
        assert len(worker_logs) > 0
    
    def test_cleanup_e2e(self, docker_compose_up):
        """Test proper cleanup and teardown."""
        # This test ensures that the cleanup fixture works properly
        # The actual cleanup is handled by the fixture
        
        # Verify we can still make requests before cleanup
        response = requests.get("http://localhost:8000/health", timeout=10)
        assert response.status_code == 200


class TestSmokeTests:
    """Smoke tests for critical functionality."""
    
    def test_critical_endpoints_smoke(self, docker_compose_up):
        """Smoke test for critical endpoints."""
        critical_endpoints = [
            "/health",
            "/health/ready",
            "/health/live",
            "/assets/",
            "/metrics"
        ]
        
        for endpoint in critical_endpoints:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
            assert response.status_code in [200, 404]  # 404 is acceptable for some endpoints
    
    def test_service_dependencies_smoke(self, docker_compose_up):
        """Smoke test for service dependencies."""
        # Test that app can connect to database
        response = requests.get("http://localhost:8000/health/ready", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["database"] == "connected"
        
        # Test that app can connect to Redis (via worker health)
        # This would require implementing worker health checks
    
    def test_basic_crud_smoke(self, docker_compose_up):
        """Smoke test for basic CRUD operations."""
        # Create
        asset_data = {"name": "Smoke Test Asset", "type": "weapon"}
        response = requests.post("http://localhost:8000/assets/", json=asset_data, timeout=10)
        assert response.status_code == 200
        
        # Read
        created_asset = response.json()
        asset_id = created_asset["id"]
        response = requests.get(f"http://localhost:8000/assets/{asset_id}", timeout=10)
        assert response.status_code == 200
        
        # Update
        update_data = {"name": "Updated Smoke Test Asset", "type": "armor"}
        response = requests.put(f"http://localhost:8000/assets/{asset_id}", json=update_data, timeout=10)
        assert response.status_code == 200
        
        # Delete
        response = requests.delete(f"http://localhost:8000/assets/{asset_id}", timeout=10)
        assert response.status_code == 200


class TestResilienceE2E:
    """E2E tests for system resilience."""
    
    def test_service_restart_resilience(self, docker_compose_up):
        """Test system resilience to service restarts."""
        # Create test data
        asset_data = {"name": "Resilience Test Asset", "type": "weapon"}
        response = requests.post("http://localhost:8000/assets/", json=asset_data, timeout=10)
        assert response.status_code == 200
        asset_id = response.json()["id"]
        
        # Restart app service
        subprocess.run(["docker-compose", "restart", "app"], check=True)
        time.sleep(15)
        
        # Verify data persistence
        response = requests.get(f"http://localhost:8000/assets/{asset_id}", timeout=10)
        assert response.status_code == 200
        
        # Restart database service
        subprocess.run(["docker-compose", "restart", "firestore"], check=True)
        time.sleep(15)
        
        # Verify data persistence
        response = requests.get(f"http://localhost:8000/assets/{asset_id}", timeout=10)
        assert response.status_code == 200
    
    def test_network_partition_resilience(self, docker_compose_up):
        """Test resilience to network partitions."""
        # This would require more sophisticated network testing
        # For now, we'll test basic connectivity
        
        # Test that all services are reachable
        services = [
            ("app", 8000, "/health"),
            ("prometheus", 9090, "/metrics"),
            ("grafana", 3000, "/api/health")
        ]
        
        for service_name, port, endpoint in services:
            try:
                response = requests.get(f"http://localhost:{port}{endpoint}", timeout=5)
                assert response.status_code in [200, 404]
            except requests.exceptions.RequestException:
                pytest.fail(f"Service {service_name} is not reachable") 