"""API Routes for Salon Flow.

This module exports all API routers for the Salon Flow application.
Each router handles a specific domain of the application.
"""
from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.tenants import router as tenants_router
from app.api.customers import router as customers_router
from app.api.staff import router as staff_router
from app.api.services import router as services_router
from app.api.bookings import router as bookings_router
from app.api.payments import router as payments_router
from app.api.memberships import router as memberships_router
from app.api.resources import router as resources_router
from app.api.shifts import router as shifts_router
from app.api.inventory import router as inventory_router
from app.api.loyalty import router as loyalty_router
from app.api.waitlist import router as waitlist_router
from app.api.feedback import router as feedback_router
from app.api.analytics import router as analytics_router
from app.api.integrations import router as integrations_router
from app.api.billing import router as billing_router

# Main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(tenants_router)
api_router.include_router(customers_router)
api_router.include_router(staff_router)
api_router.include_router(services_router)
api_router.include_router(bookings_router)
api_router.include_router(payments_router)
api_router.include_router(memberships_router)
api_router.include_router(resources_router)
api_router.include_router(shifts_router)
api_router.include_router(inventory_router)
api_router.include_router(loyalty_router)
api_router.include_router(waitlist_router)
api_router.include_router(feedback_router)
api_router.include_router(analytics_router)
api_router.include_router(integrations_router)
api_router.include_router(billing_router)

__all__ = [
    "api_router",
    "auth_router",
    "tenants_router",
    "customers_router",
    "staff_router",
    "services_router",
    "bookings_router",
    "payments_router",
    "memberships_router",
    "resources_router",
    "shifts_router",
    "inventory_router",
    "loyalty_router",
    "waitlist_router",
    "feedback_router",
    "analytics_router",
    "integrations_router",
    "billing_router",
]
