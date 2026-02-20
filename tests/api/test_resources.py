"""Comprehensive tests for Resource API endpoints.

Covers:
- Resource CRUD operations
- Capacity management
- Multi-tenant isolation
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date, time
from decimal import Decimal

from fastapi import FastAPI, status
from httpx import AsyncClient, ASGITransport

from app.api.resources import router
from app.api.dependencies import AuthContext
from app.schemas import (
    ResourceCreate,
    ResourceUpdate,
    Resource,
    ResourceSummary,
    ResourceCapacity,
    PaginatedResponse,
)
from app.schemas.base import StaffRole, ResourceType, ResourceStatus


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
def mock_capacity():
    """Sample resource capacity."""
    return ResourceCapacity(
        max_concurrent_services=1,
        avg_service_duration_minutes=30,
        max_daily_bookings=20,
    )


@pytest.fixture
def mock_resource(mock_capacity):
    """Sample resource object."""
    return Resource(
        id="resource_001",
        salon_id="salon_001",
        name="Chair 1",
        resource_type=ResourceType.CHAIR_MENS,
        zone="Main Floor",
        capacity=mock_capacity,
        is_active=True,
        is_exclusive=False,
        blocked_dates=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_resource_summary():
    """Sample resource summary."""
    return ResourceSummary(
        id="resource_001",
        salon_id="salon_001",
        name="Chair 1",
        resource_type=ResourceType.CHAIR_MENS,
        is_active=True,
    )


# ============================================================================
# Resource List Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestResourceList:
    """Test resource listing endpoints."""
    
    async def test_list_resources_success(self, app, mock_auth_context, mock_resource_summary):
        """Test successful resource listing."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.resources.ResourceModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[mock_resource_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/resources")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        
        app.dependency_overrides.clear()
    
    async def test_list_resources_with_type_filter(self, app, mock_auth_context, mock_resource_summary):
        """Test resource listing with type filter."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.resources.ResourceModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.search = AsyncMock(return_value=PaginatedResponse(
                items=[mock_resource_summary],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            ))
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/resources?resource_type=chair_mens")
        
        assert response.status_code == status.HTTP_200_OK
        
        app.dependency_overrides.clear()


# ============================================================================
# Resource Create Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestResourceCreate:
    """Test resource creation."""
    
    async def test_create_resource_success(self, app, mock_auth_context, mock_resource):
        """Test successful resource creation."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.resources.ResourceModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.create = AsyncMock(return_value=mock_resource)
            mock_instance.find_by_name = AsyncMock(return_value=None)  # No existing resource
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/resources",
                    json={
                        "name": "Chair 1",
                        "resource_type": "chair_mens",
                        "zone": "Main Floor",
                    }
                )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Chair 1"
        
        app.dependency_overrides.clear()
    
    async def test_create_resource_duplicate_name(self, app, mock_auth_context, mock_resource):
        """Test resource creation fails with duplicate name."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.resources.ResourceModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.create = AsyncMock(
                side_effect=ValueError("Resource with this name already exists")
            )
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/resources",
                    json={
                        "name": "Chair 1",
                        "resource_type": "chair_mens",
                    }
                )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        app.dependency_overrides.clear()


# ============================================================================
# Resource Get Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestResourceGet:
    """Test resource retrieval."""
    
    async def test_get_resource_success(self, app, mock_auth_context, mock_resource):
        """Test successful resource retrieval."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.resources.ResourceModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_resource)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/resources/resource_001")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "resource_001"
        
        app.dependency_overrides.clear()
    
    async def test_get_resource_not_found(self, app, mock_auth_context):
        """Test resource not found returns 404."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        with patch('app.api.resources.ResourceModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=None)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/resources/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        app.dependency_overrides.clear()


# ============================================================================
# Resource Update Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestResourceUpdate:
    """Test resource update."""
    
    async def test_update_resource_success(self, app, mock_auth_context, mock_resource):
        """Test successful resource update."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        updated_resource = mock_resource.model_copy(update={"name": "Premium Chair"})
        
        with patch('app.api.resources.ResourceModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_resource)
            mock_instance.update = AsyncMock(return_value=updated_resource)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/resources/resource_001",
                    json={"name": "Premium Chair"}
                )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Premium Chair"
        
        app.dependency_overrides.clear()
    
    async def test_deactivate_resource_success(self, app, mock_auth_context, mock_resource):
        """Test successful resource deactivation."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        deactivated_resource = mock_resource.model_copy(update={"is_active": False})
        
        with patch('app.api.resources.ResourceModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_resource)
            mock_instance.update = AsyncMock(return_value=deactivated_resource)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.put(
                    "/resources/resource_001",
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
class TestResourceEdgeCases:
    """Test edge cases for resource operations."""
    
    async def test_create_resource_empty_name(self, app, mock_auth_context):
        """Test resource creation with empty name fails."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/resources",
                json={
                    "name": "",  # Empty name
                    "resource_type": "chair_mens",
                }
            )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()
    
    async def test_create_resource_invalid_type(self, app, mock_auth_context):
        """Test resource creation with invalid type fails."""
        from app.api.dependencies import require_manager, get_salon_id
        
        app.dependency_overrides[require_manager] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/resources",
                json={
                    "name": "Test Resource",
                    "resource_type": "invalid_type",  # Invalid type
                }
            )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()


# ============================================================================
# Multi-Tenant Isolation Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
class TestResourceMultiTenant:
    """Test multi-tenant isolation for resources."""
    
    async def test_get_resource_wrong_salon(self, app, mock_auth_context, mock_capacity):
        """Test access denied for resource from different salon."""
        from app.api.dependencies import get_current_user, get_salon_id
        
        app.dependency_overrides[get_current_user] = lambda: mock_auth_context
        app.dependency_overrides[get_salon_id] = lambda: "salon_001"
        
        # Resource from different salon
        wrong_resource = Resource(
            id="resource_002",
            salon_id="salon_002",  # Different salon
            name="Chair 2",
            resource_type=ResourceType.CHAIR_MENS,
            capacity=mock_capacity,
            is_active=True,
            blocked_dates=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        with patch('app.api.resources.ResourceModel') as MockModel:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=wrong_resource)
            MockModel.return_value = mock_instance
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/resources/resource_002")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
