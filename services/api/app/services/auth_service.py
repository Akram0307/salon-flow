"""Authentication service for Salon Flow API.

This module provides business logic for authentication operations:
- User registration and login
- Token management (access and refresh)
- Phone OTP authentication
- Password management
- Firebase authentication integration
"""

# Standard library imports
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# Third-party imports
import structlog
from fastapi import Depends, HTTPException, status
from google.cloud.firestore import AsyncClient

# Local imports
from app.core.auth import (
    AuthError,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.core.config import settings
from app.core.firebase import get_firestore_async
from app.schemas import StaffRole

logger = structlog.get_logger()


class AuthService:
    """Service for handling authentication operations.
    
    This service provides methods for user authentication, registration,
    token management, and password operations.
    
    Attributes:
        db: Firestore async client for database operations
    """
    
    def __init__(self, db: AsyncClient) -> None:
        """Initialize the auth service.
        
        Args:
            db: Firestore async client instance
        """
        self.db = db
    
    async def register_user(
        self,
        email: Optional[str],
        phone: Optional[str],
        password: str,
        display_name: Optional[str],
        role: StaffRole,
        salon_id: Optional[str]
    ) -> Dict[str, Any]:
        """Register a new user.
        
        Creates a new user account with the provided credentials and role.
        
        Args:
            email: User's email address (optional for phone-only registration)
            phone: User's phone number in E.164 format
            password: User's password (will be hashed)
            display_name: User's display name
            role: User's role in the salon system
            salon_id: Salon ID for staff/customer registration
            
        Returns:
            Dictionary containing access_token, refresh_token, and user data
            
        Raises:
            AuthError: If registration fails due to validation or conflicts
        """
        # Validate that at least one identifier is provided
        if not email and not phone:
            raise AuthError("Email or phone required", "missing_identifier")
        
        # Check for existing user
        users_ref = self.db.collection("users")
        
        if email:
            existing = await users_ref.where("email", "==", email).limit(1).get()
            if existing:
                raise AuthError("Email already registered", "email_exists")
        
        if phone:
            existing = await users_ref.where("phone", "==", phone).limit(1).get()
            if existing:
                raise AuthError("Phone already registered", "phone_exists")
        
        # Create user document
        user_id = users_ref.document().id
        hashed_password = get_password_hash(password)
        
        user_data = {
            "uid": user_id,
            "email": email,
            "phone": phone,
            "display_name": display_name,
            "password_hash": hashed_password,
            "role": role.value,
            "salon_id": salon_id,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        await users_ref.document(user_id).set(user_data)
        
        # Generate tokens
        access_token = create_access_token(
            data={"sub": user_id, "role": role.value, "salon_id": salon_id}
        )
        refresh_token = create_refresh_token(data={"sub": user_id})
        
        # Store refresh token
        await self._store_refresh_token(user_id, refresh_token)
        
        logger.info(
            "User registered",
            user_id=user_id,
            email=email,
            phone=phone,
            role=role.value,
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "uid": user_id,
                "email": email,
                "phone": phone,
                "display_name": display_name,
                "role": role.value,
            },
        }
    
    async def login(
        self,
        email: Optional[str],
        phone: Optional[str],
        password: str
    ) -> Dict[str, Any]:
        """Authenticate user with email/phone and password.
        
        Args:
            email: User's email address
            phone: User's phone number
            password: User's password
            
        Returns:
            Dictionary containing access_token, refresh_token, user data, role, and salon_id
            
        Raises:
            AuthError: If credentials are invalid
        """
        # Find user by email or phone
        users_ref = self.db.collection("users")
        
        if email:
            query = users_ref.where("email", "==", email).limit(1)
        elif phone:
            query = users_ref.where("phone", "==", phone).limit(1)
        else:
            raise AuthError("Email or phone required", "missing_identifier")
        
        snapshot = await query.get()
        
        if not snapshot:
            raise AuthError("Invalid credentials", "invalid_credentials")
        
        user_doc = snapshot[0]
        user_data = user_doc.to_dict()
        
        # Verify password
        if not verify_password(password, user_data.get("password_hash", "")):
            raise AuthError("Invalid credentials", "invalid_credentials")
        
        # Check if user is active
        if not user_data.get("is_active", True):
            raise AuthError("Account is disabled", "account_disabled")
        
        # Generate tokens
        user_id = user_data["uid"]
        role = user_data.get("role", "customer")
        salon_id = user_data.get("salon_id")
        
        access_token = create_access_token(
            data={"sub": user_id, "role": role, "salon_id": salon_id}
        )
        refresh_token = create_refresh_token(data={"sub": user_id})
        
        # Store refresh token
        await self._store_refresh_token(user_id, refresh_token)
        
        # Update last login
        await users_ref.document(user_id).update({
            "last_login": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })
        
        logger.info(
            "User logged in",
            user_id=user_id,
            email=email,
            phone=phone,
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "uid": user_id,
                "email": user_data.get("email"),
                "phone": user_data.get("phone"),
                "display_name": user_data.get("display_name"),
                "role": role,
            },
            "role": role,
            "salon_id": salon_id,
        }
    
    async def send_phone_otp(self, phone: str) -> Dict[str, Any]:
        """Send OTP to phone number.
        
        Generates and stores a one-time password for phone verification.
        In production, this would integrate with an SMS provider.
        
        Args:
            phone: Phone number in E.164 format
            
        Returns:
            Dictionary with success status
            
        Raises:
            AuthError: If OTP generation fails
        """
        # Generate 6-digit OTP
        import random
        otp = str(random.randint(100000, 999999))
        
        # Store OTP with expiry (5 minutes)
        otp_ref = self.db.collection("otps").document(phone)
        await otp_ref.set({
            "otp": otp,
            "phone": phone,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=5),
            "attempts": 0,
        })
        
        # In production, send via SMS provider (Twilio, etc.)
        logger.info("OTP generated", phone=phone, otp=otp)  # Remove OTP in production
        
        return {"success": True, "message": "OTP sent"}
    
    async def verify_phone_otp(
        self,
        phone: str,
        otp: str
    ) -> Dict[str, Any]:
        """Verify OTP and authenticate user.
        
        Validates the OTP and returns authentication tokens if valid.
        
        Args:
            phone: Phone number that received the OTP
            otp: One-time password to verify
            
        Returns:
            Dictionary containing access_token, refresh_token, and user data
            
        Raises:
            AuthError: If OTP is invalid or expired
        """
        # Retrieve stored OTP
        otp_ref = self.db.collection("otps").document(phone)
        otp_doc = await otp_ref.get()
        
        if not otp_doc.exists:
            raise AuthError("OTP not found or expired", "invalid_otp")
        
        otp_data = otp_doc.to_dict()
        
        # Check expiry
        if datetime.utcnow() > otp_data.get("expires_at", datetime.min):
            await otp_ref.delete()
            raise AuthError("OTP expired", "otp_expired")
        
        # Check attempts (max 3)
        if otp_data.get("attempts", 0) >= 3:
            await otp_ref.delete()
            raise AuthError("Too many attempts", "too_many_attempts")
        
        # Verify OTP
        if otp_data.get("otp") != otp:
            await otp_ref.update({"attempts": otp_data.get("attempts", 0) + 1})
            raise AuthError("Invalid OTP", "invalid_otp")
        
        # Delete used OTP
        await otp_ref.delete()
        
        # Find or create user
        users_ref = self.db.collection("users")
        query = users_ref.where("phone", "==", phone).limit(1)
        snapshot = await query.get()
        
        if snapshot:
            # Existing user - login
            user_doc = snapshot[0]
            user_data = user_doc.to_dict()
            user_id = user_data["uid"]
            role = user_data.get("role", "customer")
            salon_id = user_data.get("salon_id")
        else:
            # New user - create account
            user_id = users_ref.document().id
            role = StaffRole.CUSTOMER.value
            salon_id = None
            
            user_data = {
                "uid": user_id,
                "phone": phone,
                "role": role,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            await users_ref.document(user_id).set(user_data)
        
        # Generate tokens
        access_token = create_access_token(
            data={"sub": user_id, "role": role, "salon_id": salon_id}
        )
        refresh_token = create_refresh_token(data={"sub": user_id})
        
        # Store refresh token
        await self._store_refresh_token(user_id, refresh_token)
        
        logger.info(
            "OTP verified",
            user_id=user_id,
            phone=phone,
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "uid": user_id,
                "phone": phone,
                "display_name": user_data.get("display_name"),
                "role": role,
            },
            "role": role,
            "salon_id": salon_id,
        }
    
    async def refresh_access_token(
        self,
        refresh_token: str
    ) -> Dict[str, Any]:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Dictionary containing new access_token and refresh_token
            
        Raises:
            AuthError: If refresh token is invalid or revoked
        """
        # Decode and validate refresh token
        try:
            payload = decode_token(refresh_token)
            user_id = payload.get("sub")
        except Exception:
            raise AuthError("Invalid refresh token", "invalid_token")
        
        # Check if token is revoked
        token_ref = self.db.collection("refresh_tokens").document(user_id)
        token_doc = await token_ref.get()
        
        if not token_doc.exists or token_doc.to_dict().get("token") != refresh_token:
            raise AuthError("Refresh token revoked", "token_revoked")
        
        # Get user data
        user_doc = await self.db.collection("users").document(user_id).get()
        if not user_doc.exists:
            raise AuthError("User not found", "user_not_found")
        
        user_data = user_doc.to_dict()
        role = user_data.get("role", "customer")
        salon_id = user_data.get("salon_id")
        
        # Generate new tokens
        new_access_token = create_access_token(
            data={"sub": user_id, "role": role, "salon_id": salon_id}
        )
        new_refresh_token = create_refresh_token(data={"sub": user_id})
        
        # Store new refresh token
        await self._store_refresh_token(user_id, new_refresh_token)
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        }
    
    async def logout(self, token: str) -> None:
        """Logout user by revoking refresh token.
        
        Args:
            token: Access token to identify user
            
        Raises:
            AuthError: If logout fails
        """
        try:
            payload = decode_token(token)
            user_id = payload.get("sub")
            
            # Delete refresh token
            token_ref = self.db.collection("refresh_tokens").document(user_id)
            await token_ref.delete()
            
            logger.info("User logged out", user_id=user_id)
        except Exception:
            # Silently fail for invalid tokens during logout
            pass
    
    async def change_password(
        self,
        uid: str,
        current_password: str,
        new_password: str
    ) -> None:
        """Change user password.
        
        Args:
            uid: User ID
            current_password: Current password for verification
            new_password: New password to set
            
        Raises:
            AuthError: If current password is incorrect or update fails
        """
        # Get user
        user_ref = self.db.collection("users").document(uid)
        user_doc = await user_ref.get()
        
        if not user_doc.exists:
            raise AuthError("User not found", "user_not_found")
        
        user_data = user_doc.to_dict()
        
        # Verify current password
        if not verify_password(current_password, user_data.get("password_hash", "")):
            raise AuthError("Current password is incorrect", "invalid_password")
        
        # Update password
        new_hash = get_password_hash(new_password)
        await user_ref.update({
            "password_hash": new_hash,
            "updated_at": datetime.utcnow(),
        })
        
        # Revoke all refresh tokens (force re-login)
        await self.db.collection("refresh_tokens").document(uid).delete()
        
        logger.info("Password changed", user_id=uid)
    
    async def login_with_firebase(
        self,
        uid: str,
        email: Optional[str],
        phone: Optional[str]
    ) -> Dict[str, Any]:
        """Login or create user from Firebase authentication.
        
        Args:
            uid: Firebase user ID
            email: User's email from Firebase
            phone: User's phone from Firebase
            
        Returns:
            Dictionary containing access_token, refresh_token, and user data
            
        Raises:
            AuthError: If Firebase user creation fails
        """
        # Check if user exists
        user_ref = self.db.collection("users").document(uid)
        user_doc = await user_ref.get()
        
        if user_doc.exists:
            # Existing user
            user_data = user_doc.to_dict()
            role = user_data.get("role", "customer")
            salon_id = user_data.get("salon_id")
        else:
            # Create new user from Firebase data
            role = StaffRole.CUSTOMER.value
            salon_id = None
            
            user_data = {
                "uid": uid,
                "email": email,
                "phone": phone,
                "role": role,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            await user_ref.set(user_data)
        
        # Generate tokens
        access_token = create_access_token(
            data={"sub": uid, "role": role, "salon_id": salon_id}
        )
        refresh_token = create_refresh_token(data={"sub": uid})
        
        # Store refresh token
        await self._store_refresh_token(uid, refresh_token)
        
        logger.info(
            "Firebase login",
            user_id=uid,
            email=email,
            phone=phone,
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "uid": uid,
                "email": email,
                "phone": phone,
                "display_name": user_data.get("display_name"),
                "role": role,
            },
            "role": role,
            "salon_id": salon_id,
        }
    
    async def _store_refresh_token(
        self,
        user_id: str,
        refresh_token: str
    ) -> None:
        """Store refresh token in database.
        
        Args:
            user_id: User ID to associate token with
            refresh_token: Refresh token to store
        """
        token_ref = self.db.collection("refresh_tokens").document(user_id)
        await token_ref.set({
            "token": refresh_token,
            "created_at": datetime.utcnow(),
        })


async def get_auth_service() -> AuthService:
    """Dependency injection for AuthService.
    
    Creates and returns an AuthService instance with a Firestore client.
    
    Yields:
        AuthService instance
    """
    db = get_firestore_async()
    yield AuthService(db)


__all__ = [
    "AuthService",
    "get_auth_service",
]
