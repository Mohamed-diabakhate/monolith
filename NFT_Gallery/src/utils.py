"""
Utility functions for Solana NFT Downloader.
"""
import os
import sys
import logging
from typing import Optional, Dict, Any
from pathlib import Path


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("solana_nft_downloader")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def validate_environment() -> Dict[str, Any]:
    """
    Validate required environment variables and system requirements.
    
    Returns:
        Dictionary with validation results
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check required environment variables
    if not os.getenv("HELIUS_API_KEY"):
        results["valid"] = False
        results["errors"].append("HELIUS_API_KEY environment variable is required")
    
    # Check if running on macOS (for Photos app integration)
    if sys.platform != "darwin":
        results["warnings"].append("Not running on macOS - Photos app integration may not work")
    
    # Check if output directory is writable
    # Use OUTPUT_DIR environment variable if available, otherwise default to ~/Pictures/SolanaNFTs
    output_dir = Path(os.getenv("OUTPUT_DIR", "~/Pictures/SolanaNFTs")).expanduser()
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        test_file = output_dir / ".test_write"
        test_file.write_text("test")
        test_file.unlink()
    except Exception as e:
        results["valid"] = False
        results["errors"].append(f"Cannot write to output directory {output_dir}: {str(e)}")
    
    return results


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def get_system_info() -> Dict[str, str]:
    """
    Get system information for debugging.
    
    Returns:
        Dictionary with system information
    """
    import platform
    
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "home_directory": str(Path.home()),
        "current_working_directory": os.getcwd()
    }


def create_backup_filename(original_filename: str) -> str:
    """
    Create a backup filename with timestamp.
    
    Args:
        original_filename: Original filename
        
    Returns:
        Backup filename with timestamp
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(original_filename)
    return f"{name}_backup_{timestamp}{ext}"


def is_valid_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        Decorated function
    """
    import time
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        raise last_exception
            
            raise last_exception
        
        return wrapper
    return decorator


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename for safe filesystem usage.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Sanitized filename
    """
    import re
    
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*\x00-\x1f'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        max_name_length = max_length - len(ext)
        filename = name[:max_name_length] + ext
    
    # Ensure not empty
    if not filename:
        filename = "unnamed"
    
    return filename


def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> Optional[str]:
    """
    Calculate file hash.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        File hash or None if calculation fails
    """
    import hashlib
    
    if not file_path.exists():
        return None
    
    try:
        hash_obj = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception:
        return None 