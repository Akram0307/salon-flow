"""
Payment schemas for Salon Flow SaaS.
Handles billing, invoices, and payment processing.
"""
from datetime import datetime, date as date_type, time as time_type
from decimal import Decimal
from typing import Optional, Dict, List, Any
from enum import Enum

from pydantic import Field, field_validator, model_validator

from .base import (
    FirestoreModel,
    TimestampMixin,
    PaymentMethod,
    PaymentStatus,
    generate_entity_id,
)


class InvoiceDetails(FirestoreModel):
    """Invoice details for a payment."""
    invoice_number: str = Field(..., description="Unique invoice number")
    invoice_date: date_type = Field(default_factory=date_type.today, description="Invoice date")
    due_date: Optional[date_type] = Field(default=None, description="Due date")
    invoice_url: Optional[str] = Field(default=None, description="Invoice PDF URL")
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['invoice_date'] = self.invoice_date.isoformat()
        if self.due_date:
            data['due_date'] = self.due_date.isoformat()
        return data


class InvoiceLineItem(FirestoreModel):
    """Line item in an invoice."""
    description: str = Field(..., description="Item description")
    quantity: int = Field(default=1, ge=1)
    unit_price: Decimal = Field(..., description="Price per unit")
    total_price: Decimal = Field(..., description="Total price")
    gst_rate: Decimal = Field(default=Decimal("5.0"), description="GST percentage")
    gst_amount: Decimal = Field(default=Decimal("0"), description="GST amount")
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['unit_price'] = float(self.unit_price)
        data['total_price'] = float(self.total_price)
        data['gst_rate'] = float(self.gst_rate)
        data['gst_amount'] = float(self.gst_amount)
        return data


class PaymentBreakdown(FirestoreModel):
    """Payment breakdown details."""
    subtotal: Decimal = Field(..., description="Subtotal before GST")
    gst_amount: Decimal = Field(default=Decimal("0"), description="Total GST")
    discount_amount: Decimal = Field(default=Decimal("0"), description="Discount applied")
    tip_amount: Decimal = Field(default=Decimal("0"), description="Tip amount")
    total_amount: Decimal = Field(..., description="Final total")
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['subtotal'] = float(self.subtotal)
        data['gst_amount'] = float(self.gst_amount)
        data['discount_amount'] = float(self.discount_amount)
        data['tip_amount'] = float(self.tip_amount)
        data['total_amount'] = float(self.total_amount)
        return data


class PaymentSplit(FirestoreModel):
    """Payment split across methods."""
    method: PaymentMethod = Field(..., description="Payment method")
    amount: Decimal = Field(..., description="Amount paid via this method")
    reference: Optional[str] = Field(default=None, description="Transaction reference")
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['amount'] = float(self.amount)
        return data


class PaymentBase(FirestoreModel, TimestampMixin):
    """Base payment schema."""
    salon_id: str = Field(default="", description="Salon ID")
    booking_id: str = Field(..., description="Associated booking ID")
    customer_id: str = Field(..., description="Customer ID")
    customer_name: str = Field(..., description="Customer name")
    
    # Amounts
    subtotal: Decimal = Field(..., ge=Decimal("0"), description="Subtotal before GST")
    gst_amount: Decimal = Field(default=Decimal("0"), description="GST amount")
    total_amount: Decimal = Field(..., description="Total amount")
    
    # Payment details
    payment_method: PaymentMethod = Field(default=PaymentMethod.CASH)
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    
    # Transaction info
    transaction_id: Optional[str] = Field(default=None, description="External transaction ID")
    transaction_time: Optional[datetime] = Field(default=None)
    
    # Invoice
    invoice: Optional[InvoiceDetails] = Field(default=None)
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    
    # Additional
    tip_amount: Decimal = Field(default=Decimal("0"))
    discount_amount: Decimal = Field(default=Decimal("0"))
    notes: Optional[str] = Field(default=None)
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['subtotal'] = float(self.subtotal)
        data['gst_amount'] = float(self.gst_amount)
        data['total_amount'] = float(self.total_amount)
        data['tip_amount'] = float(self.tip_amount)
        data['discount_amount'] = float(self.discount_amount)
        return data


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""
    pass


class PaymentUpdate(FirestoreModel):
    """Schema for updating a payment."""
    payment_status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None
    transaction_time: Optional[datetime] = None
    tip_amount: Optional[Decimal] = None
    notes: Optional[str] = None


class Payment(PaymentBase):
    """Complete payment schema."""
    id: str = Field(default_factory=lambda: generate_entity_id("payment"))
    payment_splits: List[PaymentSplit] = Field(default_factory=list)


class PaymentSummary(FirestoreModel):
    """Summary view of a payment."""
    id: str
    salon_id: str
    booking_id: str
    customer_name: str
    total_amount: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    created_at: datetime


class PaymentSearch(FirestoreModel):
    """Search parameters for payments."""
    salon_id: str
    customer_id: Optional[str] = None
    booking_id: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    payment_status: Optional[PaymentStatus] = None
    date_from: Optional[date_type] = None
    date_to: Optional[date_type] = None


class PaymentStats(FirestoreModel):
    """Payment statistics."""
    total_payments: int = Field(default=0)
    total_amount: Decimal = Field(default=Decimal("0"))
    total_gst: Decimal = Field(default=Decimal("0"))
    total_tips: Decimal = Field(default=Decimal("0"))
    by_method: Dict[str, Decimal] = Field(default_factory=dict)
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['total_amount'] = float(self.total_amount)
        data['total_gst'] = float(self.total_gst)
        data['total_tips'] = float(self.total_tips)
        data['by_method'] = {k: float(v) for k, v in self.by_method.items()}
        return data


class DailyRevenue(FirestoreModel):
    """Daily revenue report."""
    salon_id: str
    revenue_date: date_type = Field(..., description="Revenue date")
    total_bookings: int = Field(default=0)
    total_revenue: Decimal = Field(default=Decimal("0"))
    total_gst: Decimal = Field(default=Decimal("0"))
    total_tips: Decimal = Field(default=Decimal("0"))
    cash_revenue: Decimal = Field(default=Decimal("0"))
    upi_revenue: Decimal = Field(default=Decimal("0"))
    card_revenue: Decimal = Field(default=Decimal("0"))
    
    def to_firestore(self) -> Dict[str, Any]:
        data = super().to_firestore()
        data['revenue_date'] = self.revenue_date.isoformat()
        data['total_revenue'] = float(self.total_revenue)
        data['total_gst'] = float(self.total_gst)
        data['total_tips'] = float(self.total_tips)
        data['cash_revenue'] = float(self.cash_revenue)
        data['upi_revenue'] = float(self.upi_revenue)
        data['card_revenue'] = float(self.card_revenue)
        return data
