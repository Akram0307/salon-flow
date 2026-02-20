"""Waitlist API Router"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_current_user, require_role, get_salon_id
from app.schemas.waitlist import (
    WaitlistEntryCreate, WaitlistEntryUpdate, WaitlistEntryResponse,
    WaitlistSummary, WaitlistStatus, WaitlistPriority
)
from app.models.base import FirestoreBase
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Waitlist"])


class WaitlistEntry(FirestoreBase):
    """Waitlist entry model"""
    collection_name = "waitlist_entries"
    id_field = "entry_id"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.entry_id = data.get("entry_id", str(uuid.uuid4()))
        self.salon_id = data.get("salon_id", "")
        self.customer_id = data.get("customer_id", "")
        self.service_id = data.get("service_id", "")
        self.preferred_staff_id = data.get("preferred_staff_id")
        self.preferred_time_start = data.get("preferred_time_start")
        self.preferred_time_end = data.get("preferred_time_end")
        self.notes = data.get("notes")
        self.priority = data.get("priority", WaitlistPriority.NORMAL.value)
        self.queue_position = data.get("queue_position", 0)
        self.status = data.get("status", WaitlistStatus.WAITING.value)
        self.estimated_wait_minutes = data.get("estimated_wait_minutes")
        self.notified_at = data.get("notified_at")
        self.confirmed_at = data.get("confirmed_at")
        self.booking_id = data.get("booking_id")
        self.created_at = data.get("created_at", datetime.utcnow())
        self.updated_at = data.get("updated_at", datetime.utcnow())
    
    def to_dict(self):
        return {
            "id": self.entry_id,
            "salon_id": self.salon_id,
            "customer_id": self.customer_id,
            "service_id": self.service_id,
            "preferred_staff_id": self.preferred_staff_id,
            "preferred_time_start": self.preferred_time_start.isoformat() if self.preferred_time_start else None,
            "preferred_time_end": self.preferred_time_end.isoformat() if self.preferred_time_end else None,
            "notes": self.notes,
            "priority": self.priority,
            "queue_position": self.queue_position,
            "status": self.status,
            "estimated_wait_minutes": self.estimated_wait_minutes,
            "notified_at": self.notified_at.isoformat() if self.notified_at else None,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
            "booking_id": self.booking_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


async def _calculate_queue_position(salon_id: str, service_id: str = None) -> int:
    """Calculate next queue position"""
    entries = await WaitlistEntry.find_all(
        salon_id=salon_id,
        status=WaitlistStatus.WAITING.value
    )
    return len(entries) + 1


async def _estimate_wait_time(salon_id: str, queue_position: int) -> int:
    """Estimate wait time in minutes based on queue position"""
    # Average service time ~30 minutes
    avg_service_time = 30
    return queue_position * avg_service_time


@router.post("/", response_model=WaitlistEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_waitlist_entry(
    data: WaitlistEntryCreate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager", "receptionist"]))
):
    """Add customer to waitlist"""
    # Check if customer already in waitlist
    existing = await WaitlistEntry.find_all(
        customer_id=data.customer_id,
        salon_id=salon_id,
        status=WaitlistStatus.WAITING.value
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Customer already has an active waitlist entry"
        )
    
    queue_position = await _calculate_queue_position(salon_id, data.service_id)
    estimated_wait = await _estimate_wait_time(salon_id, queue_position)
    
    entry = WaitlistEntry(
        salon_id=salon_id,
        customer_id=data.customer_id,
        service_id=data.service_id,
        preferred_staff_id=data.preferred_staff_id,
        preferred_time_start=data.preferred_time_start,
        preferred_time_end=data.preferred_time_end,
        notes=data.notes,
        priority=data.priority.value if isinstance(data.priority, WaitlistPriority) else data.priority,
        queue_position=queue_position,
        estimated_wait_minutes=estimated_wait
    )
    await entry.save()
    
    return WaitlistEntryResponse(**entry.to_dict())


@router.get("/", response_model=List[WaitlistEntryResponse])
async def list_waitlist(
    status: Optional[WaitlistStatus] = Query(None),
    service_id: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """List waitlist entries"""
    filters = {"salon_id": salon_id}
    if status:
        filters["status"] = status.value
    if service_id:
        filters["service_id"] = service_id
    
    entries = await WaitlistEntry.find_all(**filters, limit=limit)
    
    # Sort by priority and queue position
    priority_order = {WaitlistPriority.VIP.value: 0, WaitlistPriority.HIGH.value: 1, WaitlistPriority.NORMAL.value: 2}
    entries.sort(key=lambda x: (priority_order.get(x.priority, 2), x.queue_position))
    
    return [WaitlistEntryResponse(**e.to_dict()) for e in entries]


@router.get("/{entry_id}", response_model=WaitlistEntryResponse)
async def get_waitlist_entry(
    entry_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """Get a specific waitlist entry"""
    entry = await WaitlistEntry.find_by_id(entry_id, salon_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    return WaitlistEntryResponse(**entry.to_dict())


@router.put("/{entry_id}", response_model=WaitlistEntryResponse)
async def update_waitlist_entry(
    entry_id: str,
    data: WaitlistEntryUpdate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager", "receptionist"]))
):
    """Update a waitlist entry"""
    entry = await WaitlistEntry.find_by_id(entry_id, salon_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if isinstance(value, WaitlistPriority):
            value = value.value
        elif isinstance(value, WaitlistStatus):
            value = value.value
        setattr(entry, field, value)
    
    entry.updated_at = datetime.utcnow()
    await entry.save()
    
    return WaitlistEntryResponse(**entry.to_dict())


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_waitlist_entry(
    entry_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager", "receptionist"]))
):
    """Cancel a waitlist entry"""
    entry = await WaitlistEntry.find_by_id(entry_id, salon_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    
    entry.status = WaitlistStatus.CANCELLED.value
    entry.updated_at = datetime.utcnow()
    await entry.save()


@router.post("/{entry_id}/notify", response_model=WaitlistEntryResponse)
async def notify_waitlist_entry(
    entry_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager", "receptionist"]))
):
    """Mark customer as notified for slot availability"""
    entry = await WaitlistEntry.find_by_id(entry_id, salon_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    
    if entry.status != WaitlistStatus.WAITING.value:
        raise HTTPException(status_code=400, detail="Entry is not in waiting status")
    
    entry.status = WaitlistStatus.NOTIFIED.value
    entry.notified_at = datetime.utcnow()
    entry.updated_at = datetime.utcnow()
    await entry.save()
    
    return WaitlistEntryResponse(**entry.to_dict())


@router.post("/{entry_id}/confirm", response_model=WaitlistEntryResponse)
async def confirm_waitlist_entry(
    entry_id: str,
    booking_id: str = Query(..., description="ID of the created booking"),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager", "receptionist"]))
):
    """Confirm waitlist entry with a booking"""
    entry = await WaitlistEntry.find_by_id(entry_id, salon_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    
    entry.status = WaitlistStatus.CONFIRMED.value
    entry.booking_id = booking_id
    entry.confirmed_at = datetime.utcnow()
    entry.updated_at = datetime.utcnow()
    await entry.save()
    
    return WaitlistEntryResponse(**entry.to_dict())


@router.post("/expire", response_model=int)
async def expire_old_entries(
    max_wait_hours: int = Query(4, description="Maximum wait time in hours before expiry"),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Expire waitlist entries older than specified hours"""
    cutoff = datetime.utcnow() - timedelta(hours=max_wait_hours)
    
    entries = await WaitlistEntry.find_all(
        salon_id=salon_id,
        status=WaitlistStatus.WAITING.value
    )
    
    expired_count = 0
    for entry in entries:
        if entry.created_at < cutoff:
            entry.status = WaitlistStatus.EXPIRED.value
            entry.updated_at = datetime.utcnow()
            await entry.save()
            expired_count += 1
    
    return expired_count


@router.get("/summary", response_model=WaitlistSummary)
async def get_waitlist_summary(
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """Get waitlist summary statistics"""
    entries = await WaitlistEntry.find_all(
        salon_id=salon_id,
        status=WaitlistStatus.WAITING.value
    )
    
    total_waiting = len(entries)
    
    # Calculate average wait time
    if entries:
        avg_wait = sum(e.estimated_wait_minutes or 0 for e in entries) // len(entries)
        oldest = min(e.created_at for e in entries)
        oldest_minutes = int((datetime.utcnow() - oldest).total_seconds() / 60)
    else:
        avg_wait = 0
        oldest_minutes = 0
    
    # By service
    by_service = {}
    for e in entries:
        by_service[e.service_id] = by_service.get(e.service_id, 0) + 1
    
    # By priority
    by_priority = {}
    for e in entries:
        by_priority[e.priority] = by_priority.get(e.priority, 0) + 1
    
    return WaitlistSummary(
        total_waiting=total_waiting,
        average_wait_time=avg_wait,
        by_service=by_service,
        by_priority=by_priority,
        oldest_entry_minutes=oldest_minutes
    )
