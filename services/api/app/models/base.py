"""Base Firestore Model with CRUD operations.

Provides a generic base class for all Firestore models with:
- Async CRUD operations using singleton client
- Query builder for filtering
- Pagination support with cursor-based optimization
- Batch operations
- Built-in caching support
"""
from datetime import datetime
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    Callable,
)
from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import BaseQuery, FieldFilter
import structlog

from app.core.firebase import get_firestore_async
from app.core.redis import redis_client, CacheConfig
from app.schemas.base import FirestoreModel, PaginatedResponse

logger = structlog.get_logger()

# Generic type for model schema
ModelType = TypeVar("ModelType", bound=FirestoreModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=FirestoreModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=FirestoreModel)


class FirestoreBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base class for Firestore models with async CRUD operations.

    Uses singleton async client for optimal connection management.
    Includes caching support for frequently accessed data.
    """

    collection_name: str = ""
    id_field: str = "id"
    model: Type[ModelType] = None
    create_schema: Type[CreateSchemaType] = None
    update_schema: Type[UpdateSchemaType] = None

    # Cache settings - override in subclasses
    cache_ttl: int = 300  # 5 minutes default
    cache_enabled: bool = True

    def __init__(self):
        """Initialize the model with singleton async client."""
        self._async_client: AsyncClient = None

    @property
    def async_client(self) -> AsyncClient:
        """Get singleton async Firestore client."""
        if self._async_client is None:
            self._async_client = get_firestore_async()
        return self._async_client

    @property
    def collection(self) -> BaseQuery:
        """Get the Firestore collection reference."""
        return self.async_client.collection(self.collection_name)

    def _get_cache_key(self, document_id: str) -> str:
        """Generate cache key for a document."""
        return f"{self.collection_name}:{document_id}"

    def _get_list_cache_key(self, salon_id: str, **filters) -> str:
        """Generate cache key for list queries."""
        filter_str = ":".join(f"{k}={v}" for k, v in sorted(filters.items()) if v is not None)
        return f"{self.collection_name}:list:{salon_id}:{filter_str}"

    async def _invalidate_cache(self, document_id: str, salon_id: str = None):
        """Invalidate cache for a document and related lists."""
        if not self.cache_enabled or not redis_client.is_connected:
            return

        # Delete document cache
        await redis_client.delete(self._get_cache_key(document_id))

        # Delete list caches for the salon
        if salon_id:
            pattern = f"{self.collection_name}:list:{salon_id}:*"
            await redis_client.delete_pattern(pattern)

    # ========================================================================
    # CREATE Operations
    # ========================================================================

    async def create(
        self,
        data: Union[CreateSchemaType, Dict[str, Any]],
        document_id: Optional[str] = None,
    ) -> ModelType:
        """Create a new document in the collection."""
        try:
            if isinstance(data, FirestoreModel):
                doc_data = data.to_firestore()
            else:
                doc_data = data

            now = datetime.utcnow()
            doc_data["created_at"] = now
            doc_data["updated_at"] = now

            if document_id:
                doc_ref = self.collection.document(document_id)
                await doc_ref.set(doc_data)
            else:
                doc_ref = self.collection.document()
                await doc_ref.set(doc_data)
                document_id = doc_ref.id

            doc_data[self.id_field] = document_id

            # Invalidate list cache for this salon
            salon_id = doc_data.get("salon_id")
            if salon_id:
                await self._invalidate_cache(document_id, salon_id)

            logger.info(
                "Document created",
                collection=self.collection_name,
                document_id=document_id,
            )

            return self.model.model_validate(doc_data)

        except Exception as e:
            logger.error(
                "Failed to create document",
                collection=self.collection_name,
                error=str(e),
            )
            raise

    async def create_batch(
        self,
        items: List[Union[CreateSchemaType, Dict[str, Any]]],
    ) -> List[ModelType]:
        """Create multiple documents in a batch."""
        if not items:
            return []

        try:
            batch = self.async_client.batch()
            now = datetime.utcnow()
            created_items = []
            salon_ids = set()

            for item in items:
                if isinstance(item, FirestoreModel):
                    doc_data = item.to_firestore()
                else:
                    doc_data = item.copy()

                doc_data["created_at"] = now
                doc_data["updated_at"] = now

                doc_ref = self.collection.document()
                doc_data["id"] = doc_ref.id

                if "salon_id" in doc_data:
                    salon_ids.add(doc_data["salon_id"])

                batch.set(doc_ref, doc_data)
                created_items.append(self.model.model_validate(doc_data))

            await batch.commit()

            # Invalidate list caches
            for salon_id in salon_ids:
                await self._invalidate_cache(None, salon_id)

            logger.info(
                "Batch created",
                collection=self.collection_name,
                count=len(items),
            )

            return created_items

        except Exception as e:
            logger.error(
                "Failed to create batch",
                collection=self.collection_name,
                error=str(e),
            )
            raise

    # ========================================================================
    # READ Operations (with caching)
    # ========================================================================

    async def get(self, document_id: str, use_cache: bool = True) -> Optional[ModelType]:
        """Get a document by ID with optional caching."""
        cache_key = self._get_cache_key(document_id)

        # Try cache first
        if use_cache and self.cache_enabled and redis_client.is_connected:
            cached = await redis_client.get(cache_key)
            if cached is not None:
                logger.debug("Cache hit", collection=self.collection_name, document_id=document_id)
                return self.model.model_validate(cached)

        try:
            doc_ref = self.collection.document(document_id)
            doc = await doc_ref.get()

            if not doc.exists:
                logger.debug(
                    "Document not found",
                    collection=self.collection_name,
                    document_id=document_id,
                )
                return None

            data = doc.to_dict()
            data["id"] = doc.id

            result = self.model.model_validate(data)

            # Cache the result
            if use_cache and self.cache_enabled and redis_client.is_connected:
                await redis_client.set(cache_key, data, expire=self.cache_ttl)

            return result

        except Exception as e:
            logger.error(
                "Failed to get document",
                collection=self.collection_name,
                document_id=document_id,
                error=str(e),
            )
            raise

    async def get_multi(
        self,
        document_ids: List[str],
        use_cache: bool = True,
    ) -> List[ModelType]:
        """Get multiple documents by IDs with caching."""
        if not document_ids:
            return []

        results = []
        uncached_ids = []
        cached_data = {}

        # Check cache for all documents
        if use_cache and self.cache_enabled and redis_client.is_connected:
            cache_keys = [self._get_cache_key(doc_id) for doc_id in document_ids]
            cached_data = await redis_client.get_multi(cache_keys)

            for doc_id in document_ids:
                cache_key = self._get_cache_key(doc_id)
                if cache_key in cached_data:
                    results.append(self.model.model_validate(cached_data[cache_key]))
                else:
                    uncached_ids.append(doc_id)
        else:
            uncached_ids = document_ids

        # Fetch uncached documents
        if uncached_ids:
            try:
                doc_refs = [
                    self.collection.document(doc_id)
                    for doc_id in uncached_ids
                ]
                docs = await self.async_client.get_all(doc_refs)

                for doc in docs:
                    if doc.exists:
                        data = doc.to_dict()
                        data["id"] = doc.id
                        results.append(self.model.model_validate(data))

                        # Cache the result
                        if use_cache and self.cache_enabled and redis_client.is_connected:
                            await redis_client.set(
                                self._get_cache_key(doc.id),
                                data,
                                expire=self.cache_ttl
                            )
            except Exception as e:
                logger.error(
                    "Failed to get multiple documents",
                    collection=self.collection_name,
                    error=str(e),
                )
                raise

        return results

    async def get_by_field(
        self,
        field: str,
        value: Any,
        salon_id: Optional[str] = None,
    ) -> Optional[ModelType]:
        """Get a document by a specific field value."""
        try:
            query = self.collection.where(filter=FieldFilter(field, "==", value))

            if salon_id:
                query = query.where(filter=FieldFilter("salon_id", "==", salon_id))

            query = query.limit(1)
            docs = query.stream()

            async for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                return self.model.model_validate(data)

            return None

        except Exception as e:
            logger.error(
                "Failed to get document by field",
                collection=self.collection_name,
                field=field,
                error=str(e),
            )
            raise

    # ========================================================================
    # UPDATE Operations
    # ========================================================================

    async def update(
        self,
        document_id: str,
        data: Union[UpdateSchemaType, Dict[str, Any]],
        merge: bool = True,
    ) -> Optional[ModelType]:
        """Update a document by ID."""
        try:
            doc_ref = self.collection.document(document_id)
            doc = await doc_ref.get()

            if not doc.exists:
                logger.warning(
                    "Document not found for update",
                    collection=self.collection_name,
                    document_id=document_id,
                )
                return None

            if isinstance(data, FirestoreModel):
                update_data = data.to_firestore()
            else:
                update_data = data.copy()

            update_data["updated_at"] = datetime.utcnow()

            if merge:
                await doc_ref.update(update_data)
            else:
                existing_data = doc.to_dict()
                update_data["id"] = document_id
                update_data["created_at"] = existing_data.get("created_at")
                await doc_ref.set(update_data)

            # Invalidate cache
            existing_data = doc.to_dict()
            salon_id = existing_data.get("salon_id")
            await self._invalidate_cache(document_id, salon_id)

            return await self.get(document_id, use_cache=False)

        except Exception as e:
            logger.error(
                "Failed to update document",
                collection=self.collection_name,
                document_id=document_id,
                error=str(e),
            )
            raise

    async def update_batch(
        self,
        updates: Dict[str, Union[UpdateSchemaType, Dict[str, Any]]],
    ) -> int:
        """Update multiple documents in a batch."""
        if not updates:
            return 0

        try:
            batch = self.async_client.batch()
            now = datetime.utcnow()
            count = 0
            salon_ids = set()

            for doc_id, data in updates.items():
                if isinstance(data, FirestoreModel):
                    update_data = data.to_firestore()
                else:
                    update_data = data.copy()

                update_data["updated_at"] = now

                doc_ref = self.collection.document(doc_id)
                batch.update(doc_ref, update_data)
                count += 1

            await batch.commit()

            # Invalidate caches
            for doc_id in updates.keys():
                await self._invalidate_cache(doc_id, None)

            logger.info(
                "Batch updated",
                collection=self.collection_name,
                count=count,
            )

            return count

        except Exception as e:
            logger.error(
                "Failed to update batch",
                collection=self.collection_name,
                error=str(e),
            )
            raise

    # ========================================================================
    # DELETE Operations
    # ========================================================================

    async def delete(self, document_id: str) -> bool:
        """Delete a document by ID."""
        try:
            doc_ref = self.collection.document(document_id)
            doc = await doc_ref.get()

            if not doc.exists:
                logger.debug(
                    "Document not found for deletion",
                    collection=self.collection_name,
                    document_id=document_id,
                )
                return False

            # Get salon_id before deletion for cache invalidation
            data = doc.to_dict()
            salon_id = data.get("salon_id")

            await doc_ref.delete()

            # Invalidate cache
            await self._invalidate_cache(document_id, salon_id)

            logger.info(
                "Document deleted",
                collection=self.collection_name,
                document_id=document_id,
            )

            return True

        except Exception as e:
            logger.error(
                "Failed to delete document",
                collection=self.collection_name,
                document_id=document_id,
                error=str(e),
            )
            raise

    async def soft_delete(self, document_id: str) -> bool:
        """Soft delete by setting is_active=False."""
        return await self.update(document_id, {"is_active": False}) is not None

    # ========================================================================
    # QUERY Operations (with cursor-based pagination)
    # ========================================================================

    async def list(
        self,
        salon_id: Optional[str] = None,
        filters: Optional[List[tuple]] = None,
        order_by: Optional[str] = None,
        order_direction: str = "ASCENDING",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        start_after: Optional[Any] = None,
        end_before: Optional[Any] = None,
        use_cache: bool = False,
    ) -> List[ModelType]:
        """List documents with optional filtering and cursor-based pagination."""
        try:
            query = self.collection

            if salon_id:
                query = query.where(filter=FieldFilter("salon_id", "==", salon_id))

            if filters:
                for field, op, value in filters:
                    query = query.where(filter=FieldFilter(field, op, value))

            if order_by:
                direction = BaseQuery.DESCENDING if order_direction.upper() == "DESCENDING" else BaseQuery.ASCENDING
                query = query.order_by(order_by, direction=direction)

            # Cursor-based pagination (preferred)
            if start_after is not None and order_by:
                query = query.start_after({order_by: start_after})
            if end_before is not None and order_by:
                query = query.end_before({order_by: end_before})

            if limit:
                query = query.limit(limit)

            results = []
            async for doc in query.stream():
                data = doc.to_dict()
                data["id"] = doc.id
                results.append(self.model.model_validate(data))

            # Offset is applied after fetch (not recommended for large datasets)
            if offset and offset > 0:
                results = results[offset:]

            return results

        except Exception as e:
            logger.error(
                "Failed to list documents",
                collection=self.collection_name,
                error=str(e),
            )
            raise

    async def count(
        self,
        salon_id: Optional[str] = None,
        filters: Optional[List[tuple]] = None,
    ) -> int:
        """Count documents matching filters."""
        try:
            query = self.collection

            if salon_id:
                query = query.where(filter=FieldFilter("salon_id", "==", salon_id))

            if filters:
                for field, op, value in filters:
                    query = query.where(filter=FieldFilter(field, op, value))

            count_query = query.count()
            result = await count_query.get()

            return result[0][0].value if result else 0

        except Exception as e:
            logger.error(
                "Failed to count documents",
                collection=self.collection_name,
                error=str(e),
            )
            raise

    async def paginate(
        self,
        page: int = 1,
        page_size: int = 20,
        salon_id: Optional[str] = None,
        filters: Optional[List[tuple]] = None,
        order_by: Optional[str] = None,
        order_direction: str = "ASCENDING",
        use_cache: bool = False,
    ) -> PaginatedResponse:
        """Get paginated results with optimized counting."""
        try:
            # Run count and items in parallel for better performance
            import asyncio

            count_task = self.count(salon_id=salon_id, filters=filters)

            offset = (page - 1) * page_size
            items_task = self.list(
                salon_id=salon_id,
                filters=filters,
                order_by=order_by,
                order_direction=order_direction,
                limit=page_size,
                offset=offset,
                use_cache=use_cache,
            )

            total, items = await asyncio.gather(count_task, items_task)

            return PaginatedResponse(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
            )

        except Exception as e:
            logger.error(
                "Failed to paginate documents",
                collection=self.collection_name,
                error=str(e),
            )
            raise

    async def search(
        self,
        field: str,
        search_term: str,
        salon_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[ModelType]:
        """Search documents by field with prefix matching."""
        try:
            end_term = search_term + "\uf8ff"

            filters = [
                (field, ">=", search_term),
                (field, "<", end_term),
            ]

            return await self.list(
                salon_id=salon_id,
                filters=filters,
                order_by=field,
                limit=limit,
            )

        except Exception as e:
            logger.error(
                "Failed to search documents",
                collection=self.collection_name,
                field=field,
                error=str(e),
            )
            raise


class TimestampMixin:
    """Mixin class for adding timestamp fields to models.
    
    Provides created_at and updated_at fields with automatic management.
    """
    
    def __init__(self, **data):
        self.created_at = data.get("created_at") or datetime.utcnow()
        self.updated_at = data.get("updated_at") or datetime.utcnow()
        super().__init__(**data)
    
    def touch(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
