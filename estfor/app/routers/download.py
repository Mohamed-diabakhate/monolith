"""
Endpoints for downloading external marketplace data (e.g., PaintSwap sales).
"""

from typing import List, Optional, Dict, Any
import re
import structlog
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from pydantic import field_validator

from app.services.paintswap_client import paintswap_client
from app.dependencies.auth import verify_api_key


logger = structlog.get_logger()
router = APIRouter(prefix="/download", tags=["download"])


class SalesResponse(Dict[str, Any]):
    pass


def validate_collection_slug(collection: str) -> str:
    """Validate collection slug format and length."""
    # Allow alphanumeric, hyphens, underscores, max 100 chars
    pattern = r'^[a-zA-Z0-9_-]{1,100}$'
    if not re.match(pattern, collection):
        raise ValueError(f"Invalid collection slug format: {collection}")
    return collection


@router.get("/sales", response_model=None)
async def download_sales(
    request: Request,
    api_key: str = Depends(verify_api_key),
    collections: List[str] = Query(..., description="Collection slugs or IDs to filter sales by", min_length=1, max_length=50),
    limit: int = Query(100, ge=1, le=500, description="Number of sales to return"),
    offset: int = Query(0, ge=0, description="Number of sales to skip"),
    page: Optional[int] = Query(None, ge=0, description="Page number (0-indexed). If provided, overrides offset as page*limit"),
    page_size: Optional[int] = Query(None, ge=1, le=500, description="Alias for limit when using page-based pagination"),
    sort: Optional[str] = Query(None, description="Optional sort parameter passed through to PaintSwap"),
    fetch_all: bool = Query(False, description="If true, auto-paginate to fetch multiple pages"),
    max_pages: int = Query(10, ge=1, le=100, description="Maximum pages to fetch when all=true"),
    max_records: Optional[int] = Query(None, ge=1, description="Hard cap of records to fetch when all=true"),
):
    """Proxy endpoint to fetch sales from PaintSwap with pagination.

    Base: api.paintswap.finance
    Path: /sales/
    Input: collections (query, repeated or comma-separated)
    Pagination: limit, offset
    """
    try:
        # Validate each collection slug
        validated_collections = []
        for collection in collections:
            try:
                validated_collections.append(validate_collection_slug(collection))
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        # Support page-based pagination
        effective_limit = page_size if page_size is not None else limit
        effective_offset = (page * effective_limit) if page is not None else offset

        def extract_results(payload: Any) -> List[Any]:
            if isinstance(payload, dict):
                if "results" in payload and isinstance(payload["results"], list):
                    return payload["results"]
                if "sales" in payload and isinstance(payload["sales"], list):
                    return payload["sales"]
                if "data" in payload and isinstance(payload["data"], list):
                    return payload["data"]
                return []
            if isinstance(payload, list):
                return payload
            return []

        aggregated: List[Any] = []
        current_offset = effective_offset
        pages_fetched = 0

        while True:
            data = await paintswap_client.get_sales(
                collections=validated_collections,
                limit=effective_limit,
                offset=current_offset,
                sort=sort,
            )
            batch = extract_results(data)
            aggregated.extend(batch)
            pages_fetched += 1

            # Stop if not auto-paginating
            if not fetch_all:
                break

            # Stop if batch smaller than page size (no more results)
            if len(batch) < effective_limit:
                break

            # Stop if limits reached
            if pages_fetched >= max_pages:
                break
            if max_records is not None and len(aggregated) >= max_records:
                aggregated = aggregated[:max_records]
                break

            current_offset += effective_limit

        results = aggregated
        returned = len(results)
        computed_page = (effective_offset // effective_limit) if effective_limit else 0
        has_more = (
            returned >= effective_limit and (
                fetch_all or len(results) == effective_limit
            )
        )

        # Build HATEOAS-style pagination links
        self_url = str(request.url)
        next_url = None
        prev_url = None
        if not fetch_all:
            if has_more:
                next_url = str(
                    request.url.include_query_params(
                        offset=effective_offset + effective_limit,
                        limit=effective_limit,
                        page=None,
                        page_size=None,
                    )
                )
            if effective_offset > 0:
                prev_offset = max(0, effective_offset - effective_limit)
                prev_url = str(
                    request.url.include_query_params(
                        offset=prev_offset,
                        limit=effective_limit,
                        page=None,
                        page_size=None,
                    )
                )

        return {
            "collections": validated_collections,
            "pagination": {
                "limit": effective_limit,
                "offset": effective_offset,
                "page": computed_page,
                "page_size": effective_limit,
                "returned": returned,
                "has_more": has_more,
                "pages_fetched": pages_fetched,
                "aggregated": fetch_all,
            },
            "links": {
                "self": self_url,
                "next": next_url,
                "prev": prev_url,
            },
            "results": results,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to download PaintSwap sales", error=str(e))
        raise HTTPException(status_code=502, detail="Failed to fetch sales from PaintSwap")


