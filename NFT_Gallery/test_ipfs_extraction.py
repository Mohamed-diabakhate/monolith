#!/usr/bin/env python3
"""
Test script to verify IPFS metadata extraction functionality.
"""
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.nft_processor import NFTProcessor, NFTProcessorError


def test_ipfs_metadata_extraction():
    """Test IPFS metadata extraction functionality."""
    print("Testing IPFS Metadata Extraction...")
    
    # Create a mock processor (without API key)
    try:
        processor = NFTProcessor("test_wallet", "~/Pictures/SolanaNFTs")
        
        # Test cases for different NFT metadata structures
        test_cases = [
            {
                "name": "Standard IPFS Metadata",
                "asset": {
                    "id": "test1",
                    "metadata": {
                        "uri": "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
                    }
                }
            },
            {
                "name": "Arweave Metadata",
                "asset": {
                    "id": "test2",
                    "metadata": {
                        "uri": "ar://jK4utkbAoAHjJqo3XJnP8KqH7KqH7KqH7KqH7KqH7KqH7"
                    }
                }
            },
            {
                "name": "HTTP Metadata",
                "asset": {
                    "id": "test3",
                    "metadata": {
                        "uri": "https://example.com/metadata.json"
                    }
                }
            },
            {
                "name": "Direct URI in Asset",
                "asset": {
                    "id": "test4",
                    "uri": "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
                }
            },
            {
                "name": "Content Metadata URI",
                "asset": {
                    "id": "test5",
                    "content": {
                        "metadata": {
                            "uri": "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
                        }
                    }
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\nTest {i+1}: {test_case['name']}")
            
            # Test metadata URI extraction
            metadata_uri = processor._get_metadata_uri(test_case['asset'])
            print(f"  Metadata URI: {metadata_uri}")
            
            # Test image URL extraction (this will try to fetch metadata)
            image_url = processor._extract_image_url(test_case['asset'])
            print(f"  Image URL: {image_url}")
        
        print("\nIPFS Metadata Extraction tests completed!")
        
    except NFTProcessorError as e:
        print(f"Could not test NFT processor (expected without API key): {e}")


def test_metadata_parsing():
    """Test metadata parsing with sample data."""
    print("\nTesting Metadata Parsing...")
    
    try:
        processor = NFTProcessor("test_wallet", "~/Pictures/SolanaNFTs")
        
        # Sample metadata structures
        sample_metadata = [
            {
                "name": "Standard Image Field",
                "metadata": {
                    "image": "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
                }
            },
            {
                "name": "Properties Files",
                "metadata": {
                    "properties": {
                        "files": [
                            {
                                "type": "image/png",
                                "uri": "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
                            }
                        ]
                    }
                }
            },
            {
                "name": "Multiple Image Fields",
                "metadata": {
                    "image": "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
                    "image_url": "https://example.com/image.png",
                    "imageUrl": "ar://jK4utkbAoAHjJqo3XJnP8KqH7KqH7KqH7KqH7KqH7KqH7"
                }
            }
        ]
        
        for i, sample in enumerate(sample_metadata):
            print(f"\nSample {i+1}: {sample['name']}")
            image_url = processor._extract_image_from_metadata(sample['metadata'])
            print(f"  Extracted Image URL: {image_url}")
        
        print("\nMetadata Parsing tests completed!")
        
    except NFTProcessorError as e:
        print(f"Could not test metadata parsing: {e}")


def test_ipfs_gateway_handling():
    """Test IPFS gateway handling."""
    print("\nTesting IPFS Gateway Handling...")
    
    try:
        processor = NFTProcessor("test_wallet", "~/Pictures/SolanaNFTs")
        
        # Test IPFS URI handling
        test_uris = [
            "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
            "ar://jK4utkbAoAHjJqo3XJnP8KqH7KqH7KqH7KqH7KqH7KqH7",
            "https://nftstorage.link/ipfs/QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
        ]
        
        for uri in test_uris:
            print(f"\nTesting URI: {uri}")
            try:
                # This will attempt to fetch from gateways
                metadata = processor._fetch_metadata(uri)
                if metadata:
                    print(f"  Successfully fetched metadata: {type(metadata)}")
                    if isinstance(metadata, dict):
                        print(f"  Metadata keys: {list(metadata.keys())}")
                else:
                    print(f"  Failed to fetch metadata (expected for test URIs)")
            except Exception as e:
                print(f"  Error fetching metadata: {str(e)}")
        
        print("\nIPFS Gateway tests completed!")
        
    except NFTProcessorError as e:
        print(f"Could not test IPFS gateway handling: {e}")


def main():
    """Run all IPFS extraction tests."""
    print("=== Testing IPFS Metadata Extraction ===\n")
    
    test_ipfs_metadata_extraction()
    test_metadata_parsing()
    test_ipfs_gateway_handling()
    
    print("\n=== All Tests Completed ===")
    print("\nThe IPFS metadata extraction system is designed to:")
    print("1. Extract metadata URIs from NFT assets")
    print("2. Fetch metadata from IPFS, Arweave, or HTTP sources")
    print("3. Parse metadata to find image URLs")
    print("4. Handle multiple IPFS gateways for redundancy")
    print("5. Support various metadata formats and structures")
    
    print("\nTo test with real data, run:")
    print("python main.py --wallet YOUR_WALLET_ADDRESS --retry-failed --verbose")


if __name__ == "__main__":
    main() 