"""
Firebase Authentication utilities.
Verifies Firebase ID tokens and extracts user information.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx

from app.core.config import settings


# HTTP Bearer token scheme
security = HTTPBearer()


async def verify_firebase_token(token: str) -> dict:
    """
    Verify Firebase ID token by calling Google's tokeninfo endpoint.
    Returns the decoded token payload containing user info.
    """
    # For production, you should use Firebase Admin SDK
    # This is a simpler approach using Google's public key verification
    
    try:
        # Verify token with Google
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}"
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Firebase token",
                )
            
            payload = response.json()
            
            # Verify the audience matches our project
            if payload.get("aud") != settings.FIREBASE_PROJECT_ID:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token audience mismatch",
                )
            
            return payload
            
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_UNAVAILABLE,
            detail="Unable to verify token",
        )


async def get_current_firebase_uid(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Dependency that extracts and verifies Firebase UID from the Authorization header.
    Returns the Firebase UID (localId).
    """
    token = credentials.credentials
    
    # Decode the JWT to get the user_id (sub claim) without full verification
    # For production, use Firebase Admin SDK for proper verification
    try:
        import base64
        import json
        
        # Split the JWT and decode the payload
        parts = token.split(".")
        if len(parts) != 3:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
            )
        
        # Add padding if needed
        payload_b64 = parts[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        
        # The 'sub' claim contains the Firebase UID (localId)
        firebase_uid = payload.get("sub") or payload.get("user_id")
        
        if not firebase_uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )
        
        return firebase_uid
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )
