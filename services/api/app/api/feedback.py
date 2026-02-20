"""Feedback and Reviews API Router"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_current_user, require_role, get_salon_id
from app.schemas.feedback import (
    FeedbackCreate, FeedbackUpdate, FeedbackResponse,
    FeedbackReplyCreate, FeedbackReplyResponse, FeedbackSummary,
    FeedbackType, FeedbackStatus, FeedbackPriority
)
from app.models.base import FirestoreBase
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feedback", tags=["Feedback"])


class Feedback(FirestoreBase):
    """Feedback model"""
    collection_name = "feedback"
    id_field = "feedback_id"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.feedback_id = data.get("feedback_id", str(uuid.uuid4()))
        self.salon_id = data.get("salon_id", "")
        self.customer_id = data.get("customer_id", "")
        self.booking_id = data.get("booking_id")
        self.feedback_type = data.get("feedback_type", FeedbackType.REVIEW.value)
        self.rating = data.get("rating")
        self.title = data.get("title")
        self.comment = data.get("comment")
        self.staff_id = data.get("staff_id")
        self.service_id = data.get("service_id")
        self.status = data.get("status", FeedbackStatus.PENDING.value)
        self.priority = data.get("priority", FeedbackPriority.MEDIUM.value)
        self.internal_notes = data.get("internal_notes")
        self.resolution_notes = data.get("resolution_notes")
        self.resolved_by = data.get("resolved_by")
        self.resolved_at = data.get("resolved_at")
        self.created_at = data.get("created_at", datetime.utcnow())
        self.updated_at = data.get("updated_at", datetime.utcnow())
    
    def to_dict(self):
        return {
            "id": self.feedback_id,
            "salon_id": self.salon_id,
            "customer_id": self.customer_id,
            "booking_id": self.booking_id,
            "feedback_type": self.feedback_type,
            "rating": self.rating,
            "title": self.title,
            "comment": self.comment,
            "staff_id": self.staff_id,
            "service_id": self.service_id,
            "status": self.status,
            "priority": self.priority,
            "internal_notes": self.internal_notes,
            "resolution_notes": self.resolution_notes,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FeedbackReply(FirestoreBase):
    """Feedback reply model"""
    collection_name = "feedback_replies"
    id_field = "reply_id"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.reply_id = data.get("reply_id", str(uuid.uuid4()))
        self.feedback_id = data.get("feedback_id", "")
        self.salon_id = data.get("salon_id", "")
        self.reply_text = data.get("reply_text", "")
        self.is_public = data.get("is_public", False)
        self.replied_by = data.get("replied_by")
        self.created_at = data.get("created_at", datetime.utcnow())
    
    def to_dict(self):
        return {
            "id": self.reply_id,
            "feedback_id": self.feedback_id,
            "salon_id": self.salon_id,
            "reply_text": self.reply_text,
            "is_public": self.is_public,
            "replied_by": self.replied_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    data: FeedbackCreate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """Submit customer feedback"""
    # Determine priority based on type and rating
    priority = FeedbackPriority.MEDIUM.value
    if data.feedback_type == FeedbackType.COMPLAINT:
        priority = FeedbackPriority.HIGH.value
    elif data.rating and data.rating <= 2:
        priority = FeedbackPriority.HIGH.value
    elif data.feedback_type == FeedbackType.SUGGESTION:
        priority = FeedbackPriority.LOW.value
    
    feedback = Feedback(
        salon_id=salon_id,
        customer_id=data.customer_id,
        booking_id=data.booking_id,
        feedback_type=data.feedback_type.value if isinstance(data.feedback_type, FeedbackType) else data.feedback_type,
        rating=data.rating,
        title=data.title,
        comment=data.comment,
        staff_id=data.staff_id,
        service_id=data.service_id,
        priority=priority
    )
    await feedback.save()
    
    return FeedbackResponse(**feedback.to_dict())


@router.get("", response_model=List[FeedbackResponse])
async def list_feedback(
    feedback_type: Optional[FeedbackType] = Query(None),
    status: Optional[FeedbackStatus] = Query(None),
    priority: Optional[FeedbackPriority] = Query(None),
    staff_id: Optional[str] = Query(None),
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    max_rating: Optional[int] = Query(None, ge=1, le=5),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """List feedback with filters"""
    filters = {"salon_id": salon_id}
    
    if feedback_type:
        filters["feedback_type"] = feedback_type.value
    if status:
        filters["status"] = status.value
    if priority:
        filters["priority"] = priority.value
    if staff_id:
        filters["staff_id"] = staff_id
    
    feedbacks = await Feedback.find_all(**filters, limit=limit, offset=offset)
    
    # Filter by rating range
    if min_rating is not None or max_rating is not None:
        filtered = []
        for f in feedbacks:
            if f.rating is None:
                continue
            if min_rating is not None and f.rating < min_rating:
                continue
            if max_rating is not None and f.rating > max_rating:
                continue
            filtered.append(f)
        feedbacks = filtered
    
    return [FeedbackResponse(**f.to_dict()) for f in feedbacks]


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """Get specific feedback"""
    feedback = await Feedback.find_by_id(feedback_id, salon_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return FeedbackResponse(**feedback.to_dict())


@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: str,
    data: FeedbackUpdate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Update feedback status and notes"""
    feedback = await Feedback.find_by_id(feedback_id, salon_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if isinstance(value, (FeedbackStatus, FeedbackPriority)):
            value = value.value
        setattr(feedback, field, value)
    
    feedback.updated_at = datetime.utcnow()
    await feedback.save()
    
    return FeedbackResponse(**feedback.to_dict())


@router.post("/{feedback_id}/resolve", response_model=FeedbackResponse)
async def resolve_feedback(
    feedback_id: str,
    resolution_notes: str = Query(..., min_length=1),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Mark feedback as resolved"""
    feedback = await Feedback.find_by_id(feedback_id, salon_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    feedback.status = FeedbackStatus.RESOLVED.value
    feedback.resolution_notes = resolution_notes
    feedback.resolved_by = user.get("uid")
    feedback.resolved_at = datetime.utcnow()
    feedback.updated_at = datetime.utcnow()
    await feedback.save()
    
    return FeedbackResponse(**feedback.to_dict())


@router.post("/{feedback_id}/escalate", response_model=FeedbackResponse)
async def escalate_feedback(
    feedback_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Escalate feedback priority"""
    feedback = await Feedback.find_by_id(feedback_id, salon_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    priority_order = [FeedbackPriority.LOW.value, FeedbackPriority.MEDIUM.value, 
                      FeedbackPriority.HIGH.value, FeedbackPriority.URGENT.value]
    current_idx = priority_order.index(feedback.priority) if feedback.priority in priority_order else 0
    
    if current_idx < len(priority_order) - 1:
        feedback.priority = priority_order[current_idx + 1]
    
    feedback.updated_at = datetime.utcnow()
    await feedback.save()
    
    return FeedbackResponse(**feedback.to_dict())


@router.post("/{feedback_id}/reply", response_model=FeedbackReplyResponse, status_code=status.HTTP_201_CREATED)
async def reply_to_feedback(
    feedback_id: str,
    data: FeedbackReplyCreate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Reply to feedback"""
    feedback = await Feedback.find_by_id(feedback_id, salon_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    reply = FeedbackReply(
        feedback_id=feedback_id,
        salon_id=salon_id,
        reply_text=data.reply_text,
        is_public=data.is_public,
        replied_by=user.get("uid")
    )
    await reply.save()
    
    # Update feedback status
    if feedback.status == FeedbackStatus.PENDING.value:
        feedback.status = FeedbackStatus.ACKNOWLEDGED.value
        feedback.updated_at = datetime.utcnow()
        await feedback.save()
    
    return FeedbackReplyResponse(**reply.to_dict())


@router.get("/{feedback_id}/replies", response_model=List[FeedbackReplyResponse])
async def list_feedback_replies(
    feedback_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """List replies for feedback"""
    replies = await FeedbackReply.find_all(feedback_id=feedback_id, salon_id=salon_id)
    return [FeedbackReplyResponse(**r.to_dict()) for r in replies]


@router.get("/summary", response_model=FeedbackSummary)
async def get_feedback_summary(
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Get feedback summary statistics"""
    feedbacks = await Feedback.find_all(salon_id=salon_id)
    
    total_feedback = len(feedbacks)
    
    # Average rating
    ratings = [f.rating for f in feedbacks if f.rating is not None]
    average_rating = Decimal(str(sum(ratings) / len(ratings))) if ratings else None
    
    # Rating distribution
    rating_distribution = {str(i): 0 for i in range(1, 6)}
    for r in ratings:
        rating_distribution[str(r)] = rating_distribution.get(str(r), 0) + 1
    
    # By type
    by_type = {}
    for f in feedbacks:
        by_type[f.feedback_type] = by_type.get(f.feedback_type, 0) + 1
    
    # By status
    by_status = {}
    for f in feedbacks:
        by_status[f.status] = by_status.get(f.status, 0) + 1
    
    # Pending complaints
    pending_complaints = sum(1 for f in feedbacks 
                            if f.feedback_type == FeedbackType.COMPLAINT.value 
                            and f.status in [FeedbackStatus.PENDING.value, FeedbackStatus.IN_PROGRESS.value])
    
    # Top rated staff
    staff_ratings = {}
    for f in feedbacks:
        if f.staff_id and f.rating:
            if f.staff_id not in staff_ratings:
                staff_ratings[f.staff_id] = {"total": 0, "count": 0}
            staff_ratings[f.staff_id]["total"] += f.rating
            staff_ratings[f.staff_id]["count"] += 1
    
    top_rated_staff = [
        {"staff_id": sid, "average_rating": data["total"] / data["count"], "review_count": data["count"]}
        for sid, data in staff_ratings.items()
    ]
    top_rated_staff.sort(key=lambda x: x["average_rating"], reverse=True)
    top_rated_staff = top_rated_staff[:5]
    
    # Low rated services
    service_ratings = {}
    for f in feedbacks:
        if f.service_id and f.rating:
            if f.service_id not in service_ratings:
                service_ratings[f.service_id] = {"total": 0, "count": 0}
            service_ratings[f.service_id]["total"] += f.rating
            service_ratings[f.service_id]["count"] += 1
    
    low_rated_services = [
        {"service_id": sid, "average_rating": data["total"] / data["count"], "review_count": data["count"]}
        for sid, data in service_ratings.items()
        if data["count"] >= 3  # Minimum reviews
    ]
    low_rated_services.sort(key=lambda x: x["average_rating"])
    low_rated_services = low_rated_services[:5]
    
    return FeedbackSummary(
        total_feedback=total_feedback,
        average_rating=average_rating,
        rating_distribution=rating_distribution,
        by_type=by_type,
        by_status=by_status,
        pending_complaints=pending_complaints,
        top_rated_staff=top_rated_staff,
        low_rated_services=low_rated_services
    )
