#!/usr/bin/env python3
"""
Test script to verify the improvements for handling missing NFTs.
"""
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.file_manager import FileManager, FileManagerError
from src.nft_processor import NFTProcessor, NFTProcessorError


def test_file_manager_improvements():
    """Test the improved file manager functionality."""
    print("Testing File Manager improvements...")
    
    # Create a temporary file manager
    file_manager = FileManager("~/Pictures/SolanaNFTs")
    
    # Test problematic domain handling
    test_urls = [
        "https://www.hi-hi.vip/json/5000wif.json",
        "https://img.hi-hi.vip/json/img/5000wif.png",
        "https://nftstorage.link/ipfs/bafybeiahfsbxvuvvwyxvual6o43f56wx3ciiylh7b37eekrqd76fruggl4"
    ]
    
    for url in test_urls:
        fixed_url = file_manager._handle_problematic_domains(url)
        print(f"Original: {url}")
        print(f"Fixed: {fixed_url}")
        print()
    
    # Test error classification
    test_errors = [
        "403 Client Error: Forbidden",
        "404 Client Error: Not Found",
        "SSL: WRONG_VERSION_NUMBER",
        "Timeout",
        "Connection error"
    ]
    
    for error_str in test_errors:
        class MockError:
            def __init__(self, msg):
                self.msg = msg
            def __str__(self):
                return self.msg
        
        error = MockError(error_str)
        should_retry = file_manager._should_retry_error(error)
        print(f"Error: {error_str} -> Should retry: {should_retry}")
    
    print("File Manager tests completed!\n")


def test_nft_processor_improvements():
    """Test the improved NFT processor functionality."""
    print("Testing NFT Processor improvements...")
    
    # Test image URL extraction with various formats
    test_assets = [
        {
            "id": "test1",
            "content": {
                "files": [
                    {"mime": "image/png", "uri": "https://example.com/image.png"}
                ]
            }
        },
        {
            "id": "test2",
            "content": {
                "links": {
                    "image": "https://example.com/image.jpg"
                }
            }
        },
        {
            "id": "test3",
            "content": {
                "metadata": {
                    "image": "https://example.com/image.gif",
                    "external_url": "https://ipfs.io/ipfs/QmHash"
                }
            }
        }
    ]
    
    # Create a mock processor (without API key)
    try:
        processor = NFTProcessor("test_wallet", "~/Pictures/SolanaNFTs")
        
        for i, asset in enumerate(test_assets):
            image_url = processor._extract_image_url(asset)
            print(f"Test {i+1}: {image_url}")
        
        print("NFT Processor tests completed!\n")
        
    except NFTProcessorError as e:
        print(f"Could not test NFT processor (expected without API key): {e}\n")


def main():
    """Run all tests."""
    print("=== Testing NFT Downloader Improvements ===\n")
    
    test_file_manager_improvements()
    test_nft_processor_improvements()
    
    print("All tests completed!")
    print("\nTo test with real data, run:")
    print("python main.py --wallet YOUR_WALLET_ADDRESS --retry-failed --max-retries 5")


if __name__ == "__main__":
    main() 