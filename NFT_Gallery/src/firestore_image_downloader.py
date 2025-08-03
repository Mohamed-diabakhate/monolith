"""
Firestore Image Downloader - Downloads images from Firestore documents and updates status.
"""
import os
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore

from .firestore_manager import FirestoreManager, FirestoreManagerError
from .file_manager import FileManager, FileManagerError


class FirestoreImageDownloaderError(Exception):
    """Custom exception for Firestore image downloader operations."""
    pass


class FirestoreImageDownloader:
    """Downloads images from Firestore documents and updates their status."""
    
    def __init__(self, firestore_manager: FirestoreManager, file_manager: FileManager,
                 max_concurrent_downloads: int = 5, max_retries: int = 3):
        """
        Initialize Firestore image downloader.
        
        Args:
            firestore_manager: Firestore manager instance
            file_manager: File manager instance
            max_concurrent_downloads: Maximum concurrent downloads
            max_retries: Maximum retry attempts per download
            
        Raises:
            FirestoreImageDownloaderError: If initialization fails
        """
        self.firestore_manager = firestore_manager
        self.file_manager = file_manager
        self.max_concurrent_downloads = max_concurrent_downloads
        self.max_retries = max_retries
        self.semaphore = Semaphore(max_concurrent_downloads)
        self.logger = logging.getLogger(__name__)
        
        # Statistics tracking
        self.stats = {
            "total_processed": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "skipped_downloads": 0,
            "total_file_size": 0
        }
    
    def download_pending_images(self, wallet_address: Optional[str] = None, 
                              batch_size: int = 50) -> Dict[str, Any]:
        """
        Download all pending images from Firestore.
        
        Args:
            wallet_address: Optional wallet address filter
            batch_size: Number of documents to process in each batch
            
        Returns:
            Download results summary
        """
        try:
            self.logger.info(f"Starting download of pending images for wallet: {wallet_address or 'all'}")
            self._reset_stats()
            
            # Get pending documents
            pending_docs = self.firestore_manager.get_nfts_by_download_status(
                "pending", wallet_address, batch_size
            )
            
            if not pending_docs:
                self.logger.info("No pending downloads found")
                return self._get_results_summary()
            
            self.logger.info(f"Found {len(pending_docs)} pending downloads")
            
            # Process downloads
            self._process_download_batch(pending_docs)
            
            return self._get_results_summary()
            
        except Exception as e:
            raise FirestoreImageDownloaderError(f"Failed to download pending images: {str(e)}")
    
    def download_wallet_images(self, wallet_address: str, 
                             status_filter: str = "pending") -> Dict[str, Any]:
        """
        Download images for a specific wallet.
        
        Args:
            wallet_address: Wallet address to download for
            status_filter: Download status to filter by (pending, failed, etc.)
            
        Returns:
            Download results summary
        """
        try:
            self.logger.info(f"Starting download for wallet {wallet_address} with status filter: {status_filter}")
            self._reset_stats()
            
            # Get documents by status for specific wallet
            docs = self.firestore_manager.get_nfts_by_download_status(
                status_filter, wallet_address, 1000
            )
            
            if not docs:
                self.logger.info(f"No documents found for wallet {wallet_address} with status {status_filter}")
                self.logger.info("Trying to download from all available documents...")
                
                # Fallback: get documents from all wallets
                docs = self.firestore_manager.get_nfts_by_download_status(
                    status_filter, None, 1000
                )
                
                if not docs:
                    self.logger.info(f"No documents found with status {status_filter} in any wallet")
                    return self._get_results_summary()
                
                self.logger.info(f"Found {len(docs)} documents from all wallets to process")
            else:
                self.logger.info(f"Found {len(docs)} documents for wallet {wallet_address} to process")
            
            # Process downloads
            self._process_download_batch(docs)
            
            return self._get_results_summary()
            
        except Exception as e:
            raise FirestoreImageDownloaderError(f"Failed to download wallet images: {str(e)}")
    
    def retry_failed_downloads(self, wallet_address: Optional[str] = None, 
                             max_attempts: int = 3) -> Dict[str, Any]:
        """
        Retry downloads that previously failed.
        
        Args:
            wallet_address: Optional wallet address filter
            max_attempts: Maximum attempts to retry
            
        Returns:
            Retry results summary
        """
        try:
            self.logger.info(f"Starting retry of failed downloads for wallet: {wallet_address or 'all'}")
            self._reset_stats()
            
            # Get failed documents
            failed_docs = self.firestore_manager.get_nfts_by_download_status(
                "failed", wallet_address, 1000
            )
            
            if not failed_docs:
                self.logger.info("No failed downloads found to retry")
                return self._get_results_summary()
            
            # Filter by attempt count
            retry_docs = [
                doc for doc in failed_docs 
                if doc.get("download_attempts", 0) < max_attempts
            ]
            
            if not retry_docs:
                self.logger.info(f"No failed downloads within retry limit ({max_attempts} attempts)")
                return self._get_results_summary()
            
            self.logger.info(f"Found {len(retry_docs)} failed downloads to retry")
            
            # Process retries
            self._process_download_batch(retry_docs)
            
            return self._get_results_summary()
            
        except Exception as e:
            raise FirestoreImageDownloaderError(f"Failed to retry downloads: {str(e)}")
    
    def download_single_nft(self, asset_id: str) -> bool:
        """
        Download a single NFT image.
        
        Args:
            asset_id: NFT asset ID to download
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            # Get NFT document
            nft_data = self.firestore_manager.get_nft_by_asset_id(asset_id)
            if not nft_data:
                self.logger.error(f"NFT document not found for asset {asset_id}")
                return False
            
            return self._download_single_nft(nft_data)
            
        except Exception as e:
            self.logger.error(f"Failed to download single NFT {asset_id}: {str(e)}")
            return False
    
    def get_download_progress(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current download progress and statistics.
        
        Args:
            wallet_address: Optional wallet address filter
            
        Returns:
            Progress statistics
        """
        try:
            stats = self.firestore_manager.get_download_statistics(wallet_address)
            
            # Add current session stats
            stats.update({
                "session_processed": self.stats["total_processed"],
                "session_successful": self.stats["successful_downloads"],
                "session_failed": self.stats["failed_downloads"],
                "session_skipped": self.stats["skipped_downloads"],
                "session_file_size": self.stats["total_file_size"]
            })
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get download progress: {str(e)}")
            return {}
    
    def _process_download_batch(self, docs: List[Dict[str, Any]]) -> None:
        """
        Process a batch of documents for download.
        
        Args:
            docs: List of NFT documents to process
        """
        self.stats["total_processed"] = len(docs)
        
        # Use ThreadPoolExecutor for concurrent downloads
        with ThreadPoolExecutor(max_workers=self.max_concurrent_downloads) as executor:
            # Submit download tasks
            future_to_doc = {
                executor.submit(self._download_single_nft, doc): doc 
                for doc in docs
            }
            
            # Process completed downloads
            for future in as_completed(future_to_doc):
                doc = future_to_doc[future]
                try:
                    success = future.result()
                    if success:
                        self.stats["successful_downloads"] += 1
                    else:
                        self.stats["failed_downloads"] += 1
                except Exception as e:
                    self.logger.error(f"Download failed for {doc.get('asset_id', 'unknown')}: {str(e)}")
                    self.stats["failed_downloads"] += 1
    
    def _download_single_nft(self, nft_data: Dict[str, Any]) -> bool:
        """
        Download a single NFT image.
        
        Args:
            nft_data: NFT document data
            
        Returns:
            True if download successful, False otherwise
        """
        asset_id = nft_data.get("asset_id")
        image_url = nft_data.get("image_url")
        name = nft_data.get("name", f"NFT_{asset_id[:8]}")
        
        if not image_url:
            self.logger.warning(f"No image URL found for {name} ({asset_id})")
            self._update_download_status(asset_id, "failed", "No image URL available")
            return False
        
        # Check if already downloaded
        if nft_data.get("download_status") == "completed":
            local_path = nft_data.get("local_file_path")
            if local_path and self.file_manager.file_exists(Path(local_path).name):
                self.logger.info(f"Image already downloaded for {name} ({asset_id})")
                self.stats["skipped_downloads"] += 1
                return True
        
        # Update status to downloading
        self._update_download_status(asset_id, "downloading")
        
        try:
            # Generate filename
            filename = self._generate_filename(nft_data)
            
            # Download image
            success = self.file_manager.download_image(image_url, filename, self.max_retries)
            
            if success:
                # Get file info
                file_path = self.file_manager.output_dir / filename
                file_size = file_path.stat().st_size if file_path.exists() else 0
                
                # Update status to completed
                self._update_download_status(
                    asset_id, "completed", 
                    local_file_path=str(file_path),
                    file_size=file_size
                )
                
                self.stats["total_file_size"] += file_size
                self.logger.info(f"Successfully downloaded {name} ({asset_id}) - {file_size} bytes")
                return True
            else:
                # Update status to failed
                self._update_download_status(asset_id, "failed", "Download failed")
                self.logger.error(f"Failed to download {name} ({asset_id})")
                return False
                
        except Exception as e:
            error_msg = f"Download error: {str(e)}"
            self._update_download_status(asset_id, "failed", error_msg)
            self.logger.error(f"Error downloading {name} ({asset_id}): {str(e)}")
            return False
    
    def _generate_filename(self, nft_data: Dict[str, Any]) -> str:
        """
        Generate filename for NFT image.
        
        Args:
            nft_data: NFT document data
            
        Returns:
            Generated filename
        """
        asset_id = nft_data.get("asset_id", "")
        name = nft_data.get("name", f"NFT_{asset_id[:8]}")
        image_url = nft_data.get("image_url", "")
        
        # Use existing file manager method
        return self.file_manager._generate_safe_filename(
            name, asset_id, asset_id, image_url
        )
    
    def _update_download_status(self, asset_id: str, status: str, 
                              error: Optional[str] = None,
                              local_file_path: Optional[str] = None,
                              file_size: Optional[int] = None) -> None:
        """
        Update download status in Firestore.
        
        Args:
            asset_id: NFT asset ID
            status: Download status
            error: Error message if failed
            local_file_path: Path to downloaded file
            file_size: Size of downloaded file
        """
        try:
            self.firestore_manager.update_download_status(
                asset_id, status, error, local_file_path, file_size
            )
        except Exception as e:
            self.logger.error(f"Failed to update download status for {asset_id}: {str(e)}")
    
    def _reset_stats(self) -> None:
        """Reset download statistics."""
        self.stats = {
            "total_processed": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "skipped_downloads": 0,
            "total_file_size": 0
        }
    
    def _get_results_summary(self) -> Dict[str, Any]:
        """
        Get download results summary.
        
        Returns:
            Results summary dictionary
        """
        total = self.stats["total_processed"]
        success_rate = (self.stats["successful_downloads"] / total * 100) if total > 0 else 0
        
        return {
            "total_processed": total,
            "successful_downloads": self.stats["successful_downloads"],
            "failed_downloads": self.stats["failed_downloads"],
            "skipped_downloads": self.stats["skipped_downloads"],
            "total_file_size": self.stats["total_file_size"],
            "success_rate": f"{success_rate:.1f}%",
            "timestamp": time.time()
        } 