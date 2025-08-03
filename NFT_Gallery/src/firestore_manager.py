"""
Firestore manager for storing and managing NFT data from Helius API.
"""
import os
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
import json
from google.cloud import firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.base_query import FieldFilter


class FirestoreManagerError(Exception):
    """Custom exception for Firestore operations."""
    pass


class FirestoreManager:
    """Firestore manager for NFT data storage and retrieval."""
    
    def __init__(self, project_id: Optional[str] = None, database_name: str = "develop", collection_name: str = "nfts"):
        """
        Initialize Firestore manager.
        
        Args:
            project_id: Google Cloud project ID (defaults to GOOGLE_CLOUD_PROJECT env var)
            database_name: Firestore database name (defaults to "develop")
            collection_name: Firestore collection name for NFTs
            
        Raises:
            FirestoreManagerError: If initialization fails
        """
        self.collection_name = collection_name
        
        try:
            # Initialize Firestore client with specific database
            if project_id:
                self.db = firestore.Client(project=project_id, database=database_name)
            else:
                self.db = firestore.Client(database=database_name)
            
            self.collection = self.db.collection(collection_name)
            self.logger = logging.getLogger(__name__)
            
        except Exception as e:
            raise FirestoreManagerError(f"Failed to initialize Firestore client: {str(e)}")
    
    def store_nft_data(self, wallet_address: str, nft_data: Dict[str, Any]) -> str:
        """
        Store NFT data in Firestore.
        
        Args:
            wallet_address: Owner wallet address
            nft_data: NFT data from Helius API
            
        Returns:
            Document ID of the stored NFT
            
        Raises:
            FirestoreManagerError: If storage fails
        """
        try:
            # Extract key information from Helius DAS API response
            asset_id = nft_data.get("id", "")
            if not asset_id:
                raise FirestoreManagerError("NFT data missing required 'id' field")
            
            # Prepare document data
            doc_data = {
                "asset_id": asset_id,
                "wallet_address": wallet_address,
                "name": self._extract_name(nft_data),
                "symbol": self._extract_symbol(nft_data),
                "description": self._extract_description(nft_data),
                "image_url": self._extract_image_url(nft_data),
                "metadata_uri": self._extract_metadata_uri(nft_data),
                "attributes": self._extract_attributes(nft_data),
                "collection": self._extract_collection_info(nft_data),
                "compressed": nft_data.get("compression", {}).get("compressed", False),
                "royalties": self._extract_royalties(nft_data),
                "creators": self._extract_creators(nft_data),
                "supply": self._extract_supply(nft_data),
                "decimals": nft_data.get("content", {}).get("metadata", {}).get("decimals", 0),
                "token_standard": nft_data.get("content", {}).get("metadata", {}).get("tokenStandard", "Unknown"),
                "raw_data": nft_data,  # Store complete raw data for reference
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "last_synced": datetime.now(timezone.utc),
                "sync_status": "synced",
                # Download status fields
                "download_status": "pending",
                "download_attempts": 0,
                "download_error": None,
                "local_file_path": None,
                "file_size": None,
                "download_completed_at": None,
                "last_download_attempt": None
            }
            
            # Use asset_id as document ID for easy lookup
            doc_ref = self.collection.document(asset_id)
            doc_ref.set(doc_data, merge=True)
            
            self.logger.info(f"Stored NFT data for asset {asset_id}")
            return asset_id
            
        except Exception as e:
            raise FirestoreManagerError(f"Failed to store NFT data: {str(e)}")
    
    def store_wallet_nfts(self, wallet_address: str, nfts_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Store multiple NFTs for a wallet in Firestore.
        
        Args:
            wallet_address: Owner wallet address
            nfts_data: List of NFT data from Helius API
            
        Returns:
            Summary of storage operation
            
        Raises:
            FirestoreManagerError: If storage fails
        """
        try:
            results = {
                "total_nfts": len(nfts_data),
                "stored": 0,
                "failed": 0,
                "errors": []
            }
            
            # Store each NFT
            for nft_data in nfts_data:
                try:
                    self.store_nft_data(wallet_address, nft_data)
                    results["stored"] += 1
                except Exception as e:
                    results["failed"] += 1
                    error_msg = f"Failed to store NFT {nft_data.get('id', 'unknown')}: {str(e)}"
                    results["errors"].append(error_msg)
                    self.logger.error(error_msg)
            
            # Update wallet summary
            self._update_wallet_summary(wallet_address, results)
            
            return results
            
        except Exception as e:
            raise FirestoreManagerError(f"Failed to store wallet NFTs: {str(e)}")
    
    def get_nft_by_asset_id(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve NFT data by asset ID.
        
        Args:
            asset_id: NFT asset ID
            
        Returns:
            NFT data or None if not found
        """
        try:
            doc_ref = self.collection.document(asset_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve NFT {asset_id}: {str(e)}")
            return None
    
    def get_nfts_by_wallet(self, wallet_address: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve all NFTs for a wallet address.
        
        Args:
            wallet_address: Wallet address
            limit: Maximum number of NFTs to retrieve
            
        Returns:
            List of NFT data
        """
        try:
            query = self.collection.where("wallet_address", "==", wallet_address).limit(limit)
            docs = query.stream()
            
            nfts = []
            for doc in docs:
                nfts.append(doc.to_dict())
            
            return nfts
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve NFTs for wallet {wallet_address}: {str(e)}")
            return []
    
    def search_nfts(self, 
                   wallet_address: Optional[str] = None,
                   collection_name: Optional[str] = None,
                   compressed: Optional[bool] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search NFTs with various filters.
        
        Args:
            wallet_address: Filter by wallet address
            collection_name: Filter by collection name
            compressed: Filter by compression status
            limit: Maximum number of results
            
        Returns:
            List of matching NFTs
        """
        try:
            query = self.collection
            
            # Apply filters
            if wallet_address:
                query = query.where("wallet_address", "==", wallet_address)
            
            if collection_name:
                query = query.where("collection.name", "==", collection_name)
            
            if compressed is not None:
                query = query.where("compressed", "==", compressed)
            
            # Apply limit
            query = query.limit(limit)
            
            docs = query.stream()
            nfts = []
            for doc in docs:
                nfts.append(doc.to_dict())
            
            return nfts
            
        except Exception as e:
            self.logger.error(f"Failed to search NFTs: {str(e)}")
            return []
    
    def update_nft_sync_status(self, asset_id: str, status: str = "synced") -> bool:
        """
        Update NFT sync status in Firestore.
        
        Args:
            asset_id: NFT asset ID
            status: New sync status
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            doc_ref = self.collection.document(asset_id)
            doc_ref.update({
                "sync_status": status,
                "updated_at": datetime.now(timezone.utc)
            })
            self.logger.info(f"Updated sync status for asset {asset_id} to {status}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update sync status for asset {asset_id}: {str(e)}")
            return False

    def update_download_status(self, asset_id: str, status: str, error: Optional[str] = None, 
                             local_file_path: Optional[str] = None, file_size: Optional[int] = None) -> bool:
        """
        Update NFT download status in Firestore.
        
        Args:
            asset_id: NFT asset ID
            status: Download status (pending, downloading, completed, failed)
            error: Error message if download failed
            local_file_path: Path to downloaded file
            file_size: Size of downloaded file in bytes
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            update_data = {
                "download_status": status,
                "last_download_attempt": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            if status == "downloading":
                # Increment download attempts
                doc_ref = self.collection.document(asset_id)
                doc = doc_ref.get()
                if doc.exists:
                    current_attempts = doc.to_dict().get("download_attempts", 0)
                    update_data["download_attempts"] = current_attempts + 1
            
            elif status == "completed":
                update_data.update({
                    "download_completed_at": datetime.now(timezone.utc),
                    "download_error": None
                })
                if local_file_path:
                    update_data["local_file_path"] = local_file_path
                if file_size:
                    update_data["file_size"] = file_size
                    
            elif status == "failed":
                if error:
                    update_data["download_error"] = error
            
            doc_ref = self.collection.document(asset_id)
            doc_ref.update(update_data)
            
            self.logger.info(f"Updated download status for asset {asset_id} to {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update download status for asset {asset_id}: {str(e)}")
            return False

    def get_nfts_by_download_status(self, status: str, wallet_address: Optional[str] = None, 
                                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get NFTs by download status.
        
        Args:
            status: Download status to filter by
            wallet_address: Optional wallet address filter
            limit: Maximum number of documents to return
            
        Returns:
            List of NFT documents matching the criteria
        """
        try:
            query = self.collection.where("download_status", "==", status)
            
            if wallet_address:
                query = query.where("wallet_address", "==", wallet_address)
            
            docs = query.limit(limit).stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
            
        except Exception as e:
            self.logger.error(f"Failed to get NFTs by download status {status}: {str(e)}")
            return []

    def get_download_statistics(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get download statistics for NFTs.
        
        Args:
            wallet_address: Optional wallet address filter
            
        Returns:
            Dictionary with download statistics
        """
        try:
            # Build base query
            if wallet_address:
                query = self.collection.where("wallet_address", "==", wallet_address)
            else:
                query = self.collection
            
            # Get all documents
            docs = list(query.stream())
            
            if not docs:
                return {
                    "total_documents": 0,
                    "pending_downloads": 0,
                    "downloading": 0,
                    "completed_downloads": 0,
                    "failed_downloads": 0,
                    "total_file_size": 0,
                    "download_success_rate": "0%"
                }
            
            # Count by status
            status_counts = {}
            total_file_size = 0
            completed_count = 0
            
            for doc in docs:
                data = doc.to_dict()
                status = data.get("download_status", "pending")
                status_counts[status] = status_counts.get(status, 0) + 1
                
                if status == "completed":
                    completed_count += 1
                    file_size = data.get("file_size", 0)
                    total_file_size += file_size
            
            total_docs = len(docs)
            success_rate = (completed_count / total_docs * 100) if total_docs > 0 else 0
            
            return {
                "total_documents": total_docs,
                "pending_downloads": status_counts.get("pending", 0),
                "downloading": status_counts.get("downloading", 0),
                "completed_downloads": status_counts.get("completed", 0),
                "failed_downloads": status_counts.get("failed", 0),
                "total_file_size": total_file_size,
                "download_success_rate": f"{success_rate:.1f}%"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get download statistics: {str(e)}")
            return {}

    def batch_update_download_status(self, updates: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Batch update download status for multiple NFTs.
        
        Args:
            updates: List of update dictionaries with keys: asset_id, status, error, local_file_path, file_size
            
        Returns:
            Dictionary with success and failure counts
        """
        try:
            batch = self.db.batch()
            success_count = 0
            failure_count = 0
            
            for update in updates:
                try:
                    asset_id = update["asset_id"]
                    status = update["status"]
                    error = update.get("error")
                    local_file_path = update.get("local_file_path")
                    file_size = update.get("file_size")
                    
                    doc_ref = self.collection.document(asset_id)
                    
                    update_data = {
                        "download_status": status,
                        "last_download_attempt": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                    
                    if status == "completed":
                        update_data.update({
                            "download_completed_at": datetime.now(timezone.utc),
                            "download_error": None
                        })
                        if local_file_path:
                            update_data["local_file_path"] = local_file_path
                        if file_size:
                            update_data["file_size"] = file_size
                    elif status == "failed" and error:
                        update_data["download_error"] = error
                    
                    batch.update(doc_ref, update_data)
                    success_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to prepare batch update for {update.get('asset_id', 'unknown')}: {str(e)}")
                    failure_count += 1
            
            # Commit batch
            batch.commit()
            self.logger.info(f"Batch update completed: {success_count} successful, {failure_count} failed")
            
            return {
                "success_count": success_count,
                "failure_count": failure_count
            }
            
        except Exception as e:
            self.logger.error(f"Failed to execute batch update: {str(e)}")
            return {"success_count": 0, "failure_count": len(updates)}

    def reset_download_status(self, asset_ids: Optional[List[str]] = None, 
                            wallet_address: Optional[str] = None) -> int:
        """
        Reset download status to pending for specified NFTs.
        
        Args:
            asset_ids: List of asset IDs to reset (if None, reset all for wallet)
            wallet_address: Wallet address filter (required if asset_ids is None)
            
        Returns:
            Number of documents updated
        """
        try:
            if asset_ids:
                # Reset specific assets
                batch = self.db.batch()
                for asset_id in asset_ids:
                    doc_ref = self.collection.document(asset_id)
                    batch.update(doc_ref, {
                        "download_status": "pending",
                        "download_attempts": 0,
                        "download_error": None,
                        "local_file_path": None,
                        "file_size": None,
                        "download_completed_at": None,
                        "updated_at": datetime.now(timezone.utc)
                    })
                batch.commit()
                return len(asset_ids)
            else:
                # Reset all for wallet
                if not wallet_address:
                    raise ValueError("wallet_address is required when asset_ids is None")
                
                docs = self.collection.where("wallet_address", "==", wallet_address).stream()
                batch = self.db.batch()
                count = 0
                
                for doc in docs:
                    batch.update(doc.reference, {
                        "download_status": "pending",
                        "download_attempts": 0,
                        "download_error": None,
                        "local_file_path": None,
                        "file_size": None,
                        "download_completed_at": None,
                        "updated_at": datetime.now(timezone.utc)
                    })
                    count += 1
                    
                    # Commit in batches of 500 (Firestore limit)
                    if count % 500 == 0:
                        batch.commit()
                        batch = self.db.batch()
                
                if count % 500 != 0:
                    batch.commit()
                
                return count
                
        except Exception as e:
            self.logger.error(f"Failed to reset download status: {str(e)}")
            return 0
    
    def delete_nft(self, asset_id: str) -> bool:
        """
        Delete NFT from Firestore.
        
        Args:
            asset_id: NFT asset ID
            
        Returns:
            True if deleted successfully
        """
        try:
            doc_ref = self.collection.document(asset_id)
            doc_ref.delete()
            self.logger.info(f"Deleted NFT {asset_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete NFT {asset_id}: {str(e)}")
            return False
    
    def get_collection_stats(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about stored NFTs.
        
        Args:
            wallet_address: Optional wallet address filter
            
        Returns:
            Statistics dictionary
        """
        try:
            query = self.collection
            if wallet_address:
                query = query.where("wallet_address", "==", wallet_address)
            
            docs = query.stream()
            
            stats = {
                "total_nfts": 0,
                "collections": {},
                "compressed_count": 0,
                "sync_status_counts": {},
                "recent_additions": []
            }
            
            for doc in docs:
                data = doc.to_dict()
                stats["total_nfts"] += 1
                
                # Count by collection
                collection_name = data.get("collection", {}).get("name", "Unknown")
                stats["collections"][collection_name] = stats["collections"].get(collection_name, 0) + 1
                
                # Count compressed NFTs
                if data.get("compressed", False):
                    stats["compressed_count"] += 1
                
                # Count by sync status
                sync_status = data.get("sync_status", "unknown")
                stats["sync_status_counts"][sync_status] = stats["sync_status_counts"].get(sync_status, 0) + 1
                
                # Track recent additions
                created_at = data.get("created_at")
                if created_at:
                    stats["recent_additions"].append({
                        "asset_id": data.get("asset_id"),
                        "name": data.get("name"),
                        "created_at": created_at
                    })
            
            # Sort recent additions by creation date
            stats["recent_additions"].sort(key=lambda x: x["created_at"], reverse=True)
            stats["recent_additions"] = stats["recent_additions"][:10]  # Keep only top 10
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get collection stats: {str(e)}")
            return {}
    
    def _extract_name(self, nft_data: Dict[str, Any]) -> str:
        """Extract NFT name from Helius data."""
        content = nft_data.get("content", {})
        metadata = content.get("metadata", {})
        return metadata.get("name", "Unknown NFT")
    
    def _extract_symbol(self, nft_data: Dict[str, Any]) -> str:
        """Extract NFT symbol from Helius data."""
        content = nft_data.get("content", {})
        metadata = content.get("metadata", {})
        return metadata.get("symbol", "")
    
    def _extract_description(self, nft_data: Dict[str, Any]) -> str:
        """Extract NFT description from Helius data."""
        content = nft_data.get("content", {})
        metadata = content.get("metadata", {})
        return metadata.get("description", "")
    
    def _extract_image_url(self, nft_data: Dict[str, Any]) -> str:
        """Extract image URL from Helius data."""
        content = nft_data.get("content", {})
        
        # Check files array for image files
        files = content.get("files", [])
        for file_info in files:
            mime_type = file_info.get("mime", "").lower()
            if mime_type.startswith("image/"):
                uri = file_info.get("uri", "")
                if uri:
                    return uri
        
        # Check links.image field
        links = content.get("links", {})
        if links and "image" in links:
            return links["image"]
        
        # Check metadata for image fields
        metadata = content.get("metadata", {})
        for field in ["image", "image_url", "imageUrl"]:
            if field in metadata:
                return metadata[field]
        
        return ""
    
    def _extract_metadata_uri(self, nft_data: Dict[str, Any]) -> str:
        """Extract metadata URI from Helius data."""
        content = nft_data.get("content", {})
        metadata = content.get("metadata", {})
        return metadata.get("uri", "")
    
    def _extract_attributes(self, nft_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract NFT attributes from Helius data."""
        content = nft_data.get("content", {})
        metadata = content.get("metadata", {})
        return metadata.get("attributes", [])
    
    def _extract_collection_info(self, nft_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract collection information from Helius data."""
        content = nft_data.get("content", {})
        metadata = content.get("metadata", {})
        
        collection = metadata.get("collection", {})
        if isinstance(collection, dict):
            return {
                "name": collection.get("name", ""),
                "family": collection.get("family", "")
            }
        
        return {"name": "", "family": ""}
    
    def _extract_royalties(self, nft_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract royalty information from Helius data."""
        content = nft_data.get("content", {})
        metadata = content.get("metadata", {})
        return metadata.get("royalties", [])
    
    def _extract_creators(self, nft_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract creator information from Helius data."""
        content = nft_data.get("content", {})
        metadata = content.get("metadata", {})
        return metadata.get("creators", [])
    
    def _extract_supply(self, nft_data: Dict[str, Any]) -> int:
        """Extract supply information from Helius data."""
        content = nft_data.get("content", {})
        metadata = content.get("metadata", {})
        return metadata.get("supply", 1)
    
    def _update_wallet_summary(self, wallet_address: str, results: Dict[str, Any]) -> None:
        """Update wallet summary in Firestore."""
        try:
            # Create or update wallet summary document
            wallet_summary_ref = self.db.collection("wallet_summaries").document(wallet_address)
            
            summary_data = {
                "wallet_address": wallet_address,
                "total_nfts": results["total_nfts"],
                "last_sync": datetime.now(timezone.utc),
                "sync_status": "completed" if results["failed"] == 0 else "partial",
                "failed_count": results["failed"],
                "updated_at": datetime.now(timezone.utc)
            }
            
            wallet_summary_ref.set(summary_data, merge=True)
            
        except Exception as e:
            self.logger.error(f"Failed to update wallet summary for {wallet_address}: {str(e)}") 