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
        self.api_key = settings.ESTFOR_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_assets(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Fetch assets from EstFor API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/assets",
                    headers=self.headers,
                    params={"limit": limit, "offset": offset}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("Failed to fetch assets from EstFor API", error=str(e))
            raise
    
    async def get_asset_by_id(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific asset by ID."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/assets/{asset_id}",
                    headers=self.headers
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("Failed to fetch asset from EstFor API", error=str(e), asset_id=asset_id)
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


# Global client instance
estfor_client = EstForClient() 