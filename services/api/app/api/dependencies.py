"""API dependencies for Salon Flow API.

This module provides FastAPI dependencies for:
- Authentication context extraction and validation
- Role-based access control
- Permission-based access control
- Resource verification helpers
"""

# Standard library imports
from typing import List, Optional

# Third-party imports
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Local imports
from app.core.auth import (
    AuthError,
    decode_token,
    get_permissions_for_role,
    has_permission as check_has_permission,
)
from app.schemas import StaffRole

logger = structlog.get_logger()
security = HTTPBearer(auto_error=False)


# ============================================================================
# Auth Context Class
# ============================================================================

class AuthContext:
    """Authentication context containing user and tenant information.
    
    This class encapsulates all authentication and authorization data
    for the current request, including user identity, role, permissions,
    and salon association.
    
    Attributes:
        uid: Unique user identifier
        email: User's email address
        phone: User's phone number
        salon_id: Salon ID the user belongs to
        role: User's role in the salon
        staff_id: Staff ID if user is a staff member
        customer_id: Customer ID if user is a customer
        permissions: List of permissions granted to the user
        name: User's display name
        is_owner: Whether the user is the salon owner
    """
    
    def __init__(
        self,
        uid: str,
        email: Optional[str],
        phone: Optional[str],
        salon_id: str,
        role: StaffRole,
        staff_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        name: Optional[str] = None,
        is_owner: bool = False,
    ) -> None:
        """Initialize AuthContext with user data.
        
        Args:
            uid: Unique user identifier
            email: User's email address
            phone: User's phone number
            salon_id: Salon ID the user belongs to
            role: User's role in the salon
            staff_id: Staff ID if user is a staff member
            customer_id: Customer ID if user is a customer
            permissions: List of permissions granted to the user
            name: User's display name
            is_owner: Whether the user is the salon owner
        """
        self.uid = uid
        self.email = email
        self.phone = phone
        self.salon_id = salon_id
        self.role = role
        self.staff_id = staff_id
        self.customer_id = customer_id
        self.permissions = permissions or []
        self.name = name
        self.is_owner = is_owner
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission.
        
        Args:
            permission: Permission string to check (e.g., 'booking:create')
            
        Returns:
            True if user has the permission, False otherwise
        """
        return check_has_permission(self.role, permission)
    
    def has_role(self, roles: List[StaffRole]) -> bool:
        """Check if user has one of the specified roles.
        
        Args:
            roles: List of roles to check against
            
        Returns:
            True if user's role is in the list, False otherwise
        """
        return self.role in roles
    
    def get_permissions(self) -> List[str]:
        """Get all permissions for this user.
        
        Returns:
            List of permission strings
        """
        return self.permissions
    
    def is_staff(self) -> bool:
        """Check if user is a staff member.
        
        Returns:
            True if user has a staff role, False otherwise
        """
        return self.role in [
            StaffRole.OWNER,
            StaffRole.MANAGER,
            StaffRole.RECEPTIONIST,
            StaffRole.STYLIST
        ]
    
    def is_customer(self) -> bool:
        """Check if user is a customer.
        
        Returns:
            True if user is a customer, False otherwise
        """
        return self.role == StaffRole.CUSTOMER
    
    def to_dict(self) -> dict:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of the context
        """
        return {
            "uid": self.uid,
            "email": self.email,
            "phone": self.phone,
            "salon_id": self.salon_id,
            "role": self.role,
            "staff_id": self.staff_id,
            "customer_id": self.customer_id,
            "permissions": self.permissions,
            "name": self.name,
            "is_owner": self.is_owner,
        }
    
    def __repr__(self) -> str:
        """String representation of AuthContext."""
        return f"AuthContext(uid={self.uid}, role={self.role.value if hasattr(self.role, 'value') else self.role}, salon_id={self.salon_id})"


# ============================================================================
# Authentication Dependencies
# ============================================================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> AuthContext:
    """Extract and validate JWT token from request.
    
    This dependency extracts the Bearer token from the Authorization header,
    validates it, and returns an AuthContext with the user's information.
    
    Args:
        credentials: HTTP Bearer credentials from the request
        
    Returns:
        AuthContext object with user information
        
    Raises:
        HTTPException: 401 if not authenticated or token is invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Not authenticated", "code": "not_authenticated"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        
        # Validate token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"message": "Invalid token type", "code": "invalid_token_type"},
            )
        
        uid = payload.get("sub")
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"message": "Invalid token payload", "code": "invalid_payload"},
            )
        
        # Extract user info from token
        role_str = payload.get("role")
        role = StaffRole(role_str) if role_str else None
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"message": "Invalid role in token", "code": "invalid_role"},
            )
        
        return AuthContext(
            uid=uid,
            email=payload.get("email"),
            phone=payload.get("phone"),
            salon_id=payload.get("salon_id", ""),
            role=role,
            staff_id=payload.get("staff_id"),
            customer_id=payload.get("customer_id"),
            permissions=get_permissions_for_role(role) if role else [],
            name=payload.get("name"),
            is_owner=(role == StaffRole.OWNER),
        )
        
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": e.message, "code": e.code},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Authentication failed", "code": "auth_failed"},
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_salon(
    current_user: AuthContext = Depends(get_current_user)
) -> str:
    """Get current salon ID from user context.
    
    Args:
        current_user: Authenticated user context
        
    Returns:
        Salon ID string
        
    Raises:
        HTTPException: 403 if user is not associated with any salon
    """
    salon_id = current_user.salon_id
    if not salon_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "User not associated with any salon", "code": "no_salon"},
        )
    return salon_id


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[AuthContext]:
    """Get current user if authenticated, otherwise return None.
    
    Useful for endpoints that work for both authenticated and anonymous users.
    
    Args:
        credentials: HTTP Bearer credentials from the request
        
    Returns:
        AuthContext if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# ============================================================================
# Role-Based Access Control Dependencies
# ============================================================================

def require_role(roles: List[StaffRole]):
    """Dependency that requires specific roles.
    
    Creates a dependency that validates the user has one of the specified roles.
    
    Args:
        roles: List of roles that are allowed access
        
    Returns:
        Dependency function that validates role
        
    Example:
        @router.get("/protected")
        async def protected_route(
            user: AuthContext = Depends(require_role([StaffRole.OWNER, StaffRole.MANAGER]))
        ):
            ...
    """
    async def role_checker(
        current_user: AuthContext = Depends(get_current_user)
    ) -> AuthContext:
        if not current_user.role or current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": f"Role {current_user.role} not authorized. Required: {[r.value for r in roles]}",
                    "code": "insufficient_role"
                },
            )
        return current_user
    
    return role_checker


# Convenience dependencies for common roles
require_owner = require_role([StaffRole.OWNER])
require_manager = require_role([StaffRole.OWNER, StaffRole.MANAGER])
require_receptionist = require_role([StaffRole.OWNER, StaffRole.MANAGER, StaffRole.RECEPTIONIST])
require_staff = require_role([StaffRole.OWNER, StaffRole.MANAGER, StaffRole.RECEPTIONIST, StaffRole.STYLIST])
require_customer = require_role([StaffRole.CUSTOMER])


# ============================================================================
# Permission-Based Access Control Dependencies
# ============================================================================

def require_permission(permission: str):
    """Dependency that requires a specific permission.
    
    Creates a dependency that validates the user has the specified permission.
    
    Args:
        permission: Permission string required (e.g., 'report:read')
        
    Returns:
        Dependency function that validates permission
        
    Example:
        @router.get("/reports")
        async def reports(
            user: AuthContext = Depends(require_permission("report:read"))
        ):
            ...
    """
    async def permission_checker(
        current_user: AuthContext = Depends(get_current_user)
    ) -> AuthContext:
        if not current_user.role or not check_has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": f"Permission '{permission}' not granted",
                    "code": "insufficient_permission"
                },
            )
        return current_user
    
    return permission_checker


# ============================================================================
# Resource Verification Helpers
# ============================================================================

async def verify_customer_access(
    customer_id: str,
    salon_id: str
) -> dict:
    """Verify customer exists and belongs to the specified salon.
    
    This helper extracts the duplicated customer verification logic used
    across multiple endpoints in the customers module.
    
    Args:
        customer_id: Customer ID to verify
        salon_id: Expected salon ID
        
    Returns:
        Customer data dictionary if verification passes
        
    Raises:
        HTTPException: 404 if customer not found, 403 if access denied
    """
    from app.models import CustomerModel
    
    customer_model = CustomerModel()
    customer = await customer_model.get(customer_id)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Customer not found", "code": "customer_not_found"},
        )
    
    if customer.salon_id != salon_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Access denied", "code": "access_denied"},
        )
    
    return customer


async def verify_booking_access(
    booking_id: str,
    salon_id: str
) -> dict:
    """Verify booking exists and belongs to the specified salon.
    
    This helper extracts the duplicated booking verification logic used
    across multiple endpoints in the bookings module.
    
    Args:
        booking_id: Booking ID to verify
        salon_id: Expected salon ID
        
    Returns:
        Booking data dictionary if verification passes
        
    Raises:
        HTTPException: 404 if booking not found, 403 if access denied
    """
    from app.models import BookingModel
    
    booking_model = BookingModel()
    booking = await booking_model.get(booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Booking not found", "code": "booking_not_found"},
        )
    
    if booking.salon_id != salon_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Access denied", "code": "access_denied"},
        )
    
    return booking


# ============================================================================
# Backward Compatibility Aliases
# ============================================================================

get_salon_id = get_current_salon


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Auth context
    "AuthContext",
    # Authentication dependencies
    "get_current_user",
    "get_current_salon",
    "get_optional_user",
    "get_salon_id",
    # Role-based dependencies
    "require_role",
    "require_owner",
    "require_manager",
    "require_receptionist",
    "require_staff",
    "require_customer",
    # Permission-based dependencies
    "require_permission",
    # Verification helpers
    "verify_customer_access",
    "verify_booking_access",
]


# ============================================================================
# String-based Role Check (for convenience)
# ============================================================================

def require_roles(role_names: List[str]):
    """Dependency that requires specific roles by string name.
    
    Convenience wrapper around require_role that accepts string role names
    instead of StaffRole enums.
    
    Args:
        role_names: List of role name strings (e.g., ['owner', 'manager'])
        
    Returns:
        Dependency function that validates role
        
    Example:
        @router.get("/protected")
        async def protected_route(
            user: AuthContext = Depends(require_roles(['owner', 'manager']))
        ):
            ...
    """
    # Convert string names to StaffRole enums
    roles = []
    for name in role_names:
        try:
            role = StaffRole(name.lower())
            roles.append(role)
        except ValueError:
            # Invalid role name, will be caught during validation
            pass
    
    return require_role(roles)


# Update exports
__all__.append('require_roles')
