"""Gap Fill Orchestration Service.

Coordinates gap detection, customer matching, and outreach.
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import structlog

from app.models.autonomous import (
    GapModel,
    GapStatus,
    GapPriority,
    AutonomousDecisionModel,
    DecisionType,
    AutonomyLevel,
    AgentStateModel,
    AgentStatus,
    CustomerScoreModel,
    CustomerSegment,
    OutreachModel,
    OutreachType,
    OutreachChannel,
)
from app.services.autonomous.event_publisher import EventPublisher

logger = structlog.get_logger()


class GapFillService:
    """Orchestrates gap fill operations.
    
    Coordinates between:
    - Gap detection and tracking
    - Customer scoring and matching
    - Outreach execution
    - Decision recording
    """
    
    def __init__(self):
        self.gap_model = GapModel()
        self.decision_model = AutonomousDecisionModel()
        self.agent_model = AgentStateModel()
        self.customer_model = CustomerScoreModel()
        self.outreach_model = OutreachModel()
        self.event_publisher = EventPublisher()
    
    async def detect_gaps(
        self,
        salon_id: str,
        target_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """Detect schedule gaps for a date.
        
        Scans staff schedules and identifies gaps >= 30 minutes.
        
        Args:
            salon_id: Salon ID
            target_date: Date to scan (defaults to today)
            
        Returns:
            List of detected gaps
        """
        # This would integrate with the booking system
        # For now, return open gaps from database
        return await self.gap_model.get_open_gaps(
            salon_id=salon_id,
            date=target_date,
            min_duration_minutes=30,
        )
    
    async def get_fill_candidates(
        self,
        salon_id: str,
        gap: Dict[str, Any],
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get customer candidates for gap fill.
        
        Prioritizes customers based on:
        - Segment (VIP, HIGH_VALUE first)
        - Churn risk (AT_RISK customers)
        - Recent engagement
        - Service preferences matching gap
        
        Args:
            salon_id: Salon ID
            gap: Gap details
            limit: Maximum candidates
            
        Returns:
            List of candidate customers
        """
        candidates = []
        
        # Get at-risk customers first (retention focus)
        at_risk = await self.customer_model.get_at_risk_customers(
            salon_id=salon_id,
            min_risk="medium",
            limit=limit // 2,
        )
        candidates.extend(at_risk)
        
        # Get VIP/high-value customers
        vip = await self.customer_model.get_by_segment(
            segment=CustomerSegment.VIP,
            salon_id=salon_id,
            limit=limit // 2,
        )
        candidates.extend(vip)
        
        # Deduplicate and return top candidates
        seen_ids = set()
        unique_candidates = []
        for c in candidates:
            cid = c.get("customer_id")
            if cid and cid not in seen_ids:
                seen_ids.add(cid)
                unique_candidates.append(c)
        
        return unique_candidates[:limit]
    
    async def calculate_fill_priority(
        self,
        gap: Dict[str, Any],
        customer: Dict[str, Any],
    ) -> float:
        """Calculate priority score for filling a gap.
        
        Higher score = higher priority for outreach.
        
        Args:
            gap: Gap details
            customer: Customer score details
            
        Returns:
            Priority score (0-100)
        """
        score = 0.0
        
        # Gap duration factor (larger gaps = higher priority)
        duration = gap.get("duration_minutes", 0)
        if duration >= 120:
            score += 30
        elif duration >= 60:
            score += 20
        elif duration >= 30:
            score += 10
        
        # Revenue potential
        potential_revenue = gap.get("potential_revenue", 0)
        score += min(20, potential_revenue / 100)  # Max 20 points
        
        # Customer segment factor
        segment = customer.get("segment", "regular")
        segment_scores = {
            "vip": 25,
            "high_value": 20,
            "at_risk": 15,  # Retention focus
            "regular": 10,
            "new": 5,
        }
        score += segment_scores.get(segment, 5)
        
        # Churn risk factor (higher risk = higher priority for retention)
        churn_risk = customer.get("churn_risk", {}).get("score", 0)
        score += min(15, churn_risk / 10)  # Max 15 points
        
        # LTV factor
        ltv = customer.get("ltv", {}).get("total", 0)
        score += min(10, ltv / 5000)  # Max 10 points
        
        return min(100, score)
    
    async def execute_gap_fill(
        self,
        salon_id: str,
        gap_id: str,
        autonomy_level: AutonomyLevel = AutonomyLevel.SUPERVISED,
    ) -> Dict[str, Any]:
        """Execute gap fill workflow.
        
        Args:
            salon_id: Salon ID
            gap_id: Gap document ID
            autonomy_level: Autonomy level for the action
            
        Returns:
            Execution result
        """
        # Get gap details
        gap = await self.gap_model.get(gap_id)
        if not gap or gap.get("salon_id") != salon_id:
            return {"success": False, "error": "Gap not found"}
        
        if gap.get("status") != GapStatus.OPEN.value:
            return {"success": False, "error": f"Gap already {gap.get('status')}"}
        
        # Check agent state and rate limits
        agent_state = await self.agent_model.get_agent_state(salon_id, "gap_fill_agent")
        if agent_state:
            # Check circuit breaker
            cb_check = await self.agent_model.check_circuit_breaker(salon_id, "gap_fill_agent")
            if not cb_check.get("can_operate"):
                return {
                    "success": False,
                    "error": "Agent circuit breaker active",
                    "circuit_breaker": cb_check,
                }
            
            # Check rate limit
            rate_check = await self.agent_model.check_rate_limit(salon_id, "gap_fill_agent", "hourly")
            if not rate_check.get("allowed"):
                return {
                    "success": False,
                    "error": "Hourly rate limit exceeded",
                    "rate_limit": rate_check,
                }
        
        # Get fill candidates
        candidates = await self.get_fill_candidates(salon_id, gap)
        
        if not candidates:
            return {"success": False, "error": "No suitable candidates found"}
        
        # Calculate priorities
        prioritized = []
        for candidate in candidates:
            priority = await self.calculate_fill_priority(gap, candidate)
            prioritized.append({
                "customer": candidate,
                "priority": priority,
            })
        
        # Sort by priority
        prioritized.sort(key=lambda x: x["priority"], reverse=True)
        
        # Create decision record
        top_candidate = prioritized[0]
        customer = top_candidate["customer"]
        
        decision = await self.decision_model.create_decision(
            salon_id=salon_id,
            agent_name="gap_fill_agent",
            decision_type=DecisionType.GAP_FILL,
            autonomy_level=autonomy_level,
            context={
                "trigger_id": gap_id,
                "trigger_type": "schedule_gap",
                "customer_id": customer.get("customer_id"),
                "staff_id": gap.get("staff_id"),
                "staff_name": gap.get("staff_name"),
                "time_slot": gap.get("start_time"),
            },
            action_taken="outreach_initiated",
            action_details={
                "gap_duration_minutes": gap.get("duration_minutes"),
                "potential_revenue": gap.get("potential_revenue"),
                "customer_segment": customer.get("segment"),
                "priority_score": top_candidate["priority"],
            },
            revenue_impact={
                "potential": gap.get("potential_revenue", 0),
                "actual": 0,
            },
            approval_required=(autonomy_level == AutonomyLevel.SUPERVISED),
        )
        
        # Increment gap attempts
        await self.gap_model.increment_attempts(gap_id)
        
        # Record action in agent state
        await self.agent_model.record_action(
            salon_id=salon_id,
            agent_name="gap_fill_agent",
            action_type="gap_fill_outreach",
            success=True,
        )
        
        # Publish event
        await self.event_publisher.publish_decision_event(
            salon_id=salon_id,
            decision_id=decision["id"],
            agent_name="gap_fill_agent",
            decision_type="gap_fill",
            action="outreach_initiated",
            outcome="pending",
        )
        
        logger.info(
            "gap_fill_initiated",
            salon_id=salon_id,
            gap_id=gap_id,
            decision_id=decision["id"],
            customer_id=customer.get("customer_id"),
        )
        
        return {
            "success": True,
            "decision_id": decision["id"],
            "gap_id": gap_id,
            "candidate": customer,
            "priority": top_candidate["priority"],
            "requires_approval": autonomy_level == AutonomyLevel.SUPERVISED,
        }
    
    async def process_gap_filled(
        self,
        salon_id: str,
        gap_id: str,
        booking_id: str,
        customer_id: str,
    ) -> bool:
        """Process successful gap fill.
        
        Updates gap status, decision outcome, and records revenue.
        
        Args:
            salon_id: Salon ID
            gap_id: Gap document ID
            booking_id: Created booking ID
            customer_id: Customer who booked
            
        Returns:
            True if processed successfully
        """
        # Update gap status
        await self.gap_model.mark_filled(gap_id, booking_id, customer_id)
        
        # Find and update decision
        decision = await self.decision_model.get_by_gap(gap_id, salon_id)
        if decision:
            await self.decision_model.update_outcome(
                decision_id=decision["id"],
                status="success",
                result="Gap filled successfully",
                booking_id=booking_id,
            )
            
            # Record successful action
            revenue = decision.get("revenue_impact", {}).get("potential", 0)
            await self.agent_model.record_action(
                salon_id=salon_id,
                agent_name="gap_fill_agent",
                action_type="gap_fill_success",
                success=True,
                revenue=revenue,
            )
            
            # Publish event
            await self.event_publisher.publish_decision_event(
                salon_id=salon_id,
                decision_id=decision["id"],
                agent_name="gap_fill_agent",
                decision_type="gap_fill",
                action="gap_filled",
                outcome="success",
                revenue_impact=revenue,
            )
        
        logger.info(
            "gap_filled",
            salon_id=salon_id,
            gap_id=gap_id,
            booking_id=booking_id,
        )
        
        return True
