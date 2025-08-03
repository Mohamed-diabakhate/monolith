"""
Local file system operations for NFT image management.
"""
import os
import shutil
import requests
from pathlib import Path
from typing import Optional, List, Tuple
from urllib.parse import urlparse
import hashlib


class FileManagerError(Exception):
    """Custom exception for file operations."""
    pass


class FileManager:
    """Manages local file operations for NFT images."""
    
    def __init__(self, output_dir: str = "~/Pictures/SolanaNFTs"):
        """
        Initialize file manager.
        
        Args:
            output_dir: Directory to store NFT images (default: ~/Pictures/SolanaNFTs)
        """
        self.output_dir = Path(output_dir).expanduser().resolve()
        self._ensure_output_directory()
    
    def _ensure_output_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise FileManagerError(f"Permission denied creating directory: {self.output_dir}")
        except Exception as e:
            raise FileManagerError(f"Failed to create output directory: {str(e)}")
    
    def _generate_safe_filename(self, nft_name: str, token_id: str, contract: str, url: str) -> str:
        """
        Generate a safe filename for NFT image.
        
        Args:
            nft_name: NFT name
            token_id: Token ID
            contract: Contract address
            url: Image URL
            
        Returns:
            Safe filename with extension
        """
        # Clean NFT name for filename
        safe_name = self._sanitize_filename(nft_name or f"NFT_{token_id}")
        
        # Get file extension from URL
        extension = self._get_extension_from_url(url)
        
        # Create unique filename
        filename = f"{safe_name}_{token_id[:8]}_{contract[:8]}{extension}"
        
        return filename
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe filesystem usage.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        
        # Ensure not empty
        if not filename:
            filename = "unnamed"
        
        return filename
    
    def _get_extension_from_url(self, url: str) -> str:
        """
        Extract file extension from URL.
        
        Args:
            url: Image URL
            
        Returns:
            File extension with dot (e.g., '.jpg')
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Common image extensions
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']
        
        for ext in extensions:
            if path.endswith(ext):
                return ext
        
        # Default to .jpg if no extension found
        return '.jpg'
    
    def file_exists(self, filename: str) -> bool:
        """
        Check if file already exists in output directory.
        
        Args:
            filename: Filename to check
            
        Returns:
            True if file exists, False otherwise
        """
        file_path = self.output_dir / filename
        return file_path.exists() and file_path.is_file()
    
    def download_image(self, url: str, filename: str, max_retries: int = 3) -> bool:
        """
        Download image from URL and save to output directory.
        
        Args:
            url: Image URL to download
            filename: Target filename
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if download successful, False otherwise
            
        Raises:
            FileManagerError: If download fails
        """
        if not url or not filename:
            raise FileManagerError("URL and filename are required")
        
        file_path = self.output_dir / filename
        
        # Handle problematic domains and get alternative URLs
        fixed_url = self._handle_problematic_domains(url)
        urls_to_try = [fixed_url] if isinstance(fixed_url, str) else fixed_url
        
        for url_to_try in urls_to_try:
            for attempt in range(max_retries):
                try:
                    # Download image with more flexible settings
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    
                    response = requests.get(
                        url_to_try, 
                        stream=True, 
                        timeout=30,
                        headers=headers,
                        allow_redirects=True,
                        verify=False  # Disable SSL verification for problematic sites
                    )
                    response.raise_for_status()
                    
                    # Check content type - be more flexible
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # Allow common image types and some edge cases
                    allowed_types = [
                        'image/',  # Standard image types
                        'application/octet-stream',  # Some servers send this for images
                        'text/html',  # Some image URLs redirect to HTML pages
                        'application/json',  # Some servers send JSON with image data
                        'text/plain',  # Some servers send plain text
                        'binary/octet-stream'  # Generic binary data
                    ]
                    
                    is_allowed_type = any(content_type.startswith(t) for t in allowed_types)
                    
                    # Additional check: if content type is not clearly an image, check the URL and content
                    if not is_allowed_type:
                        # Check if URL has image extension
                        url_lower = url_to_try.lower()
                        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff', '.ico']
                        has_image_extension = any(ext in url_lower for ext in image_extensions)
                        
                        if not has_image_extension:
                            # For JSON responses, try to extract image URL from the JSON
                            if content_type.startswith('application/json'):
                                try:
                                    json_data = response.json()
                                    # Look for common image URL fields in JSON
                                    image_url = self._extract_image_from_json(json_data)
                                    if image_url:
                                        # Recursively try to download from the extracted URL
                                        return self.download_image(image_url, filename, max_retries - 1)
                                except (ValueError, KeyError):
                                    pass
                            
                            # If we still can't determine it's an image, check the first few bytes
                            content = response.content[:10]
                            if not any(magic in content for magic in [b'\xff\xd8\xff', b'\x89PNG', b'GIF8', b'RIFF']):
                                raise FileManagerError(f"URL does not point to an image: {content_type}")
                    
                    # Save file
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Verify the file was actually saved and has content
                    if file_path.stat().st_size == 0:
                        raise FileManagerError("Downloaded file is empty")
                    
                    return True
                    
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1 and self._should_retry_error(e):
                        continue
                    else:
                        raise FileManagerError(f"Failed to download image from {url_to_try}: {str(e)}")
                except IOError as e:
                    raise FileManagerError(f"Failed to save image to {file_path}: {str(e)}")
                except Exception as e:
                    if attempt < max_retries - 1 and self._should_retry_error(e):
                        continue
                    else:
                        raise FileManagerError(f"Unexpected error downloading image: {str(e)}")
        
        return False
    
    def _extract_image_from_json(self, json_data: dict) -> str:
        """
        Extract image URL from JSON response.
        
        Args:
            json_data: JSON data that might contain image URL
            
        Returns:
            Image URL or empty string if not found
        """
        # Common patterns for image URLs in JSON responses
        image_fields = [
            'image', 'image_url', 'imageUrl', 'url', 'uri', 'src', 'link',
            'thumbnail', 'preview', 'display', 'media', 'file'
        ]
        
        def search_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Check if this key looks like an image field
                    if key.lower() in [field.lower() for field in image_fields]:
                        if isinstance(value, str) and value:
                            # Check if it looks like a URL
                            if value.startswith(('http://', 'https://', 'ipfs://', 'ar://')):
                                return value
                    
                    # Recursively search nested objects
                    result = search_recursive(value, current_path)
                    if result:
                        return result
                        
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    result = search_recursive(item, current_path)
                    if result:
                        return result
        
        return search_recursive(json_data) or ""
    
    def get_file_info(self, filename: str) -> Optional[dict]:
        """
        Get information about a file.
        
        Args:
            filename: Filename to check
            
        Returns:
            File info dictionary or None if file doesn't exist
        """
        file_path = self.output_dir / filename
        
        if not file_path.exists():
            return None
        
        try:
            stat = file_path.stat()
            return {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'path': str(file_path)
            }
        except Exception:
            return None
    
    def list_downloaded_files(self) -> List[str]:
        """
        List all downloaded NFT files.
        
        Returns:
            List of filenames
        """
        try:
            files = []
            for file_path in self.output_dir.iterdir():
                if file_path.is_file():
                    files.append(file_path.name)
            return sorted(files)
        except Exception as e:
            raise FileManagerError(f"Failed to list files: {str(e)}")
    
    def get_disk_space(self) -> Tuple[int, int]:
        """
        Get available and total disk space.
        
        Returns:
            Tuple of (available_bytes, total_bytes)
        """
        try:
            stat = shutil.disk_usage(self.output_dir)
            return stat.free, stat.total
        except Exception as e:
            raise FileManagerError(f"Failed to get disk space: {str(e)}")
    
    def cleanup_temp_files(self, pattern: str = "*.tmp") -> int:
        """
        Clean up temporary files.
        
        Args:
            pattern: File pattern to match
            
        Returns:
            Number of files cleaned up
        """
        try:
            count = 0
            for file_path in self.output_dir.glob(pattern):
                if file_path.is_file():
                    file_path.unlink()
                    count += 1
            return count
        except Exception as e:
            raise FileManagerError(f"Failed to cleanup temp files: {str(e)}")
    
    def get_file_hash(self, filename: str) -> Optional[str]:
        """
        Calculate SHA256 hash of a file.
        
        Args:
            filename: Filename to hash
            
        Returns:
            SHA256 hash or None if file doesn't exist
        """
        file_path = self.output_dir / filename
        
        if not file_path.exists():
            return None
        
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return None 

    def _handle_problematic_domains(self, url: str) -> str:
        """
        Handle known problematic domains by applying fixes.
        
        Args:
            url: Original URL
            
        Returns:
            Fixed URL or original URL if no fix needed
        """
        # Handle hi-hi.vip domain issues
        if 'hi-hi.vip' in url:
            # Try different subdomains or paths
            if '/json/' in url:
                # Replace JSON endpoint with image endpoint
                url = url.replace('/json/', '/img/')
                url = url.replace('.json', '.png')
            elif 'img.hi-hi.vip' in url and '/img/img/' in url:
                # Fix double img path
                url = url.replace('/img/img/', '/img/')
            elif 'img.hi-hi.vip' in url:
                # Try alternative subdomain
                url = url.replace('img.hi-hi.vip', 'www.hi-hi.vip')
        
        # Handle IPFS gateway issues
        if 'nftstorage.link' in url:
            # Try alternative IPFS gateways
            if 'ipfs/' in url:
                # Extract IPFS hash and try different gateways
                ipfs_hash = url.split('ipfs/')[-1].split('/')[0]
                gateways = [
                    f'https://ipfs.io/ipfs/{ipfs_hash}',
                    f'https://cloudflare-ipfs.com/ipfs/{ipfs_hash}',
                    f'https://gateway.pinata.cloud/ipfs/{ipfs_hash}',
                    f'https://dweb.link/ipfs/{ipfs_hash}'
                ]
                return gateways  # Return list for retry attempts
        
        # Handle IPFS protocol URLs
        if url.startswith('ipfs://'):
            ipfs_hash = url.replace('ipfs://', '')
            # Try multiple IPFS gateways
            gateways = [
                f'https://ipfs.io/ipfs/{ipfs_hash}',
                f'https://cloudflare-ipfs.com/ipfs/{ipfs_hash}',
                f'https://gateway.pinata.cloud/ipfs/{ipfs_hash}',
                f'https://dweb.link/ipfs/{ipfs_hash}',
                f'https://nftstorage.link/ipfs/{ipfs_hash}'
            ]
            return gateways  # Return list for retry attempts
        
        # Handle Arweave protocol URLs
        if url.startswith('ar://'):
            ar_hash = url.replace('ar://', '')
            return f'https://arweave.net/{ar_hash}'
        
        return url
    
    def _should_retry_error(self, error: Exception) -> bool:
        """
        Determine if an error should trigger a retry.
        
        Args:
            error: The exception that occurred
            
        Returns:
            True if retry should be attempted, False otherwise
        """
        error_str = str(error).lower()
        
        # Retry on these errors
        retry_errors = [
            'timeout', 'connection', 'dns', 'ssl', 'certificate', 
            'forbidden', 'too many requests', 'rate limit',
            'temporary', 'server error', 'bad gateway', 'service unavailable'
        ]
        
        # Don't retry on these errors
        no_retry_errors = [
            'not found', '404', 'unauthorized', '401', '403',
            'malformed', 'invalid url', 'empty file'
        ]
        
        for retry_error in retry_errors:
            if retry_error in error_str:
                return True
        
        for no_retry_error in no_retry_errors:
            if no_retry_error in error_str:
                return False
        
        # Default to retry for unknown errors
        return True 