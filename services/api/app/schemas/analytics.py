"""Analytics Schemas"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TimeGranularity(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class MetricType(str, Enum):
    REVENUE = "revenue"
    BOOKINGS = "bookings"
    CUSTOMERS = "customers"
    SERVICES = "services"
    STAFF_PERFORMANCE = "staff_performance"
    INVENTORY = "inventory"


class DateRange(BaseModel):
    """Date range for analytics queries"""
    start_date: datetime
    end_date: datetime


class RevenueMetrics(BaseModel):
    """Revenue analytics metrics"""
    total_revenue: Decimal
    total_bookings: int
    average_booking_value: Decimal
    revenue_by_day: List[Dict[str, Any]]
    revenue_by_service: List[Dict[str, Any]]
    revenue_by_staff: List[Dict[str, Any]]
    payment_method_breakdown: Dict[str, Decimal]
    growth_percentage: Optional[Decimal] = None


class BookingMetrics(BaseModel):
    """Booking analytics metrics"""
    total_bookings: int
    completed_bookings: int
    cancelled_bookings: int
    no_show_count: int
    cancellation_rate: Decimal
    average_duration: int  # minutes
    bookings_by_hour: List[Dict[str, Any]]
    bookings_by_day: List[Dict[str, Any]]
    bookings_by_service: List[Dict[str, Any]]
    peak_hours: List[int]


class CustomerMetrics(BaseModel):
    """Customer analytics metrics"""
    total_customers: int
    new_customers: int
    returning_customers: int
    retention_rate: Decimal
    average_visits_per_customer: Decimal
    top_customers: List[Dict[str, Any]]
    customers_by_age_group: Dict[str, int]
    customers_by_gender: Dict[str, int]


class StaffPerformanceMetrics(BaseModel):
    """Staff performance metrics"""
    staff_id: str
    staff_name: str
    total_bookings: int
    total_revenue: Decimal
    average_rating: Optional[Decimal]
    total_tips: Decimal
    services_performed: Dict[str, int]
    utilization_rate: Decimal
    average_service_time: int  # minutes


class ServiceMetrics(BaseModel):
    """Service analytics metrics"""
    service_id: str
    service_name: str
    total_bookings: int
    total_revenue: Decimal
    average_rating: Optional[Decimal]
    popularity_rank: int
    growth_percentage: Optional[Decimal]


class InventoryMetrics(BaseModel):
    """Inventory analytics metrics"""
    total_products: int
    low_stock_products: int
    out_of_stock_products: int
    total_inventory_value: Decimal
    top_selling_products: List[Dict[str, Any]]
    slow_moving_products: List[Dict[str, Any]]
    inventory_turnover_rate: Decimal


class DashboardSummary(BaseModel):
    """Dashboard summary for quick overview"""
    today_revenue: Decimal
    today_bookings: int
    today_new_customers: int
    pending_bookings: int
    low_stock_alerts: int
    pending_feedback: int
    staff_on_duty: int
    occupancy_rate: Decimal
    revenue_trend: List[Dict[str, Any]]
    booking_trend: List[Dict[str, Any]]


class ReportRequest(BaseModel):
    """Schema for generating reports"""
    report_type: str
    start_date: datetime
    end_date: datetime
    granularity: TimeGranularity = TimeGranularity.DAY
    filters: Optional[Dict[str, Any]] = None


class ReportResponse(BaseModel):
    """Schema for report response"""
    report_id: str
    report_type: str
    generated_at: datetime
    date_range: DateRange
    data: Dict[str, Any]
    summary: Optional[Dict[str, Any]] = None
