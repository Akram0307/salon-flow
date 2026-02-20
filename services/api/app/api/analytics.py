"""Analytics API Router"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from app.api.dependencies import get_current_user, require_role, get_salon_id
from app.schemas.analytics import (
    RevenueMetrics, BookingMetrics, CustomerMetrics,
    StaffPerformanceMetrics, ServiceMetrics, InventoryMetrics,
    DashboardSummary, ReportRequest, ReportResponse, DateRange,
    TimeGranularity, MetricType
)
from app.models.base import FirestoreBase
from app.models.booking import BookingModel
from app.models.customer import CustomerModel
from app.models.staff import StaffModel
from app.models.service import ServiceModel
from app.models.payment import PaymentModel
import uuid
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """Get dashboard summary for quick overview"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Today's metrics
    today_bookings = await BookingModel.find_all(salon_id=salon_id)
    today_bookings = [b for b in today_bookings if b.created_at and b.created_at >= today]
    
    today_payments = await PaymentModel.find_all(salon_id=salon_id)
    today_payments = [p for p in today_payments if p.created_at and p.created_at >= today]
    
    today_revenue = sum(float(p.amount or 0) for p in today_payments if p.status == "completed")
    
    # New customers today
    all_customers = await CustomerModel.find_all(salon_id=salon_id)
    new_customers_today = [c for c in all_customers if c.created_at and c.created_at >= today]
    
    # Pending bookings
    pending_bookings = [b for b in today_bookings if b.status == "pending"]
    
    # Staff on duty (simplified - would need shift data)
    staff_list = await StaffModel.find_all(salon_id=salon_id, is_active=True)
    
    # Revenue trend (last 7 days)
    revenue_trend = []
    for i in range(7):
        day = today - timedelta(days=i)
        day_payments = [p for p in await PaymentModel.find_all(salon_id=salon_id) 
                       if p.created_at and p.created_at >= day and p.created_at < day + timedelta(days=1)]
        day_revenue = sum(float(p.amount or 0) for p in day_payments if p.status == "completed")
        revenue_trend.append({"date": day.isoformat(), "revenue": day_revenue})
    revenue_trend.reverse()
    
    # Booking trend (last 7 days)
    booking_trend = []
    for i in range(7):
        day = today - timedelta(days=i)
        day_bookings = [b for b in await BookingModel.find_all(salon_id=salon_id)
                       if b.created_at and b.created_at >= day and b.created_at < day + timedelta(days=1)]
        booking_trend.append({"date": day.isoformat(), "count": len(day_bookings)})
    booking_trend.reverse()
    
    # Calculate occupancy rate (simplified)
    total_slots = 6 * 10  # 6 chairs * 10 hours
    booked_slots = len([b for b in today_bookings if b.status in ["confirmed", "in_progress"]])
    occupancy_rate = Decimal(str(min(booked_slots / total_slots * 100, 100))) if total_slots > 0 else Decimal("0")
    
    return DashboardSummary(
        today_revenue=Decimal(str(today_revenue)),
        today_bookings=len(today_bookings),
        today_new_customers=len(new_customers_today),
        pending_bookings=len(pending_bookings),
        low_stock_alerts=0,  # Would need inventory data
        pending_feedback=0,  # Would need feedback data
        staff_on_duty=len(staff_list),
        occupancy_rate=occupancy_rate,
        revenue_trend=revenue_trend,
        booking_trend=booking_trend
    )


@router.get("/revenue", response_model=RevenueMetrics)
async def get_revenue_metrics(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Get revenue analytics"""
    payments = await PaymentModel.find_all(salon_id=salon_id)
    
    # Filter by date range
    filtered_payments = [
        p for p in payments 
        if p.created_at and start_date <= p.created_at <= end_date and p.status == "completed"
    ]
    
    total_revenue = sum(float(p.amount or 0) for p in filtered_payments)
    total_bookings = len(set(p.booking_id for p in filtered_payments if p.booking_id))
    average_booking_value = Decimal(str(total_revenue / total_bookings)) if total_bookings > 0 else Decimal("0")
    
    # Revenue by day
    revenue_by_day = defaultdict(float)
    for p in filtered_payments:
        if p.created_at:
            day_key = p.created_at.strftime("%Y-%m-%d")
            revenue_by_day[day_key] += float(p.amount or 0)
    
    revenue_by_day_list = [{"date": k, "revenue": v} for k, v in sorted(revenue_by_day.items())]
    
    # Revenue by service (simplified)
    revenue_by_service = []
    
    # Revenue by staff (simplified)
    revenue_by_staff = []
    
    # Payment method breakdown
    payment_methods = defaultdict(float)
    for p in filtered_payments:
        method = p.payment_method or "unknown"
        payment_methods[method] += float(p.amount or 0)
    
    return RevenueMetrics(
        total_revenue=Decimal(str(total_revenue)),
        total_bookings=total_bookings,
        average_booking_value=average_booking_value,
        revenue_by_day=revenue_by_day_list,
        revenue_by_service=revenue_by_service,
        revenue_by_staff=revenue_by_staff,
        payment_method_breakdown={k: Decimal(str(v)) for k, v in payment_methods.items()},
        growth_percentage=None
    )


@router.get("/bookings", response_model=BookingMetrics)
async def get_booking_metrics(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Get booking analytics"""
    bookings = await BookingModel.find_all(salon_id=salon_id)
    
    # Filter by date range
    filtered_bookings = [
        b for b in bookings 
        if b.created_at and start_date <= b.created_at <= end_date
    ]
    
    total_bookings = len(filtered_bookings)
    completed_bookings = len([b for b in filtered_bookings if b.status == "completed"])
    cancelled_bookings = len([b for b in filtered_bookings if b.status == "cancelled"])
    no_show_count = len([b for b in filtered_bookings if b.status == "no_show"])
    
    cancellation_rate = Decimal(str(cancelled_bookings / total_bookings * 100)) if total_bookings > 0 else Decimal("0")
    
    # Bookings by hour
    bookings_by_hour = defaultdict(int)
    for b in filtered_bookings:
        if b.start_time:
            hour = b.start_time.hour
            bookings_by_hour[hour] += 1
    
    bookings_by_hour_list = [{"hour": h, "count": c} for h, c in sorted(bookings_by_hour.items())]
    
    # Bookings by day
    bookings_by_day = defaultdict(int)
    for b in filtered_bookings:
        if b.created_at:
            day_key = b.created_at.strftime("%Y-%m-%d")
            bookings_by_day[day_key] += 1
    
    bookings_by_day_list = [{"date": d, "count": c} for d, c in sorted(bookings_by_day.items())]
    
    # Peak hours
    peak_hours = sorted(bookings_by_hour.items(), key=lambda x: x[1], reverse=True)[:3]
    peak_hours = [h[0] for h in peak_hours]
    
    return BookingMetrics(
        total_bookings=total_bookings,
        completed_bookings=completed_bookings,
        cancelled_bookings=cancelled_bookings,
        no_show_count=no_show_count,
        cancellation_rate=cancellation_rate,
        average_duration=30,  # Default average
        bookings_by_hour=bookings_by_hour_list,
        bookings_by_day=bookings_by_day_list,
        bookings_by_service=[],
        peak_hours=peak_hours
    )


@router.get("/customers", response_model=CustomerMetrics)
async def get_customer_metrics(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Get customer analytics"""
    customers = await CustomerModel.find_all(salon_id=salon_id)
    bookings = await BookingModel.find_all(salon_id=salon_id)
    
    total_customers = len(customers)
    
    # New customers in date range
    new_customers = [c for c in customers if c.created_at and start_date <= c.created_at <= end_date]
    
    # Returning customers (customers with more than 1 booking)
    customer_booking_counts = defaultdict(int)
    for b in bookings:
        if b.customer_id:
            customer_booking_counts[b.customer_id] += 1
    
    returning_customers = sum(1 for count in customer_booking_counts.values() if count > 1)
    
    # Retention rate
    retention_rate = Decimal(str(returning_customers / total_customers * 100)) if total_customers > 0 else Decimal("0")
    
    # Average visits per customer
    total_visits = sum(customer_booking_counts.values())
    average_visits = Decimal(str(total_visits / total_customers)) if total_customers > 0 else Decimal("0")
    
    # Top customers by revenue
    customer_revenue = defaultdict(float)
    payments = await PaymentModel.find_all(salon_id=salon_id)
    for p in payments:
        if p.customer_id and p.status == "completed":
            customer_revenue[p.customer_id] += float(p.amount or 0)
    
    top_customers = [
        {"customer_id": cid, "total_revenue": rev, "visits": customer_booking_counts.get(cid, 0)}
        for cid, rev in sorted(customer_revenue.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    return CustomerMetrics(
        total_customers=total_customers,
        new_customers=len(new_customers),
        returning_customers=returning_customers,
        retention_rate=retention_rate,
        average_visits_per_customer=average_visits,
        top_customers=top_customers,
        customers_by_age_group={},
        customers_by_gender={}
    )


@router.get("/staff/{staff_id}", response_model=StaffPerformanceMetrics)
async def get_staff_performance(
    staff_id: str,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Get individual staff performance metrics"""
    staff = await StaffModel.find_by_id(staff_id, salon_id)
    if not staff:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Staff not found")
    
    bookings = await BookingModel.find_all(salon_id=salon_id, staff_id=staff_id)
    filtered_bookings = [
        b for b in bookings 
        if b.created_at and start_date <= b.created_at <= end_date
    ]
    
    total_bookings = len(filtered_bookings)
    
    # Revenue from this staff's bookings
    payments = await PaymentModel.find_all(salon_id=salon_id)
    staff_revenue = sum(
        float(p.amount or 0) 
        for p in payments 
        if p.staff_id == staff_id and p.status == "completed" and 
           p.created_at and start_date <= p.created_at <= end_date
    )
    
    # Services performed
    services_performed = defaultdict(int)
    for b in filtered_bookings:
        if b.service_id:
            services_performed[b.service_id] += 1
    
    return StaffPerformanceMetrics(
        staff_id=staff_id,
        staff_name=staff.name,
        total_bookings=total_bookings,
        total_revenue=Decimal(str(staff_revenue)),
        average_rating=None,  # Would need feedback data
        total_tips=Decimal("0"),  # Would need tip tracking
        services_performed=dict(services_performed),
        utilization_rate=Decimal("0"),  # Would need shift data
        average_service_time=30
    )


@router.get("/services", response_model=List[ServiceMetrics])
async def get_service_metrics(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Get service analytics"""
    services = await ServiceModel.find_all(salon_id=salon_id)
    bookings = await BookingModel.find_all(salon_id=salon_id)
    
    # Filter bookings by date
    filtered_bookings = [
        b for b in bookings 
        if b.created_at and start_date <= b.created_at <= end_date
    ]
    
    # Calculate metrics per service
    service_metrics = []
    service_booking_counts = defaultdict(int)
    service_revenue = defaultdict(float)
    
    for b in filtered_bookings:
        if b.service_id:
            service_booking_counts[b.service_id] += 1
            # Would need to get service price
    
    for service in services:
        metrics = ServiceMetrics(
            service_id=service.service_id,
            service_name=service.name,
            total_bookings=service_booking_counts.get(service.service_id, 0),
            total_revenue=Decimal(str(service_revenue.get(service.service_id, 0))),
            average_rating=None,
            popularity_rank=0,
            growth_percentage=None
        )
        service_metrics.append(metrics)
    
    # Sort by bookings and assign rank
    service_metrics.sort(key=lambda x: x.total_bookings, reverse=True)
    for i, m in enumerate(service_metrics):
        m.popularity_rank = i + 1
    
    return service_metrics


@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    data: ReportRequest,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Generate a custom report"""
    report_id = str(uuid.uuid4())
    
    # Generate report based on type
    report_data = {}
    
    if data.report_type == "revenue":
        payments = await PaymentModel.find_all(salon_id=salon_id)
        filtered = [p for p in payments if p.created_at and 
                   data.start_date <= p.created_at <= data.end_date]
        report_data = {
            "total_revenue": sum(float(p.amount or 0) for p in filtered if p.status == "completed"),
            "transaction_count": len(filtered)
        }
    elif data.report_type == "bookings":
        bookings = await BookingModel.find_all(salon_id=salon_id)
        filtered = [b for b in bookings if b.created_at and 
                   data.start_date <= b.created_at <= data.end_date]
        report_data = {
            "total_bookings": len(filtered),
            "by_status": defaultdict(int)
        }
        for b in filtered:
            report_data["by_status"][b.status] += 1
    
    return ReportResponse(
        report_id=report_id,
        report_type=data.report_type,
        generated_at=datetime.utcnow(),
        date_range=DateRange(start_date=data.start_date, end_date=data.end_date),
        data=report_data,
        summary=None
    )
