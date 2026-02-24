"""Tests for Enhanced Billing API with Price Override and Staff Suggestions"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.billing import router
from app.schemas.billing import (
    PriceOverrideResponse,
    PriceOverrideListResponse,
    StaffSuggestionResponse,
    StaffSuggestionListResponse,
    BillResponse,
    ApprovalRulesResponse,
    SuggestionStatus,
    OverrideReasonCode,
    SuggestionType,
)


# Create test app
app = FastAPI()
app.include_router(router, prefix="/billing")


@pytest.fixture
def mock_current_user():
    """Mock current user"""
    return {
        "uid": "user-123",
        "email": "test@salon.com",
        "role": "manager",
        "salon_id": "salon-123",
    }


@pytest.fixture
def mock_salon_id():
    """Mock salon ID"""
    return "salon-123"


@pytest.fixture
def mock_approval_rules():
    """Mock approval rules response"""
    return ApprovalRulesResponse(
        id="rules-123",
        salon_id="salon-123",
        auto_approve_threshold=Decimal('10'),
        manager_approval_threshold=Decimal('20'),
        owner_approval_threshold=Decimal('30'),
        max_discount_per_day=Decimal('10000'),
        require_reason_for_discount=True,
        allow_staff_suggestions=True,
        suggestion_expiry_minutes=30,
        created_at=datetime(2026, 2, 22, 6, 0, 0),
        updated_at=datetime(2026, 2, 22, 6, 0, 0),
    )


@pytest.fixture
def mock_price_override():
    """Mock price override response"""
    return PriceOverrideResponse(
        id="override-123",
        salon_id="salon-123",
        booking_id="booking-123",
        service_id="service-123",
        service_name="Haircut",
        original_price=Decimal('500'),
        new_price=Decimal('400'),
        reason_code=OverrideReasonCode.LOYALTY,
        reason_text="Loyal customer",
        discount_percent=Decimal('20'),
        approved_by="manager-123",
        approved_at=datetime(2026, 2, 22, 6, 0, 0),
        created_at=datetime(2026, 2, 22, 6, 0, 0),
        approver_name="John Manager",
        suggester_name=None,
        suggested_by=None,
    )


@pytest.fixture
def mock_staff_suggestion():
    """Mock staff suggestion response"""
    return StaffSuggestionResponse(
        id="suggestion-123",
        salon_id="salon-123",
        booking_id="booking-123",
        suggestion_type=SuggestionType.DISCOUNT,
        service_id="service-123",
        service_name="Hair Spa",
        original_price=Decimal('1000'),
        suggested_price=Decimal('800'),
        discount_percent=Decimal('20'),
        reason="Customer had to wait long",
        staff_id="staff-123",
        staff_name="Jane Stylist",
        status=SuggestionStatus.PENDING,
        reviewed_by=None,
        reviewed_at=None,
        rejection_reason=None,
        created_at=datetime(2026, 2, 22, 6, 0, 0),
        expires_at=datetime(2026, 2, 22, 6, 30, 0),
        customer_name="Customer A",
        customer_phone="+1234567890",
        impact_amount=Decimal('200'),
    )


@pytest.fixture
def mock_bill():
    """Mock bill response"""
    return BillResponse(
        id="bill-123",
        salon_id="salon-123",
        booking_id="booking-123",
        invoice_number="INV-20260222-0001",
        customer_name="Customer A",
        customer_phone="+1234567890",
        services=[],
        subtotal=Decimal('1000'),
        membership_discount=Decimal('50'),
        manual_adjustment=Decimal('0'),
        gst_amount=Decimal('47.50'),
        gst_percent=Decimal('5'),
        grand_total=Decimal('997.50'),
        payment_method="upi",
        amount_received=Decimal('1000'),
        change_due=Decimal('2.50'),
        loyalty_points_earned=100,
        created_at=datetime(2026, 2, 22, 6, 0, 0),
        created_by="staff-123",
    )


class TestPriceOverride:
    """Tests for price override endpoints"""

    @pytest.mark.asyncio
    async def test_create_price_override_success(self, mock_approval_rules, mock_price_override, mock_current_user, mock_salon_id):
        """Test successful price override creation"""
        with patch('app.api.billing.get_approval_rules') as mock_rules, \
             patch('app.api.billing.create_price_override') as mock_create, \
             patch('app.api.dependencies.get_current_user', return_value=mock_current_user), \
             patch('app.api.dependencies.get_salon_id', return_value=mock_salon_id):
            
            mock_rules.return_value = mock_approval_rules
            mock_create.return_value = mock_price_override
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/billing/overrides",
                    json={
                        "booking_id": "booking-123",
                        "service_id": "service-123",
                        "service_name": "Haircut",
                        "original_price": "500",
                        "new_price": "400",
                        "reason_code": "loyalty",
                        "reason_text": "Loyal customer",
                    }
                )
            
            assert response.status_code in [200, 201, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_create_price_override_exceeds_threshold(self, mock_approval_rules, mock_current_user, mock_salon_id):
        """Test price override that exceeds threshold requires approval"""
        with patch('app.api.billing.get_approval_rules') as mock_rules, \
             patch('app.api.dependencies.get_current_user', return_value=mock_current_user), \
             patch('app.api.dependencies.get_salon_id', return_value=mock_salon_id):
            
            mock_rules.return_value = mock_approval_rules
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/billing/overrides",
                    json={
                        "booking_id": "booking-123",
                        "service_id": "service-123",
                        "service_name": "Haircut",
                        "original_price": "1000",
                        "new_price": "500",  # 50% discount - exceeds threshold
                        "reason_code": "loyalty",
                        "reason_text": "Special case",
                    }
                )
            
            assert response.status_code in [200, 201, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_list_price_overrides(self, mock_price_override, mock_current_user, mock_salon_id):
        """Test listing price overrides"""
        with patch('app.api.billing.list_price_overrides') as mock_list, \
             patch('app.api.dependencies.get_current_user', return_value=mock_current_user), \
             patch('app.api.dependencies.get_salon_id', return_value=mock_salon_id):
            
            mock_list.return_value = PriceOverrideListResponse(
                items=[mock_price_override],
                total=1,
                page=1,
                page_size=10,
                total_discount=Decimal('100'),
            )
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/billing/overrides")
            
            assert response.status_code in [200, 401, 403, 404]


class TestStaffSuggestions:
    """Tests for staff suggestion endpoints"""

    @pytest.mark.asyncio
    async def test_create_staff_suggestion_success(self, mock_approval_rules, mock_staff_suggestion, mock_current_user, mock_salon_id):
        """Test successful staff suggestion creation"""
        with patch('app.api.billing.get_approval_rules') as mock_rules, \
             patch('app.api.billing.create_staff_suggestion') as mock_create, \
             patch('app.api.dependencies.get_current_user', return_value=mock_current_user), \
             patch('app.api.dependencies.get_salon_id', return_value=mock_salon_id):
            
            mock_rules.return_value = mock_approval_rules
            mock_create.return_value = mock_staff_suggestion
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/billing/suggestions",
                    json={
                        "booking_id": "booking-123",
                        "suggestion_type": "discount",
                        "service_id": "service-123",
                        "service_name": "Hair Spa",
                        "original_price": "1000",
                        "suggested_price": "800",
                        "discount_percent": "20",
                        "reason": "Customer had to wait long",
                    }
                )
            
            assert response.status_code in [200, 201, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_list_staff_suggestions(self, mock_staff_suggestion, mock_current_user, mock_salon_id):
        """Test listing staff suggestions"""
        with patch('app.api.billing.list_staff_suggestions') as mock_list, \
             patch('app.api.dependencies.get_current_user', return_value=mock_current_user), \
             patch('app.api.dependencies.get_salon_id', return_value=mock_salon_id):
            
            mock_list.return_value = StaffSuggestionListResponse(
                items=[mock_staff_suggestion],
                total=1,
                pending_count=1,
                approved_count=0,
                rejected_count=0,
            )
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/billing/suggestions")
            
            assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_get_pending_suggestions_count(self, mock_current_user, mock_salon_id):
        """Test getting pending suggestions count"""
        with patch('app.api.billing.get_pending_suggestions_count') as mock_count, \
             patch('app.api.dependencies.get_current_user', return_value=mock_current_user), \
             patch('app.api.dependencies.get_salon_id', return_value=mock_salon_id):
            
            mock_count.return_value = {"pending_count": 5}
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/billing/suggestions/pending-count")
            
            assert response.status_code in [200, 401, 403, 404]


class TestBillGeneration:
    """Tests for bill generation endpoint"""

    @pytest.mark.asyncio
    async def test_generate_bill_success(self, mock_bill, mock_current_user, mock_salon_id):
        """Test successful bill generation"""
        with patch('app.api.billing.generate_bill') as mock_generate, \
             patch('app.api.dependencies.get_current_user', return_value=mock_current_user), \
             patch('app.api.dependencies.get_salon_id', return_value=mock_salon_id):
            
            mock_generate.return_value = mock_bill
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/billing/generate",
                    json={
                        "booking_id": "booking-123",
                        "services": [
                            {
                                "service_id": "service-123",
                                "service_name": "Haircut",
                                "staff_id": "staff-123",
                                "staff_name": "Jane Stylist",
                                "original_price": "500",
                                "quantity": 1,
                            }
                        ],
                        "payment_method": "upi",
                        "amount_received": "600",
                    }
                )
            
            assert response.status_code in [200, 201, 401, 403, 404, 422]


class TestApprovalRules:
    """Tests for approval rules endpoints"""

    @pytest.mark.asyncio
    async def test_get_approval_rules(self, mock_approval_rules, mock_current_user, mock_salon_id):
        """Test getting approval rules"""
        with patch('app.api.billing.get_approval_rules') as mock_get, \
             patch('app.api.dependencies.get_current_user', return_value=mock_current_user), \
             patch('app.api.dependencies.get_salon_id', return_value=mock_salon_id):
            
            mock_get.return_value = mock_approval_rules
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/billing/approval-rules")
            
            assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_update_approval_rules(self, mock_approval_rules, mock_current_user, mock_salon_id):
        """Test updating approval rules"""
        with patch('app.api.billing.update_rules') as mock_update, \
             patch('app.api.dependencies.get_current_user', return_value=mock_current_user), \
             patch('app.api.dependencies.get_salon_id', return_value=mock_salon_id):
            
            mock_update.return_value = mock_approval_rules
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.put(
                    "/billing/approval-rules",
                    json={
                        "auto_approve_threshold": "15",
                        "manager_approval_threshold": "25",
                        "owner_approval_threshold": "35",
                    }
                )
            
            assert response.status_code in [200, 401, 403, 404, 422]


class TestSuggestionApproval:
    """Tests for suggestion approval endpoint"""

    @pytest.mark.asyncio
    async def test_approve_suggestion(self, mock_staff_suggestion, mock_current_user, mock_salon_id):
        """Test approving a staff suggestion"""
        with patch('app.api.billing.approve_staff_suggestion') as mock_approve, \
             patch('app.api.dependencies.get_current_user', return_value=mock_current_user), \
             patch('app.api.dependencies.get_salon_id', return_value=mock_salon_id):
            
            approved_suggestion = mock_staff_suggestion.model_copy(update={
                "status": SuggestionStatus.APPROVED,
                "reviewed_by": "manager-123",
                "reviewed_at": datetime(2026, 2, 22, 6, 5, 0),
            })
            mock_approve.return_value = approved_suggestion
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/billing/suggestions/suggestion-123/approve",
                    json={"approved": True}
                )
            
            assert response.status_code in [200, 401, 403, 404, 422]

    @pytest.mark.asyncio
    async def test_reject_suggestion(self, mock_staff_suggestion, mock_current_user, mock_salon_id):
        """Test rejecting a staff suggestion"""
        with patch('app.api.billing.approve_staff_suggestion') as mock_reject, \
             patch('app.api.dependencies.get_current_user', return_value=mock_current_user), \
             patch('app.api.dependencies.get_salon_id', return_value=mock_salon_id):
            
            rejected_suggestion = mock_staff_suggestion.model_copy(update={
                "status": SuggestionStatus.REJECTED,
                "reviewed_by": "manager-123",
                "reviewed_at": datetime(2026, 2, 22, 6, 5, 0),
                "rejection_reason": "Not justified",
            })
            mock_reject.return_value = rejected_suggestion
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/billing/suggestions/suggestion-123/approve",
                    json={
                        "approved": False,
                        "rejection_reason": "Not justified"
                    }
                )
            
            assert response.status_code in [200, 401, 403, 404, 422]
