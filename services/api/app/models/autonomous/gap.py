"""Gap Detection Firestore Model.

Manages schedule gaps and optimization opportunities.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

import structlog

from app.models.base import FirestoreBase

logger = structlog.get_logger()


class GapStatus(str, Enum):
    """Status of schedule gaps."""
    OPEN = "open"
    FILLED = "filled"
    EXPIRED = "expired"
    IGNORED = "ignored"


class GapPriority(str, Enum):
    """Priority levels for gaps."""
    LOW = "low"  # < 30 min
    MEDIUM = "medium"  # 30-60 min
    HIGH = "high"  # 60-120 min
    CRITICAL = "critical"  # > 120 min


class GapModel(FirestoreBase):
    """Model for gap detection operations.
    
    Tracks schedule gaps, calculates fill potential,
    and manages gap lifecycle.
    """
    
    collection_name = "schedule_gaps"
    
    async def get_open_gaps(
        self,
        salon_id: str,
        date: Optional[date] = None,
        min_duration_minutes: int = 30,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get open gaps for a date.
        
        Args:
            salon_id: Salon ID
            date: Target date (defaults to today)
            min_duration_minutes: Minimum gap duration
            limit: Maximum results
            
        Returns:
            List of open gaps
        """
        target_date = date or datetime.utcnow().date()
        
        return await self.list(
            salon_id=salon_id,
            filters=[
                ("status", "==", GapStatus.OPEN.value),
                ("date", "==", target_date.isoformat()),
                ("duration_minutes", ">=", min_duration_minutes),
            ],
            order_by="duration_minutes",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_gaps_by_staff(
        self,
        staff_id: str,
        salon_id: str,
        date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """Get gaps for a specific staff member.
        
        Args:
            staff_id: Staff document ID
            salon_id: Salon ID
            date: Target date
            
        Returns:
            List of gaps
        """
        filters = [("staff_id", "==", staff_id)]
        
        if date:
            filters.append(("date", "==", date.isoformat()))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="start_time",
            limit=50,
        )
    
    async def create_gap(
        self,
        salon_id: str,
        staff_id: str,
        staff_name: str,
        date: date,
        start_time: datetime,
        end_time: datetime,
        duration_minutes: int,
        potential_revenue: float,
        services_fittable: List[str],
    ) -> Dict[str, Any]:
        """Create a new gap record.
        
        Args:
            salon_id: Salon ID
            staff_id: Staff document ID
            staff_name: Staff name
            date: Gap date
            start_time: Gap start time
            end_time: Gap end time
            duration_minutes: Gap duration
            potential_revenue: Estimated revenue if filled
            services_fittable: Services that can fit
            
        Returns:
            Created gap
        """
        now = datetime.utcnow()
        
        # Determine priority
        if duration_minutes >= 120:
            priority = GapPriority.CRITICAL
        elif duration_minutes >= 60:
            priority = GapPriority.HIGH
        elif duration_minutes >= 30:
            priority = GapPriority.MEDIUM
        else:
            priority = GapPriority.LOW
        
        gap_data = {
            "salon_id": salon_id,
            "staff_id": staff_id,
            "staff_name": staff_name,
            "date": date.isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_minutes": duration_minutes,
            "priority": priority.value,
            "status": GapStatus.OPEN.value,
            "potential_revenue": potential_revenue,
            "services_fittable": services_fittable,
            "fill_attempts": 0,
            "last_attempt_at": None,
            "filled_by": None,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        
        return await self.create(gap_data)
    
    async def mark_filled(
        self,
        gap_id: str,
        booking_id: str,
        customer_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Mark gap as filled.
        
        Args:
            gap_id: Gap document ID
            booking_id: Booking that filled the gap
            customer_id: Customer who booked
            
        Returns:
            Updated gap
        """
        now = datetime.utcnow()
        
        update_data = {
            "status": GapStatus.FILLED.value,
            "filled_by": {
                "booking_id": booking_id,
                "customer_id": customer_id,
                "filled_at": now.isoformat(),
            },
            "updated_at": now.isoformat(),
        }
        
        return await self.update(gap_id, update_data)
    
    async def mark_expired(
        self,
        gap_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Mark gap as expired.
        
        Args:
            gap_id: Gap document ID
            
        Returns:
            Updated gap
        """
        update_data = {
            "status": GapStatus.EXPIRED.value,
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        return await self.update(gap_id, update_data)
    
    async def increment_attempts(
        self,
        gap_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Increment fill attempts counter.
        
        Args:
            gap_id: Gap document ID
            
        Returns:
            Updated gap
        """
        gap = await self.get(gap_id)
        if not gap:
            return None
        
        update_data = {
            "fill_attempts": gap.get("fill_attempts", 0) + 1,
            "last_attempt_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        return await self.update(gap_id, update_data)
    
    async def get_gap_stats(
        self,
        salon_id: str,
        date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Get gap statistics for a date.
        
        Args:
            salon_id: Salon ID
            date: Target date
            
        Returns:
            Gap statistics
        """
        target_date = date or datetime.utcnow().date()
        
        gaps = await self.list(
            salon_id=salon_id,
            filters=[("date", "==", target_date.isoformat())],
            limit=200,
        )
        
        stats = {
            "date": target_date.isoformat(),
            "total_gaps": len(gaps),
            "by_status": {},
            "by_priority": {},
            "total_duration_minutes": 0,
            "total_potential_revenue": 0,
            "filled_revenue": 0,
            "fill_rate": 0,
        }
        
        filled_count = 0
        
        for gap in gaps:
            # By status
            status = gap.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # By priority
            priority = gap.get("priority", "unknown")
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
            
            # Totals
            stats["total_duration_minutes"] += gap.get("duration_minutes", 0)
            stats["total_potential_revenue"] += gap.get("potential_revenue", 0)
            
            if status == GapStatus.FILLED.value:
                filled_count += 1
                stats["filled_revenue"] += gap.get("potential_revenue", 0)
        
        if stats["total_gaps"] > 0:
            stats["fill_rate"] = filled_count / stats["total_gaps"]
        
        return stats
    
    async def get_high_priority_gaps(
        self,
        salon_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get high priority gaps for immediate action.
        
        Args:
            salon_id: Salon ID
            limit: Maximum results
            
        Returns:
            List of high priority gaps
        """
        return await self.list(
            salon_id=salon_id,
            filters=[
                ("status", "==", GapStatus.OPEN.value),
                ("priority", "in", [GapPriority.HIGH.value, GapPriority.CRITICAL.value]),
            ],
            order_by="duration_minutes",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def cleanup_expired_gaps(
        self,
        salon_id: str,
        older_than_hours: int = 24,
    ) -> int:
        """Mark old open gaps as expired.
        
        Args:
            salon_id: Salon ID
            older_than_hours: Hours after which to expire
            
        Returns:
            Number of gaps expired
        """
        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
        
        gaps = await self.list(
            salon_id=salon_id,
            filters=[
                ("status", "==", GapStatus.OPEN.value),
                ("created_at", "<", cutoff.isoformat()),
            ],
            limit=100,
        )
        
        count = 0
        for gap in gaps:
            result = await self.mark_expired(gap["id"])
            if result:
                count += 1
        
        return count
