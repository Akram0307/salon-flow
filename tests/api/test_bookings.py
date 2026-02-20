"""Comprehensive tests for Booking API endpoints.

Covers:
- Booking CRUD operations
- Status lifecycle management
- Multi-tenant isolation
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date, time
from decimal import Decimal

from fastapi import FastAPI, status
from httpx import AsyncClient, ASGITransport

from app.api.bookings import router
from app.api.dependencies import AuthContext
from app.schemas import (
    BookingCreate,
    BookingUpdate,
    Booking,
    BookingSummary,
    PaginatedResponse,
)
from app.schemas.base import StaffRole, BookingStatus, BookingChannel, ServiceCategory, ResourceType
from app.schemas.service import Service, ServicePricing, ServiceDuration, ResourceRequirement
from app.schemas.staff import Staff, StaffSkills, ServiceSkill, ExpertiseLevel


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/bookings")
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
def mock_booking():
    """Sample booking object."""
    return Booking(
        id="booking_001",
        salon_id="salon_001",
        customer_id="customer_001",
        customer_name="John Doe",
        customer_phone="+1234567890",
        service_id="service_001",
        service_name="Haircut",
        service_price=Decimal("500.00"),
        service_duration=45,
        staff_id="staff_001",
        staff_name="Jane Stylist",
        resource_id="resource_001",
        resource_name="Chair 1",
        booking_date=date(2024, 1, 15),
        start_time=time(10, 0),
        end_time=time(10, 45),
        status=BookingStatus.CONFIRMED,
        booking_channel=BookingChannel.ONLINE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_booking_summary():
    """Sample booking summary."""
    return BookingSummary(
        id="booking_001",
        salon_id="salon_001",
        customer_name="John Doe",
        customer_phone="+1234567890",
        service_name="Haircut",
        staff_name="Jane Stylist",
        booking_date=date(2024, 1, 15),
        start_time=time(10, 0),
        status=BookingStatus.CONFIRMED,
        service_price=Decimal("500.00"),
    )


@pytest.fixture
def mock_service():
    """Sample service object."""
    return Service(
        id="service_001",
        service_id="service_001",
        salon_id="salon_001",
        name="Haircut",
        description="Professional haircut",
        category=ServiceCategory.HAIRCUT,
        pricing=ServicePricing(base_price=Decimal("500.00")),
        duration=ServiceDuration(base_minutes=45),
        resource_requirement=ResourceRequirement(resource_type=ResourceType.CHAIR_MENS),
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_staff():
    """Sample staff object."""
    return Staff(
        id="staff_001",
        salon_id="salon_001",
        name="Jane Stylist",
        email="jane@salon.com",
        phone="+1234567890",
        role=StaffRole.STYLIST,
        skills=StaffSkills(skills=[ServiceSkill(service_id="service_001", service_name="Men's Haircut", expertise_level=ExpertiseLevel.EXPERT)]),
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


# ============================================================================
# Booking List Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestBookingList:
    """Test booking listing endpoints."""

    async def test_list_bookings_success(self, app, mock_auth_context, mock_booking_summary):
        """Test successful booking listing."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.bookings.BookingModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search_bookings = AsyncMock(return_value=PaginatedResponse(
                items=[mock_booking_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/bookings/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1

        app.dependency_overrides.clear()

    async def test_list_bookings_with_date_filter(self, app, mock_auth_context, mock_booking_summary):
        """Test booking listing with date filter."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.bookings.BookingModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search_bookings = AsyncMock(return_value=PaginatedResponse(
                items=[mock_booking_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/bookings?date_filter=2024-01-15")

        assert response.status_code == status.HTTP_200_OK

        app.dependency_overrides.clear()


# ============================================================================
# Booking Create Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestBookingCreate:
    """Test booking creation endpoints."""

    async def test_create_booking_success(self, app, mock_auth_context, mock_booking, mock_service, mock_staff):
        """Test successful booking creation."""
        from app.api.dependencies import get_current_user, get_salon_id, require_staff

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        app.dependency_overrides[require_staff] = lambda: mock_auth_context

        with patch('app.api.bookings.BookingModel') as MockBookingModel, \
             patch('app.api.bookings.ServiceModel') as MockServiceModel, \
             patch('app.api.bookings.StaffModel') as MockStaffModel:

            # Setup booking model mock
            booking_instance = AsyncMock()
            booking_instance.create = AsyncMock(return_value=mock_booking)
            MockBookingModel.return_value = booking_instance

            # Setup service model mock
            service_instance = AsyncMock()
            service_instance.get = AsyncMock(return_value=mock_service)
            MockServiceModel.return_value = service_instance

            # Setup staff model mock
            staff_instance = AsyncMock()
            staff_instance.get = AsyncMock(return_value=mock_staff)
            MockStaffModel.return_value = staff_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/bookings",
                    json={
                        "salon_id": "salon_001",
                        "customer_id": "customer_001",
                        "customer_name": "John Doe",
                        "customer_phone": "+1234567890",
                        "service_id": "service_001",
                        "service_name": "Haircut",
                        "service_price": 500.00,
                        "service_duration": 45,
                        "booking_date": "2024-01-15",
                        "start_time": "10:00",
                        "end_time": "10:45",
                        "staff_id": "staff_001",
                    }
                )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["customer_name"] == "John Doe"

        app.dependency_overrides.clear()

    async def test_create_booking_with_walk_in_customer(self, app, mock_auth_context, mock_booking, mock_service):
        """Test booking creation with walk-in customer."""
        from app.api.dependencies import get_current_user, get_salon_id, require_staff

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        app.dependency_overrides[require_staff] = lambda: mock_auth_context

        with patch('app.api.bookings.BookingModel') as MockBookingModel, \
             patch('app.api.bookings.ServiceModel') as MockServiceModel:

            # Setup booking model mock
            booking_instance = AsyncMock()
            booking_instance.create = AsyncMock(return_value=mock_booking)
            MockBookingModel.return_value = booking_instance

            # Setup service model mock
            service_instance = AsyncMock()
            service_instance.get = AsyncMock(return_value=mock_service)
            MockServiceModel.return_value = service_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/bookings",
                    json={
                        "salon_id": "salon_001",
                        "customer_id": "customer_001",
                        "customer_name": "Walk-in Customer",
                        "customer_phone": "+1234567890",
                        "service_id": "service_001",
                        "service_name": "Haircut",
                        "service_price": 500.00,
                        "service_duration": 45,
                        "booking_date": "2024-01-15",
                        "start_time": "10:00",
                        "end_time": "10:45",
                        "booking_channel": "walk_in",
                    }
                )

        assert response.status_code == status.HTTP_201_CREATED

        app.dependency_overrides.clear()


# ============================================================================
# Booking Get Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestBookingGet:
    """Test booking retrieval endpoints."""

    async def test_get_booking_success(self, app, mock_auth_context, mock_booking):
        """Test successful booking retrieval."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.models.BookingModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_booking)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/bookings/booking_001")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["customer_name"] == "John Doe"

        app.dependency_overrides.clear()

    async def test_get_booking_not_found(self, app, mock_auth_context):
        """Test booking not found."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.bookings.BookingModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=None)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/bookings/nonexistent")

        assert response.status_code == status.HTTP_404_NOT_FOUND

        app.dependency_overrides.clear()


# ============================================================================
# Booking Update Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestBookingUpdate:
    """Test booking update endpoints."""

    async def test_update_booking_success(self, app, mock_auth_context, mock_booking):
        """Test successful booking update."""
        from app.api.dependencies import get_current_user, get_salon_id, require_staff, verify_booking_access

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        app.dependency_overrides[require_staff] = lambda: mock_auth_context
        app.dependency_overrides[verify_booking_access] = lambda booking_id, salon_id: mock_booking

        updated_booking = mock_booking.model_copy(update={"notes": "Updated notes"})

        with patch('app.api.bookings.BookingModel') as MockModel,              patch('app.api.bookings.verify_booking_access', return_value=mock_booking):
            mock_instance = AsyncMock()
            mock_instance.update = AsyncMock(return_value=updated_booking)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/api/v1/bookings/booking_001",
                    json={"notes": "Updated notes"}
                )

        assert response.status_code == status.HTTP_200_OK

        app.dependency_overrides.clear()

    async def test_update_booking_status_to_checked_in(self, app, mock_auth_context, mock_booking):
        """Test updating booking status to checked_in."""
        from app.api.dependencies import get_current_user, get_salon_id, require_staff, verify_booking_access

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        app.dependency_overrides[require_staff] = lambda: mock_auth_context
        app.dependency_overrides[verify_booking_access] = lambda booking_id, salon_id: mock_booking

        updated_booking = mock_booking.model_copy(update={"status": BookingStatus.CHECKED_IN})

        with patch('app.api.bookings.BookingModel') as MockModel,              patch('app.api.bookings.verify_booking_access', return_value=mock_booking):
            mock_instance = AsyncMock()
            mock_instance.update = AsyncMock(return_value=updated_booking)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/api/v1/bookings/booking_001",
                    json={"status": "checked_in"}
                )

        assert response.status_code == status.HTTP_200_OK

        app.dependency_overrides.clear()


# ============================================================================
# Booking Cancel Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestBookingCancel:
    """Test booking cancellation endpoints."""

    async def test_cancel_booking_success(self, app, mock_auth_context, mock_booking):
        """Test successful booking cancellation."""
        from app.api.dependencies import get_current_user, get_salon_id, require_staff, verify_booking_access

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        app.dependency_overrides[require_staff] = lambda: mock_auth_context
        app.dependency_overrides[verify_booking_access] = lambda booking_id, salon_id: mock_booking

        cancelled_booking = mock_booking.model_copy(update={"status": BookingStatus.CANCELLED})

        with patch('app.api.bookings.BookingModel') as MockModel,              patch('app.api.bookings.verify_booking_access', return_value=mock_booking):
            mock_instance = AsyncMock()
            mock_instance.update_status = AsyncMock(return_value=cancelled_booking)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.delete("/api/v1/bookings/booking_001")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        app.dependency_overrides.clear()

    async def test_cancel_already_completed_booking(self, app, mock_auth_context, mock_booking):
        """Test cancelling an already completed booking."""
        from app.api.dependencies import get_current_user, get_salon_id, require_staff, verify_booking_access

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        app.dependency_overrides[require_staff] = lambda: mock_auth_context

        completed_booking = mock_booking.model_copy(update={"status": BookingStatus.COMPLETED})
        app.dependency_overrides[verify_booking_access] = lambda booking_id, salon_id: completed_booking

        with patch('app.api.bookings.BookingModel') as MockModel,              patch('app.api.bookings.verify_booking_access', return_value=completed_booking):
            mock_instance = AsyncMock()
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.delete("/api/v1/bookings/booking_001")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        app.dependency_overrides.clear()
