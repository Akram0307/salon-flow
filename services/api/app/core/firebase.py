"""Firebase initialization with async support and connection pooling."""
import os
import json
import asyncio
from typing import Optional, Dict, Any, List
from functools import lru_cache
from unittest.mock import MagicMock, AsyncMock

import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_admin.firestore import AsyncClient
from google.cloud.firestore_v1 import Client as SyncClient
import structlog

logger = structlog.get_logger()

# Singleton instances
_firestore_sync_client: Optional[SyncClient] = None
_firestore_async_client: Optional[AsyncClient] = None
_initialized = False

# In-memory storage for test mode
_test_data: Dict[str, Dict[str, Any]] = {}


class MockDocumentSnapshot:
    """Mock Firestore document snapshot."""
    def __init__(self, doc_id: str, data: Dict[str, Any] = None):
        self.id = doc_id
        self._data = data or {}
        self.exists = data is not None

    def to_dict(self) -> Dict[str, Any]:
        return self._data.copy() if self._data else {}


class MockDocumentRef:
    """Mock Firestore document reference."""
    def __init__(self, collection_name: str, doc_id: str = None):
        self.collection_name = collection_name
        self.doc_id = doc_id or f"auto_{collection_name}_{len(_test_data.get(collection_name, {}))}"
        self.id = self.doc_id

    async def get(self) -> MockDocumentSnapshot:
        collection_data = _test_data.get(self.collection_name, {})
        data = collection_data.get(self.doc_id)
        return MockDocumentSnapshot(self.doc_id, data)

    async def set(self, data: Dict[str, Any]):
        if self.collection_name not in _test_data:
            _test_data[self.collection_name] = {}
        _test_data[self.collection_name][self.doc_id] = data

    async def update(self, data: Dict[str, Any]):
        if self.collection_name in _test_data and self.doc_id in _test_data[self.collection_name]:
            _test_data[self.collection_name][self.doc_id].update(data)

    async def delete(self):
        if self.collection_name in _test_data and self.doc_id in _test_data[self.collection_name]:
            del _test_data[self.collection_name][self.doc_id]




class MockCountQuery:
    """Mock Firestore count query."""
    def __init__(self, query: "MockQuery"):
        self._query = query

    async def get(self) -> List[List]:
        """Get count result."""
        results = await self._query.get()
        # Return count in the format Firestore returns: [[AggregationResult(value=...)]]
        from unittest.mock import MagicMock
        count_result = MagicMock()
        count_result.value = len(results)
        return [[count_result]]

class MockQuery:
    """Mock Firestore query."""
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self._filters: List[tuple] = []
        self._order_by: List[tuple] = []
        self._limit_val: Optional[int] = None
        self._offset_val: Optional[int] = None
        self._start_after_val: Optional[Any] = None
        self._end_before_val: Optional[Any] = None

    def where(self, field: str = None, op: str = None, value: Any = None, filter=None) -> "MockQuery":
        # Support both where(field, op, value) and where(filter=FieldFilter(...))
        if filter is not None:
            # Extract field, op, value from FieldFilter
            # FieldFilter has field_path, op_string, and value attributes
            try:
                field = getattr(filter, 'field_path', None) or getattr(filter, 'field', None)
                op = getattr(filter, 'op_string', None) or getattr(filter, 'op', None)
                value = getattr(filter, 'value', None)
            except:
                # If we can't extract, just skip this filter
                pass
        if field and op:
            self._filters.append((field, op, value))
        return self

    def order_by(self, field: str, direction: str = "ASCENDING") -> "MockQuery":
        self._order_by.append((field, direction))
        return self

    def limit(self, n: int) -> "MockQuery":
        self._limit_val = n
        return self

    def count(self) -> "MockCountQuery":
        """Return a count query."""
        return MockCountQuery(self)

    async def stream(self):
        """Stream results as async generator."""
        results = await self.get()
        for result in results:
            yield result

    async def get(self) -> List[MockDocumentSnapshot]:
        collection_data = _test_data.get(self.collection_name, {})
        results = []

        for doc_id, data in collection_data.items():
            # Apply filters
            match = True
            for field, op, value in self._filters:
                field_val = data.get(field)
                if op == "==" and field_val != value:
                    match = False
                    break
                elif op == ">=" and (field_val is None or field_val < value):
                    match = False
                    break
                elif op == "<=" and (field_val is None or field_val > value):
                    match = False
                    break

            if match:
                results.append(MockDocumentSnapshot(doc_id, data))

        # Apply ordering
        if self._order_by:
            for field, direction in reversed(self._order_by):
                reverse = direction == "DESCENDING"
                results.sort(key=lambda x: x.to_dict().get(field, ""), reverse=reverse)

        # Apply limit
        if self._limit_val:
            results = results[:self._limit_val]

        return results


class MockCollectionRef:
    """Mock Firestore collection reference."""
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    def document(self, doc_id: str = None) -> MockDocumentRef:
        return MockDocumentRef(self.collection_name, doc_id)

    def where(self, field: str = None, op: str = None, value: Any = None, filter=None) -> MockQuery:
        query = MockQuery(self.collection_name)
        query.where(field, op, value, filter)
        return query

    def order_by(self, field: str, direction: str = "ASCENDING") -> MockQuery:
        query = MockQuery(self.collection_name)
        query.order_by(field, direction)
        return query

    def limit(self, n: int) -> MockQuery:
        query = MockQuery(self.collection_name)
        query.limit(n)
        return query

    async def add(self, data: Dict[str, Any]) -> tuple:
        doc_ref = MockDocumentRef(self.collection_name)
        await doc_ref.set(data)
        return (None, doc_ref)


class MockFirestoreClient:
    """Mock Firestore client for testing."""

    def collection(self, name: str) -> MockCollectionRef:
        return MockCollectionRef(name)


def _create_mock_client():
    """Create a mock Firestore client for testing."""
    return MockFirestoreClient()


def init_firebase():
    """Initialize Firebase Admin SDK with connection pooling."""
    global _firestore_sync_client, _firestore_async_client, _initialized

    if _initialized:
        logger.debug("Firebase already initialized")
        return

    # Check for test environment - use mock client
    if os.getenv("ENVIRONMENT") == "test":
        logger.info("Test environment detected - using mock Firestore client")
        _firestore_sync_client = _create_mock_client()
        _firestore_async_client = _create_mock_client()
        _initialized = True
        return

    project_id = os.getenv("FIREBASE_PROJECT_ID", "salon-saas-487508")

    # Check for emulator mode
    emulator_host = os.getenv("FIRESTORE_EMULATOR_HOST")
    auth_emulator = os.getenv("FIREBASE_AUTH_EMULATOR_HOST")

    # Check for service account credentials
    gcp_key_json = os.getenv("GCP_JSON_KEY")
    gcp_key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    cred = None

    if emulator_host:
        # Emulator mode - use Application Default Credentials with project override
        logger.info("Initializing Firebase in emulator mode",
                   emulator_host=emulator_host,
                   auth_emulator=auth_emulator)

        # For emulator, we can use Application Default Credentials
        # or just initialize without credentials
        if not firebase_admin._apps:
            firebase_admin.initialize_app(options={
                "projectId": project_id,
            })
    elif gcp_key_json:
        try:
            key_dict = json.loads(gcp_key_json)
            cred = credentials.Certificate(key_dict)
            project_id = key_dict.get("project_id", project_id)
            logger.info("Initializing Firebase with service account from env",
                       project_id=project_id)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred, {
                    "projectId": project_id,
                })
        except json.JSONDecodeError as e:
            logger.error("Failed to parse GCP_JSON_KEY", error=str(e))
            raise
    elif gcp_key_path and os.path.exists(gcp_key_path):
        cred = credentials.Certificate(gcp_key_path)
        logger.info("Initializing Firebase with service account file",
                   path=gcp_key_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                "projectId": project_id,
            })
    else:
        logger.info("Initializing Firebase with Application Default Credentials")
        if not firebase_admin._apps:
            firebase_admin.initialize_app(options={
                "projectId": project_id,
            })

    # Create sync client
    _firestore_sync_client = firestore.client()

    # Create async client with optimized settings
    _firestore_async_client = AsyncClient(
        project=project_id,
    )

    _initialized = True
    logger.info("Firebase initialized successfully", project_id=project_id)


def get_firestore() -> SyncClient:
    """Get synchronous Firestore client (singleton)."""
    global _firestore_sync_client
    if _firestore_sync_client is None:
        init_firebase()
    return _firestore_sync_client


def get_firestore_async() -> AsyncClient:
    """Get async Firestore client (singleton).

    This is the preferred client for all async operations.
    Uses connection pooling for optimal performance.
    """
    global _firestore_async_client
    if _firestore_async_client is None:
        init_firebase()
    return _firestore_async_client


def get_auth():
    """Get Firebase Auth."""
    return auth


async def close_firestore():
    """Close Firestore connections gracefully."""
    global _firestore_sync_client, _firestore_async_client

    if _firestore_async_client:
        await _firestore_async_client.close()
        _firestore_async_client = None
        logger.info("Async Firestore client closed")

    # Sync client doesn't have async close
    _firestore_sync_client = None


# Aliases for backward compatibility
get_firestore_client = get_firestore


__all__ = [
    "init_firebase",
    "get_firestore",
    "get_firestore_async",
    "get_firestore_client",
    "get_auth",
    "close_firestore",
]
