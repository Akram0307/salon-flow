"""Enhanced Billing Router with Price Override and Staff Suggestions"""

from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from app.schemas.billing import (
    PriceOverrideCreate,
    PriceOverrideResponse,
    PriceOverrideListResponse,
    StaffSuggestionCreate,
    StaffSuggestionResponse,
    StaffSuggestionListResponse,
    SuggestionApproval,
    BillingCreate,
    BillResponse,
    ApprovalRulesCreate,
    ApprovalRulesResponse,
    OverrideReasonCode,
    SuggestionType,
    SuggestionStatus,
)
from app.models.billing import (
    PriceOverrideModel,
    StaffSuggestionModel,
    ApprovalRulesModel,
    BillModel,
    DailyDiscountTracker,
)
from app.models.booking import BookingModel
from app.models.customer import CustomerModel
from app.models.staff import StaffModel
from app.models.service import ServiceModel
from app.api.dependencies import get_current_user, get_salon_id, require_role, require_roles
from app.core.config import settings
from app.core.firebase import get_firestore_async
from app.core.redis import get_redis_client
import json
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["Billing"])


# ============== Helper Functions ==============

def calculate_discount_percent(original: Decimal, new: Decimal) -> Decimal:
    """Calculate discount percentage"""
    if original <= 0:
        return Decimal('0')
    return round(((original - new) / original) * 100, 2)


async def get_approval_rules(salon_id: str) -> ApprovalRulesModel:
    """Get salon-specific approval rules or create default"""
    db = get_firestore_async()
    rules_ref = db.collection('approval_rules').where('salon_id', '==', salon_id).limit(1)
    rules_docs = await rules_ref.get()
    
    if rules_docs:
        return ApprovalRulesModel.from_dict(rules_docs[0].to_dict())
    
    # Create default rules
    default_rules = ApprovalRulesModel(
        rules_id=str(uuid.uuid4()),
        salon_id=salon_id,
        auto_approve_threshold=Decimal('10'),
        manager_approval_threshold=Decimal('20'),
        owner_approval_threshold=Decimal('30'),
        max_discount_per_day=Decimal('10000'),
        require_reason_for_discount=True,
        allow_staff_suggestions=True,
        suggestion_expiry_minutes=30,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await db.collection('approval_rules').document(default_rules.rules_id).set(default_rules.to_dict())
    return default_rules


async def check_discount_approval_needed(
    salon_id: str,
    discount_percent: Decimal,
    user_role: str
) -> tuple[bool, str]:
    """Check if additional approval is needed for discount
    
    Returns: (needs_approval, approver_role_needed)
    """
    rules = await get_approval_rules(salon_id)
    
    if discount_percent <= rules.auto_approve_threshold:
        return False, "auto"
    elif discount_percent <= rules.manager_approval_threshold:
        if user_role in ['manager', 'owner']:
            return False, "manager"
        return True, "manager"
    else:
        if user_role == 'owner':
            return False, "owner"
        return True, "owner"


async def update_daily_discount_tracker(salon_id: str, discount_amount: Decimal):
    """Update daily discount tracker"""
    db = get_firestore_async()
    today = date.today().isoformat()
    tracker_id = f"{salon_id}_{today}"
    
    tracker_ref = db.collection('daily_discount_tracker').document(tracker_id)
    tracker_doc = await tracker_ref.get()
    
    if tracker_doc.exists:
        await tracker_ref.update({
            'total_discount': tracker_doc.to_dict()['total_discount'] + discount_amount,
            'override_count': tracker_doc.to_dict()['override_count'] + 1,
            'updated_at': datetime.utcnow()
        })
    else:
        await tracker_ref.set({
            'tracker_id': tracker_id,
            'salon_id': salon_id,
            'date': today,
            'total_discount': discount_amount,
            'override_count': 1,
            'updated_at': datetime.utcnow()
        })


async def notify_suggestion_update(salon_id: str, suggestion: StaffSuggestionModel, action: str):
    """Notify connected clients about suggestion update via Redis pub/sub"""
    try:
        redis = get_redis_client()
        channel = f"suggestions:{salon_id}"
        message = json.dumps({
            'type': 'suggestion_update',
            'action': action,  # 'new', 'approved', 'rejected'
            'suggestion': suggestion.to_dict()
        })
        redis.publish(channel, message)
    except Exception as e:
        logger.error(f"Failed to notify suggestion update: {e}")


# ============== Price Override Endpoints ==============

@router.post("/overrides", response_model=PriceOverrideResponse, status_code=status.HTTP_201_CREATED)
async def create_price_override(
    override_data: PriceOverrideCreate,
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_salon_id)):
    """Create a price override for a service in a booking
    
    Managers can override prices with proper audit trail.
    Staff suggestions can be converted to overrides.
    """
    db = get_firestore_async()
    
    # Verify booking exists and belongs to salon
    booking_doc = await db.collection('bookings').document(override_data.booking_id).get()
    if not booking_doc.exists:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking_data = booking_doc.to_dict()
    if booking_data.get('salon_id') != salon_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Calculate discount percentage
    discount_percent = calculate_discount_percent(override_data.original_price, override_data.new_price)
    
    # Check if approval is needed
    needs_approval, approver_role = await check_discount_approval_needed(
        salon_id, discount_percent, current_user.get('role')
    )
    
    if needs_approval:
        raise HTTPException(
            status_code=403,
            detail=f"Discount of {discount_percent}% requires {approver_role} approval"
        )
    
    # Check daily discount limit
    rules = await get_approval_rules(salon_id)
    today = date.today().isoformat()
    tracker_id = f"{salon_id}_{today}"
    tracker_doc = await db.collection('daily_discount_tracker').document(tracker_id).get()
    
    current_total = Decimal('0')
    if tracker_doc.exists:
        current_total = Decimal(str(tracker_doc.to_dict().get('total_discount', 0)))
    
    discount_amount = override_data.original_price - override_data.new_price
    if current_total + discount_amount > rules.max_discount_per_day:
        raise HTTPException(
            status_code=400,
            detail=f"Daily discount limit of ₹{rules.max_discount_per_day} exceeded"
        )
    
    # Create override
    override_id = str(uuid.uuid4())
    override = PriceOverrideModel(
        override_id=override_id,
        salon_id=salon_id,
        booking_id=override_data.booking_id,
        service_id=override_data.service_id,
        service_name=override_data.service_name,
        original_price=override_data.original_price,
        new_price=override_data.new_price,
        discount_percent=discount_percent,
        reason_code=override_data.reason_code.value,
        reason_text=override_data.reason_text,
        suggested_by=override_data.suggested_by,
        approved_by=current_user.get('uid'),
        approved_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    
    await db.collection('price_overrides').document(override_id).set(override.to_dict())
    
    # Update daily tracker
    await update_daily_discount_tracker(salon_id, discount_amount)
    
    # If this was from a suggestion, update suggestion status
    if override_data.suggested_by:
        suggestion_query = db.collection('staff_suggestions').where('staff_id', '==', override_data.suggested_by).where('booking_id', '==', override_data.booking_id).where('service_id', '==', override_data.service_id).where('status', '==', 'pending').limit(1)
        suggestion_docs = await suggestion_query.get()
        if suggestion_docs:
            suggestion_ref = suggestion_docs[0].reference
            await suggestion_ref.update({
                'status': 'approved',
                'reviewed_by': current_user.get('uid'),
                'reviewed_at': datetime.utcnow()
            })
    
    # Get approver name
    approver_doc = await db.collection('staff').document(current_user.get('uid')).get()
    approver_name = approver_doc.to_dict().get('name', 'Unknown') if approver_doc.exists else 'Unknown'
    
    return PriceOverrideResponse(
        **override.to_dict(),
        approver_name=approver_name
    )


@router.get("/overrides", response_model=PriceOverrideListResponse)
async def list_price_overrides(
    booking_id: Optional[str] = None,
    staff_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_salon_id)
):
    """List price overrides with filters"""
    db = get_firestore_async()
    
    query = db.collection('price_overrides').where('salon_id', '==', salon_id)
    
    if booking_id:
        query = query.where('booking_id', '==', booking_id)
    if staff_id:
        query = query.where('suggested_by', '==', staff_id)
    if date_from:
        query = query.where('created_at', '>=', datetime.fromisoformat(date_from))
    if date_to:
        query = query.where('created_at', '<=', datetime.fromisoformat(date_to))
    
    query = query.order_by('created_at', direction='DESCENDING')
    
    # Get total count
    all_docs = await query.get()
    total = len(all_docs)
    
    # Paginate
    offset = (page - 1) * page_size
    docs = await query.offset(offset).limit(page_size).get()
    
    overrides = []
    total_discount = Decimal('0')
    
    for doc in docs:
        data = doc.to_dict()
        total_discount += Decimal(str(data.get('discount_percent', 0)))
        
        # Get approver name
        approver_id = data.get('approved_by')
        approver_doc = await db.collection('staff').document(approver_id).get()
        approver_name = approver_doc.to_dict().get('name', 'Unknown') if approver_doc.exists else 'Unknown'
        
        # Get suggester name if applicable
        suggester_name = None
        if data.get('suggested_by'):
            suggester_doc = await db.collection('staff').document(data['suggested_by']).get()
            suggester_name = suggester_doc.to_dict().get('name', 'Unknown') if suggester_doc.exists else 'Unknown'
        
        overrides.append(PriceOverrideResponse(
            **data,
            approver_name=approver_name,
            suggester_name=suggester_name
        ))
    
    return PriceOverrideListResponse(
        items=overrides,
        total=total,
        page=page,
        page_size=page_size,
        total_discount=total_discount
    )


@router.delete("/overrides/{override_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_price_override(
    override_id: str,
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_salon_id)
):
    """Delete a price override (only if not used in a finalized bill)"""
    db = get_firestore_async()
    
    override_doc = await db.collection('price_overrides').document(override_id).get()
    if not override_doc.exists:
        raise HTTPException(status_code=404, detail="Override not found")
    
    override_data = override_doc.to_dict()
    if override_data.get('salon_id') != salon_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if used in a bill
    bills_query = db.collection('bills').where('override_ids', 'array_contains', override_id).limit(1)
    if await bills_query.get():
        raise HTTPException(status_code=400, detail="Cannot delete override used in finalized bill")
    
    await db.collection('price_overrides').document(override_id).delete()


# ============== Staff Suggestion Endpoints ==============

@router.post("/suggestions", response_model=StaffSuggestionResponse, status_code=status.HTTP_201_CREATED)
async def create_staff_suggestion(
    suggestion_data: StaffSuggestionCreate,
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_salon_id)
):
    """Staff creates a price/discount suggestion for manager approval"""
    db = get_firestore_async()
    
    # Check if suggestions are allowed
    rules = await get_approval_rules(salon_id)
    if not rules.allow_staff_suggestions:
        raise HTTPException(status_code=403, detail="Staff suggestions are not enabled")
    
    # Verify booking exists
    booking_doc = await db.collection('bookings').document(suggestion_data.booking_id).get()
    if not booking_doc.exists:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking_data = booking_doc.to_dict()
    if booking_data.get('salon_id') != salon_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get staff info
    staff_doc = await db.collection('staff').document(current_user.get('uid')).get()
    staff_name = staff_doc.to_dict().get('name', 'Unknown') if staff_doc.exists else 'Unknown'
    
    # Calculate discount percent
    discount_percent = Decimal('0')
    if suggestion_data.original_price > 0 and suggestion_data.suggested_price < suggestion_data.original_price:
        discount_percent = calculate_discount_percent(
            suggestion_data.original_price,
            suggestion_data.suggested_price
        )
    
    # Create suggestion
    suggestion_id = str(uuid.uuid4())
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=rules.suggestion_expiry_minutes)
    
    suggestion = StaffSuggestionModel(
        suggestion_id=suggestion_id,
        salon_id=salon_id,
        booking_id=suggestion_data.booking_id,
        staff_id=current_user.get('uid'),
        staff_name=staff_name,
        suggestion_type=suggestion_data.suggestion_type.value,
        service_id=suggestion_data.service_id,
        service_name=suggestion_data.service_name,
        original_price=suggestion_data.original_price,
        suggested_price=suggestion_data.suggested_price,
        discount_percent=discount_percent,
        reason=suggestion_data.reason,
        status='pending',
        created_at=now,
        expires_at=expires_at,
    )
    
    await db.collection('staff_suggestions').document(suggestion_id).set(suggestion.to_dict())
    
    # Notify managers
    await notify_suggestion_update(salon_id, suggestion, 'new')
    
    # Get customer info for response
    customer_id = booking_data.get('customer_id')
    customer_name = None
    customer_phone = None
    if customer_id:
        customer_doc = await db.collection('customers').document(customer_id).get()
        if customer_doc.exists:
            customer_data = customer_doc.to_dict()
            customer_name = customer_data.get('name')
            customer_phone = customer_data.get('phone')
    
    impact_amount = suggestion_data.original_price - suggestion_data.suggested_price
    
    return StaffSuggestionResponse(
        **suggestion.to_dict(),
        customer_name=customer_name,
        customer_phone=customer_phone,
        impact_amount=impact_amount
    )


@router.get("/suggestions", response_model=StaffSuggestionListResponse)
async def list_staff_suggestions(
    status_filter: Optional[str] = Query(None, alias="status"),
    booking_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_salon_id)
):
    """List staff suggestions (for manager dashboard)"""
    db = get_firestore_async()
    
    query = db.collection('staff_suggestions').where('salon_id', '==', salon_id)
    
    if status_filter:
        query = query.where('status', '==', status_filter)
    if booking_id:
        query = query.where('booking_id', '==', booking_id)
    
    query = query.order_by('created_at', direction='DESCENDING')
    
    docs = await query.get()
    
    suggestions = []
    pending_count = 0
    approved_count = 0
    rejected_count = 0
    
    for doc in docs:
        data = doc.to_dict()
        s_status = data.get('status', 'pending')
        
        if s_status == 'pending':
            pending_count += 1
        elif s_status == 'approved':
            approved_count += 1
        elif s_status == 'rejected':
            rejected_count += 1
        
        # Get customer info
        booking_doc = await db.collection('bookings').document(data.get('booking_id')).get()
        customer_name = None
        customer_phone = None
        if booking_doc.exists:
            booking_data = booking_doc.to_dict()
            customer_id = booking_data.get('customer_id')
            if customer_id:
                customer_doc = await db.collection('customers').document(customer_id).get()
                if customer_doc.exists:
                    customer_data = customer_doc.to_dict()
                    customer_name = customer_data.get('name')
                    customer_phone = customer_data.get('phone')
        
        impact_amount = Decimal(str(data.get('original_price', 0))) - Decimal(str(data.get('suggested_price', 0)))
        
        suggestions.append(StaffSuggestionResponse(
            **data,
            customer_name=customer_name,
            customer_phone=customer_phone,
            impact_amount=impact_amount
        ))
    
    # Paginate
    total = len(suggestions)
    offset = (page - 1) * page_size
    paginated_suggestions = suggestions[offset:offset + page_size]
    
    return StaffSuggestionListResponse(
        items=paginated_suggestions,
        total=total,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count
    )


@router.post("/suggestions/{suggestion_id}/approve", response_model=PriceOverrideResponse)
async def approve_staff_suggestion(
    suggestion_id: str,
    approval_data: SuggestionApproval,
    current_user = Depends(require_roles(['manager', 'owner'])),
    salon_id: str = Depends(get_salon_id)
):
    """Approve or reject a staff suggestion"""
    db = get_firestore_async()
    
    suggestion_doc = await db.collection('staff_suggestions').document(suggestion_id).get()
    if not suggestion_doc.exists:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    suggestion_data = suggestion_doc.to_dict()
    if suggestion_data.get('salon_id') != salon_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if suggestion_data.get('status') != 'pending':
        raise HTTPException(status_code=400, detail=f"Suggestion already {suggestion_data.get('status')}")
    
    # Check if expired
    if datetime.utcnow() > datetime.fromisoformat(str(suggestion_data.get('expires_at'))):
        await db.collection('staff_suggestions').document(suggestion_id).update({'status': 'expired'})
        raise HTTPException(status_code=400, detail="Suggestion has expired")
    
    if not approval_data.approved:
        # Reject the suggestion
        await db.collection('staff_suggestions').document(suggestion_id).update({
            'status': 'rejected',
            'reviewed_by': current_user.get('uid'),
            'reviewed_at': datetime.utcnow(),
            'rejection_reason': approval_data.rejection_reason
        })
        
        # Notify
        suggestion = StaffSuggestionModel(**suggestion_data)
        suggestion.status = 'rejected'
        await notify_suggestion_update(salon_id, suggestion, 'rejected')
        
        raise HTTPException(status_code=200, detail="Suggestion rejected")
    
    # Approve - create price override
    override_id = str(uuid.uuid4())
    discount_percent = Decimal('0')
    if suggestion_data.get('original_price', 0) > 0:
        discount_percent = calculate_discount_percent(
            Decimal(str(suggestion_data['original_price'])),
            Decimal(str(suggestion_data['suggested_price']))
        )
    
    override = PriceOverrideModel(
        override_id=override_id,
        salon_id=salon_id,
        booking_id=suggestion_data['booking_id'],
        service_id=suggestion_data.get('service_id', ''),
        service_name=suggestion_data.get('service_name', ''),
        original_price=Decimal(str(suggestion_data.get('original_price', 0))),
        new_price=Decimal(str(suggestion_data.get('suggested_price', 0))),
        discount_percent=discount_percent,
        reason_code='staff_suggestion',
        reason_text=suggestion_data.get('reason', ''),
        suggested_by=suggestion_data['staff_id'],
        approved_by=current_user.get('uid'),
        approved_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    
    # Save override
    await db.collection('price_overrides').document(override_id).set(override.to_dict())
    
    # Update suggestion status
    await db.collection('staff_suggestions').document(suggestion_id).update({
        'status': 'approved',
        'reviewed_by': current_user.get('uid'),
        'reviewed_at': datetime.utcnow()
    })
    
    # Update daily tracker
    discount_amount = override.original_price - override.new_price
    await update_daily_discount_tracker(salon_id, discount_amount)
    
    # Notify
    suggestion = StaffSuggestionModel(**suggestion_data)
    suggestion.status = 'approved'
    await notify_suggestion_update(salon_id, suggestion, 'approved')
    
    # Get approver name
    approver_doc = await db.collection('staff').document(current_user.get('uid')).get()
    approver_name = approver_doc.to_dict().get('name', 'Unknown') if approver_doc.exists else 'Unknown'
    
    return PriceOverrideResponse(
        **override.to_dict(),
        approver_name=approver_name,
        suggester_name=suggestion_data.get('staff_name')
    )


@router.get("/suggestions/pending")
async def get_pending_suggestions_count(
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_salon_id)
):
    """Get count of pending suggestions for notification badge"""
    db = get_firestore_async()
    
    query = db.collection('staff_suggestions').where('salon_id', '==', salon_id).where('status', '==', 'pending')
    docs = await query.get()
    
    # Filter out expired
    now = datetime.utcnow()
    active_count = sum(1 for doc in docs if datetime.fromisoformat(str(doc.to_dict().get('expires_at'))) > now)
    
    return {"pending_count": active_count}


# ============== Bill Generation Endpoints ==============

@router.post("/generate", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
async def generate_bill(
    bill_data: BillingCreate,
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_salon_id)
):
    """Generate final bill for a booking"""
    db = get_firestore_async()
    
    # Verify booking
    booking_doc = await db.collection('bookings').document(bill_data.booking_id).get()
    if not booking_doc.exists:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking_data = booking_doc.to_dict()
    if booking_data.get('salon_id') != salon_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get customer info
    customer_id = booking_data.get('customer_id')
    customer_doc = await db.collection('customers').document(customer_id).get()
    customer_data = customer_doc.to_dict() if customer_doc.exists else {}
    
    # Calculate totals
    subtotal = Decimal('0')
    service_items = []
    override_ids = []
    
    for item in bill_data.services:
        final_price = item.override_price if item.override_price else item.original_price
        subtotal += final_price * item.quantity
        
        if item.override_id:
            override_ids.append(item.override_id)
        
        service_items.append({
            'service_id': item.service_id,
            'service_name': item.service_name,
            'staff_id': item.staff_id,
            'staff_name': item.staff_name,
            'original_price': float(item.original_price),
            'override_price': float(item.override_price) if item.override_price else None,
            'override_id': item.override_id,
            'quantity': item.quantity,
            'final_price': float(final_price)
        })
    
    # Apply membership discount
    membership_discount = Decimal('0')
    if bill_data.membership_discount_percent > 0:
        membership_discount = subtotal * (bill_data.membership_discount_percent / 100)
    
    # Apply manual adjustment
    manual_adjustment = bill_data.manual_adjustment
    
    # Calculate GST
    taxable_amount = subtotal - membership_discount - manual_adjustment
    gst_amount = taxable_amount * Decimal('0.05')  # 5% GST
    
    # Grand total
    grand_total = taxable_amount + gst_amount
    
    # Calculate change
    change_due = bill_data.amount_received - grand_total
    
    # Calculate loyalty points (1 point per ₹10)
    loyalty_points_earned = int(grand_total / 10)
    
    # Generate invoice number
    today = date.today()
    counter_ref = db.collection('invoice_counters').document(f"{salon_id}_{today.year}")
    counter_doc = await counter_ref.get()
    sequence = 1
    if counter_doc.exists:
        sequence = counter_doc.to_dict().get('sequence', 0) + 1
    await counter_ref.set({'sequence': sequence})
    
    invoice_number = f"INV-{salon_id[:4].upper()}-{today.year}-{sequence:06d}"
    
    # Create bill
    bill_id = str(uuid.uuid4())
    bill = BillModel(
        bill_id=bill_id,
        salon_id=salon_id,
        booking_id=bill_data.booking_id,
        invoice_number=invoice_number,
        customer_id=customer_id,
        customer_name=customer_data.get('name', 'Unknown'),
        customer_phone=customer_data.get('phone', ''),
        services=service_items,
        subtotal=subtotal,
        membership_discount=membership_discount,
        membership_discount_percent=bill_data.membership_discount_percent,
        manual_adjustment=manual_adjustment,
        manual_adjustment_reason=bill_data.manual_adjustment_reason,
        gst_percent=Decimal('5'),
        gst_amount=gst_amount,
        grand_total=grand_total,
        payment_method=bill_data.payment_method,
        amount_received=bill_data.amount_received,
        change_due=change_due,
        loyalty_points_earned=loyalty_points_earned,
        override_ids=override_ids,
        created_at=datetime.utcnow(),
        created_by=current_user.get('uid'),
    )
    
    await db.collection('bills').document(bill_id).set(bill.to_dict())
    
    # Update customer loyalty points
    if loyalty_points_earned > 0:
        customer_ref = db.collection('customers').document(customer_id)
        await customer_ref.update({
            'loyalty_points': customer_data.get('loyalty_points', 0) + loyalty_points_earned,
            'total_visits': customer_data.get('total_visits', 0) + 1,
            'last_visit': datetime.utcnow().isoformat()
        })
    
    # Update booking status
    await db.collection('bookings').document(bill_data.booking_id).update({
        'status': 'completed',
        'bill_id': bill_id,
        'completed_at': datetime.utcnow().isoformat()
    })
    
    return BillResponse(
        id=bill_id,
        salon_id=salon_id,
        booking_id=bill_data.booking_id,
        invoice_number=invoice_number,
        customer_name=customer_data.get('name', 'Unknown'),
        customer_phone=customer_data.get('phone', ''),
        services=bill_data.services,
        subtotal=subtotal,
        membership_discount=membership_discount,
        manual_adjustment=manual_adjustment,
        gst_amount=gst_amount,
        grand_total=grand_total,
        payment_method=bill_data.payment_method,
        amount_received=bill_data.amount_received,
        change_due=change_due,
        loyalty_points_earned=loyalty_points_earned,
        created_at=datetime.utcnow(),
        created_by=current_user.get('uid')
    )


# ============== Approval Rules Endpoints ==============

@router.get("/rules", response_model=ApprovalRulesResponse)
async def get_rules(
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_salon_id)
):
    """Get approval rules for the salon"""
    rules = await get_approval_rules(salon_id)
    return ApprovalRulesResponse(**rules.to_dict())


@router.put("/rules", response_model=ApprovalRulesResponse)
async def update_rules(
    rules_data: ApprovalRulesCreate,
    current_user = Depends(require_roles(['owner', 'manager'])),
    salon_id: str = Depends(get_salon_id)
):
    """Update approval rules (owner/manager only)"""
    db = get_firestore_async()
    
    # Get existing rules
    rules_ref = db.collection('approval_rules').where('salon_id', '==', salon_id).limit(1)
    rules_docs = await rules_ref.get()
    
    if rules_docs:
        rules_id = rules_docs[0].id
        await rules_ref.document(rules_id).update({
            **rules_data.model_dump(),
            'updated_at': datetime.utcnow()
        })
    else:
        rules_id = str(uuid.uuid4())
        new_rules = ApprovalRulesModel(
            rules_id=rules_id,
            salon_id=salon_id,
            **rules_data.model_dump(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await db.collection('approval_rules').document(rules_id).set(new_rules.to_dict())
    
    return await get_approval_rules(salon_id)
