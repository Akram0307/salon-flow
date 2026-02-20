"""Comprehensive tests for Shift API endpoints.

Covers:
- Shift CRUD operations
- Scheduling operations
- Multi-tenant isolation
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date, time
from decimal import Decimal

from fastapi import FastAPI, status
from httpx import AsyncClient, ASGITransport

from app.api.shifts import router
from app.api.dependencies import AuthContext
from app.schemas import (
    ShiftCreate,
    ShiftUpdate,
    Shift,
    ShiftSummary,
    PaginatedResponse,
)
from app.schemas.shift import ShiftType, ShiftStatus
from app.schemas.base import StaffRole


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/shifts")
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
def mock_shift():
    """Sample shift object."""
    return Shift(
        id="shift_001",
        salon_id="salon_001",
        staff_id="staff_001",
        shift_date=date(2024, 1, 15),
        start_time=time(9, 0),
        end_time=time(18, 0),
        shift_type=ShiftType.FULL_DAY,
        status=ShiftStatus.SCHEDULED,
        is_off_day=False,
        notes="Regular shift",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_shift_summary():
    """Sample shift summary."""
    return ShiftSummary(
        id="shift_001",
        salon_id="salon_001",
        staff_id="staff_001",
        shift_date=date(2024, 1, 15),
        start_time=time(9, 0),
        end_time=time(18, 0),
        status=ShiftStatus.SCHEDULED,
    )


# ============================================================================
# Shift List Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestShiftList:
    """Test shift listing endpoints."""
    
    async def test_list_shifts_success(self, app, mock_auth_context, mock_shift_summary):
        """Test successful shift listing."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.shifts.ShiftModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[mock_shift_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/shifts/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        
        app.dependency_overrides.clear()
    
    async def test_list_shifts_with_date_filter(self, app, mock_auth_context, mock_shift_summary):
        """Test shift listing with date filter."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.shifts.ShiftModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[mock_shift_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/shifts?shift_date=2024-01-15")
        
        assert response.status_code == status.HTTP_200_OK
        
        app.dependency_overrides.clear()


# ============================================================================
# Shift Create Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestShiftCreate:
    """Test shift creation."""
    
    async def test_create_shift_success(self, app, mock_auth_context, mock_shift):
        """Test successful shift creation."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.shifts.ShiftModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.create = AsyncMock(return_value=mock_shift)
            mock_instance.check_overlap = AsyncMock(return_value=False)  # No overlap
            MockModel.return_value = mock_instance
            
            # Mock StaffModel to return a valid staff member
            with patch('app.api.shifts.StaffModel') as MockStaff:
                mock_staff_instance = AsyncMock()
                mock_staff = AsyncMock()
                mock_staff.salon_id = "salon_001"
                mock_staff_instance.get = AsyncMock(return_value=mock_staff)
                MockStaff.return_value = mock_staff_instance
                
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/shifts",
                        json={
                            "staff_id": "staff_001",
                            "shift_date": "2024-01-15",
                            "start_time": "09:00",
                            "end_time": "18:00",
                            "shift_type": "full_day",
                        }
                    )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["staff_id"] == "staff_001"
        
        app.dependency_overrides.clear()
    
    async def test_create_shift_conflict(self, app, mock_auth_context, mock_shift):
        """Test shift creation fails with conflicting shift."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.shifts.ShiftModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.create = AsyncMock(
                side_effect=ValueError("Staff already has a shift on this date")
            )
            mock_instance.check_overlap = AsyncMock(return_value=True)  # Overlap exists
            MockModel.return_value = mock_instance
            
            # Mock StaffModel to return a valid staff member
            with patch('app.api.shifts.StaffModel') as MockStaff:
                mock_staff_instance = AsyncMock()
                mock_staff = AsyncMock()
                mock_staff.salon_id = "salon_001"
                mock_staff_instance.get = AsyncMock(return_value=mock_staff)
                MockStaff.return_value = mock_staff_instance
                
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/shifts",
                        json={
                            "staff_id": "staff_001",
                            "shift_date": "2024-01-15",
                            "start_time": "09:00",
                            "end_time": "18:00",
                            "shift_type": "full_day",
                        }
                    )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        
        app.dependency_overrides.clear()


# ============================================================================
# Shift Get Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestShiftGet:
    """Test shift retrieval."""
    
    async def test_get_shift_success(self, app, mock_auth_context, mock_shift):
        """Test successful shift retrieval."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.shifts.ShiftModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_shift)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/shifts/shift_001")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "shift_001"
        
        app.dependency_overrides.clear()
    
    async def test_get_shift_not_found(self, app, mock_auth_context):
        """Test shift not found returns 404."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.shifts.ShiftModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=None)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/shifts/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        app.dependency_overrides.clear()


# ============================================================================
# Shift Update Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestShiftUpdate:
    """Test shift update."""
    
    async def test_update_shift_success(self, app, mock_auth_context, mock_shift):
        """Test successful shift update."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        updated_shift = mock_shift.model_copy(update={"notes": "Updated notes"})
        
        with patch('app.api.shifts.ShiftModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_shift)
            mock_instance.update = AsyncMock(return_value=updated_shift)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/api/v1/shifts/shift_001",
                    json={"notes": "Updated notes"}
                )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["notes"] == "Updated notes"
        
        app.dependency_overrides.clear()
    
    async def test_cancel_shift_success(self, app, mock_auth_context, mock_shift):
        """Test successful shift cancellation."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        cancelled_shift = mock_shift.model_copy(update={"status": ShiftStatus.CANCELLED})
        
        with patch('app.api.shifts.ShiftModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_shift)
            mock_instance.update = AsyncMock(return_value=cancelled_shift)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/api/v1/shifts/shift_001",
                    json={"status": "cancelled"}
                )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "cancelled"
        
        app.dependency_overrides.clear()


# ============================================================================
# Edge Case Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestShiftEdgeCases:
    """Test edge cases for shift operations."""
    
    async def test_create_shift_invalid_time_range(self, app, mock_auth_context):
        """Test shift creation with end_time before start_time fails."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/shifts",
                json={
                    "staff_id": "staff_001",
                    "shift_date": "2024-01-15",
                    "start_time": "18:00",
                    "end_time": "09:00",  # Before start_time
                    "shift_type": "full_day",
                }
            )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()
    
    async def test_create_shift_invalid_type(self, app, mock_auth_context):
        """Test shift creation with invalid type fails."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/shifts",
                json={
                    "staff_id": "staff_001",
                    "shift_date": "2024-01-15",
                    "start_time": "09:00",
                    "end_time": "18:00",
                    "shift_type": "invalid_type",  # Invalid type
                }
            )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()


# ============================================================================
# Multi-Tenant Isolation Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestShiftMultiTenant:
    """Test multi-tenant isolation for shifts."""
    
    async def test_get_shift_wrong_salon(self, app, mock_auth_context):
        """Test access denied for shift from different salon."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        # Shift from different salon
        wrong_shift = Shift(
            id="shift_002",
            salon_id="salon_002",  # Different salon
            staff_id="staff_002",
            shift_date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(18, 0),
            shift_type=ShiftType.FULL_DAY,
            status=ShiftStatus.SCHEDULED,
            is_off_day=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        with patch('app.api.shifts.ShiftModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=wrong_shift)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/shifts/shift_002")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
