"""
PaintSwap API client for fetching sales data.
"""

from typing import Any, Dict, List, Optional
import structlog
import httpx

from app.config import settings


logger = structlog.get_logger()


class PaintSwapClient:
    """Client for interacting with the PaintSwap API."""

    def __init__(self) -> None:
        self.base_url: str = settings.PAINTSWAP_API_URL.rstrip("/")
        self.headers: Dict[str, str] = {"Content-Type": "application/json"}

    async def get_sales(
        self,
        collections: List[str],
        limit: int = 100,
        offset: int = 0,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch sales from PaintSwap API with pagination.

        Args:
            collections: List of collection identifiers to filter by.
            limit: Number of records to return.
            offset: Number of records to skip.
            sort: Optional sort parameter passed through to PaintSwap.

        Returns:
            Parsed JSON from PaintSwap response as a dictionary.
        """

        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if collections:
            # API accepts comma-separated list for collections
            params["collections"] = ",".join(collections)
        if sort:
            params["sort"] = sort

        url = f"{self.base_url}/sales/"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, (dict, list)):
                    logger.warning("Unexpected PaintSwap response structure", data=data)
                    return {"results": [], "count": 0}
                # Normalize to dict with results for consistency
                if isinstance(data, list):
                    return {"results": data, "count": len(data)}
                return data
        except httpx.HTTPStatusError as e:
            logger.error(
                "PaintSwap sales request failed",
                status_code=e.response.status_code if e.response else None,
                error=str(e),
                url=url,
                params=params,
            )
            raise
        except Exception as e:
            logger.error("Error calling PaintSwap sales API", error=str(e), url=url, params=params)
            raise


# Global client instance
paintswap_client = PaintSwapClient()


