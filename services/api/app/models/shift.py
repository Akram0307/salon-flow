"""Shift Firestore Model.

Handles all database operations for shift and leave management entities.
"""
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any

from google.cloud.firestore_v1.base_query import FieldFilter
import structlog

from app.models.base import FirestoreBase
from app.schemas import (
    Shift,
    ShiftCreate,
    ShiftUpdate,
    ShiftStatus,
    LeaveRequest,
    LeaveRequestCreate,
    LeaveRequestUpdate,
    LeaveStatus,
)
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class ShiftModel(FirestoreBase[Shift, ShiftCreate, ShiftUpdate]):
    """Model for shift operations.
    
    Provides CRUD operations and specialized queries for shift entities.
    Shifts define staff working schedules including start/end times and breaks.
    
    Attributes:
        collection_name: Firestore collection name ('shifts')
        model: Pydantic model for Shift
        create_schema: Pydantic schema for creating shifts
        update_schema: Pydantic schema for updating shifts
    
    Example:
        shift_model = ShiftModel()
        shifts = await shift_model.get_staff_shifts("staff_123", salon_id="salon_123")
    """
    
    collection_name = "shifts"
    model = Shift
    create_schema = ShiftCreate
    update_schema = ShiftUpdate
    
    async def get_staff_shifts(
        self,
        staff_id: str,
        salon_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
    ) -> List[Shift]:
        """Get all shifts for a staff member.
        
        Args:
            staff_id: Staff document ID
            salon_id: Salon ID for multi-tenant filtering
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum results to return
            
        Returns:
            List of shifts for the staff member
        
        Example:
            shifts = await shift_model.get_staff_shifts("staff_123", salon_id="salon_123")
        """
        filters = [("staff_id", "==", staff_id)]
        
        if start_date:
            filters.append(("date", ">=", start_date.isoformat()))
        if end_date:
            filters.append(("date", "<=", end_date.isoformat()))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="date",
            limit=limit,
        )
    
    async def get_leave_requests(
        self,
        salon_id: str,
        status: Optional[str] = None,
        staff_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get leave requests for a salon.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            status: Optional status filter (pending, approved, rejected)
            staff_id: Optional staff ID filter
            limit: Maximum results to return
            
        Returns:
            List of leave requests
        """
        # Leave requests are stored in a subcollection or separate collection
        # For this implementation, we'll query shifts with leave_request field
        filters = [("has_leave_request", "==", True)]
        
        if status:
            filters.append(("leave_request.status", "==", status))
        if staff_id:
            filters.append(("staff_id", "==", staff_id))
        
        shifts = await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="leave_request.requested_at",
            order_direction="DESCENDING",
            limit=limit,
        )
        
        # Extract leave request data
        leave_requests = []
        for shift in shifts:
            if hasattr(shift, 'leave_request') and shift.leave_request:
                leave_requests.append({
                    "shift_id": shift.id,
                    "staff_id": shift.staff_id,
                    **shift.leave_request,
                })
        
        return leave_requests
    
    async def approve_leave(
        self,
        shift_id: str,
        salon_id: str,
        approved_by: str,
        notes: Optional[str] = None,
    ) -> Optional[Shift]:
        """Approve a leave request.
        
        Args:
            shift_id: Shift document ID
            salon_id: Salon ID for verification
            approved_by: User ID who approved
            notes: Optional approval notes
            
        Returns:
            Updated shift if successful
        """
        shift = await self.get(shift_id)
        if not shift or shift.salon_id != salon_id:
            return None
        
        update_data = {
            "status": "leave_approved",
            "leave_request.status": "approved",
            "leave_request.approved_by": approved_by,
            "leave_request.approved_at": datetime.utcnow().isoformat(),
        }
        
        if notes:
            update_data["leave_request.approval_notes"] = notes
        
        return await self.update(shift_id, update_data)
    
    async def reject_leave(
        self,
        shift_id: str,
        salon_id: str,
        rejected_by: str,
        reason: str,
    ) -> Optional[Shift]:
        """Reject a leave request.
        
        Args:
            shift_id: Shift document ID
            salon_id: Salon ID for verification
            rejected_by: User ID who rejected
            reason: Rejection reason
            
        Returns:
            Updated shift if successful
        """
        shift = await self.get(shift_id)
        if not shift or shift.salon_id != salon_id:
            return None
        
        update_data = {
            "status": "scheduled",
            "leave_request.status": "rejected",
            "leave_request.rejected_by": rejected_by,
            "leave_request.rejected_at": datetime.utcnow().isoformat(),
            "leave_request.rejection_reason": reason,
        }
        
        return await self.update(shift_id, update_data)
    
    async def get_shift_by_date(
        self,
        staff_id: str,
        shift_date: date,
        salon_id: str,
    ) -> Optional[Shift]:
        """Get a staff member's shift for a specific date.
        
        Args:
            staff_id: Staff document ID
            shift_date: Date to query
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            Shift if found, None otherwise
        """
        shifts = await self.list(
            salon_id=salon_id,
            filters=[
                ("staff_id", "==", staff_id),
                ("date", "==", shift_date.isoformat()),
            ],
            limit=1,
        )
        
        return shifts[0] if shifts else None
    
    async def get_weekly_schedule(
        self,
        staff_id: str,
        week_start: date,
        salon_id: str,
    ) -> List[Shift]:
        """Get a staff member's schedule for a week.
        
        Args:
            staff_id: Staff document ID
            week_start: Start date of the week
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            List of shifts for the week
        """
        week_end = week_start + timedelta(days=6)
        
        return await self.get_staff_shifts(
            staff_id=staff_id,
            salon_id=salon_id,
            start_date=week_start,
            end_date=week_end,
            limit=7,
        )
    
    async def get_available_staff(
        self,
        salon_id: str,
        target_date: date,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get staff available on a specific date and time.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            target_date: Date to check
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum results to return
            
        Returns:
            List of available staff with their shifts
        """
        shifts = await self.list(
            salon_id=salon_id,
            filters=[
                ("date", "==", target_date.isoformat()),
                ("status", "==", "scheduled"),
            ],
            limit=limit,
        )
        
        available = []
        for shift in shifts:
            # Check time overlap if specified
            if start_time and end_time and shift.start_time and shift.end_time:
                shift_start = shift.start_time
                shift_end = shift.end_time
                
                # Check if shift covers the requested time
                if shift_start <= start_time and shift_end >= end_time:
                    available.append({
                        "staff_id": shift.staff_id,
                        "shift_id": shift.id,
                        "shift_start": shift_start,
                        "shift_end": shift_end,
                    })
            else:
                available.append({
                    "staff_id": shift.staff_id,
                    "shift_id": shift.id,
                    "shift_start": shift.start_time,
                    "shift_end": shift.end_time,
                })
        
        return available
    
    async def create_shift(
        self,
        staff_id: str,
        salon_id: str,
        shift_date: date,
        start_time: time,
        end_time: time,
        break_duration: int = 30,
        notes: Optional[str] = None,
    ) -> Shift:
        """Create a new shift.
        
        Args:
            staff_id: Staff document ID
            salon_id: Salon ID
            shift_date: Shift date
            start_time: Shift start time
            end_time: Shift end time
            break_duration: Break duration in minutes
            notes: Optional shift notes
            
        Returns:
            Created shift
        """
        shift_data = {
            "staff_id": staff_id,
            "salon_id": salon_id,
            "date": shift_date.isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "break_duration": break_duration,
            "status": "scheduled",
            "notes": notes,
        }
        
        return await self.create(shift_data)
    
    async def update_shift_status(
        self,
        shift_id: str,
        status: ShiftStatus,
        salon_id: str,
        notes: Optional[str] = None,
    ) -> Optional[Shift]:
        """Update shift status.
        
        Args:
            shift_id: Shift document ID
            status: New status
            salon_id: Salon ID for verification
            notes: Optional status change notes
            
        Returns:
            Updated shift if successful
        """
        shift = await self.get(shift_id)
        if not shift or shift.salon_id != salon_id:
            return None
        
        update_data = {
            "status": status.value if isinstance(status, ShiftStatus) else status,
            "status_updated_at": datetime.utcnow().isoformat(),
        }
        
        if notes:
            update_data["status_notes"] = notes
        
        return await self.update(shift_id, update_data)
    
    async def clock_in(
        self,
        shift_id: str,
        salon_id: str,
        actual_time: Optional[time] = None,
    ) -> Optional[Shift]:
        """Record staff clock in.
        
        Args:
            shift_id: Shift document ID
            salon_id: Salon ID for verification
            actual_time: Actual clock in time (defaults to now)
            
        Returns:
            Updated shift if successful
        """
        shift = await self.get(shift_id)
        if not shift or shift.salon_id != salon_id:
            return None
        
        update_data = {
            "status": "in_progress",
            "actual_start_time": (actual_time or time.now()).isoformat(),
            "clocked_in_at": datetime.utcnow().isoformat(),
        }
        
        return await self.update(shift_id, update_data)
    
    async def clock_out(
        self,
        shift_id: str,
        salon_id: str,
        actual_time: Optional[time] = None,
    ) -> Optional[Shift]:
        """Record staff clock out.
        
        Args:
            shift_id: Shift document ID
            salon_id: Salon ID for verification
            actual_time: Actual clock out time (defaults to now)
            
        Returns:
            Updated shift if successful
        """
        shift = await self.get(shift_id)
        if not shift or shift.salon_id != salon_id:
            return None
        
        update_data = {
            "status": "completed",
            "actual_end_time": (actual_time or time.now()).isoformat(),
            "clocked_out_at": datetime.utcnow().isoformat(),
        }
        
        return await self.update(shift_id, update_data)
    
    async def request_leave(
        self,
        shift_id: str,
        salon_id: str,
        reason: str,
        leave_type: str = "personal",
    ) -> Optional[Shift]:
        """Request leave for a shift.
        
        Args:
            shift_id: Shift document ID
            salon_id: Salon ID for verification
            reason: Leave reason
            leave_type: Type of leave (personal, sick, emergency)
            
        Returns:
            Updated shift if successful
        """
        shift = await self.get(shift_id)
        if not shift or shift.salon_id != salon_id:
            return None
        
        update_data = {
            "has_leave_request": True,
            "leave_request": {
                "type": leave_type,
                "reason": reason,
                "status": "pending",
                "requested_at": datetime.utcnow().isoformat(),
            },
        }
        
        return await self.update(shift_id, update_data)
    
    async def get_shift_stats(
        self,
        staff_id: str,
        salon_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Get shift statistics for a staff member.
        
        Args:
            staff_id: Staff document ID
            salon_id: Salon ID for multi-tenant filtering
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Shift statistics dictionary
        """
        shifts = await self.get_staff_shifts(
            staff_id=staff_id,
            salon_id=salon_id,
            start_date=start_date,
            end_date=end_date,
            limit=100,
        )
        
        total_shifts = len(shifts)
        completed = sum(1 for s in shifts if s.status == "completed")
        cancelled = sum(1 for s in shifts if s.status == "cancelled")
        leave_days = sum(1 for s in shifts if s.status in ["leave_approved", "leave_pending"])
        
        total_hours = 0
        for shift in shifts:
            if shift.start_time and shift.end_time:
                start = shift.start_time if isinstance(shift.start_time, time) else time.fromisoformat(shift.start_time)
                end = shift.end_time if isinstance(shift.end_time, time) else time.fromisoformat(shift.end_time)
                hours = (end.hour * 60 + end.minute - start.hour * 60 - start.minute) / 60
                total_hours += max(0, hours)
        
        return {
            "staff_id": staff_id,
            "total_shifts": total_shifts,
            "completed_shifts": completed,
            "cancelled_shifts": cancelled,
            "leave_days": leave_days,
            "total_hours": round(total_hours, 2),
            "average_hours_per_shift": round(total_hours / completed, 2) if completed > 0 else 0,
        }
    
    async def bulk_create_shifts(
        self,
        salon_id: str,
        shifts_data: List[Dict[str, Any]],
    ) -> List[Shift]:
        """Bulk create shifts.
        
        Args:
            salon_id: Salon ID
            shifts_data: List of shift data dictionaries
            
        Returns:
            List of created shifts
        """
        created_shifts = []
        
        for data in shifts_data:
            data["salon_id"] = salon_id
            shift = await self.create(data)
            created_shifts.append(shift)
        
        return created_shifts
