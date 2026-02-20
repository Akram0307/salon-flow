"""Loyalty Firestore Model.

Handles all database operations for loyalty transaction entities.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any

from google.cloud.firestore_v1.base_query import FieldFilter
import structlog

from app.models.base import FirestoreBase
from app.schemas import (
    LoyaltyTransaction,
    LoyaltyTransactionCreate,
    LoyaltyTransactionUpdate,
    LoyaltyTransactionType,
)
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()


class LoyaltyModel(FirestoreBase[LoyaltyTransaction, LoyaltyTransactionCreate, LoyaltyTransactionUpdate]):
    """Model for loyalty transaction operations.
    
    Provides CRUD operations and specialized queries for loyalty transactions.
    Tracks points earned, redeemed, and expired for customer loyalty programs.
    
    Attributes:
        collection_name: Firestore collection name ('loyalty_transactions')
        model: Pydantic model for LoyaltyTransaction
        create_schema: Pydantic schema for creating transactions
        update_schema: Pydantic schema for updating transactions
    
    Example:
        loyalty_model = LoyaltyModel()
        transactions = await loyalty_model.get_customer_transactions("customer_123", salon_id="salon_123")
    """
    
    collection_name = "loyalty_transactions"
    model = LoyaltyTransaction
    create_schema = LoyaltyTransactionCreate
    update_schema = LoyaltyTransactionUpdate
    
    # Business rule: 1 point per ₹10 spent
    POINTS_PER_RUPEE = 0.1
    # Points expire after 12 months
    EXPIRY_MONTHS = 12
    
    async def get_customer_transactions(
        self,
        customer_id: str,
        salon_id: str,
        transaction_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[LoyaltyTransaction]:
        """Get all loyalty transactions for a customer.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID for multi-tenant filtering
            transaction_type: Optional type filter (earn, redeem, expire)
            limit: Maximum results to return
            
        Returns:
            List of loyalty transactions
        
        Example:
            transactions = await loyalty_model.get_customer_transactions("customer_123", salon_id="salon_123")
        """
        filters = [("customer_id", "==", customer_id)]
        
        if transaction_type:
            filters.append(("transaction_type", "==", transaction_type))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="created_at",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def earn_points(
        self,
        customer_id: str,
        salon_id: str,
        amount_spent: float,
        booking_id: Optional[str] = None,
        payment_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> LoyaltyTransaction:
        """Create an earn transaction for loyalty points.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID
            amount_spent: Amount spent to calculate points
            booking_id: Optional associated booking
            payment_id: Optional associated payment
            description: Optional description
            
        Returns:
            Created loyalty transaction
        """
        # Calculate points (1 point per ₹10)
        points = int(amount_spent * self.POINTS_PER_RUPEE)
        
        # Set expiry date (12 months from now)
        expiry_date = date.today() + timedelta(days=365)
        
        transaction_data = {
            "customer_id": customer_id,
            "salon_id": salon_id,
            "transaction_type": "earn",
            "points": points,
            "amount_spent": amount_spent,
            "booking_id": booking_id,
            "payment_id": payment_id,
            "description": description or f"Earned {points} points for ₹{amount_spent:.2f} spent",
            "expiry_date": expiry_date.isoformat(),
            "status": "active",
        }
        
        return await self.create(transaction_data)
    
    async def redeem_points(
        self,
        customer_id: str,
        salon_id: str,
        points: int,
        booking_id: Optional[str] = None,
        payment_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[dict]:
        """Redeem loyalty points for a customer.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID for verification
            
        Returns:
            Redemption result with points redeemed and transaction ID
        """
        # Get customer's available points
        transactions = await self.list(
            salon_id=salon_id,
            filters=[("customer_id", "==", customer_id)],
            limit=500,
        )
        
        # Calculate available points (earned - redeemed - expired)
        available_points = 0
        for txn in transactions:
            if txn.transaction_type == "earn":
                available_points += txn.points
            elif txn.transaction_type in ("redeem", "expire"):
                available_points -= txn.points
        
        if available_points < points:
            return None
        
        # Create redemption transaction
        redemption_data = {
            "customer_id": customer_id,
            "salon_id": salon_id,
            "transaction_type": "redeem",
            "points": points,
            "redeemed_at": datetime.utcnow().isoformat(),
        }
        
        redemption = await self.create(redemption_data)
        
        return {
            "transaction_id": redemption.id,
            "points_redeemed": points,
            "remaining_points": available_points - points,
        }
    
    async def expire_points(
        self,
        salon_id: Optional[str] = None,
        batch_size: int = 100,
    ) -> int:
        """Expire loyalty points that have passed their expiry date.
        
        Args:
            salon_id: Optional salon ID (if None, process all salons)
            batch_size: Number of transactions to process
            
        Returns:
            Number of points expired
        """
        today = date.today()
        
        # Find earned transactions past expiry date that haven't been expired
        filters = [
            ("transaction_type", "==", "earn"),
            ("expires_at", "<", today.isoformat()),
            ("expired", "==", False),
        ]
        
        expired_txns = await self.list(
            salon_id=salon_id,
            filters=filters,
            limit=batch_size,
        )
        
        total_expired = 0
        for txn in expired_txns:
            try:
                # Create expiration transaction
                await self.create({
                    "customer_id": txn.customer_id,
                    "salon_id": txn.salon_id,
                    "transaction_type": "expire",
                    "points": txn.points,
                    "original_transaction_id": txn.id,
                    "expired_at": datetime.utcnow().isoformat(),
                })
                
                # Mark original as expired
                await self.update(txn.id, {"expired": True})
                
                total_expired += txn.points
            except Exception as e:
                logger.error(
                    "Failed to expire points",
                    transaction_id=txn.id,
                    error=str(e),
                )
        
        return total_expired
    
    async def get_customer_balance(
        self,
        customer_id: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Get loyalty points balance for a customer.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID for multi-tenant filtering
            
        Returns:
            Points balance summary
        """
        transactions = await self.list(
            salon_id=salon_id,
            filters=[("customer_id", "==", customer_id)],
            limit=500,
        )
        
        total_earned = 0
        total_redeemed = 0
        total_expired = 0
        
        for txn in transactions:
            if txn.transaction_type == "earn":
                total_earned += txn.points
            elif txn.transaction_type == "redeem":
                total_redeemed += txn.points
            elif txn.transaction_type == "expire":
                total_expired += txn.points
        
        return {
            "customer_id": customer_id,
            "total_earned": total_earned,
            "total_redeemed": total_redeemed,
            "total_expired": total_expired,
            "available_balance": total_earned - total_redeemed - total_expired,
        }
    
    async def get_transactions_by_date(
        self,
        target_date: date,
        salon_id: str,
        transaction_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[dict]:
        """Get loyalty transactions for a specific date.
        
        Args:
            target_date: Date to query
            salon_id: Salon ID for multi-tenant filtering
            transaction_type: Optional type filter
            limit: Maximum results to return
            
        Returns:
            List of transactions for the date
        """
        filters = [("created_at", ">=", target_date.isoformat())]
        
        next_day = target_date + timedelta(days=1)
        filters.append(("created_at", "<", next_day.isoformat()))
        
        if transaction_type:
            filters.append(("transaction_type", "==", transaction_type))
        
        return await self.list(
            salon_id=salon_id,
            filters=filters,
            order_by="created_at",
            limit=limit,
        )
