"""
Dependency injection utilities.
"""

from typing import Annotated, Optional

from fastapi import Depends, Header

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token


async def get_token_from_header(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> str:
    """
    Extract and validate Bearer token from Authorization header.
    """
    if not authorization:
        raise UnauthorizedException(detail="Authorization header missing")
    
    scheme, _, token = authorization.partition(" ")
    
    if scheme.lower() != "bearer":
        raise UnauthorizedException(detail="Invalid authentication scheme")
    
    if not token:
        raise UnauthorizedException(detail="Token missing")
    
    return token


async def get_current_user(
    token: Annotated[str, Depends(get_token_from_header)],
) -> dict:
    """
    Get current authenticated user from JWT token.
    """
    payload = decode_access_token(token)
    
    if payload is None:
        raise UnauthorizedException(detail="Invalid or expired token")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(detail="Invalid token payload")
    
    # Return user data from token
    return {
        "id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role"),
    }


# Type alias for authenticated user dependency
CurrentUser = Annotated[dict, Depends(get_current_user)]
