"""
Shared utilities for API routes
"""

from fastapi import Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


async def get_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_id: Optional[str] = Query(None, description="User ID for tracking")
) -> str:
    """Extract user ID for request tracking."""
    if user_id:
        return user_id
    # TODO: Extract from JWT token when authentication is implemented
    return "anonymous"