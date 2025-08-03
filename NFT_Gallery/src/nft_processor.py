"""
NFT processing logic for downloading and managing Solana NFTs.
"""
import os
import logging
from typing import Dict, List, Optional, Any
from .helius_api import HeliusAPIClient, HeliusAPIError
from .file_manager import FileManager, FileManagerError
import time
import requests


class NFTProcessorError(Exception):
    """Custom exception for NFT processing operations."""
    pass


class NFTProcessor:
    """Main processor for NFT download operations."""
    
    def __init__(self, wallet_address: str, output_dir: str = "~/Pictures/NFTs"):
        """
        Initialize NFT processor.
        
        Args:
            wallet_address: Solana wallet address to fetch NFTs from
            output_dir: Directory to store NFT images
            
        Raises:
            NFTProcessorError: If initialization fails
        """
        self.wallet_address = wallet_address
        self.output_dir = output_dir
        
        # Initialize components
        try:
            # Get Helius API key from environment variable
            self.api_key = os.getenv("HELIUS_API_KEY")
            if not self.api_key:
                raise NFTProcessorError("HELIUS_API_KEY environment variable is required")
            
            self.helius_client = HeliusAPIClient(self.api_key)
            self.file_manager = FileManager(output_dir)
        except (HeliusAPIError, FileManagerError) as e:
            raise NFTProcessorError(f"Failed to initialize NFT processor: {str(e)}")
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def process_wallet(self) -> Dict[str, Any]:
        """
        Process all NFTs in the wallet.
        
        Returns:
            Processing results summary
            
        Raises:
            NFTProcessorError: If processing fails
        """
        try:
            self.logger.info(f"Starting NFT processing for wallet: {self.wallet_address}")
            
            # Fetch NFTs from API
            nft_data = self._fetch_nfts()
            
            if not nft_data:
                raise NFTProcessorError("Invalid response from Helius API")
            
            # DAS API returns data in a specific format with 'items' array
            assets = nft_data.get("items", []) if isinstance(nft_data, dict) else []
            self.logger.info(f"Found {len(assets)} NFTs in wallet")
            
            # Process each NFT
            results = {
                "total_nfts": len(assets),
                "downloaded": 0,
                "skipped": 0,
                "failed": 0,
                "errors": []
            }
            
            for asset in assets:
                try:
                    success = self._process_single_nft(asset)
                    if success:
                        results["downloaded"] += 1
                    else:
                        results["skipped"] += 1
                except Exception as e:
                    results["failed"] += 1
                    error_msg = f"Failed to process NFT {asset.get('id', 'unknown')}: {str(e)}"
                    results["errors"].append(error_msg)
                    self.logger.error(error_msg)
            
            self.logger.info(f"Processing complete: {results['downloaded']} downloaded, {results['skipped']} skipped, {results['failed']} failed")
            return results
            
        except Exception as e:
            raise NFTProcessorError(f"Failed to process wallet: {str(e)}")
    
    def _fetch_nfts(self) -> Dict[str, Any]:
        """
        Fetch NFTs from Helius DAS API.
        
        Returns:
            NFT data from API
            
        Raises:
            NFTProcessorError: If API call fails
        """
        try:
            return self.helius_client.get_nfts_by_owner(self.wallet_address)
        except HeliusAPIError as e:
            raise NFTProcessorError(f"Failed to fetch NFTs: {str(e)}")
    
    def _process_single_nft(self, asset: Dict[str, Any]) -> bool:
        """
        Process a single NFT asset.
        
        Args:
            asset: NFT asset data from Helius DAS API
            
        Returns:
            True if processed successfully, False if skipped
            
        Raises:
            NFTProcessorError: If processing fails
        """
        # Extract NFT data from Helius DAS API format
        asset_id = asset.get("id", "")
        name = asset.get("content", {}).get("metadata", {}).get("name", "")
        image_url = self._extract_image_url(asset)
        
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
                return True
            else:
                self.logger.error(f"Failed to download: {name} ({asset_id})")
                return False
        except FileManagerError as e:
            self.logger.error(f"File manager error for {name} ({asset_id}): {str(e)}")
            # Track failed downloads for reporting
            self._track_failed_download(name, asset_id, image_url, str(e))
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error downloading {name} ({asset_id}): {str(e)}")
            self._track_failed_download(name, asset_id, image_url, str(e))
            return False
    
    def _track_failed_download(self, name: str, asset_id: str, image_url: str, error: str) -> None:
        """
        Track failed downloads for reporting purposes.
        
        Args:
            name: NFT name
            asset_id: Asset ID
            image_url: Image URL that failed
            error: Error message
        """
        if not hasattr(self, '_failed_downloads'):
            self._failed_downloads = []
        
        self._failed_downloads.append({
            'name': name,
            'asset_id': asset_id,
            'image_url': image_url,
            'error': error,
            'timestamp': time.time()
        })
    
    def get_failed_downloads_report(self) -> List[Dict[str, Any]]:
        """
        Get a report of failed downloads.
        
        Returns:
            List of failed download details
        """
        return getattr(self, '_failed_downloads', [])
    
    def get_failed_downloads_summary(self) -> Dict[str, Any]:
        """
        Get a summary of failed downloads by error type.
        
        Returns:
            Summary of failed downloads
        """
        failed_downloads = self.get_failed_downloads_report()
        
        error_counts = {}
        domain_counts = {}
        
        for failed in failed_downloads:
            error = failed['error']
            url = failed['image_url']
            
            # Count by error type
            error_type = 'unknown'
            if '403' in error:
                error_type = 'forbidden'
            elif '404' in error:
                error_type = 'not_found'
            elif 'timeout' in error.lower():
                error_type = 'timeout'
            elif 'ssl' in error.lower():
                error_type = 'ssl_error'
            elif 'json' in error.lower():
                error_type = 'json_response'
            elif 'empty' in error.lower():
                error_type = 'empty_file'
            
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            # Count by domain
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            except:
                domain_counts['unknown'] = domain_counts.get('unknown', 0) + 1
        
        return {
            'total_failed': len(failed_downloads),
            'error_counts': error_counts,
            'domain_counts': domain_counts,
            'failed_downloads': failed_downloads
        }
    
    def _extract_image_url(self, asset: Dict[str, Any]) -> str:
        """
        Extract image URL from Helius DAS API asset data.
        
        Args:
            asset: NFT asset data from Helius DAS API
            
        Returns:
            Image URL or empty string if not found
        """
        # Try multiple possible locations for image URL
        content = asset.get("content", {})
        
        # First priority: Check files array for image files
        files = content.get("files", [])
        for file_info in files:
            mime_type = file_info.get("mime", "").lower()
            if mime_type.startswith("image/"):
                uri = file_info.get("uri", "")
                if uri:
                    return uri
        
        # Second priority: Check links.image field
        links = content.get("links", {})
        if links and "image" in links:
            image_url = links["image"]
            if image_url:
                return image_url
        
        # Third priority: Check metadata for image fields
        metadata = content.get("metadata", {})
        if metadata:
            # Try common image field names
            for field in ["image", "image_url", "imageUrl", "image_uri", "imageUri"]:
                if field in metadata:
                    image_url = metadata[field]
                    if image_url:
                        return image_url
        
        # Fourth priority: Check for external_url that might be an image
        if metadata:
            external_url = metadata.get("external_url", "")
            if external_url:
                # Check if it looks like an image URL
                if any(ext in external_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff']):
                    return external_url
                # Also check for common image hosting domains
                image_domains = ['ipfs.io', 'arweave.net', 'nftstorage.link', 'cloudflare-ipfs.com', 'gateway.pinata.cloud']
                if any(domain in external_url for domain in image_domains):
                    return external_url
        
        # Fifth priority: Check for any URI fields in the asset
        if "uri" in asset:
            uri = asset["uri"]
            if uri and any(ext in uri.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff']):
                return uri
        
        # Sixth priority: Check for any URL-like fields in the entire asset
        def search_for_urls(obj, max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return None
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str) and value:
                        # Check if it looks like an image URL
                        if value.startswith(('http://', 'https://', 'ipfs://', 'ar://')):
                            if any(ext in value.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff']):
                                return value
                            # Also check for image hosting domains
                            image_domains = ['ipfs.io', 'arweave.net', 'nftstorage.link', 'cloudflare-ipfs.com', 'gateway.pinata.cloud']
                            if any(domain in value for domain in image_domains):
                                return value
                    
                    # Recursively search nested objects
                    result = search_for_urls(value, max_depth, current_depth + 1)
                    if result:
                        return result
                        
            elif isinstance(obj, list):
                for item in obj:
                    result = search_for_urls(item, max_depth, current_depth + 1)
                    if result:
                        return result
            
            return None
        
        # Search the entire asset for image URLs
        found_url = search_for_urls(asset)
        if found_url:
            return found_url
        
        # Seventh priority: Try to extract from metadata URI (IPFS/Arweave)
        # This is the most robust method for NFTs that store images in IPFS
        metadata_image_url = self._extract_image_url_from_metadata(asset)
        if metadata_image_url:
            return metadata_image_url
        
        return ""
    
    def _extract_image_url_from_metadata(self, asset: Dict[str, Any]) -> str:
        """
        Extract image URL by fetching and parsing NFT metadata from IPFS/Arweave.
        
        Args:
            asset: NFT asset data from Helius DAS API
            
        Returns:
            Image URL or empty string if not found
        """
        # First, try to get the metadata URI from the asset
        metadata_uri = self._get_metadata_uri(asset)
        if not metadata_uri:
            return ""
        
        try:
            # Fetch the metadata
            metadata = self._fetch_metadata(metadata_uri)
            if not metadata:
                return ""
            
            # Extract image URL from metadata
            image_url = self._extract_image_from_metadata(metadata)
            if image_url:
                return image_url
                
        except Exception as e:
            self.logger.debug(f"Failed to fetch metadata from {metadata_uri}: {str(e)}")
        
        return ""
    
    def _get_metadata_uri(self, asset: Dict[str, Any]) -> str:
        """
        Get the metadata URI from the asset.
        
        Args:
            asset: NFT asset data
            
        Returns:
            Metadata URI or empty string
        """
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
        
        # Priority 5: Check if the asset itself has a URI that might be metadata
        if "uri" in asset:
            uri = asset["uri"]
            if uri and isinstance(uri, str):
                # Check if it looks like a metadata URI
                if any(ext in uri.lower() for ext in ['.json', 'ipfs://', 'ar://', 'https://']):
                    return uri
        
        return ""
    
    def _fetch_metadata(self, metadata_uri: str) -> Optional[Dict[str, Any]]:
        """
        Fetch metadata from URI (IPFS, Arweave, HTTP).
        
        Args:
            metadata_uri: URI to fetch metadata from
            
        Returns:
            Parsed metadata or None if failed
        """
        try:
            # Handle IPFS URIs
            if metadata_uri.startswith('ipfs://'):
                ipfs_hash = metadata_uri.replace('ipfs://', '')
                # Try multiple IPFS gateways
                gateways = [
                    f'https://ipfs.io/ipfs/{ipfs_hash}',
                    f'https://cloudflare-ipfs.com/ipfs/{ipfs_hash}',
                    f'https://gateway.pinata.cloud/ipfs/{ipfs_hash}',
                    f'https://dweb.link/ipfs/{ipfs_hash}',
                    f'https://nftstorage.link/ipfs/{ipfs_hash}'
                ]
                
                for gateway_url in gateways:
                    try:
                        response = requests.get(gateway_url, timeout=10, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        })
                        response.raise_for_status()
                        return response.json()
                    except Exception as e:
                        self.logger.debug(f"Failed to fetch from {gateway_url}: {str(e)}")
                        continue
            
            # Handle Arweave URIs
            elif metadata_uri.startswith('ar://'):
                ar_hash = metadata_uri.replace('ar://', '')
                arweave_url = f'https://arweave.net/{ar_hash}'
                try:
                    response = requests.get(arweave_url, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    response.raise_for_status()
                    return response.json()
                except Exception as e:
                    self.logger.debug(f"Failed to fetch from Arweave {arweave_url}: {str(e)}")
            
            # Handle HTTP/HTTPS URIs
            elif metadata_uri.startswith(('http://', 'https://')):
                try:
                    response = requests.get(metadata_uri, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    response.raise_for_status()
                    return response.json()
                except Exception as e:
                    self.logger.debug(f"Failed to fetch from {metadata_uri}: {str(e)}")
            
        except Exception as e:
            self.logger.debug(f"Error fetching metadata from {metadata_uri}: {str(e)}")
        
        return None
    
    def _extract_image_from_metadata(self, metadata: Dict[str, Any]) -> str:
        """
        Extract image URL from parsed metadata.
        
        Args:
            metadata: Parsed metadata dictionary
            
        Returns:
            Image URL or empty string
        """
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
                
                # Check properties.image
                for field in image_fields:
                    if field in properties:
                        image_url = properties[field]
                        if image_url and isinstance(image_url, str):
                            return image_url
        
        # Priority 3: Check attributes for image data
        if 'attributes' in metadata:
            attributes = metadata['attributes']
            if isinstance(attributes, list):
                for attr in attributes:
                    if isinstance(attr, dict):
                        trait_type = attr.get('trait_type', '').lower()
                        if 'image' in trait_type or 'url' in trait_type:
                            value = attr.get('value', '')
                            if value and isinstance(value, str) and value.startswith(('http://', 'https://', 'ipfs://', 'ar://')):
                                return value
        
        # Priority 4: Recursive search through the entire metadata
        def search_recursive(obj, max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return None
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    # Check if this key looks like an image field
                    if key.lower() in [field.lower() for field in image_fields]:
                        if isinstance(value, str) and value:
                            # Check if it looks like a URL
                            if value.startswith(('http://', 'https://', 'ipfs://', 'ar://')):
                                return value
                    
                    # Recursively search nested objects
                    result = search_recursive(value, max_depth, current_depth + 1)
                    if result:
                        return result
                        
            elif isinstance(obj, list):
                for item in obj:
                    result = search_recursive(item, max_depth, current_depth + 1)
                    if result:
                        return result
            
            return None
        
        found_url = search_recursive(metadata)
        if found_url:
            return found_url
        
        return ""
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            downloaded_files = self.file_manager.list_downloaded_files()
            available_space, total_space = self.file_manager.get_disk_space()
            
            return {
                "downloaded_files": len(downloaded_files),
                "available_space_gb": round(available_space / (1024**3), 2),
                "total_space_gb": round(total_space / (1024**3), 2),
                "output_directory": str(self.file_manager.output_dir)
            }
        except Exception as e:
            self.logger.error(f"Failed to get processing stats: {str(e)}")
            return {}
    
    def validate_wallet_address(self) -> bool:
        """
        Validate the wallet address format.
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # This will raise an exception if the address is invalid
            self.helius_client._is_valid_solana_address(self.wallet_address)
            return True
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
    
    def cleanup_orphaned_files(self, nft_data: Dict[str, Any]) -> int:
        """
        Remove files that are no longer in the wallet.
        
        Args:
            nft_data: Current NFT data from Helius DAS API
            
        Returns:
            Number of files removed
        """
        try:
            current_nfts = set()
            
            # DAS API returns data in a specific format with 'items' array
            assets = nft_data.get("items", []) if isinstance(nft_data, dict) else []
            
            for asset in assets:
                asset_id = asset.get("id", "")
                name = asset.get("content", {}).get("metadata", {}).get("name", "")
                image_url = self._extract_image_url(asset)
                
                if image_url:
                    filename = self.file_manager._generate_safe_filename(name, asset_id, asset_id, image_url)
                    current_nfts.add(filename)
            
            downloaded_files = set(self.file_manager.list_downloaded_files())
            orphaned_files = downloaded_files - current_nfts
            
            removed_count = 0
            for filename in orphaned_files:
                try:
                    file_path = self.file_manager.output_dir / filename
                    file_path.unlink()
                    removed_count += 1
                    self.logger.info(f"Removed orphaned file: {filename}")
                except Exception as e:
                    self.logger.error(f"Failed to remove orphaned file {filename}: {str(e)}")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup orphaned files: {str(e)}")
            return 0 