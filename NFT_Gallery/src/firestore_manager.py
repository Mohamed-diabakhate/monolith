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
                "sync_status": "synced"
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
        Update NFT sync status.
        
        Args:
            asset_id: NFT asset ID
            status: Sync status ("synced", "failed", "pending")
            
        Returns:
            True if updated successfully
        """
        try:
            doc_ref = self.collection.document(asset_id)
            doc_ref.update({
                "sync_status": status,
                "last_synced": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            })
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update sync status for {asset_id}: {str(e)}")
            return False
    
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