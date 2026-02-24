# Autonomous AI Agent Architecture
## Technical Design Document for Salon Flow Platform

**Version**: 1.0  
**Date**: February 2026  
**Status**: Implementation Ready

---

## Executive Summary

This document defines the technical architecture for implementing autonomous AI agents in the Salon Flow platform, focusing on the **Smart Fill Agent** as the primary autonomous system. The architecture enables 24/7 autonomous operation for schedule optimization, no-show prevention, and revenue maximization.

### Key Objectives
- Fill 73% of cancelled slots within 30 minutes
- Reduce no-show rate by 40% through predictive intervention
- Maximize revenue through intelligent profit scoring
- Enable autonomous decision-making with governance guardrails

---

## 1. Smart Fill Agent Architecture

### 1.1 Class Structure

```python
# File: /services/ai/app/agents/smart_fill/agent.py

from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import structlog

from app.services.agents import BaseAgent, AgentResponse
from app.services.openrouter_client import OpenRouterClient

logger = structlog.get_logger()


class AutonomyLevel(str, Enum):
    """Autonomy levels for agent decisions"""
    FULL_AUTO = "full_auto"          # No approval needed
    SUPERVISED = "supervised"         # Requires approval
    MANUAL_ONLY = "manual_only"       # Human-only action


class DecisionType(str, Enum):
    """Types of autonomous decisions"""
    GAP_FILL = "gap_fill"
    NO_SHOW_PREVENTION = "no_show_prevention"
    WAITLIST_PROMOTION = "waitlist_promotion"
    DISCOUNT_OFFER = "discount_offer"
    DYNAMIC_PRICING = "dynamic_pricing"


class ProfitScore(BaseModel):
    """Profit scoring result for a booking candidate"""
    customer_id: str
    score: float = Field(ge=0.0, le=100.0)
    components: Dict[str, float] = Field(default_factory=dict)
    breakdown: Dict[str, Any] = Field(default_factory=dict)
    
    # Score components
    base_revenue: float = 0.0
    margin_contribution: float = 0.0
    ltv_multiplier: float = 0.0
    loyalty_bonus: float = 0.0
    urgency_factor: float = 0.0


class NoShowPrediction(BaseModel):
    """No-show probability prediction"""
    booking_id: str
    probability: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    risk_factors: List[Dict[str, Any]] = Field(default_factory=list)
    intervention_recommended: bool = False
    recommended_actions: List[str] = Field(default_factory=list)


class AutonomousDecision(BaseModel):
    """Record of an autonomous decision made by the agent"""
    decision_id: str
    decision_type: DecisionType
    autonomy_level: AutonomyLevel
    timestamp: datetime
    context: Dict[str, Any]
    action_taken: str
    outcome: Optional[str] = None
    revenue_impact: Optional[float] = None
    approved_by: Optional[str] = None
    

class SmartFillAgent(BaseAgent):
    """Autonomous agent for intelligent schedule gap filling and no-show prevention.
    
    Capabilities:
    - Real-time gap detection and filling
    - No-show prediction and prevention
    - Profit-optimized customer selection
    - Autonomous WhatsApp outreach
    - Dynamic discount calculation
    
    Autonomy Levels:
    - FULL_AUTO: Gap fills ≤20% discount, waitlist notifications
    - SUPERVISED: Discounts >20%, high-value customer offers
    - MANUAL_ONLY: Refunds, complaints, sensitive operations
    """
    
    name = "smart_fill"
    description = "Autonomous agent for schedule optimization and revenue maximization"
    system_prompt = """You are an autonomous Smart Fill Agent for a salon management platform.
Your mission is to maximize salon revenue by intelligently filling schedule gaps and preventing no-shows.

Core Responsibilities:
1. Monitor schedules for gaps ≥30 minutes
2. Predict no-show probability for upcoming bookings
3. Calculate profit scores for candidate customers
4. Execute autonomous outreach via WhatsApp
5. Manage waitlist promotions and escalations

Decision Framework:
- Prioritize high-LTV customers for premium slots
- Apply dynamic discounts within approved limits
- Escalate decisions exceeding autonomy bounds
- Track all decisions for audit and learning

Autonomy Rules:
- Full Auto: Discounts ≤20%, standard gap fills
- Supervised: Discounts >20%, VIP customer offers
- Manual Only: Refunds, complaints, staff issues

Always act in the salon's best interest while maintaining customer satisfaction."""

    # Configuration
    MIN_GAP_MINUTES = 30
    MAX_AUTO_DISCOUNT = 0.20  # 20%
    NO_SHOW_THRESHOLD = 0.60  # 60% probability
    RESPONSE_DEADLINE_MINUTES = 15
    MAX_CANDIDATES_PER_GAP = 5
    
    def __init__(
        self,
        client: Optional[OpenRouterClient] = None,
        autonomy_config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(client)
        self.autonomy_config = autonomy_config or self._default_autonomy_config()
        self._decision_history: List[AutonomousDecision] = []
        self._circuit_breaker_active = False
        self._error_count = 0
        self._max_errors_before_breaker = 5
    
    def _default_autonomy_config(self) -> Dict[str, Any]:
        """Default autonomy configuration"""
        return {
            "full_auto": {
                "max_discount_percent": 20,
                "max_daily_actions": 50,
                "allowed_decisions": [
                    DecisionType.GAP_FILL,
                    DecisionType.WAITLIST_PROMOTION,
                    DecisionType.NO_SHOW_PREVENTION,
                ]
            },
            "supervised": {
                "max_discount_percent": 35,
                "requires_approval": True,
                "allowed_decisions": [
                    DecisionType.DISCOUNT_OFFER,
                    DecisionType.DYNAMIC_PRICING,
                ]
            },
            "manual_only": {
                "allowed_decisions": []  # All require human
            },
            "circuit_breaker": {
                "error_threshold": 5,
                "cooldown_minutes": 30,
                "auto_recovery": True
            }
        }
    
    # =================================================================
    # CORE METHODS
    # =================================================================
    
    async def scan_for_gaps(
        self,
        salon_id: str,
        date: str,
        staff_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Scan schedule for optimization opportunities.
        
        Args:
            salon_id: Salon identifier
            date: Date to scan (YYYY-MM-DD)
            staff_id: Optional specific staff to scan
            context: Additional context
            
        Returns:
            List of detected gaps with priority scores
        """
        prompt = f"""Analyze the schedule for {date} and identify all optimization opportunities.

Salon ID: {salon_id}
Staff Filter: {staff_id or 'All staff'}

Gap Detection Rules:
- Minimum gap duration: {self.MIN_GAP_MINUTES} minutes
- Peak hours priority: 10am-7pm
- Consider buffer times between services

For each gap, provide:
1. Gap ID (generated)
2. Staff ID and name
3. Start time and end time
4. Duration in minutes
5. Priority score (0-100) based on:
   - Time of day (peak hours = higher)
   - Duration (longer = higher)
   - Staff utilization impact
6. Potential revenue loss
7. Recommended filling strategy

Output as structured JSON."""
        
        return await self.generate(prompt, context, use_cache=False)
    
    async def predict_no_show(
        self,
        booking_id: str,
        booking_data: Dict[str, Any],
        customer_history: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> NoShowPrediction:
        """Predict no-show probability for a booking.
        
        Uses weighted model:
        P(NoShow) = w1*History + w2*Time + w3*Day + w4*Service + w5*Weather + w6*LeadTime
        
        Args:
            booking_id: Booking identifier
            booking_data: Booking details
            customer_history: Customer's booking history
            context: Additional context
            
        Returns:
            NoShowPrediction with probability and recommendations
        """
        # Feature extraction
        features = self._extract_no_show_features(booking_data, customer_history)
        
        # Calculate probability using weighted model
        weights = {
            "history": 0.30,      # Past no-show rate
            "time": 0.15,         # Time of day
            "day": 0.10,          # Day of week
            "service": 0.10,      # Service type
            "weather": 0.10,      # Weather conditions
            "lead_time": 0.15,    # Days between booking and appointment
            "confirmation": 0.10  # Confirmation status
        }
        
        probability = sum(
            weights.get(feature, 0) * value
            for feature, value in features.items()
        )
        
        # Determine intervention
        intervention_recommended = probability >= self.NO_SHOW_THRESHOLD
        
        # Generate recommendations
        recommended_actions = []
        if intervention_recommended:
            if probability >= 0.80:
                recommended_actions = [
                    "immediate_confirmation_call",
                    "offer_incentive_to_confirm",
                    "prepare_waitlist_backup"
                ]
            elif probability >= 0.60:
                recommended_actions = [
                    "send_whatsapp_reminder",
                    "request_confirmation"
                ]
        
        return NoShowPrediction(
            booking_id=booking_id,
            probability=probability,
            confidence=0.85,  # Model confidence
            risk_factors=self._identify_risk_factors(features),
            intervention_recommended=intervention_recommended,
            recommended_actions=recommended_actions
        )
    
    def _extract_no_show_features(
        self,
        booking_data: Dict[str, Any],
        customer_history: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract features for no-show prediction"""
        features = {}
        
        # History: Past no-show rate
        if customer_history:
            no_shows = sum(1 for h in customer_history if h.get("status") == "no_show")
            features["history"] = no_shows / len(customer_history)
        else:
            features["history"] = 0.15  # Default for new customers
        
        # Time: Early morning and late evening have higher no-show rates
        hour = int(booking_data.get("time", "12:00").split(":")[0])
        if hour < 10 or hour > 19:
            features["time"] = 0.7
        else:
            features["time"] = 0.3
        
        # Day: Weekends have lower no-show rates
        day_of_week = datetime.strptime(booking_data.get("date", "2024-01-01"), "%Y-%m-%d").weekday()
        features["day"] = 0.3 if day_of_week >= 5 else 0.5
        
        # Service: Some services have higher no-show rates
        service_category = booking_data.get("service_category", "general")
        service_no_show_rates = {
            "haircut": 0.4,
            "color": 0.3,
            "treatment": 0.5,
            "general": 0.4
        }
        features["service"] = service_no_show_rates.get(service_category, 0.4)
        
        # Weather: Bad weather increases no-shows (would integrate weather API)
        features["weather"] = 0.4  # Default neutral
        
        # Lead time: Longer lead times increase no-show probability
        booking_date = datetime.strptime(booking_data.get("created_at", "2024-01-01"), "%Y-%m-%d")
        appointment_date = datetime.strptime(booking_data.get("date", "2024-01-01"), "%Y-%m-%d")
        lead_days = (appointment_date - booking_date).days
        if lead_days > 14:
            features["lead_time"] = 0.8
        elif lead_days > 7:
            features["lead_time"] = 0.6
        else:
            features["lead_time"] = 0.3
        
        # Confirmation: Unconfirmed bookings have higher no-show rates
        features["confirmation"] = 0.7 if not booking_data.get("confirmed") else 0.2
        
        return features
    
    def _identify_risk_factors(self, features: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify top risk factors from features"""
        risk_factors = []
        for feature, value in sorted(features.items(), key=lambda x: x[1], reverse=True):
            if value >= 0.5:
                risk_factors.append({
                    "factor": feature,
                    "value": value,
                    "severity": "high" if value >= 0.7 else "medium"
                })
        return risk_factors[:3]  # Top 3 risk factors
    
    async def calculate_profit_score(
        self,
        customer_id: str,
        customer_data: Dict[str, Any],
        slot_details: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ProfitScore:
        """Calculate profit score for a customer-slot match.
        
        Formula:
        ProfitScore = (Price × Margin) + (LTV × 0.1) + LoyaltyBonus + UrgencyFactor
        
        Args:
            customer_id: Customer identifier
            customer_data: Customer details including LTV, loyalty tier
            slot_details: Slot details including service, price
            context: Additional context
            
        Returns:
            ProfitScore with breakdown
        """
        # Base revenue from slot
        price = slot_details.get("price", 0)
        margin = slot_details.get("margin", 0.60)  # Default 60% margin
        base_revenue = price * margin
        
        # LTV multiplier
        ltv = customer_data.get("lifetime_value", 0)
        ltv_multiplier = ltv * 0.1
        
        # Loyalty bonus
        loyalty_tier = customer_data.get("loyalty_tier", "standard")
        loyalty_bonuses = {
            "platinum": 15.0,
            "gold": 10.0,
            "silver": 5.0,
            "bronze": 2.0,
            "standard": 0.0
        }
        loyalty_bonus = loyalty_bonuses.get(loyalty_tier, 0.0)
        
        # Urgency factor (how soon is the slot)
        slot_time = datetime.fromisoformat(slot_details.get("start_time", "2024-01-01T00:00:00"))
        hours_until = (slot_time - datetime.now()).total_seconds() / 3600
        if hours_until < 2:
            urgency_factor = 10.0  # High urgency
        elif hours_until < 6:
            urgency_factor = 5.0
        else:
            urgency_factor = 0.0
        
        # Calculate total score
        total_score = min(100, base_revenue + ltv_multiplier + loyalty_bonus + urgency_factor)
        
        return ProfitScore(
            customer_id=customer_id,
            score=total_score,
            components={
                "base_revenue": base_revenue,
                "ltv_multiplier": ltv_multiplier,
                "loyalty_bonus": loyalty_bonus,
                "urgency_factor": urgency_factor
            },
            breakdown={
                "price": price,
                "margin": margin,
                "ltv": ltv,
                "loyalty_tier": loyalty_tier,
                "hours_until_slot": hours_until
            },
            base_revenue=base_revenue,
            margin_contribution=margin,
            ltv_multiplier=ltv_multiplier,
            loyalty_bonus=loyalty_bonus,
            urgency_factor=urgency_factor
        )
    
    async def select_best_candidate(
        self,
        gap_details: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], ProfitScore]:
        """Select the best candidate for a gap.
        
        Args:
            gap_details: Gap information
            candidates: List of candidate customers
            context: Additional context
            
        Returns:
            Tuple of (best_candidate, profit_score)
        """
        scored_candidates = []
        
        for candidate in candidates:
            score = await self.calculate_profit_score(
                customer_id=candidate["id"],
                customer_data=candidate,
                slot_details=gap_details
            )
            scored_candidates.append((candidate, score))
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1].score, reverse=True)
        
        return scored_candidates[0] if scored_candidates else (None, None)
    
    async def generate_outreach_message(
        self,
        customer_data: Dict[str, Any],
        slot_details: Dict[str, Any],
        discount_percent: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate personalized WhatsApp outreach message.
        
        Args:
            customer_data: Customer details
            slot_details: Slot information
            discount_percent: Optional discount to offer
            context: Additional context
            
        Returns:
            Generated message content
        """
        discount_text = ""
        if discount_percent:
            discount_text = f"\n🎁 Special: {discount_percent}% off this slot!"
        
        prompt = f"""Generate a personalized WhatsApp message for a gap fill opportunity.

Customer:
- Name: {customer_data.get('name')}
- Loyalty Tier: {customer_data.get('loyalty_tier', 'Standard')}
- Preferred Services: {customer_data.get('preferred_services', [])}

Available Slot:
- Service: {slot_details.get('service_name')}
- Date: {slot_details.get('date')}
- Time: {slot_details.get('time')}
- Stylist: {slot_details.get('staff_name')}
{discount_text}

Requirements:
- Under 200 characters
- Include emoji
- Create urgency without pressure
- Include one-tap booking link placeholder
- Response deadline: {self.RESPONSE_DEADLINE_MINUTES} minutes

Generate the message."""
        
        return await self.generate(prompt, context, use_cache=False)
    
    async def execute_autonomous_fill(
        self,
        gap_id: str,
        gap_details: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AutonomousDecision:
        """Execute autonomous gap fill with full audit trail.
        
        Args:
            gap_id: Gap identifier
            gap_details: Gap information
            candidates: List of candidate customers
            context: Additional context
            
        Returns:
            AutonomousDecision record
        """
        # Check circuit breaker
        if self._circuit_breaker_active:
            logger.warning("circuit_breaker_active", gap_id=gap_id)
            return self._create_decision(
                decision_type=DecisionType.GAP_FILL,
                autonomy_level=AutonomyLevel.MANUAL_ONLY,
                context={"gap_id": gap_id, "reason": "circuit_breaker_active"},
                action_taken="deferred_due_to_circuit_breaker"
            )
        
        # Select best candidate
        best_candidate, profit_score = await self.select_best_candidate(
            gap_details, candidates, context
        )
        
        if not best_candidate:
            return self._create_decision(
                decision_type=DecisionType.GAP_FILL,
                autonomy_level=AutonomyLevel.FULL_AUTO,
                context={"gap_id": gap_id},
                action_taken="no_suitable_candidates_found"
            )
        
        # Determine discount if needed
        discount_percent = None
        if gap_details.get("urgency") == "high":
            discount_percent = 10  # 10% for high urgency
        
        # Check autonomy level
        autonomy_level = AutonomyLevel.FULL_AUTO
        if discount_percent and discount_percent > self.MAX_AUTO_DISCOUNT * 100:
            autonomy_level = AutonomyLevel.SUPERVISED
        
        # Generate and send message
        message_response = await self.generate_outreach_message(
            best_candidate, gap_details, discount_percent, context
        )
        
        # Record decision
        decision = self._create_decision(
            decision_type=DecisionType.GAP_FILL,
            autonomy_level=autonomy_level,
            context={
                "gap_id": gap_id,
                "customer_id": best_candidate["id"],
                "profit_score": profit_score.score,
                "discount_percent": discount_percent
            },
            action_taken=f"sent_whatsapp_to_{best_candidate['id']}",
            revenue_impact=gap_details.get("price", 0) * (1 - (discount_percent or 0) / 100)
        )
        
        return decision
    
    def _create_decision(
        self,
        decision_type: DecisionType,
        autonomy_level: AutonomyLevel,
        context: Dict[str, Any],
        action_taken: str,
        revenue_impact: Optional[float] = None,
    ) -> AutonomousDecision:
        """Create and record an autonomous decision"""
        import uuid
        
        decision = AutonomousDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=decision_type,
            autonomy_level=autonomy_level,
            timestamp=datetime.utcnow(),
            context=context,
            action_taken=action_taken,
            revenue_impact=revenue_impact
        )
        
        self._decision_history.append(decision)
        logger.info(
            "autonomous_decision",
            decision_id=decision.decision_id,
            type=decision_type,
            autonomy=autonomy_level,
            action=action_taken
        )
        
        return decision
    
    def record_error(self, error: Exception):
        """Record error for circuit breaker"""
        self._error_count += 1
        if self._error_count >= self._max_errors_before_breaker:
            self._activate_circuit_breaker()
    
    def _activate_circuit_breaker(self):
        """Activate circuit breaker"""
        self._circuit_breaker_active = True
        logger.error("circuit_breaker_activated", error_count=self._error_count)
        
        # Schedule auto-recovery
        # In production, this would use the task scheduler
    
    def reset_circuit_breaker(self):
        """Reset circuit breaker after cooldown"""
        self._circuit_breaker_active = False
        self._error_count = 0
        logger.info("circuit_breaker_reset")
```

### 1.2 Profit Scoring Algorithm

```python
# File: /services/ai/app/agents/smart_fill/profit_scorer.py

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ScoringWeights:
    """Configurable weights for profit scoring"""
    base_revenue: float = 1.0
    margin: float = 0.6
    ltv_factor: float = 0.1
    loyalty_platinum: float = 15.0
    loyalty_gold: float = 10.0
    loyalty_silver: float = 5.0
    loyalty_bronze: float = 2.0
    urgency_critical: float = 10.0  # < 2 hours
    urgency_high: float = 5.0      # < 6 hours
    urgency_medium: float = 2.0    # < 24 hours
    service_match_bonus: float = 5.0
    history_bonus: float = 3.0


class ProfitScorer:
    """Advanced profit scoring engine for slot optimization"""
    
    def __init__(self, weights: ScoringWeights = None):
        self.weights = weights or ScoringWeights()
    
    def score(
        self,
        customer: Dict[str, Any],
        slot: Dict[str, Any],
        salon_config: Dict[str, Any] = None,
    ) -> float:
        """Calculate comprehensive profit score.
        
        Formula:
        Score = BaseRevenue + LTVComponent + LoyaltyBonus + UrgencyFactor + Bonuses
        
        Returns:
            Float score 0-100
        """
        score = 0.0
        
        # 1. Base Revenue Component
        price = slot.get("price", 0)
        margin = slot.get("margin", self.weights.margin)
        base_revenue = price * margin
        score += base_revenue * self.weights.base_revenue
        
        # 2. LTV Component
        ltv = customer.get("lifetime_value", 0)
        ltv_component = ltv * self.weights.ltv_factor
        score += ltv_component
        
        # 3. Loyalty Bonus
        loyalty_tier = customer.get("loyalty_tier", "standard").lower()
        loyalty_map = {
            "platinum": self.weights.loyalty_platinum,
            "gold": self.weights.loyalty_gold,
            "silver": self.weights.loyalty_silver,
            "bronze": self.weights.loyalty_bronze,
        }
        score += loyalty_map.get(loyalty_tier, 0)
        
        # 4. Urgency Factor
        slot_time = self._parse_datetime(slot.get("start_time"))
        hours_until = (slot_time - datetime.now()).total_seconds() / 3600
        
        if hours_until < 2:
            score += self.weights.urgency_critical
        elif hours_until < 6:
            score += self.weights.urgency_high
        elif hours_until < 24:
            score += self.weights.urgency_medium
        
        # 5. Service Match Bonus
        customer_services = set(customer.get("preferred_services", []))
        slot_service = slot.get("service_id")
        if slot_service in customer_services:
            score += self.weights.service_match_bonus
        
        # 6. History Bonus (repeat customer)
        visit_count = customer.get("visit_count", 0)
        if visit_count >= 5:
            score += self.weights.history_bonus
        
        # Normalize to 0-100
        return min(100.0, max(0.0, score))
    
    def rank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        slot: Dict[str, Any],
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:
        """Rank candidates by profit score.
        
        Returns:
            List of candidates with scores, sorted descending
        """
        scored = []
        for candidate in candidates:
            score = self.score(candidate, slot)
            scored.append({
                **candidate,
                "profit_score": score,
                "rank": 0  # Will be set after sorting
            })
        
        # Sort by score descending
        scored.sort(key=lambda x: x["profit_score"], reverse=True)
        
        # Assign ranks
        for i, candidate in enumerate(scored[:top_n], 1):
            candidate["rank"] = i
        
        return scored[:top_n]
    
    def _parse_datetime(self, dt_str: str) -> datetime:
        """Parse datetime string"""
        if not dt_str:
            return datetime.now() + timedelta(hours=24)
        try:
            return datetime.fromisoformat(dt_str)
        except:
            return datetime.now() + timedelta(hours=24)
```

---

## 2. Agent Orchestration System

### 2.1 Event-Driven Architecture

```python
# File: /services/ai/app/orchestration/event_bus.py

from typing import Dict, Any, Callable, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import asyncio
import json
import structlog

logger = structlog.get_logger()


class EventType(str, Enum):
    """System event types"""
    # Booking events
    BOOKING_CREATED = "booking.created"
    BOOKING_CANCELLED = "booking.cancelled"
    BOOKING_NO_SHOW = "booking.no_show"
    BOOKING_COMPLETED = "booking.completed"
    BOOKING_RESCHEDULED = "booking.rescheduled"
    
    # Schedule events
    GAP_DETECTED = "schedule.gap_detected"
    GAP_FILLED = "schedule.gap_filled"
    
    # Customer events
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_LTV_UPDATED = "customer.ltv_updated"
    CUSTOMER_TIER_CHANGED = "customer.tier_changed"
    
    # Agent events
    AGENT_DECISION_MADE = "agent.decision_made"
    AGENT_ACTION_REQUIRED = "agent.action_required"
    AGENT_ERROR = "agent.error"
    
    # System events
    CIRCUIT_BREAKER_TRIGGERED = "system.circuit_breaker"
    ALERT_TRIGGERED = "system.alert"


class Event(BaseModel):
    """Event structure"""
    event_id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    salon_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None


class EventHandler(BaseModel):
    """Registered event handler"""
    handler_id: str
    event_types: List[EventType]
    callback: Callable  # In practice, use string reference
    priority: int = 0
    enabled: bool = True


class EventBus:
    """Central event bus for agent orchestration"""
    
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._event_store: List[Event] = []
        self._max_store_size = 10000
    
    def subscribe(
        self,
        event_types: List[EventType],
        callback: Callable,
        priority: int = 0,
    ) -> str:
        """Subscribe to events"""
        import uuid
        handler_id = str(uuid.uuid4())
        
        handler = EventHandler(
            handler_id=handler_id,
            event_types=event_types,
            callback=callback,
            priority=priority
        )
        
        for event_type in event_types:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
            self._handlers[event_type].sort(key=lambda h: h.priority, reverse=True)
        
        logger.info("event_handler_subscribed", handler_id=handler_id, events=[e.value for e in event_types])
        return handler_id
    
    def unsubscribe(self, handler_id: str):
        """Unsubscribe handler"""
        for event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h.handler_id != handler_id
            ]
    
    async def publish(self, event: Event):
        """Publish event to all subscribers"""
        # Store event
        self._event_store.append(event)
        if len(self._event_store) > self._max_store_size:
            self._event_store = self._event_store[-self._max_store_size:]
        
        # Get handlers
        handlers = self._handlers.get(event.event_type, [])
        
        logger.info(
            "event_published",
            event_id=event.event_id,
            type=event.event_type.value,
            handlers_count=len(handlers)
        )
        
        # Execute handlers
        for handler in handlers:
            if not handler.enabled:
                continue
            try:
                if asyncio.iscoroutinefunction(handler.callback):
                    await handler.callback(event)
                else:
                    handler.callback(event)
            except Exception as e:
                logger.error(
                    "event_handler_error",
                    handler_id=handler.handler_id,
                    event_id=event.event_id,
                    error=str(e)
                )
    
    async def publish_gcp_pubsub(self, event: Event):
        """Publish to GCP Pub/Sub for cross-service events"""
        # Implementation would use google-cloud-pubsub
        # This is a placeholder for the actual implementation
        logger.info("publishing_to_pubsub", event_type=event.event_type.value)
        pass


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get or create event bus singleton"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
```

### 2.2 Inter-Agent Communication Protocol

```python
# File: /services/ai/app/orchestration/agent_communication.py

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import structlog

logger = structlog.get_logger()


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AgentMessage(BaseModel):
    """Message structure for inter-agent communication"""
    message_id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    from_agent: str
    to_agent: str
    message_type: str
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] = Field(default_factory=dict)
    requires_response: bool = False
    response_deadline: Optional[datetime] = None
    correlation_id: Optional[str] = None
    salon_id: Optional[str] = None


class AgentResponse(BaseModel):
    """Response to agent message"""
    message_id: str
    response_to: str
    from_agent: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool
    payload: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class AgentCommunicationHub:
    """Hub for inter-agent communication"""
    
    def __init__(self):
        self._agents: Dict[str, Any] = {}  # agent_name -> agent_instance
        self._message_queue: Dict[str, List[AgentMessage]] = {}  # agent_name -> messages
        self._response_handlers: Dict[str, Any] = {}
    
    def register_agent(self, agent_name: str, agent_instance: Any):
        """Register an agent with the hub"""
        self._agents[agent_name] = agent_instance
        self._message_queue[agent_name] = []
        logger.info("agent_registered", agent=agent_name)
    
    async def send_message(self, message: AgentMessage) -> Optional[AgentResponse]:
        """Send message to another agent"""
        target_agent = self._agents.get(message.to_agent)
        if not target_agent:
            logger.error("agent_not_found", agent=message.to_agent)
            return AgentResponse(
                message_id=str(__import__("uuid").uuid4()),
                response_to=message.message_id,
                from_agent="hub",
                success=False,
                error=f"Agent {message.to_agent} not found"
            )
        
        # Queue message
        self._message_queue[message.to_agent].append(message)
        
        # Process if agent has message handler
        if hasattr(target_agent, 'handle_message'):
            try:
                response = await target_agent.handle_message(message)
                return response
            except Exception as e:
                logger.error("message_handling_error", error=str(e))
                return AgentResponse(
                    message_id=str(__import__("uuid").uuid4()),
                    response_to=message.message_id,
                    from_agent=message.to_agent,
                    success=False,
                    error=str(e)
                )
        
        return None
    
    async def broadcast(
        self,
        from_agent: str,
        message_type: str,
        payload: Dict[str, Any],
        exclude: List[str] = None,
    ):
        """Broadcast message to all agents"""
        exclude = exclude or []
        for agent_name in self._agents:
            if agent_name not in exclude and agent_name != from_agent:
                message = AgentMessage(
                    from_agent=from_agent,
                    to_agent=agent_name,
                    message_type=message_type,
                    payload=payload
                )
                await self.send_message(message)
    
    def get_pending_messages(self, agent_name: str) -> List[AgentMessage]:
        """Get pending messages for an agent"""
        return self._message_queue.get(agent_name, [])


# Global hub instance
_communication_hub: Optional[AgentCommunicationHub] = None


def get_communication_hub() -> AgentCommunicationHub:
    """Get or create communication hub singleton"""
    global _communication_hub
    if _communication_hub is None:
        _communication_hub = AgentCommunicationHub()
    return _communication_hub
```

### 2.3 Workflow Engine

```python
# File: /services/ai/app/orchestration/workflow_engine.py

from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import asyncio
import structlog

logger = structlog.get_logger()


class WorkflowState(str, Enum):
    """Workflow execution states"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep(BaseModel):
    """Single step in a workflow"""
    step_id: str
    name: str
    agent: str
    action: str
    input_mapping: Dict[str, str] = Field(default_factory=dict)
    output_key: Optional[str] = None
    condition: Optional[str] = None  # Python expression
    on_failure: str = "stop"  # stop, continue, retry
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300


class Workflow(BaseModel):
    """Multi-agent workflow definition"""
    workflow_id: str
    name: str
    description: str
    trigger_event: str
    steps: List[WorkflowStep]
    timeout_seconds: int = 3600
    max_concurrent: int = 10


class WorkflowExecution(BaseModel):
    """Workflow execution instance"""
    execution_id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    workflow_id: str
    state: WorkflowState = WorkflowState.PENDING
    current_step: int = 0
    context: Dict[str, Any] = Field(default_factory=dict)
    step_results: Dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class WorkflowEngine:
    """Engine for executing multi-agent workflows"""
    
    def __init__(self):
        self._workflows: Dict[str, Workflow] = {}
        self._executions: Dict[str, WorkflowExecution] = {}
        self._agents: Dict[str, Any] = {}
    
    def register_workflow(self, workflow: Workflow):
        """Register a workflow"""
        self._workflows[workflow.workflow_id] = workflow
        logger.info("workflow_registered", workflow_id=workflow.workflow_id)
    
    def register_agent(self, name: str, agent: Any):
        """Register an agent for workflow steps"""
        self._agents[name] = agent
    
    async def start_workflow(
        self,
        workflow_id: str,
        initial_context: Dict[str, Any] = None,
    ) -> WorkflowExecution:
        """Start a workflow execution"""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            context=initial_context or {},
            started_at=datetime.utcnow()
        )
        
        self._executions[execution.execution_id] = execution
        
        # Execute workflow
        asyncio.create_task(self._execute_workflow(execution, workflow))
        
        return execution
    
    async def _execute_workflow(
        self,
        execution: WorkflowExecution,
        workflow: Workflow,
    ):
        """Execute workflow steps"""
        execution.state = WorkflowState.RUNNING
        
        for i, step in enumerate(workflow.steps):
            execution.current_step = i
            
            try:
                # Check condition
                if step.condition:
                    if not self._evaluate_condition(step.condition, execution.context):
                        logger.info("step_condition_not_met", step=step.step_id)
                        continue
                
                # Execute step
                result = await self._execute_step(step, execution)
                execution.step_results[step.step_id] = result
                
                # Store output
                if step.output_key:
                    execution.context[step.output_key] = result
                
                logger.info(
                    "workflow_step_completed",
                    execution_id=execution.execution_id,
                    step=step.step_id
                )
                
            except Exception as e:
                logger.error(
                    "workflow_step_failed",
                    execution_id=execution.execution_id,
                    step=step.step_id,
                    error=str(e)
                )
                
                if step.on_failure == "stop":
                    execution.state = WorkflowState.FAILED
                    execution.error = str(e)
                    execution.completed_at = datetime.utcnow()
                    return
                elif step.on_failure == "retry" and step.retry_count < step.max_retries:
                    step.retry_count += 1
                    # Retry the step
                    i -= 1
                    continue
        
        execution.state = WorkflowState.COMPLETED
        execution.completed_at = datetime.utcnow()
        logger.info(
            "workflow_completed",
            execution_id=execution.execution_id,
            duration_seconds=(execution.completed_at - execution.started_at).total_seconds()
        )
    
    async def _execute_step(
        self,
        step: WorkflowStep,
        execution: WorkflowExecution,
    ) -> Any:
        """Execute a single workflow step"""
        agent = self._agents.get(step.agent)
        if not agent:
            raise ValueError(f"Agent {step.agent} not found")
        
        # Map inputs
        inputs = {}
        for target_key, source_key in step.input_mapping.items():
            inputs[target_key] = execution.context.get(source_key)
        
        # Get agent method
        method = getattr(agent, step.action)
        if not method:
            raise ValueError(f"Method {step.action} not found on agent {step.agent}")
        
        # Execute
        if asyncio.iscoroutinefunction(method):
            return await method(**inputs)
        else:
            return method(**inputs)
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition expression"""
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return False
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status"""
        return self._executions.get(execution_id)


# Predefined workflows

NO_SHOW_WORKFLOW = Workflow(
    workflow_id="no_show_handling",
    name="No-Show Handling Workflow",
    description="Handles no-show events with prediction, outreach, and gap filling",
    trigger_event="booking.no_show",
    steps=[
        WorkflowStep(
            step_id="predict_no_show",
            name="Predict No-Show Probability",
            agent="smart_fill",
            action="predict_no_show",
            input_mapping={
                "booking_id": "booking_id",
                "booking_data": "booking_data",
                "customer_history": "customer_history"
            },
            output_key="no_show_prediction"
        ),
        WorkflowStep(
            step_id="check_prediction",
            name="Check if Intervention Needed",
            agent="smart_fill",
            action="check_intervention_needed",
            input_mapping={"prediction": "no_show_prediction"},
            output_key="intervention_needed",
            condition="no_show_prediction.get('probability', 0) >= 0.6"
        ),
        WorkflowStep(
            step_id="find_waitlist_candidates",
            name="Find Waitlist Candidates",
            agent="waitlist",
            action="get_candidates_for_slot",
            input_mapping={
                "service_id": "booking_data.service_id",
                "date": "booking_data.date",
                "time": "booking_data.time"
            },
            output_key="waitlist_candidates"
        ),
        WorkflowStep(
            step_id="select_best_candidate",
            name="Select Best Candidate",
            agent="smart_fill",
            action="select_best_candidate",
            input_mapping={
                "gap_details": "booking_data",
                "candidates": "waitlist_candidates"
            },
            output_key="selected_candidate"
        ),
        WorkflowStep(
            step_id="send_outreach",
            name="Send WhatsApp Outreach",
            agent="smart_fill",
            action="execute_autonomous_fill",
            input_mapping={
                "gap_id": "booking_id",
                "gap_details": "booking_data",
                "candidates": "waitlist_candidates"
            },
            output_key="outreach_result"
        )
    ]
)


# Global workflow engine
_workflow_engine: Optional[WorkflowEngine] = None


def get_workflow_engine() -> WorkflowEngine:
    """Get or create workflow engine singleton"""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
        _workflow_engine.register_workflow(NO_SHOW_WORKFLOW)
    return _workflow_engine
```

---

## 3. Autonomous Task Scheduler

### 3.1 Background Job Design

```python
# File: /services/ai/app/scheduler/task_scheduler.py

from typing import Dict, Any, Optional, List, Callable
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import structlog

logger = structlog.get_logger()


class TaskType(str, Enum):
    """Types of scheduled tasks"""
    GAP_SCAN = "gap_scan"
    NO_SHOW_CHECK = "no_show_check"
    WAITLIST_ESCALATION = "waitlist_escalation"
    DAILY_SUMMARY = "daily_summary"
    CLEANUP = "cleanup"
    MONITORING = "monitoring"


class TaskPriority(str, Enum):
    """Task priority levels"""
    CRITICAL = "critical"    # Execute immediately
    HIGH = "high"            # Execute within 1 minute
    NORMAL = "normal"        # Execute within 5 minutes
    LOW = "low"              # Execute when resources available


class ScheduledTask(BaseModel):
    """Scheduled task definition"""
    task_id: str
    task_type: TaskType
    name: str
    description: str
    interval_seconds: int
    priority: TaskPriority = TaskPriority.NORMAL
    enabled: bool = True
    max_retries: int = 3
    timeout_seconds: int = 300
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    last_error: Optional[str] = None
    success_count: int = 0
    failure_count: int = 0


class TaskExecution(BaseModel):
    """Task execution record"""
    execution_id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    task_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    success: bool = False
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None


class TaskScheduler:
    """Autonomous task scheduler for agent operations"""
    
    def __init__(self):
        self._tasks: Dict[str, ScheduledTask] = {}
        self._handlers: Dict[TaskType, Callable] = {}
        self._executions: List[TaskExecution] = []
        self._running = False
        self._max_concurrent = 5
        self._semaphore = asyncio.Semaphore(self._max_concurrent)
    
    def register_task(self, task: ScheduledTask, handler: Callable):
        """Register a scheduled task"""
        self._tasks[task.task_id] = task
        self._handlers[task.task_type] = handler
        logger.info(
            "task_registered",
            task_id=task.task_id,
            type=task.task_type.value,
            interval=task.interval_seconds
        )
    
    async def start(self):
        """Start the scheduler"""
        self._running = True
        logger.info("scheduler_started")
        
        while self._running:
            try:
                await self._run_pending_tasks()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error("scheduler_error", error=str(e))
                await asyncio.sleep(30)
    
    def stop(self):
        """Stop the scheduler"""
        self._running = False
        logger.info("scheduler_stopped")
    
    async def _run_pending_tasks(self):
        """Run all pending tasks"""
        now = datetime.utcnow()
        
        for task_id, task in self._tasks.items():
            if not task.enabled:
                continue
            
            if task.next_run and task.next_run <= now:
                asyncio.create_task(self._execute_task(task))
    
    async def _execute_task(self, task: ScheduledTask):
        """Execute a single task"""
        async with self._semaphore:
            execution = TaskExecution(task_id=task.task_id)
            
            try:
                logger.info("task_started", task_id=task.task_id)
                
                handler = self._handlers.get(task.task_type)
                if not handler:
                    raise ValueError(f"No handler for task type {task.task_type}")
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    handler(),
                    timeout=task.timeout_seconds
                )
                
                execution.success = True
                execution.result = result
                task.success_count += 1
                task.last_error = None
                
                logger.info(
                    "task_completed",
                    task_id=task.task_id,
                    success_count=task.success_count
                )
                
            except asyncio.TimeoutError:
                execution.error = "Task timeout"
                task.failure_count += 1
                task.last_error = "Timeout"
                logger.error("task_timeout", task_id=task.task_id)
                
            except Exception as e:
                execution.error = str(e)
                task.failure_count += 1
                task.last_error = str(e)
                logger.error("task_failed", task_id=task.task_id, error=str(e))
                
                # Retry logic
                if task.failure_count < task.max_retries:
                    task.next_run = datetime.utcnow() + timedelta(minutes=5)
                    logger.info("task_retry_scheduled", task_id=task.task_id)
            
            finally:
                execution.completed_at = datetime.utcnow()
                execution.duration_ms = int(
                    (execution.completed_at - execution.started_at).total_seconds() * 1000
                )
                
                self._executions.append(execution)
                task.last_run = execution.started_at
                task.next_run = datetime.utcnow() + timedelta(seconds=task.interval_seconds)
    
    def get_task_status(self, task_id: str) -> Optional[ScheduledTask]:
        """Get task status"""
        return self._tasks.get(task_id)
    
    def get_recent_executions(self, limit: int = 100) -> List[TaskExecution]:
        """Get recent task executions"""
        return self._executions[-limit:]


# Default scheduled tasks
DEFAULT_TASKS = [
    ScheduledTask(
        task_id="gap_scan_5min",
        task_type=TaskType.GAP_SCAN,
        name="Schedule Gap Scanner",
        description="Scan all salon schedules for gaps >= 30 minutes",
        interval_seconds=300,  # 5 minutes
        priority=TaskPriority.HIGH,
        timeout_seconds=120
    ),
    ScheduledTask(
        task_id="no_show_check_15min",
        task_type=TaskType.NO_SHOW_CHECK,
        name="No-Show Prediction Check",
        description="Check upcoming bookings for no-show probability",
        interval_seconds=900,  # 15 minutes
        priority=TaskPriority.NORMAL,
        timeout_seconds=180
    ),
    ScheduledTask(
        task_id="waitlist_escalation_1min",
        task_type=TaskType.WAITLIST_ESCALATION,
        name="Waitlist Escalation Handler",
        description="Escalate waitlist notifications with no response",
        interval_seconds=60,  # 1 minute
        priority=TaskPriority.CRITICAL,
        timeout_seconds=30
    ),
    ScheduledTask(
        task_id="daily_summary_6am",
        task_type=TaskType.DAILY_SUMMARY,
        name="Daily Summary Generator",
        description="Generate daily summary for salon owners",
        interval_seconds=86400,  # 24 hours
        priority=TaskPriority.LOW,
        timeout_seconds=600
    ),
]


# Global scheduler instance
_task_scheduler: Optional[TaskScheduler] = None


def get_task_scheduler() -> TaskScheduler:
    """Get or create task scheduler singleton"""
    global _task_scheduler
    if _task_scheduler is None:
        _task_scheduler = TaskScheduler()
    return _task_scheduler
```

### 3.2 Circuit Breaker Pattern

```python
# File: /services/ai/app/scheduler/circuit_breaker.py

from typing import Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import structlog

logger = structlog.get_logger()


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject all calls
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """Circuit breaker for protecting autonomous operations"""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 300,  # 5 minutes
        half_open_max_calls: int = 3,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._half_open_calls = 0
    
    @property
    def state(self) -> CircuitState:
        """Get current state"""
        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self._last_failure_time:
                elapsed = (datetime.utcnow() - self._last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self._transition_to(CircuitState.HALF_OPEN)
        
        return self._state
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerOpenError(
                f"Circuit breaker {self.name} is open"
            )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.half_open_max_calls:
                self._transition_to(CircuitState.CLOSED)
        else:
            self._failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self._failure_count += 1
        self._last_failure_time = datetime.utcnow()
        
        if self._state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)
        elif self._failure_count >= self.failure_threshold:
            self._transition_to(CircuitState.OPEN)
    
    def _transition_to(self, new_state: CircuitState):
        """Transition to new state"""
        old_state = self._state
        self._state = new_state
        
        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
            self._success_count = 0
        
        logger.info(
            "circuit_breaker_state_change",
            name=self.name,
            old_state=old_state.value,
            new_state=new_state.value
        )
    
    def reset(self):
        """Manually reset the circuit breaker"""
        self._transition_to(CircuitState.CLOSED)


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


# Circuit breaker registry
_circuit_breakers: dict = {}


def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """Get or create circuit breaker"""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name, **kwargs)
    return _circuit_breakers[name]
```

---

## 4. ML Model Integration

### 4.1 No-Show Prediction Model

```python
# File: /services/ai/app/ml/no_show_model.py

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
import structlog
import json

logger = structlog.get_logger()


class NoShowFeatures(BaseModel):
    """Features for no-show prediction"""
    # Customer features
    customer_id: str
    past_no_show_rate: float = 0.0
    total_bookings: int = 0
    avg_days_between_visits: float = 30.0
    loyalty_tier: str = "standard"
    lifetime_value: float = 0.0
    
    # Booking features
    booking_id: str
    service_category: str = "general"
    service_price: float = 0.0
    lead_time_days: int = 0
    booking_hour: int = 12
    booking_day_of_week: int = 0
    
    # Temporal features
    appointment_hour: int = 12
    appointment_day_of_week: int = 0
    is_weekend: bool = False
    is_holiday: bool = False
    
    # Weather features (would integrate weather API)
    weather_condition: str = "clear"
    temperature: float = 25.0
    
    # Confirmation features
    is_confirmed: bool = False
    confirmation_lead_hours: float = 0.0
    reminder_sent: bool = False


class NoShowPredictionResult(BaseModel):
    """Prediction result"""
    booking_id: str
    no_show_probability: float
    confidence: float
    risk_level: str  # low, medium, high, critical
    top_risk_factors: List[Dict[str, Any]]
    recommended_interventions: List[str]
    model_version: str


class NoShowPredictor:
    """ML model for no-show prediction"""
    
    def __init__(self, model_version: str = "v1.0.0"):
        self.model_version = model_version
        self._feature_weights = self._load_weights()
        self._thresholds = {
            "low": 0.3,
            "medium": 0.5,
            "high": 0.7,
            "critical": 0.85
        }
    
    def _load_weights(self) -> Dict[str, float]:
        """Load model weights (would load from Vertex AI or storage)"""
        return {
            # Customer features
            "past_no_show_rate": 0.25,
            "total_bookings": -0.05,  # More bookings = lower risk
            "loyalty_tier_platinum": -0.15,
            "loyalty_tier_gold": -0.10,
            "loyalty_tier_silver": -0.05,
            
            # Booking features
            "lead_time_days": 0.02,
            "service_price": -0.001,  # Higher price = lower no-show
            
            # Temporal features
            "appointment_hour_early": 0.10,  # Before 10am
            "appointment_hour_late": 0.08,   # After 7pm
            "is_weekend": -0.05,
            
            # Weather
            "weather_bad": 0.12,
            
            # Confirmation
            "is_confirmed": -0.20,
            "reminder_sent": -0.10,
        }
    
    def predict(self, features: NoShowFeatures) -> NoShowPredictionResult:
        """Predict no-show probability"""
        score = 0.0
        risk_factors = []
        
        # Customer history
        score += features.past_no_show_rate * self._feature_weights["past_no_show_rate"]
        if features.past_no_show_rate > 0.2:
            risk_factors.append({
                "factor": "high_no_show_history",
                "value": features.past_no_show_rate,
                "impact": "high"
            })
        
        # Loyalty tier
        tier_weight = self._feature_weights.get(f"loyalty_tier_{features.loyalty_tier}", 0)
        score += tier_weight
        
        # Lead time
        lead_time_contribution = min(features.lead_time_days * self._feature_weights["lead_time_days"], 0.3)
        score += lead_time_contribution
        if features.lead_time_days > 14:
            risk_factors.append({
                "factor": "long_lead_time",
                "value": features.lead_time_days,
                "impact": "medium"
            })
        
        # Appointment time
        if features.appointment_hour < 10:
            score += self._feature_weights["appointment_hour_early"]
            risk_factors.append({
                "factor": "early_appointment",
                "value": features.appointment_hour,
                "impact": "low"
            })
        elif features.appointment_hour > 19:
            score += self._feature_weights["appointment_hour_late"]
        
        # Weekend
        if features.is_weekend:
            score += self._feature_weights["is_weekend"]
        
        # Weather
        if features.weather_condition in ["rain", "storm", "extreme"]:
            score += self._feature_weights["weather_bad"]
            risk_factors.append({
                "factor": "bad_weather",
                "value": features.weather_condition,
                "impact": "medium"
            })
        
        # Confirmation
        if features.is_confirmed:
            score += self._feature_weights["is_confirmed"]
        else:
            risk_factors.append({
                "factor": "not_confirmed",
                "value": False,
                "impact": "high"
            })
        
        if features.reminder_sent:
            score += self._feature_weights["reminder_sent"]
        
        # Normalize to 0-1
        probability = max(0.0, min(1.0, score + 0.3))  # Base rate adjustment
        
        # Determine risk level
        risk_level = "low"
        for level, threshold in sorted(self._thresholds.items(), key=lambda x: x[1], reverse=True):
            if probability >= threshold:
                risk_level = level
                break
        
        # Generate interventions
        interventions = self._generate_interventions(probability, risk_factors)
        
        return NoShowPredictionResult(
            booking_id=features.booking_id,
            no_show_probability=probability,
            confidence=0.85,  # Model confidence
            risk_level=risk_level,
            top_risk_factors=risk_factors[:3],
            recommended_interventions=interventions,
            model_version=self.model_version
        )
    
    def _generate_interventions(
        self,
        probability: float,
        risk_factors: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommended interventions"""
        interventions = []
        
        if probability >= 0.7:
            interventions.append("immediate_phone_call")
            interventions.append("offer_incentive_to_confirm")
            interventions.append("prepare_waitlist_backup")
        elif probability >= 0.5:
            interventions.append("send_whatsapp_confirmation_request")
            interventions.append("send_reminder_with_benefit")
        elif probability >= 0.3:
            interventions.append("send_standard_reminder")
        
        # Factor-specific interventions
        factor_types = [f["factor"] for f in risk_factors]
        
        if "not_confirmed" in factor_types:
            interventions.append("request_confirmation")
        
        if "long_lead_time" in factor_types:
            interventions.append("send_appointment_approaching_reminder")
        
        if "bad_weather" in factor_types:
            interventions.append("send_weather_consideration_message")
        
        return list(set(interventions))  # Unique interventions
    
    def batch_predict(
        self,
        features_list: List[NoShowFeatures]
    ) -> List[NoShowPredictionResult]:
        """Batch prediction for multiple bookings"""
        return [self.predict(features) for features in features_list]
```

### 4.2 Customer LTV Scoring

```python
# File: /services/ai/app/ml/ltv_scorer.py

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()


class LTVScore(BaseModel):
    """Customer Lifetime Value score"""
    customer_id: str
    ltv_value: float
    ltv_tier: str  # bronze, silver, gold, platinum
    components: Dict[str, float]
    prediction_confidence: float
    recommended_actions: List[str]


class LTVScorer:
    """Customer Lifetime Value scoring engine"""
    
    def __init__(self):
        self._tier_thresholds = {
            "platinum": 50000,  # ₹50,000+
            "gold": 25000,
            "silver": 10000,
            "bronze": 5000,
            "standard": 0
        }
    
    def calculate_ltv(
        self,
        customer_id: str,
        customer_data: Dict[str, Any],
        transaction_history: List[Dict[str, Any]],
    ) -> LTVScore:
        """Calculate customer lifetime value.
        
        Formula:
        LTV = (Avg Transaction Value × Visit Frequency × Avg Customer Lifespan) + Referral Value
        """
        # Calculate components
        avg_transaction = self._calculate_avg_transaction(transaction_history)
        visit_frequency = self._calculate_visit_frequency(transaction_history)
        lifespan_months = self._estimate_lifespan(transaction_history)
        referral_value = self._calculate_referral_value(customer_data)
        
        # Calculate LTV
        ltv = (avg_transaction * visit_frequency * (lifespan_months / 12)) + referral_value
        
        # Determine tier
        tier = "standard"
        for t, threshold in sorted(self._tier_thresholds.items(), key=lambda x: x[1], reverse=True):
            if ltv >= threshold:
                tier = t
                break
        
        # Generate recommendations
        recommendations = self._generate_recommendations(tier, customer_data, transaction_history)
        
        return LTVScore(
            customer_id=customer_id,
            ltv_value=ltv,
            ltv_tier=tier,
            components={
                "avg_transaction": avg_transaction,
                "visit_frequency": visit_frequency,
                "lifespan_months": lifespan_months,
                "referral_value": referral_value
            },
            prediction_confidence=0.80,
            recommended_actions=recommendations
        )
    
    def _calculate_avg_transaction(self, transactions: List[Dict[str, Any]]) -> float:
        """Calculate average transaction value"""
        if not transactions:
            return 500.0  # Default
        
        total = sum(t.get("amount", 0) for t in transactions)
        return total / len(transactions)
    
    def _calculate_visit_frequency(self, transactions: List[Dict[str, Any]]) -> float:
        """Calculate visits per month"""
        if len(transactions) < 2:
            return 1.0  # Default: once per month
        
        dates = [t.get("date", datetime.utcnow()) for t in transactions]
        if isinstance(dates[0], str):
            dates = [datetime.fromisoformat(d) for d in dates]
        
        dates.sort()
        span_months = (dates[-1] - dates[0]).days / 30
        
        if span_months < 1:
            return len(transactions)
        
        return len(transactions) / span_months
    
    def _estimate_lifespan(self, transactions: List[Dict[str, Any]]) -> float:
        """Estimate customer lifespan in months"""
        if not transactions:
            return 12.0  # Default: 1 year
        
        dates = [t.get("date", datetime.utcnow()) for t in transactions]
        if isinstance(dates[0], str):
            dates = [datetime.fromisoformat(d) for d in dates]
        
        dates.sort()
        current_lifespan = (datetime.utcnow() - dates[0]).days / 30
        
        # Estimate future lifespan based on recency
        last_visit = dates[-1]
        months_since_last = (datetime.utcnow() - last_visit).days / 30
        
        if months_since_last > 6:
            # Churned customer
            return current_lifespan
        elif months_since_last > 3:
            # At risk
            return current_lifespan + 6
        else:
            # Active
            return current_lifespan + 24  # Assume 2 more years
    
    def _calculate_referral_value(self, customer_data: Dict[str, Any]) -> float:
        """Calculate referral value"""
        referrals = customer_data.get("referrals", 0)
        avg_referral_value = 500  # Average value per referral
        return referrals * avg_referral_value
    
    def _generate_recommendations(
        self,
        tier: str,
        customer_data: Dict[str, Any],
        transactions: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate tier-specific recommendations"""
        recommendations = []
        
        if tier == "platinum":
            recommendations.extend([
                "offer_vip_perks",
                "personal_stylist_assignment",
                "exclusive_event_invites",
                "priority_booking"
            ])
        elif tier == "gold":
            recommendations.extend([
                "loyalty_bonus_points",
                "birthday_special",
                "upgrade_opportunities"
            ])
        elif tier == "silver":
            recommendations.extend([
                "membership_upgrade_offer",
                "referral_incentive"
            ])
        else:
            recommendations.extend([
                "welcome_offer",
                "first_visit_discount"
            ])
        
        return recommendations
```

---

## 5. Integration Points

### 5.1 WhatsApp/Twilio Integration

```python
# File: /services/ai/app/integrations/whatsapp_integration.py

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import structlog

from app.adapters.whatsapp_adapter import WhatsAppAdapter, WhatsAppResult

logger = structlog.get_logger()


class AutonomousMessage(BaseModel):
    """Autonomous message with tracking"""
    message_id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    to: str
    message_type: str
    content: str
    salon_id: str
    customer_id: str
    triggered_by: str  # What triggered this message
    autonomy_level: str
    response_deadline: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    response: Optional[str] = None


class WhatsAppIntegration:
    """WhatsApp integration for autonomous messaging"""
    
    def __init__(self, adapter: WhatsAppAdapter = None):
        self.adapter = adapter or WhatsAppAdapter()
        self._pending_messages: Dict[str, AutonomousMessage] = {}
    
    async def send_autonomous_message(
        self,
        to: str,
        message_type: str,
        content: str,
        salon_id: str,
        customer_id: str,
        triggered_by: str,
        autonomy_level: str,
        response_deadline_minutes: int = 15,
    ) -> AutonomousMessage:
        """Send autonomous message with tracking"""
        message = AutonomousMessage(
            to=to,
            message_type=message_type,
            content=content,
            salon_id=salon_id,
            customer_id=customer_id,
            triggered_by=triggered_by,
            autonomy_level=autonomy_level,
            response_deadline=datetime.utcnow() + timedelta(minutes=response_deadline_minutes)
        )
        
        # Send via adapter
        result: WhatsAppResult = await self.adapter.send_message(
            to=to,
            message=content,
            salon_id=salon_id
        )
        
        if result.success:
            message.sent_at = datetime.utcnow()
            self._pending_messages[message.message_id] = message
            
            logger.info(
                "autonomous_message_sent",
                message_id=message.message_id,
                to=to,
                type=message_type
            )
        else:
            logger.error(
                "autonomous_message_failed",
                message_id=message.message_id,
                error=result.error
            )
        
        return message
    
    async def send_gap_fill_offer(
        self,
        customer_phone: str,
        customer_name: str,
        slot_details: Dict[str, Any],
        discount_percent: Optional[float],
        salon_id: str,
        customer_id: str,
    ) -> AutonomousMessage:
        """Send gap fill offer message"""
        discount_text = f"\n🎁 Special: {discount_percent}% off!" if discount_percent else ""
        
        content = f"""✨ Slot Available!

Hi {customer_name}! A slot just opened:

💇 {slot_details['service_name']}
📅 {slot_details['date']} at {slot_details['time']}
👤 {slot_details['staff_name']}
{discount_text}

⏰ Reply within 15 minutes to book!

Reply BOOK to confirm."""
        
        return await self.send_autonomous_message(
            to=customer_phone,
            message_type="gap_fill_offer",
            content=content,
            salon_id=salon_id,
            customer_id=customer_id,
            triggered_by="gap_detected",
            autonomy_level="full_auto",
            response_deadline_minutes=15
        )
    
    async def send_no_show_prevention(
        self,
        customer_phone: str,
        customer_name: str,
        booking_details: Dict[str, Any],
        salon_id: str,
        customer_id: str,
    ) -> AutonomousMessage:
        """Send no-show prevention message"""
        content = f"""⏰ Appointment Reminder

Hi {customer_name},

Your appointment is tomorrow:

💇 {booking_details['service_name']}
📅 {booking_details['date']} at {booking_details['time']}
👤 {booking_details['staff_name']}

Please confirm by replying YES.

Need to reschedule? Reply RESCHEDULE."""
        
        return await self.send_autonomous_message(
            to=customer_phone,
            message_type="no_show_prevention",
            content=content,
            salon_id=salon_id,
            customer_id=customer_id,
            triggered_by="high_no_show_probability",
            autonomy_level="full_auto",
            response_deadline_minutes=60
        )
    
    def check_expired_messages(self) -> list:
        """Check for messages past response deadline"""
        now = datetime.utcnow()
        expired = []
        
        for msg_id, msg in self._pending_messages.items():
            if msg.response_deadline and msg.response_deadline < now and not msg.responded_at:
                expired.append(msg)
        
        return expired
```

### 5.2 Firestore Real-time Listeners

```python
# File: /services/ai/app/integrations/firestore_listener.py

from typing import Dict, Any, Callable, Optional, List
from pydantic import BaseModel
from datetime import datetime
import asyncio
import structlog

# Would import: from google.cloud import firestore

logger = structlog.get_logger()


class FirestoreListener:
    """Real-time Firestore listener for schedule changes"""
    
    def __init__(self, project_id: str = "salon-saas-487508"):
        self.project_id = project_id
        self._listeners: Dict[str, Any] = {}
        self._callbacks: Dict[str, Callable] = {}
    
    async def listen_to_bookings(
        self,
        salon_id: str,
        callback: Callable[[Dict[str, Any]], None],
    ):
        """Listen to booking changes for a salon"""
        listener_id = f"bookings_{salon_id}"
        
        # In production, this would use Firestore on_snapshot
        # This is a simplified version
        logger.info("starting_booking_listener", salon_id=salon_id)
        
        self._callbacks[listener_id] = callback
        
        # Simulate listener (replace with actual Firestore listener)
        # db = firestore.Client(project=self.project_id)
        # doc_ref = db.collection(f"tenants/{salon_id}/bookings")
        # doc_ref.on_snapshot(lambda docs: self._handle_booking_change(docs, callback))
    
    async def listen_to_schedule(
        self,
        salon_id: str,
        date: str,
        callback: Callable[[Dict[str, Any]], None],
    ):
        """Listen to schedule changes for a specific date"""
        listener_id = f"schedule_{salon_id}_{date}"
        
        logger.info("starting_schedule_listener", salon_id=salon_id, date=date)
        
        self._callbacks[listener_id] = callback
    
    def _handle_booking_change(
        self,
        docs: List[Any],
        callback: Callable,
    ):
        """Handle booking document changes"""
        for doc in docs:
            if doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                
                # Determine change type
                change_type = "modified"
                if doc._document is None:
                    change_type = "deleted"
                # Would check if new
                
                asyncio.create_task(callback({
                    "type": change_type,
                    "data": data
                }))
    
    def stop_listener(self, listener_id: str):
        """Stop a specific listener"""
        if listener_id in self._listeners:
            self._listeners[listener_id].unsubscribe()
            del self._listeners[listener_id]
            del self._callbacks[listener_id]
            logger.info("listener_stopped", listener_id=listener_id)
```

### 5.3 Backend API Endpoints

```python
# File: /services/api/app/api/autonomous_agents.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/autonomous", tags=["Autonomous Agents"])


class GapScanRequest(BaseModel):
    """Request to trigger gap scan"""
    salon_id: str
    date: str
    staff_id: Optional[str] = None


class NoShowCheckRequest(BaseModel):
    """Request for no-show prediction"""
    salon_id: str
    booking_id: str


class AutonomousActionRequest(BaseModel):
    """Request to execute autonomous action"""
    salon_id: str
    action_type: str
    context: Dict[str, Any]
    require_approval: bool = False


class AutonomousActionResponse(BaseModel):
    """Response from autonomous action"""
    action_id: str
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None
    requires_approval: bool = False


@router.post("/scan-gaps", response_model=Dict[str, Any])
async def trigger_gap_scan(
    request: GapScanRequest,
    background_tasks: BackgroundTasks,
):
    """Trigger gap scan for a salon"""
    # Would call SmartFillAgent.scan_for_gaps
    return {
        "status": "scanning",
        "salon_id": request.salon_id,
        "date": request.date,
        "message": "Gap scan initiated in background"
    }


@router.post("/predict-no-show", response_model=Dict[str, Any])
async def predict_no_show(
    request: NoShowCheckRequest,
):
    """Get no-show prediction for a booking"""
    # Would call SmartFillAgent.predict_no_show
    return {
        "booking_id": request.booking_id,
        "no_show_probability": 0.65,
        "risk_level": "high",
        "recommended_interventions": [
            "send_whatsapp_confirmation",
            "prepare_waitlist_backup"
        ]
    }


@router.post("/execute", response_model=AutonomousActionResponse)
async def execute_autonomous_action(
    request: AutonomousActionRequest,
):
    """Execute an autonomous action"""
    # Would call appropriate agent method
    return AutonomousActionResponse(
        action_id="action_123",
        status="completed",
        message="Action executed successfully",
        result={"affected_bookings": 1},
        requires_approval=request.require_approval
    )


@router.get("/status/{salon_id}", response_model=Dict[str, Any])
async def get_autonomous_status(
    salon_id: str,
):
    """Get autonomous agent status for a salon"""
    return {
        "salon_id": salon_id,
        "agents_active": True,
        "circuit_breaker_status": "closed",
        "last_gap_scan": datetime.utcnow().isoformat(),
        "pending_actions": 3,
        "today_stats": {
            "gaps_filled": 5,
            "no_shows_prevented": 2,
            "revenue_impact": 4500.00
        }
    }


@router.get("/decisions/{salon_id}", response_model=List[Dict[str, Any]])
async def get_autonomous_decisions(
    salon_id: str,
    limit: int = 50,
):
    """Get recent autonomous decisions for audit"""
    # Would fetch from decision history
    return [
        {
            "decision_id": "dec_123",
            "type": "gap_fill",
            "autonomy_level": "full_auto",
            "timestamp": datetime.utcnow().isoformat(),
            "action": "sent_whatsapp_to_customer",
            "revenue_impact": 800.00
        }
    ]


@router.post("/approve/{decision_id}", response_model=Dict[str, Any])
async def approve_supervised_decision(
    decision_id: str,
    approver_id: str,
):
    """Approve a supervised decision"""
    return {
        "decision_id": decision_id,
        "approved": True,
        "approved_by": approver_id,
        "approved_at": datetime.utcnow().isoformat()
    }


@router.post("/circuit-breaker/reset", response_model=Dict[str, Any])
async def reset_circuit_breaker(
    salon_id: str,
):
    """Manually reset circuit breaker"""
    return {
        "salon_id": salon_id,
        "circuit_breaker": "reset",
        "reset_at": datetime.utcnow().isoformat()
    }
```

---

## 6. Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] Implement SmartFillAgent class with core methods
- [ ] Set up event bus and agent communication hub
- [ ] Create basic task scheduler with gap scanning
- [ ] Implement circuit breaker pattern

### Phase 2: ML Integration (Week 3-4)
- [ ] Deploy no-show prediction model
- [ ] Implement LTV scoring engine
- [ ] Create profit scoring algorithm
- [ ] Set up model versioning

### Phase 3: Autonomous Operations (Week 5-6)
- [ ] Implement autonomous WhatsApp messaging
- [ ] Set up Firestore listeners
- [ ] Create workflow engine
- [ ] Build escalation logic

### Phase 4: Monitoring & Governance (Week 7-8)
- [ ] Build audit logging system
- [ ] Create Owner PWA dashboard integration
- [ ] Implement approval workflows
- [ ] Set up alerting and monitoring

---

## 7. Configuration Reference

```yaml
# config/autonomous_agents.yaml

smart_fill_agent:
  min_gap_minutes: 30
  max_auto_discount_percent: 20
  no_show_threshold: 0.60
  response_deadline_minutes: 15
  max_candidates_per_gap: 5
  
autonomy_levels:
  full_auto:
    max_discount_percent: 20
    max_daily_actions: 50
  supervised:
    max_discount_percent: 35
    requires_approval: true
  manual_only:
    allowed_decisions: []

circuit_breaker:
  error_threshold: 5
  cooldown_minutes: 30
  auto_recovery: true

task_scheduler:
  gap_scan_interval_seconds: 300
  no_show_check_interval_seconds: 900
  waitlist_escalation_interval_seconds: 60
  max_concurrent_tasks: 5

ml_models:
  no_show_prediction:
    version: "v1.0.0"
    confidence_threshold: 0.85
  ltv_scoring:
    version: "v1.0.0"
    update_frequency_days: 7
```

---

## 8. Monitoring & Observability

### Key Metrics to Track

```python
METRICS = {
    # Operational metrics
    "gaps_detected_total": "counter",
    "gaps_filled_total": "counter",
    "gap_fill_success_rate": "gauge",
    "no_show_predictions_total": "counter",
    "no_show_prevention_success_rate": "gauge",
    
    # Performance metrics
    "gap_scan_duration_seconds": "histogram",
    "prediction_latency_seconds": "histogram",
    "message_delivery_latency_seconds": "histogram",
    
    # Business metrics
    "revenue_from_gap_fills": "counter",
    "revenue_from_no_show_prevention": "counter",
    "average_discount_used": "gauge",
    
    # System health
    "circuit_breaker_triggers": "counter",
    "autonomous_decisions_total": "counter",
    "decisions_by_autonomy_level": "counter",
    "error_rate": "gauge",
}
```

### Alerting Rules

```yaml
alerts:
  - name: high_error_rate
    condition: error_rate > 0.05
    severity: critical
    action: activate_circuit_breaker
    
  - name: gap_fill_rate_low
    condition: gap_fill_success_rate < 0.5
    severity: warning
    action: notify_admin
    
  - name: no_show_rate_high
    condition: no_show_rate > 0.15
    severity: warning
    action: increase_monitoring
```

---

## 9. Security Considerations

### Authentication & Authorization
- All autonomous actions must be logged with salon_id
- Rate limiting per salon to prevent abuse
- Approval required for high-value actions

### Data Privacy
- Customer data encrypted at rest and in transit
- WhatsApp messages follow DLT compliance (India)
- Audit trail for all autonomous decisions

### Circuit Breaker Safety
- Automatic pause on error threshold
- Manual override capability for owners
- Gradual recovery with half-open state

---

## 10. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Gap Fill Rate | 73% | Slots filled within 30 min |
| No-Show Reduction | 40% | Compare to baseline |
| Revenue Impact | ₹50K+/month | Additional revenue from fills |
| Autonomous Decision Accuracy | 95% | Correct decisions without human |
| Customer Satisfaction | >4.5/5 | Post-interaction surveys |
| System Uptime | 99.9% | Availability monitoring |

---

**Document End**
