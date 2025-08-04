"""
EstFor API client for fetching assets.
"""

import httpx
from typing import Dict, Any, List, Optional
import structlog

from app.config import settings

logger = structlog.get_logger()


class EstForClient:
    """Client for interacting with the EstFor API."""
    
    def __init__(self):
        self.base_url = settings.ESTFOR_API_URL
        # EstFor API doesn't require authentication
        self.headers = {
            "Content-Type": "application/json"
        }
    
    async def get_assets(self, limit: int = 100, offset: int = 0, asset_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch items from EstFor API."""
        try:
            async with httpx.AsyncClient() as client:
                params = {"limit": limit, "offset": offset}
                if asset_type:
                    params["type"] = asset_type
                
                response = await client.get(
                    f"{self.base_url}/items",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                # Handle the API response structure: {"items": [...]}
                if isinstance(data, dict) and "items" in data:
                    return data["items"]
                elif isinstance(data, list):
                    return data
                else:
                    logger.warning("Unexpected API response structure", data=data)
                    return []
        except Exception as e:
            logger.error("Failed to fetch items from EstFor API", error=str(e))
            raise
    
    async def get_asset_by_id(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific item by ID."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/items/{asset_id}",
                    headers=self.headers
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("Failed to fetch item from EstFor API", error=str(e), asset_id=asset_id)
            raise
    
    async def search_assets(self, query: str) -> List[Dict[str, Any]]:
        """Search assets by query."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/assets/search",
                    headers=self.headers,
                    params={"q": query}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("Failed to search assets from EstFor API", error=str(e), query=query)
            raise
    
    async def get_asset_stats(self) -> Dict[str, Any]:
        """Get asset statistics from EstFor API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/assets/stats",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("Failed to fetch asset stats from EstFor API", error=str(e))
            raise


# Global client instance
estfor_client = EstForClient() 