"""
Database package for EstFor application.
"""

# Import base database functions for backward compatibility
from .base import (
    init_mongodb,
    close_mongodb,
    test_connection,
    get_collection,
    store_asset,
    get_asset,
    list_assets,
    update_asset,
    delete_asset,
    get_asset_count,
)

# Import enhanced database functionality
from .enhanced import enhanced_asset_db

__all__ = [
    # Base database functions
    'init_mongodb',
    'close_mongodb', 
    'test_connection',
    'get_collection',
    'store_asset',
    'get_asset',
    'list_assets',
    'update_asset',
    'delete_asset',
    'get_asset_count',
    # Enhanced database
    'enhanced_asset_db',
]