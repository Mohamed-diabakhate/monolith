"""
Authentication dependencies for the EstFor API.
"""

from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
import structlog

from app.config import settings

logger = structlog.get_logger()

# API key header security scheme
api_key_header = APIKeyHeader(
    name=settings.API_KEY_HEADER,
    auto_error=False
)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify API key from request header.
    
    Args:
        api_key: The API key from the request header
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Check if API keys are configured
    if not settings.API_KEYS:
        logger.error("No API keys configured in settings")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key authentication not properly configured"
        )
    
    # Validate the API key
    if api_key not in settings.API_KEYS:
        logger.warning("Invalid API key attempted", api_key_prefix=api_key[:8] if len(api_key) > 8 else api_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    logger.debug("API key validated successfully")
    return api_key


async def optional_api_key(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """
    Optional API key verification.
    
    This dependency can be used for endpoints that should work both with
    and without authentication, potentially with different rate limits
    or feature sets.
    
    Args:
        api_key: The API key from the request header
        
    Returns:
        The validated API key if provided and valid, None otherwise
    """
    if not api_key:
        return None
        
    if not settings.API_KEYS:
        return None
        
    if api_key in settings.API_KEYS:
        logger.debug("Optional API key validated successfully")
        return api_key
    
    logger.warning("Invalid optional API key attempted", api_key_prefix=api_key[:8] if len(api_key) > 8 else api_key)
    return None