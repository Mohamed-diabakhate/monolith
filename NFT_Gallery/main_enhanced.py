#!/usr/bin/env python3
"""
Enhanced Solana NFT Downloader - Main Script with Firestore Integration

Downloads all NFTs from a Solana wallet using Helius DAS API,
stores metadata in Firestore, and saves images to local directory.
"""
import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.enhanced_nft_processor import EnhancedNFTProcessor, EnhancedNFTProcessorError
from src.utils import setup_logging, validate_environment, get_system_info


def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Enhanced Solana NFT Downloader with Firestore Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with Firestore integration
  python main_enhanced.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
  
  # Sync to Firestore only (no local downloads)
  python main_enhanced.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --firestore-only
  
  # Get Firestore statistics
  python main_enhanced.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --firestore-stats
  
  # Search NFTs in Firestore
  python main_enhanced.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --search-collection "Bored Ape"
        """
    )
    
    parser.add_argument(
        "--wallet",
        required=True,
        help="Solana wallet address to fetch NFTs from"
    )
    
    parser.add_argument(
        "--output",
        default=os.getenv("OUTPUT_DIR", "~/Pictures/SolanaNFTs"),
        help="Output directory for NFT images (default: ~/Pictures/SolanaNFTs or OUTPUT_DIR env var)"
    )
    
    parser.add_argument(
        "--project-id",
        default=os.getenv("GOOGLE_CLOUD_PROJECT"),
        help="Google Cloud project ID for Firestore (defaults to GOOGLE_CLOUD_PROJECT env var)"
    )
    
    parser.add_argument(
        "--database",
        default=os.getenv("FIRESTORE_DATABASE", "develop"),
        help="Firestore database name (defaults to FIRESTORE_DATABASE env var or 'develop')"
    )
    
    parser.add_argument(
        "--firestore-only",
        action="store_true",
        help="Only sync to Firestore, don't download images locally"
    )
    
    parser.add_argument(
        "--firestore-stats",
        action="store_true",
        help="Show Firestore statistics and exit"
    )
    
    parser.add_argument(
        "--search-collection",
        help="Search NFTs by collection name in Firestore"
    )
    
    parser.add_argument(
        "--compressed-only",
        action="store_true",
        help="Only process compressed NFTs"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--log-file",
        help="Log file path (default: no file logging)"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate configuration, don't process"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show processing statistics and exit"
    )
    
    return parser.parse_args()


def validate_firestore_environment():
    """Validate Firestore environment configuration."""
    errors = []
    warnings = []
    
    # Check for Google Cloud project ID
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        errors.append("GOOGLE_CLOUD_PROJECT environment variable is required for Firestore integration")
    
    # Check for Google Cloud credentials
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        warnings.append("GOOGLE_APPLICATION_CREDENTIALS not set - using Application Default Credentials")
    elif not os.path.exists(credentials_path):
        warnings.append(f"Google Cloud credentials file not found: {credentials_path} - using Application Default Credentials")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def display_firestore_stats(processor, logger):
    """Display Firestore statistics."""
    try:
        stats = processor.get_firestore_stats()
        
        logger.info("=== Firestore Statistics ===")
        logger.info(f"Total NFTs: {stats.get('total_nfts', 0)}")
        logger.info(f"Compressed NFTs: {stats.get('compressed_count', 0)}")
        
        # Display collections
        collections = stats.get('collections', {})
        if collections:
            logger.info("Collections:")
            for collection_name, count in sorted(collections.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  - {collection_name}: {count}")
        
        # Display sync status
        sync_status = stats.get('sync_status_counts', {})
        if sync_status:
            logger.info("Sync Status:")
            for status, count in sync_status.items():
                logger.info(f"  - {status}: {count}")
        
        # Display recent additions
        recent = stats.get('recent_additions', [])
        if recent:
            logger.info("Recent Additions:")
            for nft in recent[:5]:  # Show top 5
                logger.info(f"  - {nft.get('name', 'Unknown')} ({nft.get('asset_id', 'Unknown')})")
        
    except Exception as e:
        logger.error(f"Failed to get Firestore statistics: {str(e)}")


def search_nfts_in_firestore(processor, collection_name, compressed_only, logger):
    """Search NFTs in Firestore."""
    try:
        nfts = processor.search_nfts_in_firestore(
            collection_name=collection_name,
            compressed=compressed_only if compressed_only else None,
            limit=50
        )
        
        logger.info(f"=== Search Results ({len(nfts)} NFTs) ===")
        
        for nft in nfts:
            name = nft.get('name', 'Unknown')
            asset_id = nft.get('asset_id', 'Unknown')
            collection = nft.get('collection', {}).get('name', 'Unknown')
            compressed = nft.get('compressed', False)
            
            logger.info(f"  - {name}")
            logger.info(f"    Asset ID: {asset_id}")
            logger.info(f"    Collection: {collection}")
            logger.info(f"    Compressed: {compressed}")
            logger.info("")
        
    except Exception as e:
        logger.error(f"Failed to search NFTs in Firestore: {str(e)}")


def main():
    """Main entry point."""
    # Load environment variables from .env file
    load_env_file()
    
    args = parse_arguments()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logging(log_level, args.log_file)
    
    logger.info("=== Enhanced Solana NFT Downloader (Firestore Integration) ===")
    logger.info(f"Starting with arguments: {vars(args)}")
    
    try:
        # Validate environment
        logger.info("Validating environment...")
        env_validation = validate_environment()
        firestore_validation = validate_firestore_environment()
        
        # Combine validation results
        all_errors = env_validation["errors"] + firestore_validation["errors"]
        all_warnings = env_validation["warnings"] + firestore_validation["warnings"]
        
        if not env_validation["valid"] or not firestore_validation["valid"]:
            logger.error("Environment validation failed:")
            for error in all_errors:
                logger.error(f"  - {error}")
            sys.exit(1)
        
        if all_warnings:
            logger.warning("Environment warnings:")
            for warning in all_warnings:
                logger.warning(f"  - {warning}")
        
        # Create enhanced NFT processor
        logger.info("Initializing enhanced NFT processor...")
        processor = EnhancedNFTProcessor(
            args.wallet, 
            args.output,
            args.project_id,
            args.database
        )
        
        # Validate wallet address
        logger.info("Validating wallet address...")
        if not processor.validate_wallet_address():
            logger.error(f"Invalid wallet address format: {args.wallet}")
            sys.exit(1)
        
        # Check API connectivity
        logger.info("Checking Helius API connectivity...")
        if not processor.check_api_connectivity():
            logger.error("Cannot connect to Helius API. Check your API key and network connection.")
            sys.exit(1)
        
        # Check Firestore connectivity
        logger.info("Checking Firestore connectivity...")
        if not processor.check_firestore_connectivity():
            logger.error("Cannot connect to Firestore. Check your Google Cloud configuration.")
            sys.exit(1)
        
        logger.info("Environment validation successful!")
        
        if args.validate_only:
            logger.info("Validation only mode - exiting")
            return
        
        # Handle Firestore statistics
        if args.firestore_stats:
            display_firestore_stats(processor, logger)
            return
        
        # Handle Firestore search
        if args.search_collection:
            search_nfts_in_firestore(processor, args.search_collection, args.compressed_only, logger)
            return
        
        # Handle regular statistics
        if args.stats:
            # Show processing statistics
            stats = processor.get_processing_stats()
            logger.info("=== Processing Statistics ===")
            logger.info(f"Downloaded files: {stats.get('downloaded_files', 0)}")
            logger.info(f"Available space: {stats.get('available_space_gb', 0)} GB")
            logger.info(f"Total space: {stats.get('total_space_gb', 0)} GB")
            logger.info(f"Output directory: {stats.get('output_directory', 'Unknown')}")
            
            # Also show Firestore stats
            display_firestore_stats(processor, logger)
            return
        
        # Process wallet
        if args.firestore_only:
            logger.info("Starting Firestore-only sync...")
            results = processor.sync_wallet_to_firestore()
            
            # Display sync results
            logger.info("=== Firestore Sync Results ===")
            logger.info(f"Total NFTs found: {results['total_nfts']}")
            logger.info(f"Successfully stored: {results['stored']}")
            logger.info(f"Failed to store: {results['failed']}")
            
            if results['errors']:
                logger.warning("Errors encountered:")
                for error in results['errors']:
                    logger.warning(f"  - {error}")
        else:
            logger.info("Starting full processing with Firestore integration...")
            results = processor.process_wallet_with_firestore(download_images=True)
            
            # Display results
            logger.info("=== Processing Results ===")
            logger.info(f"Total NFTs found: {results['total_nfts']}")
            logger.info(f"Synced to Firestore: {results['synced_to_firestore']}")
            logger.info(f"Successfully downloaded: {results['downloaded']}")
            logger.info(f"Skipped (already exists): {results['skipped']}")
            logger.info(f"Failed: {results['failed']}")
            
            if results['errors']:
                logger.warning("Errors encountered:")
                for error in results['errors']:
                    logger.warning(f"  - {error}")
        
        # Show final statistics
        firestore_stats = processor.get_firestore_stats()
        logger.info("=== Final Firestore Statistics ===")
        logger.info(f"Total NFTs in Firestore: {firestore_stats.get('total_nfts', 0)}")
        logger.info(f"Collections: {len(firestore_stats.get('collections', {}))}")
        logger.info(f"Compressed NFTs: {firestore_stats.get('compressed_count', 0)}")
        
        # Calculate success rate
        if 'total_nfts' in results and results['total_nfts'] > 0:
            if args.firestore_only:
                success_rate = (results['stored'] / results['total_nfts']) * 100
                logger.info(f"Firestore sync success rate: {success_rate:.1f}%")
            else:
                total_processed = results['downloaded'] + results['failed']
                if total_processed > 0:
                    success_rate = (results['downloaded'] / total_processed) * 100
                    logger.info(f"Download success rate: {success_rate:.1f}%")
        
        logger.info("Processing completed successfully!")
        
    except EnhancedNFTProcessorError as e:
        logger.error(f"Enhanced NFT processing error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main() 