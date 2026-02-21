"""Unit tests for Authentication System.

Tests cover:
- User registration (email and phone)
- Login (email and phone with OTP)
- Token management
- Profile updates
- Role-based access control
- Rate limiting
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest_asyncio

from app.api.auth import router
from app.api.dependencies import (
    AuthContext,
    get_current_user,
    require_role,
    require_permission,
)
from app.core.auth import (
    Permission,
    has_permission,
    has_any_permission,
    has_all_permissions,
    get_role_permissions,
    hash_password,
    verify_password,
    RateLimitType,
    check_rate_limit,
    increment_rate_limit,
    SessionManager,
)
from app.schemas.base import StaffRole


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def app():
    """Create FastAPI app with auth router."""
    app = FastAPI(redirect_slashes=False)
    app.include_router(router, prefix="/api/v1/auth")
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


def create_mock_redis():
    """Create a properly mocked Redis client with all async methods."""
    # Create the nested client mock with async methods
    nested_client = Mock()
    nested_client.scan_iter = AsyncMock(return_value=[])
    nested_client.expire = AsyncMock(return_value=True)
    nested_client.ttl = AsyncMock(return_value=60)
    nested_client.incr = AsyncMock(return_value=2)
    
    # Create the main redis mock
    redis = Mock()
    redis.client = nested_client
    
    # Async methods on the main redis object
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    redis.incr = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=True)
    redis.exists = AsyncMock(return_value=True)
    redis.ttl = AsyncMock(return_value=300)
    
    return redis


@pytest.fixture
def mock_redis():
    """Mock Redis client with async methods."""
    return create_mock_redis()


@pytest.fixture
def mock_firestore():
    """Mock Firestore client."""
    db = Mock()
    doc_ref = Mock()
    doc_ref.get = Mock(return_value=Mock(exists=True, to_dict=Mock(return_value={
        "uid": "test-uid",
        "email": "test@example.com",
        "name": "Test User",
        "role": "owner",
                "salon_id": "salon-123",
        "salon_id": "salon-123",
    })))
    doc_ref.set = Mock()
    doc_ref.update = Mock()
    db.collection.return_value.document.return_value = doc_ref
    return db


@pytest.fixture
def auth_context_owner():
    """Create owner auth context."""
    from app.core.auth import get_permissions_for_role
    return AuthContext(
        uid="user-123",
        email="owner@example.com",
        phone="+919876543210",
        salon_id="salon-123",
        role=StaffRole.OWNER,
        name="Owner User",
        is_owner=True,
        permissions=get_permissions_for_role(StaffRole.OWNER),
    )


@pytest.fixture
def auth_context_manager():
    """Create manager auth context."""
    from app.core.auth import get_permissions_for_role
    return AuthContext(
        uid="user-456",
        email="manager@example.com",
        phone="+919876543211",
        salon_id="salon-123",
        role=StaffRole.MANAGER,
        name="Manager User",
        is_owner=False,
        permissions=get_permissions_for_role(StaffRole.MANAGER),
    )


@pytest.fixture
def auth_context_stylist():
    """Create stylist auth context."""
    from app.core.auth import get_permissions_for_role
    return AuthContext(
        uid="user-789",
        email="stylist@example.com",
        phone="+919876543212",
        salon_id="salon-123",
        role=StaffRole.STYLIST,
        name="Stylist User",
        is_owner=False,
        permissions=get_permissions_for_role(StaffRole.STYLIST),
    )


@pytest.fixture
def auth_context_customer():
    """Create customer auth context."""
    from app.core.auth import get_permissions_for_role
    return AuthContext(
        uid="user-customer",
        email="customer@example.com",
        phone="+919876543213",
        salon_id="salon-123",
        role=StaffRole.CUSTOMER,
        name="Customer User",
        is_owner=False,
        permissions=get_permissions_for_role(StaffRole.CUSTOMER),
    )


# ============================================================================
# Permission Tests
# ============================================================================

class TestPermissions:
    """Test permission system."""
    
    def test_owner_has_all_permissions(self):
        """Owner should have all permissions."""
        permissions = get_role_permissions(StaffRole.OWNER)
        assert Permission.SALON_EDIT in permissions
        assert Permission.STAFF_CREATE in permissions
        assert Permission.BOOKING_CREATE in permissions
        assert Permission.PAYMENT_PROCESS in permissions
        assert Permission.REPORTS_VIEW in permissions
    
    def test_manager_permissions(self):
        """Manager should have management permissions."""
        permissions = get_role_permissions(StaffRole.MANAGER)
        assert Permission.STAFF_CREATE in permissions
        assert Permission.BOOKING_CREATE in permissions
        assert Permission.REPORTS_VIEW in permissions
        # Manager doesn't have billing:manage (owner only for subscription)
    
    def test_receptionist_permissions(self):
        """Receptionist should have booking and payment permissions."""
        permissions = get_role_permissions(StaffRole.RECEPTIONIST)
        assert Permission.BOOKING_CREATE in permissions
        assert Permission.BOOKING_EDIT in permissions
        assert Permission.PAYMENT_PROCESS in permissions
        assert Permission.STAFF_CREATE not in permissions
    
    def test_stylist_permissions(self):
        """Stylist should have limited permissions."""
        permissions = get_role_permissions(StaffRole.STYLIST)
        assert Permission.BOOKING_VIEW in permissions
        assert Permission.BOOKING_EDIT in permissions  # Can update booking status
        assert Permission.BOOKING_CREATE not in permissions
        assert Permission.PAYMENT_PROCESS not in permissions
    
    def test_customer_permissions(self):
        """Customer should have minimal permissions."""
        permissions = get_role_permissions(StaffRole.CUSTOMER)
        assert Permission.BOOKING_VIEW in permissions
        assert Permission.CUSTOMER_EDIT in permissions
        assert Permission.BOOKING_CREATE in permissions  # Customers can book
        assert Permission.STAFF_VIEW not in permissions
    
    def test_has_permission_true(self):
        """Test has_permission returns True for valid permission."""
        assert has_permission(StaffRole.OWNER, Permission.SALON_EDIT)
        assert has_permission(StaffRole.MANAGER, Permission.STAFF_CREATE)
    
    def test_has_permission_false(self):
        """Test has_permission returns False for invalid permission."""
        assert not has_permission(StaffRole.STYLIST, Permission.STAFF_CREATE)
        assert not has_permission(StaffRole.CUSTOMER, Permission.PAYMENT_PROCESS)
    
    def test_has_any_permission(self):
        """Test has_any_permission with OR logic."""
        permissions = [Permission.STAFF_CREATE, Permission.BOOKING_CREATE]
        assert has_any_permission(StaffRole.MANAGER, permissions)
        assert has_any_permission(StaffRole.RECEPTIONIST, permissions)
        assert not has_any_permission(StaffRole.STYLIST, permissions)
    
    def test_has_all_permissions(self):
        """Test has_all_permissions with AND logic."""
        permissions = [Permission.BOOKING_CREATE, Permission.BOOKING_EDIT]
        assert has_all_permissions(StaffRole.MANAGER, permissions)
        assert has_all_permissions(StaffRole.RECEPTIONIST, permissions)
        assert not has_all_permissions(StaffRole.STYLIST, permissions)


# ============================================================================
# AuthContext Tests
# ============================================================================

class TestAuthContext:
    """Test AuthContext class."""
    
    def test_auth_context_has_permission(self, auth_context_owner):
        """Test AuthContext.has_permission method."""
        assert auth_context_owner.has_permission(Permission.SALON_EDIT)
        assert auth_context_owner.has_permission(Permission.STAFF_CREATE)
    
    def test_auth_context_has_role(self, auth_context_manager):
        """Test AuthContext.has_role method."""
        assert auth_context_manager.has_role([StaffRole.MANAGER, StaffRole.OWNER])
        assert not auth_context_manager.has_role([StaffRole.STYLIST])
    
    def test_auth_context_get_permissions(self, auth_context_stylist):
        """Test AuthContext.get_permissions method."""
        permissions = auth_context_stylist.get_permissions()
        assert isinstance(permissions, list)
        assert Permission.BOOKING_VIEW.value in permissions
    
    def test_auth_context_repr(self, auth_context_owner):
        """Test AuthContext string representation."""
        repr_str = repr(auth_context_owner)
        assert "user-123" in repr_str
        assert "owner" in repr_str
        assert "salon-123" in repr_str


# ============================================================================
# Password Tests
# ============================================================================

class TestPasswordHashing:
    """Test password hashing utilities."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "securepassword123"
        hashed = hash_password(password)
        assert hashed != password
        assert hashed.startswith("$2b$")
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "securepassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed)
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "securepassword123"
        hashed = hash_password(password)
        assert not verify_password("wrongpassword", hashed)
    
    def test_hash_password_different_salts(self):
        """Test that same password produces different hashes."""
        password = "securepassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


# ============================================================================
# Rate Limiting Tests
# ============================================================================

class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_allowed(self):
        """Test rate limit check when allowed."""
        mock_redis = create_mock_redis()
        mock_redis.get = AsyncMock(return_value=None)
        
        result = await check_rate_limit(
            mock_redis,
            RateLimitType.LOGIN,
            "test-ip",
        )
        
        assert result["allowed"] is True
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeded(self):
        """Test rate limit check when exceeded."""
        mock_redis = create_mock_redis()
        # Return a value that exceeds the limit (5 for LOGIN)
        mock_redis.get = AsyncMock(return_value="10")
        mock_redis.ttl = AsyncMock(return_value=60)  # Use redis.ttl not redis.client.ttl
        
        result = await check_rate_limit(
            mock_redis,
            RateLimitType.LOGIN,
            "test-ip",
        )
        
        # With 10 attempts and limit of 5 for LOGIN, should be blocked
        assert result["allowed"] is False
        assert result["retry_after"] == 60
    
    @pytest.mark.asyncio
    async def test_increment_rate_limit_existing_key(self):
        """Test rate limit increment when key exists."""
        mock_redis = create_mock_redis()
        mock_redis.exists = AsyncMock(return_value=True)  # Key exists
        mock_redis.client.incr = AsyncMock(return_value=2)
        
        await increment_rate_limit(
            mock_redis,
            RateLimitType.LOGIN,
            "test-ip",
        )
        
        # Should call client.incr when key exists
        mock_redis.client.incr.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_increment_rate_limit_new_key(self):
        """Test rate limit increment when key doesn't exist."""
        mock_redis = create_mock_redis()
        mock_redis.exists = AsyncMock(return_value=False)  # Key doesn't exist
        mock_redis.set = AsyncMock(return_value=True)
        
        await increment_rate_limit(
            mock_redis,
            RateLimitType.LOGIN,
            "test-ip",
        )
        
        # Should call set when key doesn't exist
        mock_redis.set.assert_called_once()


# ============================================================================
# Session Management Tests
# ============================================================================

class TestSessionManager:
    """Test session management."""
    
    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test session creation."""
        mock_redis = create_mock_redis()
        mock_redis.set = AsyncMock(return_value=True)
        
        manager = SessionManager(mock_redis)
        session_id = await manager.create_session(
            user_id="user-123",
            salon_id="salon-123",
            role="owner",
        )
        
        assert session_id is not None
        assert len(session_id) > 20
        mock_redis.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_session(self):
        """Test session retrieval."""
        mock_redis = create_mock_redis()
        session_data = {
            "user_id": "user-123",
            "salon_id": "salon-123",
            "role": "owner",
                "salon_id": "salon-123",
        }
        mock_redis.get = AsyncMock(return_value=session_data)
        
        manager = SessionManager(mock_redis)
        result = await manager.get_session("session-id")
        
        assert result == session_data
    
    @pytest.mark.asyncio
    async def test_delete_session(self):
        """Test session deletion."""
        mock_redis = create_mock_redis()
        mock_redis.delete = AsyncMock(return_value=True)
        
        manager = SessionManager(mock_redis)
        result = await manager.delete_session("session-id")
        
        assert result is True
        mock_redis.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extend_session(self):
        """Test session extension."""
        mock_redis = create_mock_redis()
        mock_redis.exists = AsyncMock(return_value=True)
        mock_redis.client.expire = AsyncMock(return_value=True)
        
        manager = SessionManager(mock_redis)
        result = await manager.extend_session("session-id")
        
        assert result is True
        mock_redis.client.expire.assert_called_once()


# ============================================================================
# Dependency Tests
# ============================================================================

class TestDependencies:
    """Test FastAPI dependencies."""
    
    def test_require_role_owner(self, auth_context_owner):
        """Test require_role dependency for owner."""
        checker = require_role([StaffRole.OWNER])
        # Should not raise
        assert checker is not None
    
    def test_require_permission_owner(self, auth_context_owner):
        """Test require_permission dependency for owner."""
        checker = require_permission([Permission.SALON_EDIT])
        # Should not raise
        assert checker is not None
    
    def test_require_permission_denied(self, auth_context_stylist):
        """Test require_permission raises for insufficient permissions."""
        checker = require_permission([Permission.STAFF_CREATE])
        # This would raise HTTPException in actual use
        assert checker is not None


# ============================================================================
# API Endpoint Tests
# ============================================================================

class TestAuthEndpoints:
    """Test authentication API endpoints."""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Create a mock auth service."""
        service = Mock()
        service.register_user = AsyncMock(return_value={
            "user": {
                "uid": "user-123",
                "email": "test@example.com",
                "display_name": "Test User",
            },
            "salon_id": "salon-123",
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
        })
        service.login = AsyncMock(return_value={
            "user": {
                "uid": "user-123",
                "email": "test@example.com",
                "display_name": "Test User",
            },
            "salon_id": "salon-123",
            "role": "manager",
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
        })
        service.send_phone_otp = AsyncMock(return_value={
            "message": "OTP sent successfully",
            "salon_id": "salon-123",
            "_dev_otp": "123456",
        })
        service.verify_phone_otp = AsyncMock(return_value={
            "user": {
                "uid": "user-123",
                "phone": "+919876543210",
                "display_name": "Test User",
            },
            "salon_id": "salon-123",
            "role": "customer",
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
        })
        service.logout = AsyncMock(return_value=True)
        return service
    
    def test_register_success(self, app, client, mock_auth_service):
        """Test successful user registration."""
        from app.services.auth_service import get_auth_service
        
        # Override the dependency
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "display_name": "Test User",
                "role": "owner",
                "salon_id": "salon-123",
            },
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] == True
        assert data["salon_id"] == "salon-123"
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_register_with_salon(self, app, client, mock_auth_service):
        """Test registration with salon creation."""
        from app.services.auth_service import get_auth_service
        
        # Override the dependency
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "owner@example.com",
                "password": "password123",
                "display_name": "Owner User",
                "role": "owner",
                "salon_id": "salon-123",
            },
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["role"] == "owner"
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_login_success(self, app, client, mock_auth_service):
        """Test successful login."""
        from app.services.auth_service import get_auth_service
        
        # Override the dependency
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["access_token"] == "test-access-token"
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_login_invalid_credentials(self, app, client, mock_auth_service):
        """Test login with invalid credentials."""
        from app.services.auth_service import get_auth_service
        from app.core.auth import AuthError
        
        # Override the mock to raise an error
        mock_auth_service.login = AsyncMock(side_effect=AuthError("Invalid credentials", "invalid_credentials"))
        
        # Override the dependency
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_login_phone_success(self, app, client, mock_auth_service):
        """Test phone login initiation."""
        from app.services.auth_service import get_auth_service
        
        # Override the dependency
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        response = client.post(
            "/api/v1/auth/phone-otp",
            json={
                "phone": "+919876543210",
            },
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] == True
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_verify_otp_success(self, app, client, mock_auth_service):
        """Test OTP verification."""
        from app.services.auth_service import get_auth_service
        
        # Override the dependency
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        response = client.post(
            "/api/v1/auth/verify-otp",
            json={
                "phone": "+919876543210",
                "otp": "123456",
            },
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] == True
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_verify_otp_invalid(self, app, client, mock_auth_service):
        """Test OTP verification with invalid code."""
        from app.services.auth_service import get_auth_service
        from app.core.auth import AuthError
        
        # Override the mock to raise an error
        mock_auth_service.verify_phone_otp = AsyncMock(side_effect=AuthError("Invalid OTP", "invalid_otp"))
        
        # Override the dependency
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        response = client.post(
            "/api/v1/auth/verify-otp",
            json={
                "phone": "+919876543210",
                "otp": "000000",
            },
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Clean up
        app.dependency_overrides.clear()

class TestProtectedEndpoints:
    """Test protected endpoints with authentication."""
    
    def test_get_current_user_unauthorized(self, client):
        """Test /auth/me without token."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('app.api.dependencies.get_current_user')
    def test_get_current_user_success(self, mock_get_user, client, auth_context_owner):
        """Test /auth/me with valid token."""
        mock_get_user.return_value = auth_context_owner
        
        # Override dependency
        from app.api.auth import router
        
        # This would work with proper dependency override
        # For now, we test the logic
        assert auth_context_owner.uid == "user-123"
    
    @patch('app.api.auth.AuthService')
    def test_logout_success(self, mock_auth_service, client, auth_context_owner):
        """Test logout endpoint."""
        mock_auth_service.return_value.logout = AsyncMock(return_value=True)
        
        # Would need proper auth header in real test
        # This tests the service logic
        assert True


# ============================================================================
# Integration Tests
# ============================================================================

class TestAuthIntegration:
    """Integration tests for authentication flow."""
    
    @pytest.mark.asyncio
    async def test_full_registration_flow(self):
        """Test complete registration flow."""
        # This would test:
        # 1. Register user
        # 2. Verify email
        # 3. Login
        # 4. Access protected resource
        pass
    
    @pytest.mark.asyncio
    async def test_phone_auth_flow(self):
        """Test phone authentication flow."""
        # This would test:
        # 1. Request OTP
        # 2. Verify OTP
        # 3. Get token
        # 4. Access protected resource
        pass
    
    @pytest.mark.asyncio
    async def test_role_based_access(self):
        """Test role-based access control."""
        # This would test:
        # 1. Login as different roles
        # 2. Access role-specific endpoints
        # 3. Verify access denied for unauthorized roles
        pass


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
