"""Comprehensive tests for Payment API endpoints.

Covers:
- Payment CRUD operations
- Payment splits and breakdowns
- Multi-tenant isolation
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date
from decimal import Decimal

from fastapi import FastAPI, status
from httpx import AsyncClient, ASGITransport

from app.api.payments import router
from app.api.dependencies import AuthContext
from app.schemas import (
    PaymentCreate,
    PaymentUpdate,
    Payment,
    PaymentSummary,
    PaymentBreakdown,
    PaymentSplit,
    PaginatedResponse,
)
from app.schemas.base import StaffRole, PaymentMethod, PaymentStatus


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI(redirect_slashes=False)
    app.include_router(router, prefix="/api/v1/payments")
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
def mock_payment():
    """Sample payment object."""
    return Payment(
        id="payment_001",
        salon_id="salon_001",
        booking_id="booking_001",
        customer_id="customer_001",
        customer_name="John Doe",
        subtotal=Decimal("1000.00"),
        gst_amount=Decimal("50.00"),
        total_amount=Decimal("1050.00"),
        discount_amount=Decimal("0.00"),
        tip_amount=Decimal("50.00"),
        payment_method=PaymentMethod.CASH,
        status=PaymentStatus.COMPLETED,
        splits=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_payment_summary():
    """Sample payment summary."""
    return PaymentSummary(
        id="payment_001",
        salon_id="salon_001",
        booking_id="booking_001",
        customer_name="John Doe",
        total_amount=Decimal("1050.00"),
        payment_method=PaymentMethod.CASH,
        payment_status=PaymentStatus.COMPLETED,
        created_at=datetime.now(),
    )


# ============================================================================
# Payment List Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestPaymentList:
    """Test payment listing endpoints."""
    
    async def test_list_payments_success(self, app, mock_auth_context, mock_payment_summary):
        """Test successful payment listing."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.payments.PaymentModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[mock_payment_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/payments/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        
        app.dependency_overrides.clear()
    
    async def test_list_payments_with_status_filter(self, app, mock_auth_context, mock_payment_summary):
        """Test payment listing with status filter."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.payments.PaymentModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[mock_payment_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/payments/?payment_status=completed")
        
        assert response.status_code == status.HTTP_200_OK
        
        app.dependency_overrides.clear()


# ============================================================================
# Payment Create Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestPaymentCreate:
    """Test payment creation."""
    
    async def test_create_payment_success(self, app, mock_auth_context, mock_payment):
        """Test successful payment creation."""
        from app.api.dependencies import require_staff, get_salon_id
        
        app.dependency_overrides[require_staff] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.payments.PaymentModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.create = AsyncMock(return_value=mock_payment)
            MockModel.return_value = mock_instance
            
            # Mock BookingModel to return a valid booking
            with patch('app.api.payments.BookingModel') as MockBooking:
                mock_booking_instance = AsyncMock()
                mock_booking = AsyncMock()
                mock_booking.salon_id = "salon_001"
                mock_booking_instance.get = AsyncMock(return_value=mock_booking)
                MockBooking.return_value = mock_booking_instance
                
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/payments/",
                        json={
                            "booking_id": "booking_001",
                            "customer_id": "customer_001",
                            "customer_name": "John Doe",
                            "subtotal": "1000.00",
                            "gst_amount": "50.00",
                            "total_amount": "1050.00",
                            "payment_method": "cash",
                        }
                    )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["booking_id"] == "booking_001"
        
        app.dependency_overrides.clear()
    
    async def test_create_payment_with_splits(self, app, mock_auth_context, mock_payment):
        """Test payment creation with split payments."""
        from app.api.dependencies import require_staff, get_salon_id
        
        app.dependency_overrides[require_staff] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        payment_with_splits = mock_payment.model_copy(update={
            "payment_method": PaymentMethod.CASH,  # Primary method
            "splits": [
                PaymentSplit(method=PaymentMethod.CASH, amount=Decimal("500.00")),
                PaymentSplit(method=PaymentMethod.UPI, amount=Decimal("550.00")),
            ]
        })
        
        with patch('app.api.payments.PaymentModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.create = AsyncMock(return_value=payment_with_splits)
            MockModel.return_value = mock_instance
            
            # Mock BookingModel to return a valid booking
            with patch('app.api.payments.BookingModel') as MockBooking:
                mock_booking_instance = AsyncMock()
                mock_booking = AsyncMock()
                mock_booking.salon_id = "salon_001"
                mock_booking_instance.get = AsyncMock(return_value=mock_booking)
                MockBooking.return_value = mock_booking_instance
                
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/payments/",
                        json={
                            "booking_id": "booking_001",
                            "customer_id": "customer_001",
                            "customer_name": "John Doe",
                            "subtotal": "1000.00",
                            "gst_amount": "50.00",
                            "total_amount": "1050.00",
                            "payment_method": "cash",
                            "splits": [
                            {"method": "cash", "amount": "500.00"},
                            {"method": "upi", "amount": "550.00"}
                        ]
                    }
                )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        app.dependency_overrides.clear()


# ============================================================================
# Payment Get Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestPaymentGet:
    """Test payment retrieval."""
    
    async def test_get_payment_success(self, app, mock_auth_context, mock_payment):
        """Test successful payment retrieval."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.payments.PaymentModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_payment)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/payments/payment_001")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "payment_001"
        
        app.dependency_overrides.clear()
    
    async def test_get_payment_not_found(self, app, mock_auth_context):
        """Test payment not found returns 404."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.payments.PaymentModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=None)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/payments/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        app.dependency_overrides.clear()


# ============================================================================
# Payment Update Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestPaymentUpdate:
    """Test payment update."""
    
    async def test_update_payment_success(self, app, mock_auth_context, mock_payment):
        """Test successful payment update."""
        from app.api.dependencies import require_staff, get_salon_id
        
        app.dependency_overrides[require_staff] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        updated_payment = mock_payment.model_copy(update={"tip_amount": Decimal("100.00")})
        
        with patch('app.api.payments.PaymentModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_payment)
            mock_instance.update = AsyncMock(return_value=updated_payment)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/api/v1/payments/payment_001",
                    json={"tip_amount": "100.00"}
                )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["tip_amount"] == 100.0
        
        app.dependency_overrides.clear()
    
    async def test_refund_payment_success(self, app, mock_auth_context, mock_payment):
        """Test successful payment refund."""
        from app.api.dependencies import require_staff, get_salon_id
        
        app.dependency_overrides[require_staff] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        refunded_payment = mock_payment.model_copy(update={"payment_status": PaymentStatus.REFUNDED})
        
        with patch('app.api.payments.PaymentModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_payment)
            mock_instance.update = AsyncMock(return_value=refunded_payment)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/api/v1/payments/payment_001",
                    json={"payment_status": "refunded"}
                )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["payment_status"] == "refunded"
        
        app.dependency_overrides.clear()


# ============================================================================
# Edge Case Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestPaymentEdgeCases:
    """Test edge cases for payment operations."""
    
    async def test_create_payment_negative_amount(self, app, mock_auth_context):
        """Test payment creation with negative amount fails."""
        from app.api.dependencies import require_staff, get_salon_id
        
        app.dependency_overrides[require_staff] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        # Mock BookingModel to return a valid booking
        with patch('app.api.payments.BookingModel') as MockBooking:
            mock_booking_instance = AsyncMock()
            mock_booking = AsyncMock()
            mock_booking.salon_id = "salon_001"
            mock_booking_instance.get = AsyncMock(return_value=mock_booking)
            MockBooking.return_value = mock_booking_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/payments/",
                    json={
                        "booking_id": "booking_001",
                        "customer_id": "customer_001",
                        "customer_name": "John Doe",
                        "subtotal": "-100.00",  # Negative amount
                        "gst_amount": "0.00",
                        "total_amount": "-100.00",
                        "payment_method": "cash",
                    }
                )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()
    
    async def test_create_payment_invalid_method(self, app, mock_auth_context):
        """Test payment creation with invalid method fails."""
        from app.api.dependencies import require_staff, get_salon_id
        
        app.dependency_overrides[require_staff] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        # Mock BookingModel to return a valid booking
        with patch('app.api.payments.BookingModel') as MockBooking:
            mock_booking_instance = AsyncMock()
            mock_booking = AsyncMock()
            mock_booking.salon_id = "salon_001"
            mock_booking_instance.get = AsyncMock(return_value=mock_booking)
            MockBooking.return_value = mock_booking_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/payments/",
                    json={
                        "booking_id": "booking_001",
                        "customer_id": "customer_001",
                        "customer_name": "John Doe",
                        "subtotal": "1000.00",
                        "gst_amount": "50.00",
                        "total_amount": "1050.00",
                        "payment_method": "invalid_method",  # Invalid method
                    }
                )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()


# ============================================================================
# Multi-Tenant Isolation Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestPaymentMultiTenant:
    """Test multi-tenant isolation for payments."""
    
    async def test_get_payment_wrong_salon(self, app, mock_auth_context):
        """Test access denied for payment from different salon."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        # Payment from different salon
        wrong_payment = Payment(
            id="payment_002",
            salon_id="salon_002",  # Different salon
            booking_id="booking_002",
            customer_id="customer_002",
            customer_name="Jane Doe",
            subtotal=Decimal("1000.00"),
            gst_amount=Decimal("50.00"),
            total_amount=Decimal("1050.00"),
            payment_method=PaymentMethod.CASH,
            status=PaymentStatus.COMPLETED,
            splits=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        with patch('app.api.payments.PaymentModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=wrong_payment)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/payments/payment_002")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
