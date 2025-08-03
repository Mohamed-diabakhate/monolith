#!/usr/bin/env python3
"""
Simple test script to verify IPFS metadata extraction functionality without API key.
"""
import requests


def test_ipfs_gateway_handling():
    """Test IPFS gateway handling."""
    print("Testing IPFS Gateway Handling...")
    
    # Test IPFS URI handling
    test_uris = [
        "ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
        "ar://jK4utkbAoAHjJqo3XJnP8KqH7KqH7KqH7KqH7KqH7KqH7",
        "https://nftstorage.link/ipfs/QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
    ]
    
    for uri in test_uris:
        print(f"\nTesting URI: {uri}")
        
        # Convert IPFS URI to HTTP URLs
        if uri.startswith('ipfs://'):
            ipfs_hash = uri.replace('ipfs://', '')
            gateways = [
                f'https://ipfs.io/ipfs/{ipfs_hash}',
                f'https://cloudflare-ipfs.com/ipfs/{ipfs_hash}',
                f'https://gateway.pinata.cloud/ipfs/{ipfs_hash}',
                f'https://dweb.link/ipfs/{ipfs_hash}',
                f'https://nftstorage.link/ipfs/{ipfs_hash}'
            ]
            print(f"  Converted to gateways: {gateways[:2]}...")  # Show first 2
            
        elif uri.startswith('ar://'):
            ar_hash = uri.replace('ar://', '')
            arweave_url = f'https://arweave.net/{ar_hash}'
            print(f"  Converted to Arweave: {arweave_url}")
    
    print("\nIPFS Gateway conversion tests completed!")


def test_metadata_parsing_logic():
    """Test metadata parsing logic with sample data."""
    print("\nTesting Metadata Parsing Logic...")
    
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
    
    def extract_image_from_metadata(metadata):
        """Extract image URL from metadata."""
        # Common image field names in NFT metadata
        image_fields = [
            'image', 'image_url', 'imageUrl', 'image_uri', 'imageUri',
            'image_data', 'imageData', 'img', 'img_url', 'imgUrl'
        ]
        
        # Priority 1: Direct image fields
        for field in image_fields:
            if field in metadata:
                image_url = metadata[field]
                if image_url and isinstance(image_url, str):
                    return image_url
        
        # Priority 2: Check nested structures
        if 'properties' in metadata:
            properties = metadata['properties']
            if isinstance(properties, dict):
                # Check properties.files
                if 'files' in properties:
                    files = properties['files']
                    if isinstance(files, list) and files:
                        for file_info in files:
                            if isinstance(file_info, dict):
                                # Check for image files
                                mime_type = file_info.get('type', '').lower()
                                if mime_type.startswith('image/'):
                                    uri = file_info.get('uri', '')
                                    if uri:
                                        return uri
        
        return ""
    
    for i, sample in enumerate(sample_metadata):
        print(f"\nSample {i+1}: {sample['name']}")
        image_url = extract_image_from_metadata(sample['metadata'])
        print(f"  Extracted Image URL: {image_url}")
    
    print("\nMetadata Parsing logic tests completed!")


def test_metadata_uri_extraction():
    """Test metadata URI extraction logic."""
    print("\nTesting Metadata URI Extraction Logic...")
    
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
    
    def get_metadata_uri(asset):
        """Get the metadata URI from the asset."""
        # Check various possible locations for metadata URI
        content = asset.get("content", {})
        
        # Priority 1: Check for explicit metadata URI
        if "metadata" in asset:
            metadata = asset["metadata"]
            if isinstance(metadata, dict) and "uri" in metadata:
                return metadata["uri"]
        
        # Priority 2: Check content.metadata.uri
        metadata = content.get("metadata", {})
        if isinstance(metadata, dict) and "uri" in metadata:
            return metadata["uri"]
        
        # Priority 3: Check for token URI in various fields
        for field in ["token_uri", "tokenUri", "uri", "metadata_uri"]:
            if field in asset:
                uri = asset[field]
                if uri and isinstance(uri, str):
                    return uri
        
        # Priority 4: Check content for URI fields
        for field in ["uri", "metadata_uri", "token_uri"]:
            if field in content:
                uri = content[field]
                if uri and isinstance(uri, str):
                    return uri
        
        return ""
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case['name']}")
        
        # Test metadata URI extraction
        metadata_uri = get_metadata_uri(test_case['asset'])
        print(f"  Metadata URI: {metadata_uri}")
    
    print("\nMetadata URI extraction tests completed!")


def main():
    """Run all IPFS extraction tests."""
    print("=== Testing IPFS Metadata Extraction (Simple) ===\n")
    
    test_ipfs_gateway_handling()
    test_metadata_parsing_logic()
    test_metadata_uri_extraction()
    
    print("\n=== All Tests Completed ===")
    print("\nThe IPFS metadata extraction system is designed to:")
    print("1. Extract metadata URIs from NFT assets")
    print("2. Fetch metadata from IPFS, Arweave, or HTTP sources")
    print("3. Parse metadata to find image URLs")
    print("4. Handle multiple IPFS gateways for redundancy")
    print("5. Support various metadata formats and structures")
    
    print("\nThis should significantly improve NFT download success rates by:")
    print("- Finding images stored in IPFS metadata")
    print("- Handling multiple IPFS gateways")
    print("- Supporting various metadata formats")
    print("- Providing fallback strategies")


if __name__ == "__main__":
    main() 