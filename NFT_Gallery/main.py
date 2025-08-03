#!/usr/bin/env python3
"""
Solana NFT Downloader - Main Script

Downloads all NFTs from a Solana wallet using Helius DAS API
and saves images to ~/Pictures/SolanaNFTs/ for macOS Photos integration.
"""
import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.nft_processor import NFTProcessor, NFTProcessorError
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
        description="Download Solana NFTs to local directory using Helius DAS API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
  python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --output ~/Desktop/NFTs
  python main.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --verbose
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
        help="Only validate configuration, don't download"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show processing statistics and exit"
    )
    
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Retry failed downloads with improved error handling"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retry attempts for failed downloads (default: 3)"
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    # Load environment variables from .env file
    load_env_file()
    
    args = parse_arguments()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logging(log_level, args.log_file)
    
    logger.info("=== Solana NFT Downloader (Helius DAS API) ===")
    logger.info(f"Starting with arguments: {vars(args)}")
    
    try:
        # Validate environment
        logger.info("Validating environment...")
        env_validation = validate_environment()
        
        if not env_validation["valid"]:
            logger.error("Environment validation failed:")
            for error in env_validation["errors"]:
                logger.error(f"  - {error}")
            sys.exit(1)
        
        if env_validation["warnings"]:
            logger.warning("Environment warnings:")
            for warning in env_validation["warnings"]:
                logger.warning(f"  - {warning}")
        
        # Create NFT processor
        logger.info("Initializing NFT processor...")
        processor = NFTProcessor(args.wallet, args.output)
        
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
        
        logger.info("Environment validation successful!")
        
        if args.validate_only:
            logger.info("Validation only mode - exiting")
            return
        
        if args.stats:
            # Show statistics
            stats = processor.get_processing_stats()
            logger.info("=== Processing Statistics ===")
            logger.info(f"Downloaded files: {stats.get('downloaded_files', 0)}")
            logger.info(f"Available space: {stats.get('available_space_gb', 0)} GB")
            logger.info(f"Total space: {stats.get('total_space_gb', 0)} GB")
            logger.info(f"Output directory: {stats.get('output_directory', 'Unknown')}")
            return
        
        # Process wallet
        logger.info("Starting NFT processing...")
        results = processor.process_wallet()
        
        # Display results
        logger.info("=== Processing Results ===")
        logger.info(f"Total NFTs found: {results['total_nfts']}")
        logger.info(f"Successfully downloaded: {results['downloaded']}")
        logger.info(f"Skipped (already exists): {results['skipped']}")
        logger.info(f"Failed: {results['failed']}")
        
        if results['errors']:
            logger.warning("Errors encountered:")
            for error in results['errors']:
                logger.warning(f"  - {error}")
        
        # Show failed downloads analysis
        failed_summary = processor.get_failed_downloads_summary()
        if failed_summary['total_failed'] > 0:
            logger.warning("=== Failed Downloads Analysis ===")
            logger.warning(f"Total failed downloads: {failed_summary['total_failed']}")
            
            if failed_summary['error_counts']:
                logger.warning("Failed by error type:")
                for error_type, count in failed_summary['error_counts'].items():
                    logger.warning(f"  - {error_type}: {count}")
            
            if failed_summary['domain_counts']:
                logger.warning("Failed by domain:")
                for domain, count in sorted(failed_summary['domain_counts'].items(), key=lambda x: x[1], reverse=True)[:10]:
                    logger.warning(f"  - {domain}: {count}")
        
        # Show final statistics
        stats = processor.get_processing_stats()
        logger.info("=== Final Statistics ===")
        logger.info(f"Total downloaded files: {stats.get('downloaded_files', 0)}")
        logger.info(f"Available space remaining: {stats.get('available_space_gb', 0)} GB")
        
        # Calculate success rate
        total_processed = results['downloaded'] + results['failed']
        if total_processed > 0:
            success_rate = (results['downloaded'] / total_processed) * 100
            logger.info(f"Success rate: {success_rate:.1f}%")
        
        logger.info("Processing completed successfully!")
        
    except NFTProcessorError as e:
        logger.error(f"NFT processing error: {str(e)}")
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