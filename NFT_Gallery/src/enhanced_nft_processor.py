"""
Enhanced NFT processor that integrates Helius API with Firestore as a middle layer.
"""
import os
import logging
from typing import Dict, List, Optional, Any
from .helius_api import HeliusAPIClient, HeliusAPIError
from .firestore_manager import FirestoreManager, FirestoreManagerError
from .file_manager import FileManager, FileManagerError
import time


class EnhancedNFTProcessorError(Exception):
    """Custom exception for enhanced NFT processing operations."""
    pass


class EnhancedNFTProcessor:
    """Enhanced processor that uses Firestore as a middle layer between Helius and local storage."""
    
    def __init__(self, wallet_address: str, output_dir: str = "~/Pictures/NFTs", 
                 project_id: Optional[str] = None, database_name: Optional[str] = None):
        """
        Initialize enhanced NFT processor.
        
        Args:
            wallet_address: Solana wallet address to fetch NFTs from
            output_dir: Directory to store NFT images
            project_id: Google Cloud project ID for Firestore
            database_name: Firestore database name (defaults to FIRESTORE_DATABASE env var or "develop")
            
        Raises:
            EnhancedNFTProcessorError: If initialization fails
        """
        self.wallet_address = wallet_address
        self.output_dir = output_dir
        
        # Initialize components
        try:
            # Get Helius API key from environment variable
            self.api_key = os.getenv("HELIUS_API_KEY")
            if not self.api_key:
                raise EnhancedNFTProcessorError("HELIUS_API_KEY environment variable is required")
            
            self.helius_client = HeliusAPIClient(self.api_key)
            
            # Get database name from parameter, environment, or use default
            db_name = database_name or os.getenv("FIRESTORE_DATABASE", "develop")
            self.firestore_manager = FirestoreManager(project_id, db_name)
            self.file_manager = FileManager(output_dir)
        except (HeliusAPIError, FirestoreManagerError, FileManagerError) as e:
            raise EnhancedNFTProcessorError(f"Failed to initialize enhanced NFT processor: {str(e)}")
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def sync_wallet_to_firestore(self) -> Dict[str, Any]:
        """
        Sync wallet NFTs from Helius to Firestore.
        
        Returns:
            Sync results summary
            
        Raises:
            EnhancedNFTProcessorError: If sync fails
        """
        try:
            self.logger.info(f"Starting wallet sync to Firestore for: {self.wallet_address}")
            
            # Fetch NFTs from Helius API
            nft_data = self._fetch_nfts_from_helius()
            
            if not nft_data:
                raise EnhancedNFTProcessorError("Invalid response from Helius API")
            
            # DAS API returns data in a specific format with 'items' array
            assets = nft_data.get("items", []) if isinstance(nft_data, dict) else []
            self.logger.info(f"Found {len(assets)} NFTs in wallet")
            
            # Store NFTs in Firestore
            firestore_results = self.firestore_manager.store_wallet_nfts(self.wallet_address, assets)
            
            self.logger.info(f"Firestore sync complete: {firestore_results['stored']} stored, {firestore_results['failed']} failed")
            return firestore_results
            
        except Exception as e:
            raise EnhancedNFTProcessorError(f"Failed to sync wallet to Firestore: {str(e)}")
    
    def process_wallet_with_firestore(self, download_images: bool = True) -> Dict[str, Any]:
        """
        Process wallet NFTs using Firestore as the data source.
        
        Args:
            download_images: Whether to download images to local storage
            
        Returns:
            Processing results summary
            
        Raises:
            EnhancedNFTProcessorError: If processing fails
        """
        try:
            self.logger.info(f"Processing wallet with Firestore integration: {self.wallet_address}")
            
            # First, sync to Firestore
            sync_results = self.sync_wallet_to_firestore()
            
            if sync_results['failed'] > 0:
                self.logger.warning(f"Some NFTs failed to sync to Firestore: {sync_results['failed']}")
            
            # Get NFTs from Firestore
            nfts_from_firestore = self.firestore_manager.get_nfts_by_wallet(self.wallet_address)
            
            if not nfts_from_firestore:
                self.logger.warning("No NFTs found in Firestore for this wallet")
                return {
                    "total_nfts": 0,
                    "synced_to_firestore": 0,
                    "downloaded": 0,
                    "skipped": 0,
                    "failed": 0,
                    "errors": []
                }
            
            # Process each NFT for local download
            results = {
                "total_nfts": len(nfts_from_firestore),
                "synced_to_firestore": sync_results['stored'],
                "downloaded": 0,
                "skipped": 0,
                "failed": 0,
                "errors": []
            }
            
            if download_images:
                for nft in nfts_from_firestore:
                    try:
                        success = self._process_single_nft_from_firestore(nft)
                        if success:
                            results["downloaded"] += 1
                        else:
                            results["skipped"] += 1
                    except Exception as e:
                        results["failed"] += 1
                        error_msg = f"Failed to process NFT {nft.get('asset_id', 'unknown')}: {str(e)}"
                        results["errors"].append(error_msg)
                        self.logger.error(error_msg)
            
            self.logger.info(f"Processing complete: {results['downloaded']} downloaded, {results['skipped']} skipped, {results['failed']} failed")
            return results
            
        except Exception as e:
            raise EnhancedNFTProcessorError(f"Failed to process wallet with Firestore: {str(e)}")
    
    def get_firestore_stats(self) -> Dict[str, Any]:
        """
        Get statistics from Firestore.
        
        Returns:
            Firestore statistics
        """
        try:
            return self.firestore_manager.get_collection_stats(self.wallet_address)
        except Exception as e:
            self.logger.error(f"Failed to get Firestore stats: {str(e)}")
            return {}
    
    def search_nfts_in_firestore(self, 
                                collection_name: Optional[str] = None,
                                compressed: Optional[bool] = None,
                                limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search NFTs in Firestore with filters.
        
        Args:
            collection_name: Filter by collection name
            compressed: Filter by compression status
            limit: Maximum number of results
            
        Returns:
            List of matching NFTs
        """
        try:
            return self.firestore_manager.search_nfts(
                wallet_address=self.wallet_address,
                collection_name=collection_name,
                compressed=compressed,
                limit=limit
            )
        except Exception as e:
            self.logger.error(f"Failed to search NFTs in Firestore: {str(e)}")
            return []
    
    def update_nft_sync_status(self, asset_id: str, status: str = "synced") -> bool:
        """
        Update NFT sync status in Firestore.
        
        Args:
            asset_id: NFT asset ID
            status: Sync status
            
        Returns:
            True if updated successfully
        """
        try:
            return self.firestore_manager.update_nft_sync_status(asset_id, status)
        except Exception as e:
            self.logger.error(f"Failed to update sync status: {str(e)}")
            return False
    
    def _fetch_nfts_from_helius(self) -> Dict[str, Any]:
        """
        Fetch NFTs from Helius DAS API.
        
        Returns:
            NFT data from API
            
        Raises:
            EnhancedNFTProcessorError: If API call fails
        """
        try:
            return self.helius_client.get_nfts_by_owner(self.wallet_address)
        except HeliusAPIError as e:
            raise EnhancedNFTProcessorError(f"Failed to fetch NFTs from Helius: {str(e)}")
    
    def _process_single_nft_from_firestore(self, nft_data: Dict[str, Any]) -> bool:
        """
        Process a single NFT from Firestore data.
        
        Args:
            nft_data: NFT data from Firestore
            
        Returns:
            True if processed successfully, False if skipped
            
        Raises:
            EnhancedNFTProcessorError: If processing fails
        """
        asset_id = nft_data.get("asset_id", "")
        name = nft_data.get("name", "")
        image_url = nft_data.get("image_url", "")
        
        if not image_url:
            self.logger.warning(f"NFT {asset_id} has no image URL, skipping")
            return False
        
        # Generate filename
        filename = self.file_manager._generate_safe_filename(name, asset_id, asset_id, image_url)
        
        # Check if file already exists
        if self.file_manager.file_exists(filename):
            self.logger.info(f"NFT {name} ({asset_id}) already exists, skipping")
            return False
        
        # Download image
        try:
            self.logger.debug(f"Attempting to download image for {name} ({asset_id}) from: {image_url}")
            success = self.file_manager.download_image(image_url, filename)
            if success:
                self.logger.info(f"Successfully downloaded: {name} ({asset_id})")
                # Update sync status in Firestore
                self.update_nft_sync_status(asset_id, "downloaded")
                return True
            else:
                self.logger.error(f"Failed to download: {name} ({asset_id})")
                self.update_nft_sync_status(asset_id, "download_failed")
                return False
        except FileManagerError as e:
            self.logger.error(f"File manager error for {name} ({asset_id}): {str(e)}")
            self.update_nft_sync_status(asset_id, "download_failed")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error downloading {name} ({asset_id}): {str(e)}")
            self.update_nft_sync_status(asset_id, "download_failed")
            return False
    
    def validate_wallet_address(self) -> bool:
        """
        Validate the wallet address format.
        
        Returns:
            True if valid, False otherwise
        """
        try:
            return self.helius_client._is_valid_solana_address(self.wallet_address)
        except Exception:
            return False
    
    def check_api_connectivity(self) -> bool:
        """
        Check if Helius API is accessible.
        
        Returns:
            True if accessible, False otherwise
        """
        try:
            return self.helius_client.check_api_connectivity()
        except Exception:
            return False
    
    def check_firestore_connectivity(self) -> bool:
        """
        Check if Firestore is accessible.
        
        Returns:
            True if accessible, False otherwise
        """
        try:
            # Try to get collection stats as a connectivity test
            self.firestore_manager.get_collection_stats()
            return True
        except Exception:
            return False 