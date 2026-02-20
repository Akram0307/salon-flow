"""Payment Firestore Model.

Handles all database operations for payment entities.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any

from google.cloud.firestore_v1.base_query import FieldFilter
import structlog

from app.models.base import FirestoreBase
from app.schemas import (
    Payment,
    PaymentCreate,
    PaymentUpdate,
    PaymentStatus,
    PaymentMethod,
)
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class PaymentModel(FirestoreBase[Payment, PaymentCreate, PaymentUpdate]):
    """Model for payment operations.
    
    Provides CRUD operations and specialized queries for payment entities.
    Payments track financial transactions for bookings and services.
    
    Attributes:
        collection_name: Firestore collection name ('payments')
        model: Pydantic model for Payment
        create_schema: Pydantic schema for creating payments
        update_schema: Pydantic schema for updating payments
    
    Example:
        payment_model = PaymentModel()
        payments = await payment_model.get_by_booking("booking_123", salon_id="salon_123")
    """
    
    collection_name = "payments"
    model = Payment
    create_schema = PaymentCreate
    update_schema = PaymentUpdate
    
    async def get_by_booking(
        self,
        booking_id: str,
        salon_id: str,
    ) -> List[Payment]:
        """Get all payments for a booking.
        
        Args:
            booking_id: Booking document ID
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            List of payments for the booking
        
        Example:
            payments = await payment_model.get_by_booking("booking_123", salon_id="salon_123")
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("booking_id", "==", booking_id)],
            order_by="created_at",
            order_direction="DESCENDING",
        )
    
    async def get_by_customer(
        self,
        customer_id: str,
        salon_id: str,
        limit: int = 50,
    ) -> List[Payment]:
        """Get all payments for a customer.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of payments for the customer
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("customer_id", "==", customer_id)],
            order_by="created_at",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_daily_revenue(
        self,
        salon_id: str,
        target_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Get revenue summary for a specific date.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            target_date: Date to query (defaults to today)
            
        Returns:
            Revenue summary dictionary with totals by payment method
        """
        query_date = target_date or date.today()
        
        try:
            payments = await self.list(
                salon_id=salon_id,
                filters=[
                    ("payment_date", "==", query_date.isoformat()),
                    ("status", "==", "completed"),
                ],
                limit=500,
            )
            
            # Calculate totals
            total_revenue = 0
            total_gst = 0
            by_method = {}
            
            for payment in payments:
                amount = float(payment.total_amount or 0)
                gst = float(payment.gst_amount or 0)
                method = payment.method.value if hasattr(payment.method, 'value') else payment.method
                
                total_revenue += amount
                total_gst += gst
                
                if method not in by_method:
                    by_method[method] = {"count": 0, "amount": 0}
                by_method[method]["count"] += 1
                by_method[method]["amount"] += amount
            
            return {
                "date": query_date.isoformat(),
                "total_revenue": total_revenue,
                "total_gst": total_gst,
                "payment_count": len(payments),
                "by_method": by_method,
            }
            
        except Exception as e:
            logger.error(
                "Failed to get daily revenue",
                salon_id=salon_id,
                date=query_date,
                error=str(e),
            )
            raise
    
    async def get_revenue_range(
        self,
        salon_id: str,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """Get revenue summary for a date range.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            start_date: Start date
            end_date: End date
            
        Returns:
            Revenue summary with daily breakdown
        """
        try:
            payments = await self.list(
                salon_id=salon_id,
                filters=[
                    ("payment_date", ">=", start_date.isoformat()),
                    ("payment_date", "<=", end_date.isoformat()),
                    ("status", "==", "completed"),
                ],
                limit=1000,
            )
            
            # Aggregate by date
            daily_data = {}
            total_revenue = 0
            total_gst = 0
            
            for payment in payments:
                pay_date = payment.payment_date
                if isinstance(pay_date, date):
                    date_key = pay_date.isoformat()
                else:
                    date_key = pay_date
                
                amount = float(payment.total_amount or 0)
                gst = float(payment.gst_amount or 0)
                
                total_revenue += amount
                total_gst += gst
                
                if date_key not in daily_data:
                    daily_data[date_key] = {"revenue": 0, "gst": 0, "count": 0}
                
                daily_data[date_key]["revenue"] += amount
                daily_data[date_key]["gst"] += gst
                daily_data[date_key]["count"] += 1
            
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_revenue": total_revenue,
                "total_gst": total_gst,
                "payment_count": len(payments),
                "daily_breakdown": daily_data,
            }
            
        except Exception as e:
            logger.error(
                "Failed to get revenue range",
                salon_id=salon_id,
                start_date=start_date,
                end_date=end_date,
                error=str(e),
            )
            raise
    
    async def generate_invoice_number(
        self,
        salon_id: str,
        prefix: str = "INV",
    ) -> str:
        """Generate a unique invoice number.
        
        Args:
            salon_id: Salon ID
            prefix: Invoice number prefix
            
        Returns:
            Unique invoice number in format PREFIX-YYYYMMDD-XXXX
        """
        today = date.today()
        date_str = today.strftime("%Y%m%d")
        
        try:
            # Count payments today to get sequence
            count = await self.count(
                salon_id=salon_id,
                filters=[("payment_date", "==", today.isoformat())],
            )
            
            sequence = str(count + 1).zfill(4)
            invoice_number = f"{prefix}-{date_str}-{sequence}"
            
            return invoice_number
            
        except Exception as e:
            logger.error(
                "Failed to generate invoice number",
                salon_id=salon_id,
                error=str(e),
            )
            # Fallback to timestamp-based
            return f"{prefix}-{date_str}-{datetime.utcnow().strftime('%H%M%S')}"
    
    async def get_by_status(
        self,
        status: str,
        salon_id: str,
        limit: int = 100,
    ) -> List[Payment]:
        """Get payments by status.
        
        Args:
            status: Payment status to filter
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of payments with the status
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("status", "==", status)],
            order_by="created_at",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_by_method(
        self,
        method: str,
        salon_id: str,
        target_date: Optional[date] = None,
        limit: int = 100,
    ) -> List[Payment]:
        """Get payments by payment method.
        
        Args:
            method: Payment method (cash, upi, card, wallet, membership)
            salon_id: Salon ID for multi-tenant filtering
            target_date: Optional date filter
            limit: Maximum results to return
            
        Returns:
            List of payments with the method
        """
        filters = [("method", "==", method)]
        
        if target_date:
            filters.append(("payment_date", "==", target_date.isoformat()))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="created_at",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_by_invoice_number(
        self,
        invoice_number: str,
        salon_id: str,
    ) -> Optional[Payment]:
        """Get payment by invoice number.
        
        Args:
            invoice_number: Invoice number to search
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            Payment if found, None otherwise
        """
        return await self.get_by_field("invoice_number", invoice_number, salon_id=salon_id)
    
    async def update_status(
        self,
        payment_id: str,
        status: PaymentStatus,
        salon_id: str,
        notes: Optional[str] = None,
    ) -> Optional[Payment]:
        """Update payment status.
        
        Args:
            payment_id: Payment document ID
            status: New status
            salon_id: Salon ID for verification
            notes: Optional status change notes
            
        Returns:
            Updated payment if successful
        """
        payment = await self.get(payment_id)
        if not payment or payment.salon_id != salon_id:
            return None
        
        update_data = {
            "status": status.value if isinstance(status, PaymentStatus) else status,
            "status_updated_at": datetime.utcnow().isoformat(),
        }
        
        if notes:
            update_data["status_notes"] = notes
        
        return await self.update(payment_id, update_data)
    
    async def process_refund(
        self,
        payment_id: str,
        refund_amount: float,
        reason: str,
        salon_id: str,
    ) -> Optional[Payment]:
        """Process a refund for a payment.
        
        Args:
            payment_id: Payment document ID
            refund_amount: Amount to refund
            reason: Refund reason
            salon_id: Salon ID for verification
            
        Returns:
            Updated payment if successful
        """
        payment = await self.get(payment_id)
        if not payment or payment.salon_id != salon_id:
            return None
        
        update_data = {
            "status": "refunded",
            "refund": {
                "amount": refund_amount,
                "reason": reason,
                "refunded_at": datetime.utcnow().isoformat(),
            },
        }
        
        return await self.update(payment_id, update_data)
    
    async def get_pending_payments(
        self,
        salon_id: str,
        limit: int = 50,
    ) -> List[Payment]:
        """Get all pending payments.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of pending payments
        """
        return await self.get_by_status("pending", salon_id, limit)
    
    async def get_failed_payments(
        self,
        salon_id: str,
        limit: int = 50,
    ) -> List[Payment]:
        """Get all failed payments.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            limit: Maximum results to return
            
        Returns:
            List of failed payments
        """
        return await self.get_by_status("failed", salon_id, limit)
    
    async def get_monthly_revenue(
        self,
        salon_id: str,
        year: int,
        month: int,
    ) -> Dict[str, Any]:
        """Get revenue summary for a month.
        
        Args:
            salon_id: Salon ID for multi-tenant filtering
            year: Year
            month: Month (1-12)
            
        Returns:
            Monthly revenue summary
        """
        from calendar import monthrange
        
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)
        
        return await self.get_revenue_range(salon_id, start_date, end_date)
    
    async def get_payment_stats(
        self,
        salon_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Get payment statistics for a salon.
        
        Args:
            salon_id: Salon ID
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Payment statistics dictionary
        """
        try:
            filters = [("status", "==", "completed")]
            
            if start_date:
                filters.append(("payment_date", ">=", start_date.isoformat()))
            if end_date:
                filters.append(("payment_date", "<=", end_date.isoformat()))
            
            payments = await self.list(
                salon_id=salon_id,
                filters=filters,
                limit=2000,
            )
            
            total_amount = sum(float(p.total_amount or 0) for p in payments)
            total_gst = sum(float(p.gst_amount or 0) for p in payments)
            
            # Group by method
            by_method = {}
            for payment in payments:
                method = payment.method.value if hasattr(payment.method, 'value') else payment.method
                if method not in by_method:
                    by_method[method] = {"count": 0, "amount": 0}
                by_method[method]["count"] += 1
                by_method[method]["amount"] += float(payment.total_amount or 0)
            
            return {
                "total_payments": len(payments),
                "total_amount": total_amount,
                "total_gst": total_gst,
                "average_payment": total_amount / len(payments) if payments else 0,
                "by_method": by_method,
            }
            
        except Exception as e:
            logger.error(
                "Failed to get payment stats",
                salon_id=salon_id,
                error=str(e),
            )
            raise
    
    async def create_split_payment(
        self,
        booking_id: str,
        salon_id: str,
        splits: List[Dict[str, Any]],
        total_amount: float,
    ) -> List[Payment]:
        """Create multiple payment records for a split payment.
        
        Args:
            booking_id: Booking document ID
            salon_id: Salon ID
            splits: List of payment splits with method and amount
            total_amount: Total payment amount
            
        Returns:
            List of created payment records
        """
        try:
            invoice_number = await self.generate_invoice_number(salon_id)
            payments = []
            
            for idx, split in enumerate(splits):
                payment_data = {
                    "booking_id": booking_id,
                    "salon_id": salon_id,
                    "invoice_number": f"{invoice_number}-{idx + 1}" if len(splits) > 1 else invoice_number,
                    "method": split["method"],
                    "amount": split["amount"],
                    "total_amount": split["amount"],
                    "status": "completed",
                    "payment_date": date.today().isoformat(),
                    "is_split": True,
                    "split_index": idx + 1,
                    "split_total": len(splits),
                }
                
                payment = await self.create(payment_data)
                payments.append(payment)
            
            return payments
            
        except Exception as e:
            logger.error(
                "Failed to create split payment",
                booking_id=booking_id,
                salon_id=salon_id,
                error=str(e),
            )
            raise
