"""
Dependencies module for FastAPI application.
"""

from .auth import verify_api_key, optional_api_key

__all__ = ["verify_api_key", "optional_api_key"]