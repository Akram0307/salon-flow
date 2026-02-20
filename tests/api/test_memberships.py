"""Comprehensive tests for Membership API endpoints.

Covers:
- Membership CRUD operations
- Renewal processing
- Multi-tenant isolation
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date, timedelta
from decimal import Decimal

from fastapi import FastAPI, status
from httpx import AsyncClient, ASGITransport

from app.api.memberships import router
from app.api.dependencies import AuthContext
from app.schemas import (
    MembershipCreate,
    MembershipUpdate,
    Membership,
    MembershipSummary,
    MembershipStatus,
    MembershipPlanType,
    PaginatedResponse,
)
from app.schemas.base import StaffRole


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def mock_auth_context():
    """Mock authentication context."""
    context = MagicMock(spec=AuthContext)
    context.uid = "user_001"
    context.email = "test@salon.com"
    context.role = StaffRole.MANAGER
    context.salon_id = "salon_001"
    context.has_permission = MagicMock(return_value=True)
    return context


@pytest.fixture
def mock_membership():
    """Sample membership object."""
    return Membership(
        id="membership_001",
        salon_id="salon_001",
        customer_id="customer_001",
        plan_id="plan_001",
        plan_name="Gold Membership",
        plan_type=MembershipPlanType.MONTHLY,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        amount_paid=Decimal("999.00"),
        discount_rate=Decimal("15.0"),
        status=MembershipStatus.ACTIVE,
        auto_renew=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_customer():
    """Sample customer object for mocking."""
    mock_customer = MagicMock()
    mock_customer.id = "customer_001"
    mock_customer.salon_id = "salon_001"
    mock_customer.name = "Test Customer"
    mock_customer.phone = "+1234567890"
    return mock_customer


@pytest.fixture
def mock_membership_summary():
    """Sample membership summary."""
    return MembershipSummary(
        id="membership_001",
        salon_id="salon_001",
        customer_id="customer_001",
        plan_name="Gold Membership",
        plan_type=MembershipPlanType.MONTHLY,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        status=MembershipStatus.ACTIVE,
        days_remaining=300,
    )


# ============================================================================
# Membership List Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestMembershipList:
    """Test membership listing endpoints."""
    
    async def test_list_memberships_success(self, app, mock_auth_context, mock_membership_summary):
        """Test successful membership listing."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.memberships.MembershipModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[mock_membership_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/memberships")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        
        app.dependency_overrides.clear()
    
    async def test_list_memberships_with_status_filter(self, app, mock_auth_context, mock_membership_summary):
        """Test membership listing with status filter."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.memberships.MembershipModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[mock_membership_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/memberships?status=active")
        
        assert response.status_code == status.HTTP_200_OK
        
        app.dependency_overrides.clear()


# ============================================================================
# Membership Create Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestMembershipCreate:
    """Test membership creation."""
    
    async def test_create_membership_success(self, app, mock_auth_context, mock_membership, mock_customer):
        """Test successful membership creation."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.memberships.MembershipModel') as MockModel, \
             patch('app.api.memberships.CustomerModel') as MockCustomerModel:
            # Mock MembershipModel
            mock_instance = AsyncMock()
            mock_instance.create = AsyncMock(return_value=mock_membership)
            mock_instance.get_active_for_customer = AsyncMock(return_value=None)  # No existing membership
            MockModel.return_value = mock_instance
            
            # Mock CustomerModel
            mock_customer_instance = AsyncMock()
            mock_customer_instance.get = AsyncMock(return_value=mock_customer)
            MockCustomerModel.return_value = mock_customer_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/memberships",
                    json={
                        "customer_id": "customer_001",
                        "plan_id": "plan_001",
                        "plan_name": "Gold Membership",
                        "plan_type": "monthly",
                        "duration_months": 12,
                        "amount_paid": "999.00",
                    }
                )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["customer_id"] == "customer_001"
        
        app.dependency_overrides.clear()
    
    async def test_create_membership_customer_already_has_active(self, app, mock_auth_context, mock_membership, mock_customer):
        """Test membership creation fails if customer already has active membership."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.memberships.MembershipModel') as MockModel, \
             patch('app.api.memberships.CustomerModel') as MockCustomerModel:
            # Mock MembershipModel - return existing membership for get_active_for_customer
            mock_instance = AsyncMock()
            mock_instance.get_active_for_customer = AsyncMock(return_value=mock_membership)  # Existing membership
            MockModel.return_value = mock_instance
            
            # Mock CustomerModel
            mock_customer_instance = AsyncMock()
            mock_customer_instance.get = AsyncMock(return_value=mock_customer)
            MockCustomerModel.return_value = mock_customer_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/memberships",
                    json={
                        "customer_id": "customer_001",
                        "plan_id": "plan_001",
                        "plan_name": "Gold Membership",
                        "plan_type": "monthly",
                        "duration_months": 12,
                        "amount_paid": "999.00",
                    }
                )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        app.dependency_overrides.clear()


# ============================================================================
# Membership Get Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestMembershipGet:
    """Test membership retrieval."""
    
    async def test_get_membership_success(self, app, mock_auth_context, mock_membership):
        """Test successful membership retrieval."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.memberships.MembershipModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_membership)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/memberships/membership_001")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "membership_001"
        
        app.dependency_overrides.clear()
    
    async def test_get_membership_not_found(self, app, mock_auth_context):
        """Test membership not found returns 404."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.memberships.MembershipModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=None)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/memberships/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        app.dependency_overrides.clear()


# ============================================================================
# Membership Update Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestMembershipUpdate:
    """Test membership update."""
    
    async def test_update_membership_success(self, app, mock_auth_context, mock_membership):
        """Test successful membership update."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        updated_membership = mock_membership.model_copy(update={"auto_renew": True})
        
        with patch('app.api.memberships.MembershipModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_membership)
            mock_instance.update = AsyncMock(return_value=updated_membership)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/memberships/membership_001",
                    json={"auto_renew": True}
                )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["auto_renew"] == True
        
        app.dependency_overrides.clear()
    
    async def test_cancel_membership_success(self, app, mock_auth_context, mock_membership):
        """Test successful membership cancellation."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        cancelled_membership = mock_membership.model_copy(update={"status": MembershipStatus.CANCELLED})
        
        with patch('app.api.memberships.MembershipModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_membership)
            mock_instance.update = AsyncMock(return_value=cancelled_membership)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/memberships/membership_001",
                    json={"status": "cancelled"}
                )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "cancelled"
        
        app.dependency_overrides.clear()


# ============================================================================
# Membership Renewal Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestMembershipRenewal:
    """Test membership renewal."""
    
    async def test_renew_membership_success(self, app, mock_auth_context, mock_membership):
        """Test successful membership renewal."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        renewed_membership = mock_membership.model_copy(
            update={
                "end_date": date(2025, 12, 31),
                "amount_paid": Decimal("1099.00"),
            }
        )
        
        with patch('app.api.memberships.MembershipModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_membership)
            mock_instance.update = AsyncMock(return_value=renewed_membership)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/memberships/membership_001/renew",
                    json={
                        "duration_months": 12,
                    }
                )
        
        assert response.status_code == status.HTTP_200_OK
        
        app.dependency_overrides.clear()


# ============================================================================
# Edge Case Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestMembershipEdgeCases:
    """Test edge cases for membership operations."""
    
    async def test_create_membership_invalid_duration(self, app, mock_auth_context):
        """Test membership creation with invalid duration fails."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/memberships",
                json={
                    "customer_id": "customer_001",
                    "plan_id": "plan_001",
                    "plan_name": "Gold Membership",
                    "plan_type": "monthly",
                    "duration_months": 0,  # Invalid: must be >= 1
                    "amount_paid": "999.00",
                }
            )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()
    
    async def test_create_membership_negative_amount(self, app, mock_auth_context):
        """Test membership creation with negative amount fails."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/memberships",
                json={
                    "customer_id": "customer_001",
                    "plan_id": "plan_001",
                    "plan_name": "Gold Membership",
                    "plan_type": "monthly",
                    "duration_months": 12,
                    "amount_paid": "-100.00",  # Negative amount
                }
            )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()


# ============================================================================
# Multi-Tenant Isolation Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestMembershipMultiTenant:
    """Test multi-tenant isolation for memberships."""
    
    async def test_get_membership_wrong_salon(self, app, mock_auth_context):
        """Test access denied for membership from different salon."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        # Membership from different salon
        wrong_membership = Membership(
            id="membership_002",
            salon_id="salon_002",  # Different salon
            customer_id="customer_002",
            plan_id="plan_001",
            plan_name="Gold Membership",
            plan_type=MembershipPlanType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            amount_paid=Decimal("999.00"),
            status=MembershipStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        with patch('app.api.memberships.MembershipModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=wrong_membership)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/memberships/membership_002")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
