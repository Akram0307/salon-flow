"""
Pytest configuration and fixtures
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["FIREBASE_PROJECT_ID"] = "salon-flow-test"
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = "localhost:9099"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["OPENROUTER_API_KEY"] = "test-api-key"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def is_ai_test():
    """Check if we're running AI service tests"""
    # Check if AI service path is in sys.path or if we're in AI test directory
    for path in sys.path:
        if 'services/ai' in path:
            return True
    # Check command line args for AI test path
    for arg in sys.argv:
        if 'tests/ai' in arg or 'test_ai' in arg:
            return True
    return False


@pytest.fixture(scope="session", autouse=True)
def mock_firebase():
    """Mock Firebase at the application level."""
    # Skip Firebase mock for AI service tests
    if is_ai_test():
        yield None
        return
        
    from unittest.mock import MagicMock, AsyncMock, patch

    # Create mock Firestore client with proper chain support
    mock_firestore_client = MagicMock()

    # Create mock collection reference
    mock_collection = MagicMock()
    mock_document = MagicMock()
    mock_query = MagicMock()

    # Document operations
    mock_document.get = AsyncMock(return_value=MagicMock(exists=False, to_dict=lambda: None))
    mock_document.set = AsyncMock()
    mock_document.update = AsyncMock()
    mock_document.delete = AsyncMock()

    # Query operations - support both filter and positional arguments
    def mock_where(*args, **kwargs):
        # Support both where(field, op, value) and where(filter=FieldFilter(...))
        return mock_query

    mock_query.where = mock_where
    mock_query.order_by = MagicMock(return_value=mock_query)
    mock_query.limit = MagicMock(return_value=mock_query)
    mock_query.offset = MagicMock(return_value=mock_query)
    mock_query.start_after = MagicMock(return_value=mock_query)
    mock_query.end_before = MagicMock(return_value=mock_query)
    mock_query.stream = AsyncMock(return_value=[])  # Return empty async generator
    mock_query.get = AsyncMock(return_value=[])

    # Count query support
    mock_count_query = MagicMock()
    mock_count_query.get = AsyncMock(return_value=[[MagicMock(value=0)]])
    mock_query.count = MagicMock(return_value=mock_count_query)

    # Collection operations
    mock_collection.document = MagicMock(return_value=mock_document)
    mock_collection.where = mock_where
    mock_collection.order_by = MagicMock(return_value=mock_query)
    mock_collection.limit = MagicMock(return_value=mock_query)
    mock_collection.stream = AsyncMock(return_value=[])
    mock_collection.get = AsyncMock(return_value=[])

    # Client operations
    mock_firestore_client.collection = MagicMock(return_value=mock_collection)
    mock_firestore_client.batch = MagicMock()
    mock_firestore_client.get_all = AsyncMock(return_value=[])

    # Mock the correct function names
    with patch("app.core.firebase.get_firestore_async", return_value=mock_firestore_client):
        with patch("app.core.firebase.get_firestore", return_value=mock_firestore_client):
            with patch("app.core.firebase.get_firestore_client", return_value=mock_firestore_client):
                yield mock_firestore_client


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = 1
    return mock


@pytest.fixture
def sample_salon():
    """Sample salon data"""
    return {
        "id": "salon_001",
        "name": "Test Salon",
        "address": {
            "street": "123 Main St",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001",
            "country": "India"
        },
        "phone": "+91-9876543210",
        "email": "test@salon.com",
        "gst_number": "27AABCT1234N1ZA",
        "is_active": True
    }


@pytest.fixture
def sample_customer():
    """Sample customer data"""
    return {
        "id": "customer_001",
        "name": "John Doe",
        "phone": "+91-9876543210",
        "email": "john@example.com",
        "loyalty_points": 100,
        "total_visits": 5,
        "total_spent": 5000.00
    }


@pytest.fixture
def sample_staff():
    """Sample staff data"""
    return {
        "id": "staff_001",
        "name": "Priya Sharma",
        "role": "senior_stylist",
        "phone": "+91-9876543211",
        "email": "priya@salon.com",
        "skills": ["haircut", "coloring", "styling"],
        "is_active": True
    }


@pytest.fixture
def sample_service():
    """Sample service data"""
    return {
        "id": "service_001",
        "name": "Haircut - Men",
        "category": "haircut",
        "duration_minutes": 30,
        "price": 300.00,
        "is_active": True
    }


@pytest.fixture
def sample_booking():
    """Sample booking data"""
    return {
        "id": "booking_001",
        "customer_id": "customer_001",
        "staff_id": "staff_001",
        "service_ids": ["service_001"],
        "start_time": "2024-02-20T10:00:00",
        "end_time": "2024-02-20T10:30:00",
        "status": "confirmed",
        "total_amount": 300.00
    }
