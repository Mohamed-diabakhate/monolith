#!/usr/bin/env python3
"""
Test script for Firestore image download functionality.
"""
import os
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.firestore_manager import FirestoreManager
from src.file_manager import FileManager
from src.firestore_image_downloader import FirestoreImageDownloader


def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def test_firestore_downloader():
    """Test the Firestore image downloader functionality."""
    logger = setup_logging()
    
    try:
        # Initialize components
        logger.info("Initializing Firestore manager...")
        firestore_manager = FirestoreManager()
        
        logger.info("Initializing file manager...")
        file_manager = FileManager("~/Pictures/NFTs/test")
        
        logger.info("Initializing Firestore image downloader...")
        downloader = FirestoreImageDownloader(
            firestore_manager, 
            file_manager,
            max_concurrent_downloads=3,
            max_retries=2
        )
        
        # Test 1: Get download statistics
        logger.info("Testing download statistics...")
        stats = firestore_manager.get_download_statistics()
        logger.info(f"Download statistics: {stats}")
        
        # Test 2: Get pending downloads
        logger.info("Testing pending downloads query...")
        pending_docs = firestore_manager.get_nfts_by_download_status("pending", limit=5)
        logger.info(f"Found {len(pending_docs)} pending downloads")
        
        # Test 3: Get failed downloads
        logger.info("Testing failed downloads query...")
        failed_docs = firestore_manager.get_nfts_by_download_status("failed", limit=5)
        logger.info(f"Found {len(failed_docs)} failed downloads")
        
        # Test 4: Test download progress
        logger.info("Testing download progress...")
        progress = downloader.get_download_progress()
        logger.info(f"Download progress: {progress}")
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    return True


def test_download_operations():
    """Test actual download operations (requires existing data)."""
    logger = setup_logging()
    
    try:
        # Initialize components
        firestore_manager = FirestoreManager()
        file_manager = FileManager("~/Pictures/NFTs/test")
        downloader = FirestoreImageDownloader(
            firestore_manager, 
            file_manager,
            max_concurrent_downloads=2,
            max_retries=1
        )
        
        # Test download pending (small batch)
        logger.info("Testing download pending images (batch size 2)...")
        results = downloader.download_pending_images(batch_size=2)
        logger.info(f"Download results: {results}")
        
        # Test retry failed (small batch)
        logger.info("Testing retry failed downloads...")
        retry_results = downloader.retry_failed_downloads(max_attempts=2)
        logger.info(f"Retry results: {retry_results}")
        
        logger.info("Download operations test completed!")
        
    except Exception as e:
        logger.error(f"Download operations test failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    return True


if __name__ == "__main__":
    print("=== Firestore Image Downloader Test ===")
    
    # Test basic functionality
    print("\n1. Testing basic functionality...")
    if test_firestore_downloader():
        print("✅ Basic functionality test passed")
    else:
        print("❌ Basic functionality test failed")
        sys.exit(1)
    
    # Test download operations (optional - requires existing data)
    print("\n2. Testing download operations...")
    if test_download_operations():
        print("✅ Download operations test passed")
    else:
        print("⚠️  Download operations test failed (may be expected if no data exists)")
    
    print("\n=== Test completed ===") 