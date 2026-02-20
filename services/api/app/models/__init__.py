"""Firestore Models for Salon Flow SaaS.

This module provides async CRUD operations for all Firestore collections.
Each model extends FirestoreBase with specialized domain methods.
"""

from app.models.base import FirestoreBase
from app.models.salon import SalonModel
from app.models.customer import CustomerModel
from app.models.staff import StaffModel
from app.models.service import ServiceModel
from app.models.booking import BookingModel
from app.models.payment import PaymentModel
from app.models.membership import MembershipModel
from app.models.loyalty import LoyaltyModel
from app.models.resource import ResourceModel
from app.models.shift import ShiftModel

__all__ = [
    "FirestoreBase",
    "SalonModel",
    "CustomerModel",
    "StaffModel",
    "ServiceModel",
    "BookingModel",
    "PaymentModel",
    "MembershipModel",
    "LoyaltyModel",
    "ResourceModel",
    "ShiftModel",
]
