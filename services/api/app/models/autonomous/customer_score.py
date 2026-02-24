"""Customer Score Firestore Model.

Manages customer LTV, risk scores, and engagement metrics.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

import structlog

from app.models.base import FirestoreBase

logger = structlog.get_logger()


class CustomerSegment(str, Enum):
    """Customer segmentation based on value."""
    VIP = "vip"  # Top 10% by LTV
    HIGH_VALUE = "high_value"  # Top 30%
    REGULAR = "regular"  # Middle 40%
    AT_RISK = "at_risk"  # Declining engagement
    NEW = "new"  # Less than 3 visits
    DORMANT = "dormant"  # No visits in 90+ days


class RiskLevel(str, Enum):
    """Churn risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CustomerScoreModel(FirestoreBase):
    """Model for customer scoring operations.
    
    Tracks LTV, engagement, churn risk, and segment classification
    for intelligent agent decision-making.
    """
    
    collection_name = "customer_scores"
    
    async def get_customer_score(
        self,
        customer_id: str,
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get score for a specific customer.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID
            
        Returns:
            Customer score if found
        """
        score_id = f"score_{customer_id}"
        return await self.get(score_id)
    
    async def get_by_segment(
        self,
        segment: CustomerSegment,
        salon_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get customers by segment.
        
        Args:
            segment: Customer segment
            salon_id: Salon ID
            limit: Maximum results
            
        Returns:
            List of customer scores
        """
        return await self.list(
            salon_id=salon_id,
            filters=[("segment", "==", segment.value)],
            order_by="ltv.total",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_at_risk_customers(
        self,
        salon_id: str,
        min_risk: RiskLevel = RiskLevel.MEDIUM,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get customers at risk of churning.
        
        Args:
            salon_id: Salon ID
            min_risk: Minimum risk level
            limit: Maximum results
            
        Returns:
            List of at-risk customers
        """
        risk_levels = {
            RiskLevel.LOW: [RiskLevel.MEDIUM.value, RiskLevel.HIGH.value, RiskLevel.CRITICAL.value],
            RiskLevel.MEDIUM: [RiskLevel.HIGH.value, RiskLevel.CRITICAL.value],
            RiskLevel.HIGH: [RiskLevel.HIGH.value, RiskLevel.CRITICAL.value],
            RiskLevel.CRITICAL: [RiskLevel.CRITICAL.value],
        }
        
        return await self.list(
            salon_id=salon_id,
            filters=[("churn_risk.level", "in", risk_levels.get(min_risk, []))],
            order_by="churn_risk.score",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def get_top_customers(
        self,
        salon_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get top customers by LTV.
        
        Args:
            salon_id: Salon ID
            limit: Maximum results
            
        Returns:
            List of top customers
        """
        return await self.list(
            salon_id=salon_id,
            order_by="ltv.total",
            order_direction="DESCENDING",
            limit=limit,
        )
    
    async def update_score(
        self,
        customer_id: str,
        salon_id: str,
        ltv: Dict[str, Any],
        engagement: Dict[str, Any],
        churn_risk: Dict[str, Any],
        segment: CustomerSegment,
    ) -> Optional[Dict[str, Any]]:
        """Update customer score.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID
            ltv: Lifetime value metrics
            engagement: Engagement metrics
            churn_risk: Churn risk assessment
            segment: Customer segment
            
        Returns:
            Updated score
        """
        score_id = f"score_{customer_id}"
        now = datetime.utcnow()
        
        update_data = {
            "ltv": ltv,
            "engagement": engagement,
            "churn_risk": churn_risk,
            "segment": segment.value,
            "last_updated": now.isoformat(),
        }
        
        return await self.update(score_id, update_data)
    
    async def create_or_update_score(
        self,
        customer_id: str,
        salon_id: str,
        ltv: Dict[str, Any],
        engagement: Dict[str, Any],
        churn_risk: Dict[str, Any],
        segment: CustomerSegment,
    ) -> Dict[str, Any]:
        """Create or update customer score.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID
            ltv: Lifetime value metrics
            engagement: Engagement metrics
            churn_risk: Churn risk assessment
            segment: Customer segment
            
        Returns:
            Created or updated score
        """
        score_id = f"score_{customer_id}"
        now = datetime.utcnow()
        
        score_data = {
            "id": score_id,
            "salon_id": salon_id,
            "customer_id": customer_id,
            "ltv": ltv,
            "engagement": engagement,
            "churn_risk": churn_risk,
            "segment": segment.value,
            "last_updated": now.isoformat(),
            "created_at": now.isoformat(),
        }
        
        return await self.create(score_data, document_id=score_id)
    
    async def calculate_ltv(
        self,
        customer_id: str,
        salon_id: str,
        total_spent: float,
        visit_count: int,
        avg_visit_value: float,
        membership_active: bool = False,
    ) -> Dict[str, Any]:
        """Calculate LTV metrics.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID
            total_spent: Total amount spent
            visit_count: Number of visits
            avg_visit_value: Average spend per visit
            membership_active: Whether customer has active membership
            
        Returns:
            LTV metrics dict
        """
        # Simple LTV calculation (can be enhanced with ML)
        # LTV = Avg Visit Value * Visit Frequency * Customer Lifespan
        
        # Estimate visit frequency (visits per month)
        visit_frequency = visit_count / 12 if visit_count > 0 else 0
        
        # Estimate customer lifespan (months)
        lifespan_months = min(24, max(3, visit_count * 2))
        
        # Calculate projected LTV
        projected_ltv = avg_visit_value * visit_frequency * lifespan_months
        
        # Membership bonus
        if membership_active:
            projected_ltv *= 1.3  # 30% bonus for members
        
        return {
            "total": total_spent,
            "projected": projected_ltv,
            "avg_visit_value": avg_visit_value,
            "visit_frequency_monthly": round(visit_frequency, 2),
            "estimated_lifespan_months": lifespan_months,
            "membership_bonus": membership_active,
        }
    
    async def calculate_churn_risk(
        self,
        customer_id: str,
        salon_id: str,
        days_since_last_visit: int,
        visit_count: int,
        no_show_count: int,
        avg_gap_days: float,
    ) -> Dict[str, Any]:
        """Calculate churn risk.
        
        Args:
            customer_id: Customer document ID
            salon_id: Salon ID
            days_since_last_visit: Days since last booking
            visit_count: Total visits
            no_show_count: Number of no-shows
            avg_gap_days: Average days between visits
            
        Returns:
            Churn risk assessment
        """
        # Risk score calculation (0-100, higher = more risk)
        risk_score = 0
        
        # Days since last visit factor
        if days_since_last_visit > 90:
            risk_score += 40
        elif days_since_last_visit > 60:
            risk_score += 25
        elif days_since_last_visit > 30:
            risk_score += 10
        
        # Visit count factor (loyal customers less likely to churn)
        if visit_count < 3:
            risk_score += 20
        elif visit_count < 6:
            risk_score += 10
        
        # No-show factor
        if no_show_count > 2:
            risk_score += 15
        elif no_show_count > 0:
            risk_score += 5
        
        # Gap pattern factor
        if avg_gap_days > 0 and days_since_last_visit > avg_gap_days * 1.5:
            risk_score += 15
        
        # Determine risk level
        if risk_score >= 60:
            level = RiskLevel.CRITICAL
        elif risk_score >= 40:
            level = RiskLevel.HIGH
        elif risk_score >= 20:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        return {
            "score": min(100, risk_score),
            "level": level.value,
            "factors": {
                "days_since_last_visit": days_since_last_visit,
                "visit_count": visit_count,
                "no_show_count": no_show_count,
                "avg_gap_days": avg_gap_days,
            },
        }
    
    async def determine_segment(
        self,
        ltv: Dict[str, Any],
        engagement: Dict[str, Any],
        churn_risk: Dict[str, Any],
        visit_count: int,
    ) -> CustomerSegment:
        """Determine customer segment.
        
        Args:
            ltv: LTV metrics
            engagement: Engagement metrics
            churn_risk: Churn risk assessment
            visit_count: Total visits
            
        Returns:
            Customer segment
        """
        # New customer
        if visit_count < 3:
            return CustomerSegment.NEW
        
        # Dormant (90+ days since last visit)
        if churn_risk.get("level") == RiskLevel.CRITICAL.value:
            return CustomerSegment.DORMANT
        
        # At risk
        if churn_risk.get("level") in [RiskLevel.HIGH.value, RiskLevel.MEDIUM.value]:
            return CustomerSegment.AT_RISK
        
        # Value-based segmentation
        total_ltv = ltv.get("total", 0)
        
        if total_ltv >= 50000:  # ₹50,000+
            return CustomerSegment.VIP
        elif total_ltv >= 20000:  # ₹20,000+
            return CustomerSegment.HIGH_VALUE
        else:
            return CustomerSegment.REGULAR
    
    async def get_segment_distribution(
        self,
        salon_id: str,
    ) -> Dict[str, int]:
        """Get customer distribution by segment.
        
        Args:
            salon_id: Salon ID
            
        Returns:
            Segment distribution counts
        """
        distribution = {segment.value: 0 for segment in CustomerSegment}
        
        for segment in CustomerSegment:
            scores = await self.list(
                salon_id=salon_id,
                filters=[("segment", "==", segment.value)],
                limit=1000,
            )
            distribution[segment.value] = len(scores)
        
        return distribution
