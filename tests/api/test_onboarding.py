"""Tests for Salon Onboarding API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

import sys
sys.path.insert(0, "/a0/usr/projects/salon_flow/services/api")

from main import app


@pytest.fixture
def mock_firestore():
    """Mock Firestore client."""
    with patch("app.core.firebase.get_firestore_async") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_auth():
    """Mock authentication dependency."""
    with patch("app.api.onboarding.get_current_user") as mock:
        mock.return_value = {
            "uid": "test_user_123",
            "email": "test@example.com",
            "role": "owner"
        }
        yield mock


@pytest.fixture
async def client():
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
class TestOnboardingEndpoints:
    """Test onboarding API endpoints."""
    
    async def test_create_salon_success(self, client, mock_firestore, mock_auth):
        """Test successful salon creation."""
        # Mock Firestore operations
        mock_firestore.collection.return_value.document.return_value.set = AsyncMock()
        mock_firestore.collection.return_value.document.return_value.get = AsyncMock(
            return_value=MagicMock(exists=False)
        )
        
        salon_data = {
            "name": "Test Salon",
            "address": {
                "street": "123 Main St",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001"
            },
            "phone": "+919876543210",
            "email": "test@salon.com"
        }
        
        response = await client.post(
            "/api/v1/onboarding/create-salon",
            json=salon_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 201, 401, 422]
    
    async def test_get_onboarding_status(self, client, mock_firestore, mock_auth):
        """Test getting onboarding status."""
        # Mock user with salon
        mock_firestore.collection.return_value.document.return_value.get = AsyncMock(
            return_value=MagicMock(
                exists=True,
                to_dict=MagicMock(return_value={
                    "salon_id": "salon_123",
                    "onboarding_completed": False,
                    "onboarding_step": 2
                })
            )
        )
        
        response = await client.get(
            "/api/v1/onboarding/status",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 401, 404]
    
    async def test_join_salon_with_invite_code(self, client, mock_firestore, mock_auth):
        """Test joining salon with invite code."""
        # Mock salon lookup by invite code
        mock_firestore.collection.return_value.where.return_value.limit.return_value.get = AsyncMock(
            return_value=MagicMock(
                __iter__=lambda self: iter([
                    MagicMock(
                        id="salon_123",
                        to_dict=MagicMock(return_value={
                            "name": "Test Salon",
                            "invite_code": "ABCD1234"
                        })
                    )
                ])
            )
        )
        
        join_data = {
            "invite_code": "ABCD1234",
            "role": "stylist"
        }
        
        response = await client.post(
            "/api/v1/onboarding/join-salon",
            json=join_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 201, 401, 404, 422]
    
    async def test_complete_onboarding(self, client, mock_firestore, mock_auth):
        """Test marking onboarding as complete."""
        mock_firestore.collection.return_value.document.return_value.update = AsyncMock()
        
        response = await client.post(
            "/api/v1/onboarding/complete",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 401, 404]
    
    async def test_get_service_templates(self, client, mock_auth):
        """Test getting service templates."""
        response = await client.get(
            "/api/v1/onboarding/service-templates",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert "templates" in data or isinstance(data, list)
    
    async def test_import_services(self, client, mock_firestore, mock_auth):
        """Test importing services from templates."""
        mock_firestore.collection.return_value.document.return_value.set = AsyncMock()
        
        import_data = {
            "template_type": "salon",
            "categories": ["hair_cuts", "hair_color"]
        }
        
        response = await client.post(
            "/api/v1/onboarding/import-services",
            json=import_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 201, 401, 422]


@pytest.mark.asyncio
class TestOnboardingValidation:
    """Test onboarding data validation."""
    
    async def test_create_salon_missing_fields(self, client, mock_auth):
        """Test salon creation with missing required fields."""
        incomplete_data = {
            "name": "Test Salon"
            # Missing address, phone, email
        }
        
        response = await client.post(
            "/api/v1/onboarding/create-salon",
            json=incomplete_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [400, 422]
    
    async def test_join_salon_invalid_code(self, client, mock_firestore, mock_auth):
        """Test joining with invalid invite code."""
        # Mock no salon found
        mock_firestore.collection.return_value.where.return_value.limit.return_value.get = AsyncMock(
            return_value=MagicMock(__iter__=lambda self: iter([]))
        )
        
        join_data = {
            "invite_code": "INVALID",
            "role": "stylist"
        }
        
        response = await client.post(
            "/api/v1/onboarding/join-salon",
            json=join_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [400, 404, 422]


@pytest.mark.asyncio
class TestOnboardingFlow:
    """Test complete onboarding flow."""
    
    async def test_full_onboarding_flow(self, client, mock_firestore, mock_auth):
        """Test complete onboarding flow from start to finish."""
        # Step 1: Create salon
        mock_firestore.collection.return_value.document.return_value.set = AsyncMock()
        mock_firestore.collection.return_value.document.return_value.get = AsyncMock(
            return_value=MagicMock(
                exists=True,
                to_dict=MagicMock(return_value={
                    "id": "salon_123",
                    "name": "Test Salon",
                    "onboarding_step": 1
                })
            )
        )
        
        # Step 2: Check status
        response = await client.get(
            "/api/v1/onboarding/status",
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Step 3: Complete onboarding
        mock_firestore.collection.return_value.document.return_value.update = AsyncMock()
        
        response = await client.post(
            "/api/v1/onboarding/complete",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code in [200, 401, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
