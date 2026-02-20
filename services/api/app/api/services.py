"""Service Catalog Routes for Salon Flow API.

Handles service operations including:
- Service CRUD operations
- Category management
- Service availability
- Bulk import

Optimized with Redis caching for frequently accessed data.
"""
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
import structlog

from app.api.dependencies import (
    get_current_user,
    get_salon_id,
    AuthContext,
    require_staff,
    require_manager,
)
from app.models import ServiceModel
from app.schemas import (
    ServiceCreate,
    ServiceUpdate,
    Service,
    ServiceSummary,
    ServiceCategoryGroup,
    ServiceCategory,
    PaginatedResponse,
)
from app.core.redis import redis_client, CacheConfig

logger = structlog.get_logger()
router = APIRouter(tags=["Service Catalog"])


# ============================================================================
# Cache Keys
# ============================================================================

def service_cache_key(service_id: str) -> str:
    return f"{CacheConfig.PREFIX_SERVICE}:{service_id}"

def service_list_cache_key(salon_id: str, category: str = None, page: int = 1) -> str:
    parts = [CacheConfig.PREFIX_CATALOG, salon_id, str(page)]
    if category:
        parts.append(category)
    return ":".join(parts)

def categories_cache_key(salon_id: str) -> str:
    return f"{CacheConfig.PREFIX_CATALOG}:{salon_id}:categories"


async def invalidate_service_cache(salon_id: str, service_id: str = None):
    """Invalidate service-related caches."""
    if not redis_client.is_connected:
        return

    # Delete specific service cache
    if service_id:
        await redis_client.delete(service_cache_key(service_id))

    # Delete all list/catalog caches for this salon
    await redis_client.delete_pattern(f"{CacheConfig.PREFIX_CATALOG}:{salon_id}:*")
    await redis_client.delete_pattern(f"{CacheConfig.PREFIX_SERVICE}:{salon_id}:*")


# ============================================================================
# Request/Response Schemas
# ============================================================================

class BulkImportItem(BaseModel):
    """Single item in bulk import."""
    name: str
    category: ServiceCategory
    description: Optional[str] = None
    duration_minutes: int = 30
    base_price: float
    is_active: bool = True


class BulkImportRequest(BaseModel):
    """Bulk import request."""
    services: List[BulkImportItem]
    overwrite_existing: bool = False


class BulkImportResponse(BaseModel):
    """Bulk import response."""
    total: int
    created: int
    updated: int
    skipped: int
    errors: List[str]


# ============================================================================
# Routes
# ============================================================================

@router.get(
    "/",
    response_model=PaginatedResponse[ServiceSummary],
    summary="List services",
    description="List all services with pagination and category filtering.",
)
async def list_services(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[ServiceCategory] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name"),
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """List services with pagination and filtering.

    Results are cached for 30 minutes unless a search is performed.
    """
    try:
        # Don't cache search results
        if search:
            service_model = ServiceModel()
            result = await service_model.search(
                salon_id=salon_id,
                category=category,
                is_active=is_active,
                search=search,
                page=page,
                page_size=page_size,
            )
            return result

        # Try cache for non-search queries
        cache_key = service_list_cache_key(
            salon_id, 
            category.value if category else None, 
            page
        )

        if redis_client.is_connected and is_active is None:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug("Service list cache hit", salon_id=salon_id)
                return PaginatedResponse.model_validate(cached)

        service_model = ServiceModel()
        result = await service_model.search(
            salon_id=salon_id,
            category=category,
            is_active=is_active,
            search=search,
            page=page,
            page_size=page_size,
        )

        # Cache the result
        if redis_client.is_connected and is_active is None:
            await redis_client.set(
                cache_key,
                result.model_dump(),
                expire=CacheConfig.SERVICE_CATALOG_TTL
            )

        return result

    except Exception as e:
        logger.error("Failed to list services", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve services",
        )


@router.post(
    "/",
    response_model=Service,
    status_code=status.HTTP_201_CREATED,
    summary="Create service",
    description="Create a new service in the catalog.",
)
async def create_service(
    request: ServiceCreate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Create a new service.

    Only managers and owners can create services.
    Invalidates cache on creation.
    """
    try:
        service_model = ServiceModel()

        # Check for existing service with same name
        existing = await service_model.find_by_name(request.name, salon_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service with this name already exists",
            )

        # Set salon_id from context
        service_data = request.model_copy(update={
            "salon_id": salon_id,
        })

        service = await service_model.create(service_data)

        # Invalidate cache
        await invalidate_service_cache(salon_id)

        logger.info(
            "Service created",
            service_id=service.service_id,
            salon_id=salon_id,
            created_by=current_user.uid,
        )

        return service

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create service", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create service",
        )


@router.get(
    "/categories",
    response_model=List[ServiceCategoryGroup],
    summary="List service categories",
    description="Get all service categories with service counts.",
)
async def list_categories(
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """List all service categories with counts.

    Results are cached for 30 minutes.
    """
    try:
        # Try cache first
        cache_key = categories_cache_key(salon_id)
        if redis_client.is_connected:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug("Categories cache hit", salon_id=salon_id)
                return [ServiceCategoryGroup.model_validate(c) for c in cached]

        service_model = ServiceModel()
        categories = await service_model.get_categories_with_counts(salon_id)

        # Cache the result
        if redis_client.is_connected:
            await redis_client.set(
                cache_key,
                [c.model_dump() for c in categories],
                expire=CacheConfig.SERVICE_CATALOG_TTL
            )

        return categories

    except Exception as e:
        logger.error("Failed to list categories", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve categories",
        )


@router.get(
    "/{service_id}",
    response_model=Service,
    summary="Get service",
    description="Get detailed service information.",
)
async def get_service(
    service_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(get_current_user),
):
    """Get service by ID with caching."""
    try:
        # Try cache first
        cache_key = service_cache_key(service_id)
        if redis_client.is_connected:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug("Service cache hit", service_id=service_id)
                service = Service.model_validate(cached)
                # Verify salon access
                if service.salon_id != salon_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied",
                    )
                return service

        service_model = ServiceModel()
        service = await service_model.get(service_id)

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found",
            )

        # Verify salon access
        if service.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Cache the result
        if redis_client.is_connected:
            await redis_client.set(
                cache_key,
                service.model_dump(),
                expire=CacheConfig.SERVICE_CATALOG_TTL
            )

        return service

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get service", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve service",
        )


@router.put(
    "/{service_id}",
    response_model=Service,
    summary="Update service",
    description="Update service information.",
)
async def update_service(
    service_id: str,
    request: ServiceUpdate,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Update service.

    Managers and owners can update services.
    Invalidates cache on update.
    """
    try:
        service_model = ServiceModel()

        # Verify service exists and belongs to salon
        existing = await service_model.get(service_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found",
            )

        if existing.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Update service
        updated = await service_model.update(service_id, request)

        # Invalidate cache
        await invalidate_service_cache(salon_id, service_id)

        logger.info(
            "Service updated",
            service_id=service_id,
            updated_by=current_user.uid,
        )

        return updated

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update service", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update service",
        )


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete service",
    description="Soft delete a service (mark as inactive).",
)
async def delete_service(
    service_id: str,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Soft delete service by marking as inactive.

    Invalidates cache on deletion.
    """
    try:
        service_model = ServiceModel()

        # Verify service exists and belongs to salon
        existing = await service_model.get(service_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found",
            )

        if existing.salon_id != salon_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Soft delete
        await service_model.soft_delete(service_id)

        # Invalidate cache
        await invalidate_service_cache(salon_id, service_id)

        logger.info(
            "Service deleted",
            service_id=service_id,
            deleted_by=current_user.uid,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete service", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete service",
        )


@router.post(
    "/bulk",
    response_model=BulkImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk import services",
    description="Import multiple services at once.",
)
async def bulk_import_services(
    request: BulkImportRequest,
    salon_id: str = Depends(get_salon_id),
    current_user: AuthContext = Depends(require_manager),
):
    """Bulk import services.

    Allows importing multiple services at once.
    Optionally overwrites existing services with same name.
    Invalidates cache after import.
    """
    try:
        service_model = ServiceModel()

        created = 0
        updated = 0
        skipped = 0
        errors = []

        for item in request.services:
            try:
                # Check for existing
                existing = await service_model.find_by_name(item.name, salon_id)

                if existing:
                    if request.overwrite_existing:
                        # Update existing
                        update_data = ServiceUpdate(
                            name=item.name,
                            category=item.category,
                            description=item.description,
                            duration={"base_minutes": item.duration_minutes},
                            pricing={"base_price": item.base_price},
                            is_active=item.is_active,
                        )
                        await service_model.update(existing.service_id, update_data)
                        updated += 1
                    else:
                        skipped += 1
                else:
                    # Create new
                    service_data = ServiceCreate(
                        salon_id=salon_id,
                        name=item.name,
                        category=item.category,
                        description=item.description,
                        duration={"base_minutes": item.duration_minutes},
                        pricing={"base_price": item.base_price},
                        is_active=item.is_active,
                    )
                    await service_model.create(service_data)
                    created += 1

            except Exception as e:
                errors.append(f"{item.name}: {str(e)}")

        # Invalidate cache after bulk import
        await invalidate_service_cache(salon_id)

        logger.info(
            "Bulk import completed",
            salon_id=salon_id,
            total=len(request.services),
            created=created,
            updated=updated,
            skipped=skipped,
        )

        return BulkImportResponse(
            total=len(request.services),
            created=created,
            updated=updated,
            skipped=skipped,
            errors=errors,
        )

    except Exception as e:
        logger.error("Failed to bulk import services", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to import services",
        )
