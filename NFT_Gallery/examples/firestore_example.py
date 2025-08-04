#!/usr/bin/env python3
"""
Example script demonstrating Firestore integration for NFT Gallery.

This script shows how to:
1. Initialize the enhanced NFT processor
2. Sync NFTs from Helius to Firestore
3. Search and query NFTs in Firestore
4. Get statistics and analytics
"""
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.enhanced_nft_processor import EnhancedNFTProcessor, EnhancedNFTProcessorError
from src.firestore_manager import FirestoreManager


def main():
    """Demonstrate Firestore integration features."""
    
    # Configuration
    wallet_address = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"  # Example wallet
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    output_dir = "~/Pictures/NFTs"
    
    print("🔥 Firestore Integration Example")
    print("=" * 50)
    
    try:
        # Initialize enhanced NFT processor
        print("1. Initializing enhanced NFT processor...")
        processor = EnhancedNFTProcessor(
            wallet_address=wallet_address,
            output_dir=output_dir,
            project_id=project_id
        )
        print("✅ Enhanced NFT processor initialized successfully")
        
        # Check connectivity
        print("\n2. Checking connectivity...")
        helius_connected = processor.check_api_connectivity()
        firestore_connected = processor.check_firestore_connectivity()
        
        print(f"   Helius API: {'✅ Connected' if helius_connected else '❌ Failed'}")
        print(f"   Firestore: {'✅ Connected' if firestore_connected else '❌ Failed'}")
        
        if not helius_connected or not firestore_connected:
            print("❌ Connectivity check failed. Please check your configuration.")
            return
        
        # Sync NFTs to Firestore
        print("\n3. Syncing NFTs to Firestore...")
        sync_results = processor.sync_wallet_to_firestore()
        
        print(f"   Total NFTs found: {sync_results['total_nfts']}")
        print(f"   Successfully stored: {sync_results['stored']}")
        print(f"   Failed to store: {sync_results['failed']}")
        
        if sync_results['errors']:
            print("   Errors encountered:")
            for error in sync_results['errors'][:3]:  # Show first 3 errors
                print(f"     - {error}")
        
        # Get Firestore statistics
        print("\n4. Getting Firestore statistics...")
        stats = processor.get_firestore_stats()
        
        print(f"   Total NFTs in Firestore: {stats.get('total_nfts', 0)}")
        print(f"   Compressed NFTs: {stats.get('compressed_count', 0)}")
        print(f"   Collections: {len(stats.get('collections', {}))}")
        
        # Show top collections
        collections = stats.get('collections', {})
        if collections:
            print("   Top collections:")
            sorted_collections = sorted(collections.items(), key=lambda x: x[1], reverse=True)[:5]
            for collection_name, count in sorted_collections:
                print(f"     - {collection_name}: {count}")
        
        # Search NFTs by collection
        print("\n5. Searching NFTs by collection...")
        if collections:
            # Search for the largest collection
            largest_collection = max(collections.items(), key=lambda x: x[1])[0]
            search_results = processor.search_nfts_in_firestore(
                collection_name=largest_collection,
                limit=5
            )
            
            print(f"   Found {len(search_results)} NFTs in '{largest_collection}':")
            for nft in search_results:
                print(f"     - {nft.get('name', 'Unknown')} (ID: {nft.get('asset_id', 'Unknown')[:8]}...)")
        
        # Search compressed NFTs
        print("\n6. Searching compressed NFTs...")
        compressed_nfts = processor.search_nfts_in_firestore(
            compressed=True,
            limit=5
        )
        
        print(f"   Found {len(compressed_nfts)} compressed NFTs:")
        for nft in compressed_nfts:
            print(f"     - {nft.get('name', 'Unknown')} (ID: {nft.get('asset_id', 'Unknown')[:8]}...)")
        
        # Process with full integration (sync + download)
        print("\n7. Processing with full Firestore integration...")
        results = processor.process_wallet_with_firestore(download_images=False)  # Skip downloads for demo
        
        print(f"   Total NFTs processed: {results['total_nfts']}")
        print(f"   Synced to Firestore: {results['synced_to_firestore']}")
        print(f"   Would download: {results['downloaded'] + results['skipped']}")
        
        # Show sync status breakdown
        print("\n8. Sync status breakdown:")
        sync_status = stats.get('sync_status_counts', {})
        for status, count in sync_status.items():
            print(f"   {status}: {count}")
        
        print("\n✅ Firestore integration example completed successfully!")
        print("\n📚 Next steps:")
        print("   - Use 'python main_enhanced.py --firestore-stats' to get detailed statistics")
        print("   - Use 'python main_enhanced.py --search-collection \"Collection Name\"' to search")
        print("   - Check FIRESTORE_INTEGRATION.md for advanced usage")
        
    except EnhancedNFTProcessorError as e:
        print(f"❌ Enhanced NFT processor error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 