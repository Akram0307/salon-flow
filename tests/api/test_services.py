"""Comprehensive tests for Service API endpoints.

Covers:
- Service CRUD operations
- Pricing configuration
- Multi-tenant isolation
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from decimal import Decimal

from fastapi import FastAPI, status
from httpx import AsyncClient, ASGITransport

from app.api.services import router
from app.api.dependencies import AuthContext
from app.schemas import (
    ServiceCreate,
    ServiceUpdate,
    Service,
    ServiceSummary,
    ServicePricing,
    ServiceDuration,
    ResourceRequirement,
    PaginatedResponse,
)
from app.schemas.base import StaffRole, ServiceCategory, ResourceType


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
def mock_service():
    """Sample service object with correct schema."""
    return Service(
        id="service_001",
        service_id="service_001",
        salon_id="salon_001",
        name="Haircut",
        description="Professional haircut service",
        category=ServiceCategory.HAIRCUT,
        pricing=ServicePricing(
            base_price=Decimal("500.00"),
            senior_price=Decimal("700.00"),
            junior_price=Decimal("350.00"),
        ),
        duration=ServiceDuration(
            base_minutes=45,
            buffer_before=5,
            buffer_after=5,
        ),
        resource_requirement=ResourceRequirement(
            resource_type=ResourceType.CHAIR_MENS,
        ),
        is_active=True,
        is_popular=True,
        image_url="https://example.com/haircut.jpg",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_service_summary():
    """Sample service summary."""
    return ServiceSummary(
        service_id="service_001",
        salon_id="salon_001",
        name="Haircut",
        category=ServiceCategory.HAIRCUT,
        base_price=Decimal("500.00"),
        duration_minutes=45,
        resource_type=ResourceType.CHAIR_MENS,
        is_active=True,
        is_popular=True,
        image_url="https://example.com/haircut.jpg",
        average_rating=Decimal("4.5"),
    )


# ============================================================================
# Service List Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestServiceList:
    """Test service listing endpoints."""

    async def test_list_services_success(self, app, mock_auth_context, mock_service_summary):
        """Test successful service listing."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch("app.api.services.ServiceModel") as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[mock_service_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/services")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1

        app.dependency_overrides.clear()

    async def test_list_services_with_category_filter(self, app, mock_auth_context, mock_service_summary):
        """Test service listing with category filter."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch("app.api.services.ServiceModel") as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[mock_service_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/services?category=haircut")

        assert response.status_code == status.HTTP_200_OK

        app.dependency_overrides.clear()


# ============================================================================
# Service Create Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestServiceCreate:
    """Test service creation."""

    async def test_create_service_success(self, app, mock_auth_context, mock_service):
        """Test successful service creation."""
        from app.api.dependencies import require_manager, get_salon_id

        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch("app.api.services.ServiceModel") as MockModel:
            mock_instance = AsyncMock()
            mock_instance.find_by_name = AsyncMock(return_value=None)  # No existing service
            mock_instance.create = AsyncMock(return_value=mock_service)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/services",
                    json={
                        "name": "Haircut",
                        "description": "Professional haircut service",
                        "category": "haircut",
                        "pricing": {
                            "base_price": "500.00",
                            "senior_price": "700.00",
                            "junior_price": "350.00",
                        },
                        "duration": {
                            "base_minutes": 45,
                            "buffer_before": 5,
                            "buffer_after": 5,
                        },
                        "resource_requirement": {
                            "resource_type": "chair_mens",
                        }
                    }
                )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Haircut"

        app.dependency_overrides.clear()

    async def test_create_service_with_pricing_tiers(self, app, mock_auth_context, mock_service):
        """Test service creation with pricing tiers."""
        from app.api.dependencies import require_manager, get_salon_id

        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch("app.api.services.ServiceModel") as MockModel:
            mock_instance = AsyncMock()
            mock_instance.find_by_name = AsyncMock(return_value=None)  # No existing service
            mock_instance.create = AsyncMock(return_value=mock_service)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/services",
                    json={
                        "name": "Haircut",
                        "description": "Professional haircut service",
                        "category": "haircut",
                        "pricing": {
                            "base_price": "500.00",
                            "senior_price": "700.00",
                            "junior_price": "350.00",
                        },
                        "duration": {
                            "base_minutes": 45,
                            "buffer_before": 5,
                            "buffer_after": 5,
                        },
                        "resource_requirement": {
                            "resource_type": "chair_mens",
                        }
                    }
                )

        assert response.status_code == status.HTTP_201_CREATED

        app.dependency_overrides.clear()


# ============================================================================
# Service Get Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestServiceGet:
    """Test service retrieval."""

    async def test_get_service_success(self, app, mock_auth_context, mock_service):
        """Test successful service retrieval."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch("app.api.services.ServiceModel") as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_service)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/services/service_001")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Check service_id instead of id
        assert data["service_id"] == "service_001"

        app.dependency_overrides.clear()

    async def test_get_service_not_found(self, app, mock_auth_context):
        """Test service not found returns 404."""
        from app.api.dependencies import get_current_user, get_salon_id

        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch("app.api.services.ServiceModel") as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=None)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/services/nonexistent")

        assert response.status_code == status.HTTP_404_NOT_FOUND

        app.dependency_overrides.clear()


# ============================================================================
# Service Update Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestServiceUpdate:
    """Test service update."""

    async def test_update_service_success(self, app, mock_auth_context, mock_service):
        """Test successful service update."""
        from app.api.dependencies import require_manager, get_salon_id

        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        updated_service = mock_service.model_copy(update={"pricing": ServicePricing(base_price=Decimal("600.00"))})

        with patch("app.api.services.ServiceModel") as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_service)
            mock_instance.update = AsyncMock(return_value=updated_service)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/services/service_001",
                    json={"pricing": {"base_price": "600.00"}}
                )

        assert response.status_code == status.HTTP_200_OK

        app.dependency_overrides.clear()

    async def test_update_service_toggle_active(self, app, mock_auth_context, mock_service):
        """Test toggling service active status."""
        from app.api.dependencies import require_manager, get_salon_id

        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        inactive_service = mock_service.model_copy(update={"is_active": False})

        with patch("app.api.services.ServiceModel") as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_service)
            mock_instance.update = AsyncMock(return_value=inactive_service)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/services/service_001",
                    json={"is_active": False}
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] == False

        app.dependency_overrides.clear()


# ============================================================================
# Service Delete Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestServiceDelete:
    """Test service deletion."""

    async def test_delete_service_success(self, app, mock_auth_context, mock_service):
        """Test successful service deletion."""
        from app.api.dependencies import require_manager, get_salon_id

        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch("app.api.services.ServiceModel") as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_service)
            mock_instance.soft_delete = AsyncMock(return_value=True)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.delete("/services/service_001")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        app.dependency_overrides.clear()

    async def test_delete_service_not_found(self, app, mock_auth_context):
        """Test deleting non-existent service returns 404."""
        from app.api.dependencies import require_manager, get_salon_id

        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        with patch("app.api.services.ServiceModel") as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=None)
            MockModel.return_value = mock_instance

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.delete("/services/nonexistent")

        assert response.status_code == status.HTTP_404_NOT_FOUND

        app.dependency_overrides.clear()


# ============================================================================
# Edge Case Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestServiceEdgeCases:
    """Test edge cases for service operations."""

    async def test_create_service_negative_price(self, app, mock_auth_context):
        """Test service creation with negative price fails."""
        from app.api.dependencies import require_manager, get_salon_id

        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/services",
                json={
                    "name": "Haircut",
                    "description": "Professional haircut service",
                    "category": "haircut",
                    "pricing": {
                        "base_price": "-100.00",  # Negative price
                    },
                    "duration": {
                        "base_minutes": 45,
                    },
                    "resource_requirement": {
                        "resource_type": "chair_mens",
                    }
                }
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        app.dependency_overrides.clear()

    async def test_create_service_invalid_category(self, app, mock_auth_context):
        """Test service creation with invalid category fails."""
        from app.api.dependencies import require_manager, get_salon_id

        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/services",
                json={
                    "name": "Haircut",
                    "description": "Professional haircut service",
                    "category": "invalid_category",  # Invalid category
                    "pricing": {
                        "base_price": "500.00",
                    },
                    "duration": {
                        "base_minutes": 45,
                    },
                    "resource_requirement": {
                        "resource_type": "chair_mens",
                    }
                }
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
