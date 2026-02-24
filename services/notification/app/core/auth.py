"""Authentication module for notification service.

Verifies JWT tokens issued by the main API service.
"""
import os
import jwt
from typing import Optional
from dataclasses import dataclass
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import structlog

from app.config import settings

logger = structlog.get_logger()
security = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    """Authenticated user context."""
    uid: str
    role: str
    salon_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None


def verify_token(token: str) -> AuthContext:
    """Verify JWT token and return user context.
    
    Args:
        token: JWT token string
        
    Returns:
        AuthContext with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    # Get JWT secret from settings (must be set in production)
    jwt_secret = settings.jwt_secret
    if not jwt_secret:
        if settings.environment == "production":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="JWT_SECRET not configured"
            )
        # Fallback for development
        jwt_secret = "dev-jwt-secret-key-not-for-production"
        logger.warning("Using development JWT secret - not for production!")
    
    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        
        uid = payload.get("sub")
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject"
            )
        
        return AuthContext(
            uid=uid,
            role=payload.get("role", "customer"),
            salon_id=payload.get("salon_id"),
            email=payload.get("email"),
            phone=payload.get("phone"),
            name=payload.get("name"),
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> AuthContext:
    """Dependency to get current authenticated user.
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        AuthContext with user information
        
    Raises:
        HTTPException: If not authenticated
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return verify_token(credentials.credentials)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[AuthContext]:
    """Dependency to optionally get current user (no error if not authenticated).
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        AuthContext if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return verify_token(credentials.credentials)
    except HTTPException:
        return None


__all__ = ["AuthContext", "get_current_user", "get_current_user_optional", "verify_token"]
