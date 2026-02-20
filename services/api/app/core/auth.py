"""Core authentication utilities for Salon Flow API.

This module provides core authentication functions:
- Password hashing and verification
- JWT token creation and validation
- Firebase token verification
- Rate limiting for authentication endpoints
- Role-based access control
"""

# Standard library imports
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
import json

# Third-party imports
import bcrypt
import jwt
import structlog
from fastapi import HTTPException, status

# Local imports
from app.core.config import settings

logger = structlog.get_logger()


# ============================================================================
# Constants
# ============================================================================

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ============================================================================
# Enums
# ============================================================================

class RateLimitType(str, Enum):
    """Rate limit types for authentication endpoints."""
    LOGIN = "login"
    OTP = "otp"
    PASSWORD_RESET = "password_reset"


class Permission(str, Enum):
    """Permission constants for role-based access control."""
    
    # Salon permissions
    SALON_READ = "salon:read"
    SALON_WRITE = "salon:write"
    SALON_DELETE = "salon:delete"
    SALON_EDIT = "salon:edit"
    
    # Staff permissions
    STAFF_READ = "staff:read"
    STAFF_WRITE = "staff:write"
    STAFF_DELETE = "staff:delete"
    STAFF_CREATE = "staff:create"
    STAFF_EDIT = "staff:edit"
    STAFF_VIEW = "staff:view"
    
    # Customer permissions
    CUSTOMER_READ = "customer:read"
    CUSTOMER_WRITE = "customer:write"
    CUSTOMER_DELETE = "customer:delete"
    CUSTOMER_CREATE = "customer:create"
    CUSTOMER_EDIT = "customer:edit"
    
    # Booking permissions
    BOOKING_READ = "booking:read"
    BOOKING_WRITE = "booking:write"
    BOOKING_DELETE = "booking:delete"
    BOOKING_CREATE = "booking:create"
    BOOKING_EDIT = "booking:edit"
    BOOKING_VIEW = "booking:view"
    
    # Service permissions
    SERVICE_READ = "service:read"
    SERVICE_WRITE = "service:write"
    SERVICE_DELETE = "service:delete"
    SERVICE_CREATE = "service:create"
    SERVICE_EDIT = "service:edit"
    
    # Report permissions
    REPORT_READ = "report:read"
    REPORT_WRITE = "report:write"
    REPORTS_VIEW = "reports:view"
    
    # Settings permissions
    SETTINGS_READ = "settings:read"
    SETTINGS_WRITE = "settings:write"
    
    # Payment permissions
    PAYMENT_PROCESS = "payment:process"


# ============================================================================
# Exception Classes
# ============================================================================

class AuthError(Exception):
    """Authentication error exception."""
    
    def __init__(self, message: str, code: str = "auth_error") -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)


# ============================================================================
# Role-Based Access Control
# ============================================================================

ROLE_PERMISSIONS = {
    "owner": [
        "salon:read", "salon:write", "salon:delete", "salon:edit",
        "staff:read", "staff:write", "staff:delete", "staff:create", "staff:edit",
        "customer:read", "customer:write", "customer:delete", "customer:create", "customer:edit",
        "booking:read", "booking:write", "booking:delete", "booking:create", "booking:edit", "booking:view",
        "service:read", "service:write", "service:delete", "service:create", "service:edit",
        "report:read", "report:write", "reports:view",
        "settings:read", "settings:write",
        "payment:process",
    ],
    "manager": [
        "salon:read", "salon:edit",
        "staff:read", "staff:write", "staff:create", "staff:edit",
        "customer:read", "customer:write", "customer:delete", "customer:create", "customer:edit",
        "booking:read", "booking:write", "booking:delete", "booking:create", "booking:edit", "booking:view",
        "service:read", "service:write", "service:create", "service:edit",
        "report:read", "reports:view",
        "settings:read", "settings:write",
        "payment:process",
    ],
    "receptionist": [
        "salon:read",
        "staff:read",
        "customer:read", "customer:write", "customer:create", "customer:edit",
        "booking:read", "booking:write", "booking:create", "booking:edit", "booking:view",
        "service:read",
        "payment:process",
    ],
    "stylist": [
        "salon:read",
        "customer:read",
        "booking:read", "booking:edit", "booking:view",
        "service:read",
    ],
    "customer": [
        "booking:read", "booking:create", "booking:view",
        "customer:read", "customer:edit",
    ],
}


def get_permissions_for_role(role) -> List[str]:
    """Get all permissions for a given role."""
    role_value = role.value if hasattr(role, 'value') else str(role)
    role_key = role_value.lower()
    return ROLE_PERMISSIONS.get(role_key, [])


def get_role_permissions(role) -> List[str]:
    """Alias for get_permissions_for_role."""
    return get_permissions_for_role(role)


def has_permission(role, permission: str) -> bool:
    """Check if a role has a specific permission."""
    permissions = get_permissions_for_role(role)
    perm_value = permission.value if hasattr(permission, 'value') else str(permission)
    return perm_value in permissions


def has_any_permission(role, permissions: List[str]) -> bool:
    """Check if a role has any of the specified permissions."""
    role_permissions = get_permissions_for_role(role)
    for perm in permissions:
        perm_value = perm.value if hasattr(perm, 'value') else str(perm)
        if perm_value in role_permissions:
            return True
    return False


def has_all_permissions(role, permissions: List[str]) -> bool:
    """Check if a role has all of the specified permissions."""
    role_permissions = get_permissions_for_role(role)
    for perm in permissions:
        perm_value = perm.value if hasattr(perm, 'value') else str(perm)
        if perm_value not in role_permissions:
            return False
    return True


# ============================================================================
# Password Functions
# ============================================================================

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


hash_password = get_password_hash  # Alias


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


# ============================================================================
# Token Functions
# ============================================================================

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired", "token_expired")
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token", "invalid_token")


def create_token_pair(
    user_id: str,
    role: Optional[str] = None,
    salon_id: Optional[str] = None
) -> Dict[str, str]:
    """Create both access and refresh tokens."""
    access_token = create_access_token(
        data={"sub": user_id, "role": role, "salon_id": salon_id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user_id}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


# ============================================================================
# Firebase Token Verification
# ============================================================================

def verify_firebase_token(token: str) -> Dict[str, Any]:
    """Verify a Firebase ID token."""
    try:
        import firebase_admin.auth as firebase_auth
        
        decoded_token = firebase_auth.verify_id_token(token)
        
        return {
            "uid": decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "phone": decoded_token.get("phone_number"),
            "email_verified": decoded_token.get("email_verified", False),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture"),
        }
    except firebase_admin.auth.ExpiredIdTokenError:
        raise AuthError("Firebase token has expired", "firebase_token_expired")
    except firebase_admin.auth.InvalidIdTokenError:
        raise AuthError("Invalid Firebase token", "invalid_firebase_token")
    except Exception as e:
        logger.error("Firebase token verification failed", error=str(e))
        raise AuthError("Firebase authentication failed", "firebase_auth_failed")


# ============================================================================
# Rate Limiting
# ============================================================================

async def check_rate_limit(
    redis_client,
    limit_type: RateLimitType,
    identifier: str,
    max_attempts: int = 5,
    window_seconds: int = 900
) -> Dict[str, Any]:
    """Check if rate limit has been exceeded."""
    key = f"rate_limit:{limit_type.value}:{identifier}"
    
    try:
        current = await redis_client.get(key)
        current_count = int(current) if current else 0
        
        if current_count >= max_attempts:
            ttl = await redis_client.ttl(key)
            return {"allowed": False, "retry_after": ttl}
        
        return {"allowed": True, "remaining": max_attempts - current_count}
    except Exception as e:
        logger.warning("Rate limit check failed", error=str(e))
        return {"allowed": True, "remaining": max_attempts}


async def increment_rate_limit(
    redis_client,
    limit_type: RateLimitType,
    identifier: str,
    window_seconds: int = 900
) -> None:
    """Increment rate limit counter."""
    key = f"rate_limit:{limit_type.value}:{identifier}"
    
    try:
        exists = await redis_client.exists(key)
        
        if exists:
            await redis_client.client.incr(key)
        else:
            await redis_client.set(key, "1", ex=window_seconds)
    except Exception as e:
        logger.warning("Rate limit increment failed", error=str(e))


async def apply_rate_limit(
    identifier: str,
    limit_type: RateLimitType,
    max_attempts: int = 5,
    window_minutes: int = 15
) -> bool:
    """Apply rate limiting for authentication attempts."""
    from app.core.redis import get_redis_client
    
    try:
        redis = await get_redis_client()
        key = f"rate_limit:{limit_type.value}:{identifier}"
        
        current = await redis.get(key)
        current_count = int(current) if current else 0
        
        if current_count >= max_attempts:
            ttl = await redis.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": f"Too many {limit_type.value} attempts.",
                    "code": "rate_limit_exceeded",
                    "retry_after": ttl
                }
            )
        
        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_minutes * 60)
        await pipe.execute()
        
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Rate limiting unavailable", error=str(e))
        return True


# ============================================================================
# Session Manager
# ============================================================================

class SessionManager:
    """Manages user sessions with JWT tokens."""
    
    def __init__(self, redis_client=None) -> None:
        """Initialize the session manager."""
        self._redis = redis_client
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    async def create_session(
        self,
        user_id: str,
        salon_id: Optional[str] = None,
        role: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new session for a user."""
        session_id = str(uuid.uuid4())
        session_data = {
            "user_id": user_id,
            "salon_id": salon_id,
            "role": role,
            "device_info": device_info,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        if self._redis:
            await self._redis.set(
                f"session:{session_id}",
                json.dumps(session_data),
                ex=86400
            )
        else:
            self._sessions[session_id] = session_data
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID."""
        if self._redis:
            data = await self._redis.get(f"session:{session_id}")
            if data:
                if isinstance(data, dict):
                    return data
                return json.loads(data)
            return None
        return self._sessions.get(session_id)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID."""
        if self._redis:
            result = await self._redis.delete(f"session:{session_id}")
            return bool(result)
        
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    async def extend_session(self, session_id: str, ttl: int = 3600) -> bool:
        """Extend session TTL."""
        if self._redis:
            exists = await self._redis.exists(f"session:{session_id}")
            if exists:
                await self._redis.client.expire(f"session:{session_id}", ttl)
                return True
            return False
        
        return session_id in self._sessions
    
    async def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a session token."""
        try:
            payload = decode_token(token)
            return payload
        except AuthError:
            return None
    
    async def revoke_session(self, session_id: str) -> bool:
        """Revoke a session."""
        return await self.delete_session(session_id)
    
    async def get_active_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active sessions for a user."""
        return [
            {"session_id": sid, **data}
            for sid, data in self._sessions.items()
            if data.get("user_id") == user_id
        ]


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Constants
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "REFRESH_TOKEN_EXPIRE_DAYS",
    # Enums
    "RateLimitType",
    "Permission",
    # Exceptions
    "AuthError",
    # RBAC
    "ROLE_PERMISSIONS",
    "get_permissions_for_role",
    "get_role_permissions",
    "has_permission",
    "has_any_permission",
    "has_all_permissions",
    # Password functions
    "get_password_hash",
    "hash_password",
    "verify_password",
    # Token functions
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "create_token_pair",
    # Firebase functions
    "verify_firebase_token",
    # Rate limiting
    "check_rate_limit",
    "increment_rate_limit",
    "apply_rate_limit",
    # Session management
    "SessionManager",
]
