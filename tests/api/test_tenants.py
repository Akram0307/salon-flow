"""Tests for Tenant/Salon Management API endpoints.

Uses proper mocking to isolate tests from Firebase and other external dependencies.
"""
import os
import sys

# Set test environment variables BEFORE any imports
os.environ["ENVIRONMENT"] = "test"
os.environ["FIREBASE_PROJECT_ID"] = "salon-flow-test"
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = "localhost:9099"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["OPENROUTER_API_KEY"] = "test-api-key"

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from decimal import Decimal

# Mock Firebase before importing app modules
sys.modules['firebase_admin'] = MagicMock()
sys.modules['firebase_admin.auth'] = MagicMock()
sys.modules['firebase_admin.firestore'] = MagicMock()

from app.api.tenants import router
from app.api.dependencies import AuthContext
from app.schemas.base import StaffRole, SubscriptionPlan, SubscriptionStatus
from app.schemas import Salon, SalonLayout, SalonSettings, SalonSubscription


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def app():
    """Create a test FastAPI app."""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/tenants")
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def auth_context_owner():
    """Create an owner auth context."""
    return AuthContext(
        uid="user-owner-123",
        email="owner@example.com",
        phone="+919876543210",
        role=StaffRole.OWNER,
        salon_id="salon-123",
        is_owner=True,
    )


@pytest.fixture
def auth_context_manager():
    """Create a manager auth context."""
    return AuthContext(
        uid="user-manager-123",
        email="manager@example.com",
        phone="+919876543211",
        role=StaffRole.MANAGER,
        salon_id="salon-123",
        is_owner=False,
    )


@pytest.fixture
def auth_context_staff():
    """Create a staff auth context."""
    return AuthContext(
        uid="user-staff-123",
        email="staff@example.com",
        phone="+919876543212",
        role=StaffRole.STYLIST,
        salon_id="salon-123",
        is_owner=False,
    )


@pytest.fixture
def mock_salon():
    """Create a mock salon object."""
    return Salon(
        id="salon-123",
        owner_id="user-owner-123",
        name="Jawed Habib Kurnool",
        slug="jawed-habib-kurnool",
        phone="+919876543210",
        email="contact@jawedhabibkurnool.com",
        address_line1="Main Road",
        city="Kurnool",
        state="Andhra Pradesh",
        pincode="518001",
        layout=SalonLayout(
            mens_chairs=6,
            womens_chairs=4,
            service_rooms=4,
        ),
        subscription_plan=SubscriptionPlan.PROFESSIONAL,
        subscription_status=SubscriptionStatus.ACTIVE,
        gst_rate=Decimal("5.0"),
        loyalty_rate=Decimal("0.1"),
        loyalty_expiry_months=12,
        membership_renewal_days=15,
        late_arrival_grace_minutes=15,
    )


# ============================================================================
# TEST CASES
# ============================================================================

class TestSalonEndpoints:
    """Test salon CRUD endpoints."""
    
    def test_create_salon_success(self, app, client, mock_salon, auth_context_owner):
        """Test successful salon creation."""
        from app.api.dependencies import require_owner
        
        # Create mock salon model
        mock_model = Mock()
        mock_model.create = AsyncMock(return_value=mock_salon)
        
        # Override dependencies
        app.dependency_overrides[require_owner] = lambda: auth_context_owner
        
        with patch('app.api.tenants.SalonModel', return_value=mock_model):
            response = client.post(
                "/api/v1/tenants",
                json={
                    "name": "Jawed Habib Kurnool",
                    "phone": "+919876543210",
                    "email": "contact@jawedhabibkurnool.com",
                    "address_line1": "Main Road",
                    "city": "Kurnool",
                    "state": "Andhra Pradesh",
                    "pincode": "518001",
                },
            )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_get_salon_success(self, app, client, mock_salon, auth_context_owner):
        """Test getting salon by ID."""
        from app.api.dependencies import get_current_user
        
        # Create mock salon model
        mock_model = Mock()
        mock_model.get = AsyncMock(return_value=mock_salon)
        
        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: auth_context_owner
        
        with patch('app.api.tenants.SalonModel', return_value=mock_model):
            response = client.get(f"/api/v1/tenants/{mock_salon.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == mock_salon.id
        assert data["name"] == mock_salon.name
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_get_salon_unauthorized(self, app, client, mock_salon):
        """Test getting salon with unauthorized user."""
        from app.api.dependencies import get_current_user
        
        # Create auth context for different salon
        other_context = AuthContext(
            uid="user-staff-456",
            email="staff456@example.com",
            phone="+919876543213",
            role=StaffRole.STYLIST,
            salon_id="salon-456",  # Different salon
            is_owner=False,
        )
        
        # Create mock salon model
        mock_model = Mock()
        mock_model.get = AsyncMock(return_value=mock_salon)
        
        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: other_context
        
        with patch('app.api.tenants.SalonModel', return_value=mock_model):
            response = client.get(f"/api/v1/tenants/{mock_salon.id}")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_update_salon_success(self, app, client, mock_salon, auth_context_manager):
        """Test updating salon details."""
        from app.api.dependencies import require_manager
        
        # Create mock salon model
        mock_model = Mock()
        mock_model.get = AsyncMock(return_value=mock_salon)
        mock_model.update = AsyncMock(return_value=mock_salon)
        
        # Override dependencies
        app.dependency_overrides[require_manager] = lambda: auth_context_manager
        
        with patch('app.api.tenants.SalonModel', return_value=mock_model):
            response = client.put(
                f"/api/v1/tenants/{mock_salon.id}",
                json={
                    "name": "Jawed Habib Kurnool Updated",
                    "phone": "+919876543211",
                },
            )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Clean up
        app.dependency_overrides.clear()


class TestSalonLayout:
    """Test salon layout endpoints."""
    
    def test_get_layout_success(self, app, client, mock_salon, auth_context_owner):
        """Test getting salon layout."""
        from app.api.dependencies import get_current_user
        
        # Create mock salon model
        mock_model = Mock()
        mock_model.get = AsyncMock(return_value=mock_salon)
        
        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: auth_context_owner
        
        with patch('app.api.tenants.SalonModel', return_value=mock_model):
            response = client.get(f"/api/v1/tenants/{mock_salon.id}/layout")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "mens_chairs" in data
        assert "womens_chairs" in data
        assert "service_rooms" in data
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_update_layout_success(self, app, client, mock_salon, auth_context_owner):
        """Test updating salon layout."""
        from app.api.dependencies import require_owner
        
        # Create mock salon model
        mock_model = Mock()
        mock_model.get = AsyncMock(return_value=mock_salon)
        mock_model.update = AsyncMock(return_value=mock_salon)
        
        # Override dependencies
        app.dependency_overrides[require_owner] = lambda: auth_context_owner
        
        with patch('app.api.tenants.SalonModel', return_value=mock_model):
            response = client.put(
                f"/api/v1/tenants/{mock_salon.id}/layout",
                json={
                    "mens_chairs": 8,
                    "womens_chairs": 6,
                    "service_rooms": 5,
                    "bridal_room": True,
                    "spa_rooms": 2,
                    "waiting_capacity": 15,
                },
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["mens_chairs"] == 8
        assert data["womens_chairs"] == 6
        assert data["service_rooms"] == 5
        
        # Clean up
        app.dependency_overrides.clear()


class TestSalonSettings:
    """Test salon settings endpoints."""
    
    def test_get_settings_success(self, app, client, mock_salon, auth_context_owner):
        """Test getting salon settings."""
        from app.api.dependencies import get_current_user
        
        # Create mock salon model
        mock_model = Mock()
        mock_model.get = AsyncMock(return_value=mock_salon)
        
        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: auth_context_owner
        
        with patch('app.api.tenants.SalonModel', return_value=mock_model):
            response = client.get(f"/api/v1/tenants/{mock_salon.id}/settings")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Check for SalonSettings fields
        assert "salon_id" in data
        assert "accept_cash" in data
        assert "accept_upi" in data
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_update_settings_success(self, app, client, mock_salon, auth_context_manager):
        """Test updating salon settings."""
        from app.api.dependencies import require_manager
        
        # Create mock salon model
        mock_model = Mock()
        mock_model.get = AsyncMock(return_value=mock_salon)
        mock_model.update = AsyncMock(return_value=mock_salon)
        
        # Override dependencies
        app.dependency_overrides[require_manager] = lambda: auth_context_manager
        
        with patch('app.api.tenants.SalonModel', return_value=mock_model):
            response = client.put(
                f"/api/v1/tenants/{mock_salon.id}/settings",
                json={
                    "accept_card": True,
                    "reminder_hours_before": 24,
                },
            )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Clean up
        app.dependency_overrides.clear()


class TestSalonBusinessSettings:
    """Test salon business settings endpoints."""
    
    def test_get_business_settings_success(self, app, client, mock_salon, auth_context_owner):
        """Test getting salon business settings."""
        from app.api.dependencies import get_current_user
        
        # Create mock salon model
        mock_model = Mock()
        mock_model.get = AsyncMock(return_value=mock_salon)
        
        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: auth_context_owner
        
        with patch('app.api.tenants.SalonModel', return_value=mock_model):
            response = client.get(f"/api/v1/tenants/{mock_salon.id}/business-settings")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "gst_rate" in data
        assert "loyalty_rate" in data
        assert "loyalty_expiry_months" in data
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_update_business_settings_success(self, app, client, mock_salon, auth_context_owner):
        """Test updating salon business settings."""
        from app.api.dependencies import require_owner
        
        # Create mock salon model
        mock_model = Mock()
        mock_model.get = AsyncMock(return_value=mock_salon)
        mock_model.update = AsyncMock(return_value=mock_salon)
        
        # Override dependencies
        app.dependency_overrides[require_owner] = lambda: auth_context_owner
        
        with patch('app.api.tenants.SalonModel', return_value=mock_model):
            response = client.put(
                f"/api/v1/tenants/{mock_salon.id}/business-settings",
                json={
                    "gst_rate": 5.0,
                    "loyalty_rate": 0.1,
                    "loyalty_expiry_months": 12,
                },
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["gst_rate"] == 5.0
        
        # Clean up
        app.dependency_overrides.clear()


class TestSalonSubscription:
    """Test salon subscription endpoints."""
    
    def test_get_subscription_success(self, app, client, mock_salon, auth_context_owner):
        """Test getting salon subscription."""
        from app.api.dependencies import require_owner
        
        # Create mock salon model
        mock_model = Mock()
        mock_model.get = AsyncMock(return_value=mock_salon)
        
        # Override dependencies
        app.dependency_overrides[require_owner] = lambda: auth_context_owner
        
        with patch('app.api.tenants.SalonModel', return_value=mock_model):
            response = client.get(f"/api/v1/tenants/{mock_salon.id}/subscription")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "plan" in data
        assert "status" in data
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_update_subscription_success(self, app, client, mock_salon, auth_context_owner):
        """Test updating salon subscription."""
        from app.api.dependencies import require_owner
        
        # Create mock salon model
        mock_model = Mock()
        mock_model.get = AsyncMock(return_value=mock_salon)
        mock_model.update = AsyncMock(return_value=mock_salon)
        
        # Override dependencies
        app.dependency_overrides[require_owner] = lambda: auth_context_owner
        
        with patch('app.api.tenants.SalonModel', return_value=mock_model):
            response = client.put(
                f"/api/v1/tenants/{mock_salon.id}/subscription",
                json={
                    "plan": "professional",
                    "billing_cycle": "monthly",
                },
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["plan"] == "professional"
        
        # Clean up
        app.dependency_overrides.clear()
