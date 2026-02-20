"""Comprehensive tests for Staff API endpoints.

Covers:
- Staff CRUD operations
- Skills management
- Multi-tenant isolation
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date, time
from decimal import Decimal

from fastapi import FastAPI, status
from httpx import AsyncClient, ASGITransport

from app.api.staff import router
from app.api.dependencies import AuthContext
from app.schemas import (
    StaffCreate,
    StaffUpdate,
    Staff,
    StaffSummary,
    StaffSkills,
    ServiceSkill,
    StaffAvailability,
    ShiftPreference,
    CommissionConfig,
    PaginatedResponse,
)
from app.schemas.base import StaffRole, StaffStatus, Gender, ExpertiseLevel, SalaryType


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
def mock_skills():
    """Sample staff skills."""
    return StaffSkills(
        skills=[
            ServiceSkill(
                service_id="service_001",
                service_name="Haircut",
                expertise_level=ExpertiseLevel.EXPERT,
                years_experience=5,
                is_primary=True,
            )
        ]
    )


@pytest.fixture
def mock_availability():
    """Sample staff availability."""
    return StaffAvailability(
        is_available=True,
        shift_preferences=ShiftPreference(
            preferred_start_time=time(9, 0),
            preferred_end_time=time(18, 0),
            preferred_off_days=["sunday"],
        ),
        max_daily_hours=10,
    )


@pytest.fixture
def mock_commission():
    """Sample commission configuration."""
    return CommissionConfig(
        base_commission_rate=Decimal("15.0"),
        product_commission_rate=Decimal("5.0"),
    )


@pytest.fixture
def mock_staff(mock_skills, mock_availability, mock_commission):
    """Sample staff object."""
    return Staff(
        id="staff_001",
        salon_id="salon_001",
        name="John Doe",
        phone="+1234567890",
        email="john@salon.com",
        gender=Gender.MALE,
        role=StaffRole.STYLIST,
        is_active=True,
        skills=mock_skills,
        availability=mock_availability,
        salary_type=SalaryType.COMMISSION,
        commission_config=mock_commission,
        joining_date=date(2020, 1, 15),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_staff_summary():
    """Sample staff summary."""
    return StaffSummary(
        id="staff_001",
        salon_id="salon_001",
        name="John Doe",
        phone="+1234567890",
        role=StaffRole.STYLIST,
        is_active=True,
    )


# ============================================================================
# Staff List Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestStaffList:
    """Test staff listing endpoints."""
    
    async def test_list_staff_success(self, app, mock_auth_context, mock_staff_summary):
        """Test successful staff listing."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.staff.StaffModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[mock_staff_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/staff")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        
        app.dependency_overrides.clear()
    
    async def test_list_staff_with_role_filter(self, app, mock_auth_context, mock_staff_summary):
        """Test staff listing with role filter."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.staff.StaffModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[mock_staff_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/staff?role=stylist")
        
        assert response.status_code == status.HTTP_200_OK
        
        app.dependency_overrides.clear()


# ============================================================================
# Staff Create Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestStaffCreate:
    """Test staff creation."""
    
    async def test_create_staff_success(self, app, mock_auth_context, mock_staff):
        """Test successful staff creation."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.staff.StaffModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.create = AsyncMock(return_value=mock_staff)
            mock_instance.find_by_email = AsyncMock(return_value=None)  # No existing staff
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/staff",
                    json={
                        "name": "John Doe",
                        "phone": "+1234567890",
                        "email": "john@salon.com",
                        "role": "stylist",
                    }
                )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "John Doe"
        
        app.dependency_overrides.clear()
    
    async def test_create_staff_duplicate_phone(self, app, mock_auth_context, mock_staff):
        """Test staff creation fails with duplicate phone."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.staff.StaffModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.create = AsyncMock(
                side_effect=ValueError("Staff with this phone already exists")
            )
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/staff",
                    json={
                        "name": "John Doe",
                        "phone": "+1234567890",
                        "role": "stylist",
                    }
                )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        app.dependency_overrides.clear()


# ============================================================================
# Staff Get Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestStaffGet:
    """Test staff retrieval."""
    
    async def test_get_staff_success(self, app, mock_auth_context, mock_staff):
        """Test successful staff retrieval."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.staff.StaffModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_staff)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/staff/staff_001")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "staff_001"
        
        app.dependency_overrides.clear()
    
    async def test_get_staff_not_found(self, app, mock_auth_context):
        """Test staff not found returns 404."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.staff.StaffModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=None)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/staff/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        app.dependency_overrides.clear()


# ============================================================================
# Staff Update Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestStaffUpdate:
    """Test staff update."""
    
    async def test_update_staff_success(self, app, mock_auth_context, mock_staff):
        """Test successful staff update."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        updated_staff = mock_staff.model_copy(update={"name": "John Smith"})
        
        with patch('app.api.staff.StaffModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_staff)
            mock_instance.update = AsyncMock(return_value=updated_staff)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/staff/staff_001",
                    json={"name": "John Smith"}
                )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "John Smith"
        
        app.dependency_overrides.clear()
    
    async def test_deactivate_staff_success(self, app, mock_auth_context, mock_staff):
        """Test successful staff deactivation."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        deactivated_staff = mock_staff.model_copy(update={"is_active": False})
        
        with patch('app.api.staff.StaffModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_staff)
            mock_instance.update = AsyncMock(return_value=deactivated_staff)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/staff/staff_001",
                    json={"is_active": False}
                )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] == False
        
        app.dependency_overrides.clear()


# ============================================================================
# Edge Case Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestStaffEdgeCases:
    """Test edge cases for staff operations."""
    
    async def test_create_staff_empty_name(self, app, mock_auth_context):
        """Test staff creation with empty name fails."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/staff",
                json={
                    "name": "",  # Empty name
                    "phone": "+1234567890",
                    "role": "stylist",
                }
            )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()
    
    async def test_create_staff_invalid_phone(self, app, mock_auth_context):
        """Test staff creation with invalid phone fails."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/staff",
                json={
                    "name": "John Doe",
                    "phone": "invalid",  # Invalid phone
                    "role": "stylist",
                }
            )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()


# ============================================================================
# Multi-Tenant Isolation Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestStaffMultiTenant:
    """Test multi-tenant isolation for staff."""
    
    async def test_get_staff_wrong_salon(self, app, mock_auth_context, mock_skills, mock_availability, mock_commission):
        """Test access denied for staff from different salon."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        # Staff from different salon
        wrong_staff = Staff(
            id="staff_002",
            salon_id="salon_002",  # Different salon
            name="Jane Doe",
            phone="+0987654321",
            role=StaffRole.STYLIST,
            is_active=True,
            skills=mock_skills,
            availability=mock_availability,
            salary_type=SalaryType.COMMISSION,
            commission_config=mock_commission,
            joining_date=date(2020, 1, 15),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        with patch('app.api.staff.StaffModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=wrong_staff)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/staff/staff_002")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
