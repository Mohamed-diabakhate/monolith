#!/usr/bin/env python3
"""
Test Runner for Solana NFT Downloader.
Executes tests with coverage reporting and generates test reports.
"""
import subprocess
import sys
import os
import argparse
from pathlib import Path
import json
import time


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return None


def run_unit_tests():
    """Run unit tests with coverage."""
    cmd = [
        "python", "-m", "pytest",
        "tests/unit/",
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html:test-data/htmlcov",
        "--cov-fail-under=80"
    ]
    return run_command(cmd, "Unit Tests")


def run_integration_tests():
    """Run integration tests."""
    cmd = [
        "python", "-m", "pytest",
        "tests/integration/",
        "-v",
        "--cov=src",
        "--cov-append"
    ]
    return run_command(cmd, "Integration Tests")


def run_e2e_tests():
    """Run end-to-end tests via Docker Compose."""
    cmd = [
        "docker-compose", "-f", "docker-compose.test.yml",
        "up", "--build", "--abort-on-container-exit"
    ]
    return run_command(cmd, "End-to-End Tests")


def run_all_tests():
    """Run all test suites."""
    print("🧪 Starting Comprehensive Test Suite")
    print("=" * 50)
    
    # Create test data directory
    Path("test-data").mkdir(exist_ok=True)
    
    # Run unit tests
    unit_result = run_unit_tests()
    if not unit_result:
        print("❌ Unit tests failed. Stopping.")
        return False
    
    # Run integration tests
    integration_result = run_integration_tests()
    if not integration_result:
        print("❌ Integration tests failed. Stopping.")
        return False
    
    # Run E2E tests
    e2e_result = run_e2e_tests()
    if not e2e_result:
        print("❌ E2E tests failed.")
        return False
    
    print("\n✅ All test suites completed successfully!")
    return True


def generate_test_report():
    """Generate comprehensive test report."""
    print("\n📊 Generating Test Report...")
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_suites": {
            "unit": {"status": "unknown", "coverage": 0},
            "integration": {"status": "unknown", "coverage": 0},
            "e2e": {"status": "unknown"}
        },
        "overall_status": "unknown"
    }
    
    # Check coverage report
    coverage_file = Path("test-data/htmlcov/index.html")
    if coverage_file.exists():
        print("📈 Coverage report available at: test-data/htmlcov/index.html")
    
    # Check JUnit XML report
    junit_file = Path("test-data/junit.xml")
    if junit_file.exists():
        print("📋 JUnit report available at: test-data/junit.xml")
    
    # Save report
    report_file = Path("test-data/test_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Test report saved to: {report_file}")
    
    return report


def cleanup_test_environment():
    """Clean up test environment."""
    print("\n🧹 Cleaning up test environment...")
    
    # Stop Docker containers
    cmd = ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"]
    run_command(cmd, "Stopping Docker containers")
    
    # Clean up test data (optional)
    if os.getenv("CLEANUP_TEST_DATA", "false").lower() == "true":
        import shutil
        test_data_dir = Path("test-data")
        if test_data_dir.exists():
            shutil.rmtree(test_data_dir)
            print("🗑️ Test data cleaned up")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Test Runner for Solana NFT Downloader")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--e2e", action="store_true", help="Run only E2E tests")
    parser.add_argument("--cleanup", action="store_true", help="Clean up test environment")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup_test_environment()
        return
    
    if args.report:
        generate_test_report()
        return
    
    # Run specific test suite or all tests
    if args.unit:
        success = run_unit_tests() is not None
    elif args.integration:
        success = run_integration_tests() is not None
    elif args.e2e:
        success = run_e2e_tests() is not None
    else:
        success = run_all_tests()
    
    # Generate report
    if success:
        generate_test_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 