"""
Tests for Customer API endpoints.

Covers:
- Customer CRUD operations
- Loyalty points (earn/redeem)
- Booking history
- Membership tracking
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date
from decimal import Decimal

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.api.customers import router, LoyaltyEarnRequest, LoyaltyRedeemRequest, LoyaltyBalanceResponse
from app.schemas import (
    CustomerCreate,
    CustomerUpdate,
    Customer,
    CustomerSummary,
    LoyaltyTransaction,
    LoyaltyTransactionType,
    LoyaltyReferenceType,
    Membership,
    BookingSummary,
    PaginatedResponse,
    Gender,
    MembershipStatus,
    MembershipPlanType,
    BookingStatus,
)


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
    context = MagicMock()
    context.uid = "user_001"
    context.email = "test@salon.com"
    context.role = "receptionist"
    context.salon_id = "salon_001"
    return context


@pytest.fixture
def mock_customer():
    """Sample customer object."""
    return Customer(
        customer_id="customer_001",
        salon_id="salon_001",
        name="John Doe",
        phone="9876543210",
        email="john@example.com",
        gender=Gender.MALE,
        date_of_birth="1990-01-15",
        loyalty_points_balance=150,
        loyalty_points_earned=200,
        loyalty_points_redeemed=50,
        loyalty_points_expired=0,
        total_visits=10,
        total_spent=Decimal("15000.0"),
        membership_status=MembershipStatus.ACTIVE,
        is_active=True,
        tags=["vip", "regular"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_customer_summary():
    """Sample customer summary."""
    return CustomerSummary(
        customer_id="customer_001",
        salon_id="salon_001",
        name="John Doe",
        phone="9876543210",
        email="john@example.com",
        gender=Gender.MALE,
        total_visits=10,
        total_spent=Decimal("15000.0"),
        loyalty_points_balance=150,
        membership_status=MembershipStatus.ACTIVE,
        last_visit=datetime.now(),
        tags=["vip"],
        is_active=True,
    )


@pytest.fixture
def mock_booking_summary():
    """Sample booking summary."""
    from datetime import time as time_type
    return BookingSummary(
        id="booking_001",
        salon_id="salon_001",
        customer_name="John Doe",
        customer_phone="9876543210",
        service_name="Haircut",
        staff_name="Stylist A",
        booking_date=date.today(),
        start_time=time_type(10, 0),
        status=BookingStatus.COMPLETED,
        service_price=Decimal("500.0"),
    )


@pytest.fixture
def mock_loyalty_transaction():
    """Sample loyalty transaction."""
    return LoyaltyTransaction(
        id="txn_001",
        customer_id="customer_001",
        salon_id="salon_001",
        transaction_type=LoyaltyTransactionType.EARN,
        points=50,
        balance_after=150,
        reference_type=LoyaltyReferenceType.BOOKING,
        reference_id="booking_001",
        customer_name="John Doe",
        customer_phone="9876543210",
        description="Points earned from booking",
        created_at=datetime.now(),
    )


# ============================================================================
# Customer List Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestCustomerList:
    """Test customer listing."""

    async def test_list_customers_success(self, app, mock_auth_context, mock_customer_summary):
        """Test successful customer listing."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.customers.CustomerModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[mock_customer_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/customers")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1

        app.dependency_overrides.clear()

    async def test_list_customers_empty(self, app, mock_auth_context):
        """Test empty customer list."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.customers.CustomerModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[],
                total=0,
                page=1,
                page_size=20,
                pages=0,
            ))
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/customers")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

        app.dependency_overrides.clear()


# ============================================================================
# Customer Create Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestCustomerCreate:
    """Test customer creation."""

    async def test_create_customer_success(self, app, mock_auth_context, mock_customer):
        """Test successful customer creation."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.customers.CustomerModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get_by_phone = AsyncMock(return_value=None)  # No existing customer
            mock_instance.create = AsyncMock(return_value=mock_customer)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post("/customers", json={
                    "name": "John Doe",
                    "phone": "9876543210",
                    "email": "john@example.com",
                    "gender": "male",
                })

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"

        app.dependency_overrides.clear()

    async def test_create_customer_duplicate_phone(self, app, mock_auth_context):
        """Test duplicate phone returns 400."""
        from app.api.dependencies import get_current_user, get_salon_id
        from fastapi import HTTPException

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.customers.CustomerModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.create = AsyncMock(side_effect=ValueError("Phone already exists"))
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post("/customers", json={
                    "name": "John Doe",
                    "phone": "9876543210",
                    "gender": "male",
                })

        assert response.status_code == 400

        app.dependency_overrides.clear()


# ============================================================================
# Customer Get Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestCustomerGet:
    """Test customer retrieval."""

    async def test_get_customer_success(self, app, mock_auth_context, mock_customer):
        """Test successful customer retrieval."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        # Patch verify_customer_access at the location where it's used
        with patch('app.api.customers.verify_customer_access', return_value=mock_customer):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/customers/customer_001")

        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "customer_001"
        assert data["name"] == "John Doe"

        app.dependency_overrides.clear()

    async def test_get_customer_not_found(self, app, mock_auth_context):
        """Test customer not found returns 404."""
        from app.api.dependencies import get_current_user, get_salon_id
        from fastapi import HTTPException, status

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.customers.verify_customer_access') as mock_verify:
            mock_verify.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Customer not found", "code": "customer_not_found"}
            )

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/customers/nonexistent")

        assert response.status_code == 404

        app.dependency_overrides.clear()

    async def test_get_customer_wrong_salon(self, app, mock_auth_context):
        """Test access denied for customer from different salon."""
        from app.api.dependencies import get_current_user, get_salon_id
        from fastapi import HTTPException, status

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.customers.verify_customer_access') as mock_verify:
            mock_verify.side_effect = HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"message": "Access denied", "code": "access_denied"}
            )

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/customers/customer_002")

        assert response.status_code == 403

        app.dependency_overrides.clear()


# ============================================================================
# Customer Update Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestCustomerUpdate:
    """Test customer update."""

    async def test_update_customer_success(self, app, mock_auth_context, mock_customer):
        """Test successful customer update."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        updated_customer = mock_customer.model_copy(update={"name": "Jane Doe"})

        with patch('app.api.customers.verify_customer_access', return_value=mock_customer):
            with patch('app.api.customers.CustomerModel') as MockModel:
                mock_instance = AsyncMock()
                mock_instance.update = AsyncMock(return_value=updated_customer)
                MockModel.return_value = mock_instance

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.put("/customers/customer_001", json={
                        "name": "Jane Doe",
                    })

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Doe"

        app.dependency_overrides.clear()


# ============================================================================
# Customer Delete Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestCustomerDelete:
    """Test customer deletion."""

    async def test_delete_customer_success(self, app, mock_auth_context, mock_customer):
        """Test successful customer deletion."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.customers.verify_customer_access', return_value=mock_customer):
            with patch('app.api.customers.CustomerModel') as MockModel:
                mock_instance = AsyncMock()
                mock_instance.delete = AsyncMock(return_value=True)
                MockModel.return_value = mock_instance

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.delete("/customers/customer_001")

        assert response.status_code == 204

        app.dependency_overrides.clear()


# ============================================================================
# Customer Bookings Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestCustomerBookings:
    """Test customer booking history."""

    async def test_get_customer_bookings_success(self, app, mock_auth_context, mock_customer, mock_booking_summary):
        """Test successful booking history retrieval."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.customers.verify_customer_access', return_value=mock_customer):
            with patch('app.api.customers.BookingModel') as MockModel:
                mock_instance = AsyncMock()
                mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                    items=[mock_booking_summary],
                    total=1,
                    page=1,
                    page_size=20,
                    pages=1,
                ))
                MockModel.return_value = mock_instance

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get("/customers/customer_001/bookings")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

        app.dependency_overrides.clear()


# ============================================================================
# Loyalty Points Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestLoyaltyPoints:
    """Test loyalty points operations."""

    async def test_get_loyalty_balance_success(self, app, mock_auth_context, mock_customer):
        """Test successful loyalty balance retrieval."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.customers.verify_customer_access', return_value=mock_customer):
            with patch('app.api.customers.LoyaltyModel') as MockModel:
                mock_instance = AsyncMock()
                mock_instance.get_customer_balance = AsyncMock(return_value={
                    "total_points": 200,
                    "available_points": 150,
                    "pending_points": 0,
                    "expired_points": 0,
                    "tier": "silver",
                    "next_tier_points": 100,
                })
                MockModel.return_value = mock_instance

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get("/customers/customer_001/loyalty")

        assert response.status_code == 200
        data = response.json()
        assert data["available_points"] == 150

        app.dependency_overrides.clear()

    async def test_earn_loyalty_points_success(self, app, mock_auth_context, mock_customer, mock_loyalty_transaction):
        """Test successful loyalty points earning."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.customers.verify_customer_access', return_value=mock_customer):
            with patch('app.api.customers.LoyaltyModel') as MockModel:
                mock_instance = AsyncMock()
                mock_instance.create = AsyncMock(return_value=mock_loyalty_transaction)
                MockModel.return_value = mock_instance

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post("/customers/customer_001/loyalty/earn", json={
                        "amount": 500,
                        "booking_id": "booking_001",
                    })

        assert response.status_code == 201

        app.dependency_overrides.clear()

    async def test_earn_loyalty_points_low_amount(self, app, mock_auth_context, mock_customer):
        """Test earning points with low amount returns 400."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.customers.verify_customer_access', return_value=mock_customer):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post("/customers/customer_001/loyalty/earn", json={
                    "amount": 5,  # Too low (less than 10)
                    "booking_id": "booking_001",
                })

        assert response.status_code == 400

        app.dependency_overrides.clear()

    async def test_redeem_loyalty_points_success(self, app, mock_auth_context, mock_customer, mock_loyalty_transaction):
        """Test successful loyalty points redemption."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.customers.verify_customer_access', return_value=mock_customer):
            with patch('app.api.customers.LoyaltyModel') as MockModel:
                mock_instance = AsyncMock()
                mock_instance.get_customer_balance = AsyncMock(return_value={
                    "available_points": 150,
                })
                mock_instance.create = AsyncMock(return_value=mock_loyalty_transaction)
                MockModel.return_value = mock_instance

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post("/customers/customer_001/loyalty/redeem", json={
                        "points": 50,
                        "booking_id": "booking_001",
                    })

        assert response.status_code == 201

        app.dependency_overrides.clear()

    async def test_redeem_loyalty_points_insufficient(self, app, mock_auth_context, mock_customer):
        """Test redeeming more points than available returns 400."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch('app.api.customers.verify_customer_access', return_value=mock_customer):
            with patch('app.api.customers.LoyaltyModel') as MockModel:
                mock_instance = AsyncMock()
                mock_instance.get_customer_balance = AsyncMock(return_value={
                    "available_points": 150,
                })
                MockModel.return_value = mock_instance

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post("/customers/customer_001/loyalty/redeem", json={
                        "points": 1000,  # More than balance (150)
                        "booking_id": "booking_001",
                    })

        assert response.status_code == 400

        app.dependency_overrides.clear()
