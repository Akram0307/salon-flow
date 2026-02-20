"""Booking Firestore Model.

Handles all database operations for booking entities.
"""
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any, Tuple

from google.cloud.firestore_v1.base_query import FieldFilter
import structlog

from app.models.base import FirestoreBase
from app.schemas import (
    Booking,
    BookingCreate,
    BookingUpdate,
    BookingStatus,
)
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class BookingModel(FirestoreBase[Booking, BookingCreate, BookingUpdate]):
    """Model for booking operations.
    
    Provides CRUD operations and specialized queries for booking entities.
    Bookings represent appointments with customers for services.
    
    Attributes:
        collection_name: Firestore collection name ('bookings')
        model: Pydantic model for Booking
        create_schema: Pydantic schema for creating bookings
        update_schema: Pydantic schema for updating bookings
    
    Example:
        booking_model = BookingModel()
        bookings = await booking_model.get_by_date(date.today(), salon_id="salon_123")
    """
    
    collection_name = "bookings"
    model = Booking
    create_schema = BookingCreate
    update_schema = BookingUpdate
    
    async def get_by_date(
        self,
        booking_date: date,
        salon_id: str,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Booking]:
        """Get all bookings for a specific date.
        
        Args:
            booking_date: Date to query
            salon_id: Salon ID for multi-tenant filtering
            status: Optional status filter
            limit: Maximum results to return
            
        Returns:
            List of bookings for the date
        
        Example:
            bookings = await booking_model.get_by_date(date.today(), salon_id="salon_123")
        """
        filters = [("date", "==", booking_date.isoformat())]
        
        if status:
            filters.append(("status", "==", status))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="time.start_time",
            limit=limit,
        )
    
    async def get_by_customer(
        self,
        customer_id: str,
        salon_id: str,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Booking]:
        """Get all bookings for a customer.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID for multi-tenant filtering
            status: Optional status filter
            limit: Maximum results to return
            
        Returns:
            List of bookings for the customer
        """
        filters = [("customer_id", "==", customer_id)]
        
        if status:
            filters.append(("status", "==", status))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="date",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_by_staff(
        self,
        staff_id: str,
        salon_id: str,
        booking_date: Optional[date] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Booking]:
        """Get all bookings for a staff member.
        
        Args:
            staff_id: Staff document ID
            salon_id: Salon ID for multi-tenant filtering
            booking_date: Optional date filter
            status: Optional status filter
            limit: Maximum results to return
            
        Returns:
            List of bookings for the staff member
        """
        filters = [("staff_id", "==", staff_id)]
        
        if booking_date:
            filters.append(("date", "==", booking_date.isoformat()))
        
        if status:
            filters.append(("status", "==", status))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="date",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_upcoming(
        self,
        salon_id: str,
        customer_id: Optional[str] = None,
        days: int = 7,
        limit: int = 50,
    ) -> List[Booking]:
        """Get upcoming bookings.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            customer_id: Optional customer ID filter
            days: Number of days to look ahead
            limit: Maximum results to return
            
        Returns:
            List of upcoming bookings
        """
        today = date.today()
        end_date = today + timedelta(days=days)
        
        filters = [
            ("date", ">=", today.isoformat()),
            ("date", "<=", end_date.isoformat()),
            ("status", "in", ["pending", "confirmed"]),
        ]
        
        if customer_id:
            filters.append(("customer_id", "==", customer_id))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="date",
            limit=limit,
        )
    
    async def check_availability(
        self,
        salon_id: str,
        staff_id: str,
        booking_date: date,
        start_time: time,
        end_time: time,
        exclude_booking_id: Optional[str] = None,
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """Check if a time slot is available for a staff member.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            staff_id: Staff document ID
            booking_date: Date to check
            start_time: Proposed start time
            end_time: Proposed end time
            exclude_booking_id: Booking ID to exclude from conflict check
            
        Returns:
            Tuple of (is_available, conflicting_bookings)
        """
        try:
            # Get all bookings for the staff on that date
            filters = [
                ("staff_id", "==", staff_id),
                ("date", "==", booking_date.isoformat()),
                ("status", "in", ["pending", "confirmed", "checked_in", "in_progress"]),
            ]
            
            bookings = await self.list(
                salon_id=salon_id,
                filters=filters,
                limit=100,
            )
            
            # Convert times to comparable format
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = end_time.hour * 60 + end_time.minute
            
            conflicts = []
            for booking in bookings:
                # Skip the booking being edited
                if exclude_booking_id and booking.id == exclude_booking_id:
                    continue
                
                # Check for time overlap
                booking_start = booking.time.start_time
                booking_end = booking.time.end_time
                
                booking_start_minutes = booking_start.hour * 60 + booking_start.minute
                booking_end_minutes = booking_end.hour * 60 + booking_end.minute
                
                # Overlap condition: start < existing_end AND end > existing_start
                if start_minutes < booking_end_minutes and end_minutes > booking_start_minutes:
                    conflicts.append({
                        "booking_id": booking.id,
                        "start_time": booking_start.isoformat(),
                        "end_time": booking_end.isoformat(),
                    })
            
            return len(conflicts) == 0, conflicts
            
        except Exception as e:
            logger.error(
                "Failed to check availability",
                staff_id=staff_id,
                date=booking_date,
                error=str(e),
            )
            raise
    
    async def get_by_status(
        self,
        status: str,
        salon_id: str,
        booking_date: Optional[date] = None,
        limit: int = 100,
    ) -> List[Booking]:
        """Get bookings by status.
        
        Args:
            status: Booking status to filter
            salon_id: Salon ID for multi-tenant filtering
            booking_date: Optional date filter
            limit: Maximum results to return
            
        Returns:
            List of bookings with the status
        """
        filters = [("status", "==", status)]
        
        if booking_date:
            filters.append(("date", "==", booking_date.isoformat()))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="created_at",
            limit=limit,
        )
    
    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        salon_id: str,
        status: Optional[str] = None,
        limit: int = 200,
    ) -> List[Booking]:
        """Get bookings within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            salon_id: Salon ID for multi-tenant filtering
            status: Optional status filter
            limit: Maximum results to return
            
        Returns:
            List of bookings in the date range
        """
        filters = [
            ("date", ">=", start_date.isoformat()),
            ("date", "<=", end_date.isoformat()),
        ]
        
        if status:
            filters.append(("status", "==", status))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="date",
            limit=limit,
        )
    
    async def update_status(
        self,
        booking_id: str,
        status: BookingStatus,
        salon_id: str,
    ) -> Optional[Booking]:
        """Update booking status.
        
        Args:
            booking_id: Booking document ID
            status: New status
            salon_id: Salon ID for verification
            
        Returns:
            Updated booking if successful
        """
        booking = await self.get(booking_id)
        if not booking or booking.salon_id != salon_id:
            return None
        
        update_data = {
            "status": status.value if isinstance(status, BookingStatus) else status,
            "status_history": {
                "status": status.value if isinstance(status, BookingStatus) else status,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
        
        return await self.update(booking_id, update_data)
    
    async def cancel_booking(
        self,
        booking_id: str,
        reason: str,
        cancelled_by: str,
        salon_id: str,
    ) -> Optional[Booking]:
        """Cancel a booking.
        
        Args:
            booking_id: Booking document ID
            reason: Cancellation reason
            cancelled_by: User ID who cancelled
            salon_id: Salon ID for verification
            
        Returns:
            Updated booking if successful
        """
        booking = await self.get(booking_id)
        if not booking or booking.salon_id != salon_id:
            return None
        
        update_data = {
            "status": "cancelled",
            "cancellation": {
                "reason": reason,
                "cancelled_by": cancelled_by,
                "cancelled_at": datetime.utcnow().isoformat(),
            },
        }
        
        return await self.update(booking_id, update_data)
    
    async def check_in(
        self,
        booking_id: str,
        salon_id: str,
        arrival_time: Optional[time] = None,
    ) -> Optional[Booking]:
        """Check in a customer for their booking.
        
        Args:
            booking_id: Booking document ID
            salon_id: Salon ID for verification
            arrival_time: Actual arrival time (defaults to now)
            
        Returns:
            Updated booking if successful
        """
        booking = await self.get(booking_id)
        if not booking or booking.salon_id != salon_id:
            return None
        
        update_data = {
            "status": "checked_in",
            "check_in": {
                "actual_arrival_time": (arrival_time or time.now()).isoformat(),
                "checked_in_at": datetime.utcnow().isoformat(),
            },
        }
        
        return await self.update(booking_id, update_data)
    
    async def start_service(
        self,
        booking_id: str,
        salon_id: str,
        start_time: Optional[time] = None,
    ) -> Optional[Booking]:
        """Mark booking as in progress.
        
        Args:
            booking_id: Booking document ID
            salon_id: Salon ID for verification
            start_time: Actual start time (defaults to now)
            
        Returns:
            Updated booking if successful
        """
        booking = await self.get(booking_id)
        if not booking or booking.salon_id != salon_id:
            return None
        
        update_data = {
            "status": "in_progress",
            "service_start_time": (start_time or time.now()).isoformat(),
        }
        
        return await self.update(booking_id, update_data)
    
    async def complete_booking(
        self,
        booking_id: str,
        salon_id: str,
        end_time: Optional[time] = None,
    ) -> Optional[Booking]:
        """Mark booking as completed.
        
        Args:
            booking_id: Booking document ID
            salon_id: Salon ID for verification
            end_time: Actual end time (defaults to now)
            
        Returns:
            Updated booking if successful
        """
        booking = await self.get(booking_id)
        if not booking or booking.salon_id != salon_id:
            return None
        
        update_data = {
            "status": "completed",
            "service_end_time": (end_time or time.now()).isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
        }
        
        return await self.update(booking_id, update_data)
    
    async def get_today_bookings(
        self,
        salon_id: str,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Booking]:
        """Get all bookings for today.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            status: Optional status filter
            limit: Maximum results to return
            
        Returns:
            List of today's bookings
        """
        return await self.get_by_date(
            booking_date=date.today(),
            salon_id=salon_id,
            status=status,
            limit=limit,
        )
    
    async def get_no_shows(
        self,
        salon_id: str,
        booking_date: Optional[date] = None,
        limit: int = 50,
    ) -> List[Booking]:
        """Get no-show bookings.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            booking_date: Optional date filter
            limit: Maximum results to return
            
        Returns:
            List of no-show bookings
        """
        return await self.get_by_status(
            status="no_show",
            salon_id=salon_id,
            booking_date=booking_date,
            limit=limit,
        )
    
    async def get_booking_count(
        self,
        salon_id: str,
        booking_date: Optional[date] = None,
        status: Optional[str] = None,
    ) -> int:
        """Get booking count for a salon.
        
        Args:
            salon_id: Salon ID
            booking_date: Optional date filter
            status: Optional status filter
            
        Returns:
            Number of bookings
        """
        filters = []
        if booking_date:
            filters.append(("date", "==", booking_date.isoformat()))
        if status:
            filters.append(("status", "==", status))
        
        return await self.count(
            salon_id=salon_id,
            filters=filters if filters else None,
        )
    
    async def get_revenue_by_date(
        self,
        booking_date: date,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Get total revenue from completed bookings for a date.
        
        Args:
            booking_date: Date to query
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            Revenue summary dictionary
        """
        try:
            bookings = await self.get_by_date(
                booking_date=booking_date,
                salon_id=salon_id,
                status="completed",
                limit=500,
            )
            
            total_revenue = 0
            total_gst = 0
            service_count = 0
            
            for booking in bookings:
                if booking.pricing:
                    total_revenue += float(booking.pricing.total_amount or 0)
                    total_gst += float(booking.pricing.gst_amount or 0)
                if booking.services:
                    service_count += len(booking.services)
            
            
            return {
                "date": booking_date.isoformat(),
                "total_revenue": total_revenue,
                "total_gst": total_gst,
                "booking_count": len(bookings),
                "service_count": service_count,
            }
            
        except Exception as e:
            logger.error(
                "Failed to get revenue by date",
                date=booking_date,
                salon_id=salon_id,
                error=str(e),
            )
            raise
    
    async def reschedule_booking(
        self,
        booking_id: str,
        new_date: date,
        new_start_time: time,
        new_end_time: time,
        salon_id: str,
        reason: Optional[str] = None,
    ) -> Optional[Booking]:
        """Reschedule a booking to a new date/time.
        
        Args:
            booking_id: Booking document ID
            new_date: New booking date
            new_start_time: New start time
            new_end_time: New end time
            salon_id: Salon ID for verification
            reason: Optional reschedule reason
            
        Returns:
            Updated booking if successful
        """
        booking = await self.get(booking_id)
        if not booking or booking.salon_id != salon_id:
            return None
        
        update_data = {
            "date": new_date.isoformat(),
            "time": {
                "start_time": new_start_time.isoformat(),
                "end_time": new_end_time.isoformat(),
            },
            "reschedule": {
                "previous_date": booking.date.isoformat() if booking.date else None,
                "previous_time": booking.time.model_dump() if booking.time else None,
                "reason": reason,
                "rescheduled_at": datetime.utcnow().isoformat(),
            },
        }
        
        return await self.update(booking_id, update_data)


    async def search_bookings(
        self,
        salon_id: str,
        date: Optional[date] = None,
        status: Optional[str] = None,
        staff_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> "PaginatedResponse":
        """Search bookings with filters and pagination.

        Args:
            salon_id: Salon ID for multi-tenant filtering
            date: Filter by booking date
            status: Filter by booking status
            staff_id: Filter by staff ID
            customer_id: Filter by customer ID
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Paginated response with booking summaries
        """
        filters = []

        if date:
            filters.append(("date", "==", date.isoformat()))

        if status:
            filters.append(("status", "==", status))

        if staff_id:
            filters.append(("staff_id", "==", staff_id))

        if customer_id:
            filters.append(("customer_id", "==", customer_id))

        # Get paginated results using the base class paginate method
        result = await self.paginate(
            salon_id=salon_id,
            filters=filters if filters else None,
            order_by="date",
            order_direction="DESCENDING",
            page=page,
            page_size=page_size,
        )

        return result
