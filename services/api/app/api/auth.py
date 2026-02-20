"""Authentication API endpoints.

This module provides authentication endpoints for the Salon Flow API including:
- User registration (owner, staff, customer)
- Login with email/phone and password
- Phone OTP authentication
- Token refresh and logout
- Firebase token authentication
- Password management
"""

# Standard library imports
from datetime import datetime, timedelta
from typing import Optional

# Third-party imports
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

# Local imports
from app.core.auth import (
    RateLimitType,
    apply_rate_limit,
    AuthError,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
    verify_firebase_token,
)
from app.core.config import settings
from app.schemas import StaffRole
from app.services.auth_service import AuthService, get_auth_service
from app.api.dependencies import get_current_user, AuthContext

logger = structlog.get_logger()
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


# ============================================================================
# Request/Response Models
# ============================================================================

class RegisterRequest(BaseModel):
    """User registration request model.
    
    Attributes:
        email: User's email address (optional for phone-only registration)
        phone: User's phone number in E.164 format
        password: User's password (minimum 6 characters)
        display_name: User's display name
        role: User's role in the salon system
        salon_id: Salon ID for staff/customer registration
    """
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    password: str = Field(..., min_length=6)
    display_name: Optional[str] = None
    role: StaffRole = StaffRole.CUSTOMER
    salon_id: Optional[str] = None


class LoginRequest(BaseModel):
    """User login request model.
    
    Attributes:
        email: User's email address for email-based login
        phone: User's phone number for phone-based login
        password: User's password
    """
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str


class PhoneOTPRequest(BaseModel):
    """Phone OTP login request model.
    
    Attributes:
        phone: Phone number to send OTP to in E.164 format
    """
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')


class VerifyOTPRequest(BaseModel):
    """Verify OTP request model.
    
    Attributes:
        phone: Phone number that received the OTP
        otp: One-time password (4-6 digits)
    """
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    otp: str = Field(..., min_length=4, max_length=6)


class RefreshTokenRequest(BaseModel):
    """Refresh token request model.
    
    Attributes:
        refresh_token: Valid refresh token to exchange for new access token
    """
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Change password request model.
    
    Attributes:
        current_password: User's current password for verification
        new_password: New password (minimum 6 characters)
    """
    current_password: str
    new_password: str = Field(..., min_length=6)


class AuthResponse(BaseModel):
    """Authentication response model.
    
    Attributes:
        success: Whether authentication was successful
        message: Human-readable status message
        access_token: JWT access token for API authentication
        refresh_token: JWT refresh token for token renewal
        token_type: Token type (always 'bearer')
        user: User profile information
        role: User's role in the salon
        salon_id: Salon ID the user belongs to
    """
    success: bool = True
    message: str = "Authentication successful"
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[dict] = None
    role: Optional[str] = None
    salon_id: Optional[str] = None


class UserProfileResponse(BaseModel):
    """User profile response model.
    
    Attributes:
        uid: Unique user identifier
        email: User's email address
        phone: User's phone number
        display_name: User's display name
        role: User's role in the salon
        salon_id: Salon ID the user belongs to
        created_at: Account creation timestamp
        last_login: Last login timestamp
    """
    uid: str
    email: Optional[str] = None
    phone: Optional[str] = None
    display_name: Optional[str] = None
    role: Optional[str] = None
    salon_id: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class LogoutResponse(BaseModel):
    """Logout response model.
    
    Attributes:
        success: Whether logout was successful
        message: Human-readable status message
    """
    success: bool
    message: str


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Register a new user.
    
    Creates a new user account based on the specified role:
    - OWNER: Creates a new salon and owner account
    - MANAGER/RECEPTIONIST/STYLIST: Creates staff account for existing salon
    - CUSTOMER: Creates customer account for existing salon
    
    Args:
        request: Registration details including email/phone, password, and role
        auth_service: Injected authentication service
        
    Returns:
        AuthResponse with access tokens and user information
        
    Raises:
        HTTPException: 400 if registration fails due to invalid data or conflicts
    """
    try:
        result = await auth_service.register_user(
            email=request.email,
            phone=request.phone,
            password=request.password,
            display_name=request.display_name,
            role=request.role,
            salon_id=request.salon_id
        )
        
        return AuthResponse(
            success=True,
            message="User registered successfully",
            access_token=result.get("access_token"),
            refresh_token=result.get("refresh_token"),
            user=result.get("user"),
            role=request.role.value,
            salon_id=request.salon_id
        )
    except AuthError as e:
        logger.error("Registration failed", error=e.message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code}
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Login with email/phone and password.
    
    Authenticates a user using either email or phone number along with password.
    Returns JWT tokens for subsequent API calls.
    
    Args:
        request: Login credentials (email or phone + password)
        auth_service: Injected authentication service
        
    Returns:
        AuthResponse with access tokens and user information
        
    Raises:
        HTTPException: 400 if credentials are missing, 401 if invalid
    """
    try:
        if not request.email and not request.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Email or phone required", "code": "missing_credentials"}
            )
        
        result = await auth_service.login(
            email=request.email,
            phone=request.phone,
            password=request.password
        )
        
        return AuthResponse(
            success=True,
            message="Login successful",
            access_token=result.get("access_token"),
            refresh_token=result.get("refresh_token"),
            user=result.get("user"),
            role=result.get("role"),
            salon_id=result.get("salon_id")
        )
    except AuthError as e:
        logger.error("Login failed", error=e.message)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": e.message, "code": e.code}
        )


@router.post("/phone-otp", response_model=AuthResponse)
async def send_phone_otp(
    request: PhoneOTPRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Send OTP to phone number.
    
    Generates and sends a one-time password to the specified phone number.
    The OTP is valid for 5 minutes.
    
    Args:
        request: Phone number to send OTP to
        auth_service: Injected authentication service
        
    Returns:
        AuthResponse confirming OTP was sent
        
    Raises:
        HTTPException: 400 if OTP generation/sending fails
    """
    try:
        result = await auth_service.send_phone_otp(phone=request.phone)
        
        return AuthResponse(
            success=True,
            message="OTP sent successfully",
            salon_id=result.get("salon_id")
        )
    except AuthError as e:
        logger.error("OTP send failed", error=e.message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code}
        )


@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(
    request: VerifyOTPRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Verify OTP and login.
    
    Validates the OTP sent to the phone number and authenticates the user.
    Returns JWT tokens upon successful verification.
    
    Args:
        request: Phone number and OTP code
        auth_service: Injected authentication service
        
    Returns:
        AuthResponse with access tokens and user information
        
    Raises:
        HTTPException: 401 if OTP is invalid or expired
    """
    try:
        result = await auth_service.verify_phone_otp(
            phone=request.phone,
            otp=request.otp
        )
        
        return AuthResponse(
            success=True,
            message="OTP verified successfully",
            access_token=result.get("access_token"),
            refresh_token=result.get("refresh_token"),
            user=result.get("user"),
            role=result.get("role"),
            salon_id=result.get("salon_id")
        )
    except AuthError as e:
        logger.error("OTP verification failed", error=e.message)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": e.message, "code": e.code}
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Refresh access token.
    
    Exchanges a valid refresh token for a new access token and refresh token.
    
    Args:
        request: Valid refresh token
        auth_service: Injected authentication service
        
    Returns:
        AuthResponse with new access and refresh tokens
        
    Raises:
        HTTPException: 401 if refresh token is invalid or expired
    """
    try:
        result = await auth_service.refresh_access_token(
            refresh_token=request.refresh_token
        )
        
        return AuthResponse(
            success=True,
            message="Token refreshed successfully",
            access_token=result.get("access_token"),
            refresh_token=result.get("refresh_token")
        )
    except AuthError as e:
        logger.error("Token refresh failed", error=e.message)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": e.message, "code": e.code}
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> LogoutResponse:
    """Logout user and invalidate token.
    
    Invalidates the current access token, preventing further API access.
    
    Args:
        credentials: Bearer token from Authorization header
        auth_service: Injected authentication service
        
    Returns:
        LogoutResponse confirming successful logout
        
    Raises:
        HTTPException: 400 if logout fails
    """
    try:
        if credentials:
            await auth_service.logout(token=credentials.credentials)
        
        return LogoutResponse(success=True, message="Logged out successfully")
    except AuthError as e:
        logger.error("Logout failed", error=e.message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code}
        )


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: AuthContext = Depends(get_current_user)
) -> UserProfileResponse:
    """Get current user profile.
    
    Retrieves the authenticated user's profile information.
    
    Args:
        current_user: Authenticated user context from JWT token
        
    Returns:
        UserProfileResponse with user details
        
    Raises:
        HTTPException: 401 if not authenticated
    """
    return UserProfileResponse(
        uid=current_user.uid,
        email=current_user.email,
        phone=current_user.phone,
        display_name=current_user.name,
        role=current_user.role.value if current_user.role else None,
        salon_id=current_user.salon_id,
        created_at=None,  # Would need to fetch from user service
        last_login=None   # Would need to fetch from user service
    )


@router.put("/password", response_model=LogoutResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: AuthContext = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> LogoutResponse:
    """Change user password.
    
    Updates the authenticated user's password after verifying the current password.
    
    Args:
        request: Current and new password
        current_user: Authenticated user context
        auth_service: Injected authentication service
        
    Returns:
        LogoutResponse confirming password change
        
    Raises:
        HTTPException: 400 if current password is incorrect or update fails
    """
    try:
        await auth_service.change_password(
            uid=current_user.uid,
            current_password=request.current_password,
            new_password=request.new_password
        )
        
        return LogoutResponse(success=True, message="Password changed successfully")
    except AuthError as e:
        logger.error("Password change failed", error=e.message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code}
        )


@router.post("/firebase-token", response_model=AuthResponse)
async def login_with_firebase(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Login using Firebase ID token.
    
    Authenticates a user using a Firebase ID token, typically from a mobile app
    or web client that has already authenticated with Firebase.
    
    Args:
        credentials: Firebase ID token in Bearer header
        auth_service: Injected authentication service
        
    Returns:
        AuthResponse with access tokens and user information
        
    Raises:
        HTTPException: 401 if Firebase token is invalid or user not found
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "No token provided", "code": "no_token"}
        )
    
    try:
        # Verify Firebase ID token
        decoded = verify_firebase_token(credentials.credentials)
        
        # Get or create user in our system
        result = await auth_service.login_with_firebase(
            uid=decoded.get("uid"),
            email=decoded.get("email"),
            phone=decoded.get("phone")
        )
        
        return AuthResponse(
            success=True,
            message="Firebase login successful",
            access_token=result.get("access_token"),
            refresh_token=result.get("refresh_token"),
            user=result.get("user"),
            role=result.get("role"),
            salon_id=result.get("salon_id")
        )
    except AuthError as e:
        logger.error("Firebase login failed", error=e.message)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": e.message, "code": e.code}
        )


__all__ = [
    "router",
    "RegisterRequest",
    "LoginRequest",
    "PhoneOTPRequest",
    "VerifyOTPRequest",
    "RefreshTokenRequest",
    "ChangePasswordRequest",
    "AuthResponse",
    "UserProfileResponse",
    "LogoutResponse",
]
