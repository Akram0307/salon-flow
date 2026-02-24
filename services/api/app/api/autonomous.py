"""Autonomous Agent API Router.

Provides REST endpoints for autonomous agent operations:
- Decision tracking and management
- Agent state and circuit breaker control
- Approval workflow management
- Gap detection and management
- Outreach tracking
- Analytics and reporting
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
import structlog

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.core.deps import get_current_user, get_salon_id
from app.models.autonomous import (
    AutonomousDecisionModel,
    AgentStateModel,
    ApprovalModel,
    AuditLogModel,
    CustomerScoreModel,
    GapModel,
    OutreachModel,
    DecisionType,
    DecisionStatus,
    AutonomyLevel,
    AgentStatus,
    CircuitBreakerState,
    ApprovalStatus,
    ApprovalPriority,
    AuditEventType,
    AuditSeverity,
    GapStatus,
    OutreachStatus,
    OutreachType,
)
from app.schemas.autonomous import (
    DecisionCreate,
    DecisionResponse,
    DecisionUpdate,
    DecisionListResponse,
    DecisionStatsResponse,
    AgentStateResponse,
    AgentStateUpdate,
    AgentConfigUpdate,
    CircuitBreakerResponse,
    ApprovalRequestCreate,
    ApprovalRequestResponse,
    ApprovalAction,
    ApprovalListResponse,
    ApprovalStatsResponse,
    GapCreate,
    GapResponse,
    GapListResponse,
    GapStatsResponse,
    OutreachCreate,
    OutreachResponse,
    OutreachUpdate,
    OutreachListResponse,
    OutreachStatsResponse,
)
from app.schemas.base import PaginatedResponse

logger = structlog.get_logger()
router = APIRouter(prefix="/autonomous", tags=["Autonomous Agents"])


# ==================== DECISION ENDPOINTS ====================

@router.post("/decisions", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
async def create_decision(
    data: DecisionCreate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Create a new autonomous decision record.
    
    Records a decision made by an autonomous agent for tracking
    and audit purposes.
    """
    model = AutonomousDecisionModel()
    
    decision = await model.create_decision(
        salon_id=salon_id,
        agent_name=data.agent_name,
        decision_type=data.decision_type,
        autonomy_level=data.autonomy_level,
        context=data.context.model_dump(),
        action_taken=data.action_taken,
        action_details=data.action_details,
        revenue_impact=data.revenue_impact.model_dump(),
        approval_required=data.approval_required,
    )
    
    # Log audit event
    audit = AuditLogModel()
    await audit.log_event(
        salon_id=salon_id,
        event_type=AuditEventType.DECISION_MADE,
        severity=AuditSeverity.INFO,
        actor=data.agent_name,
        action=f"Decision: {data.decision_type.value}",
        resource_type="decision",
        resource_id=decision["id"],
        details={
            "decision_type": data.decision_type.value,
            "autonomy_level": data.autonomy_level.value,
            "action_taken": data.action_taken,
        },
    )
    
    logger.info(
        "decision_created",
        salon_id=salon_id,
        decision_id=decision["id"],
        agent=data.agent_name,
        type=data.decision_type.value,
    )
    
    return decision


@router.get("/decisions", response_model=DecisionListResponse)
async def list_decisions(
    decision_type: Optional[DecisionType] = None,
    status_filter: Optional[DecisionStatus] = None,
    agent_name: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """List autonomous decisions with filters.
    
    Supports filtering by type, status, agent, and date range.
    """
    model = AutonomousDecisionModel()
    
    filters = []
    if decision_type:
        filters.append(("decision_type", "==", decision_type.value))
    if status_filter:
        filters.append(("outcome.status", "==", status_filter.value))
    if agent_name:
        filters.append(("agent_name", "==", agent_name))
    if date_from:
        filters.append(("created_at", ">=", date_from.isoformat()))
    if date_to:
        filters.append(("created_at", "<=", date_to.isoformat()))
    
    offset = (page - 1) * page_size
    
    decisions = await model.list(
        salon_id=salon_id,
        filters=filters,
        order_by="created_at",
        order_direction="DESCENDING",
        limit=page_size,
        offset=offset,
    )
    
    # Get total count (approximate)
    total_decisions = await model.list(
        salon_id=salon_id,
        filters=filters,
        limit=1000,
    )
    
    return DecisionListResponse(
        items=decisions,
        total=len(total_decisions),
        page=page,
        page_size=page_size,
        has_more=len(decisions) == page_size,
    )


@router.get("/decisions/{decision_id}", response_model=DecisionResponse)
async def get_decision(
    decision_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get a specific decision by ID."""
    model = AutonomousDecisionModel()
    decision = await model.get(decision_id)
    
    if not decision or decision.get("salon_id") != salon_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )
    
    return decision


@router.patch("/decisions/{decision_id}", response_model=DecisionResponse)
async def update_decision(
    decision_id: str,
    data: DecisionUpdate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Update decision outcome.
    
    Used to record the result of an autonomous action.
    """
    model = AutonomousDecisionModel()
    decision = await model.get(decision_id)
    
    if not decision or decision.get("salon_id") != salon_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )
    
    updated = await model.update_outcome(
        decision_id=decision_id,
        status=data.outcome_status,
        result=data.outcome_result,
        booking_id=data.booking_created_id,
    )
    
    logger.info(
        "decision_updated",
        salon_id=salon_id,
        decision_id=decision_id,
        status=data.outcome_status,
    )
    
    return updated


@router.get("/decisions/stats/daily", response_model=DecisionStatsResponse)
async def get_decision_stats(
    target_date: Optional[date] = None,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get decision statistics for a specific day."""
    model = AutonomousDecisionModel()
    stats = await model.get_daily_stats(salon_id, target_date)
    
    # Calculate success rate
    success_rate = await model.get_success_rate(salon_id, days=1)
    stats["success_rate"] = success_rate.get("rate", 0)
    
    return stats


# ==================== AGENT STATE ENDPOINTS ====================

@router.get("/agents", response_model=List[AgentStateResponse])
async def list_agents(
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """List all autonomous agents and their states."""
    model = AgentStateModel()
    return await model.get_all_agents_state(salon_id)


@router.get("/agents/{agent_name}", response_model=AgentStateResponse)
async def get_agent_state(
    agent_name: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get state for a specific agent."""
    model = AgentStateModel()
    state = await model.get_agent_state(salon_id, agent_name)
    
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_name} not found",
        )
    
    return state


@router.patch("/agents/{agent_name}", response_model=AgentStateResponse)
async def update_agent_state(
    agent_name: str,
    data: AgentStateUpdate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Update agent status (pause/resume)."""
    model = AgentStateModel()
    
    state = await model.get_agent_state(salon_id, agent_name)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_name} not found",
        )
    
    updated = await model.update_status(
        salon_id=salon_id,
        agent_name=agent_name,
        status=data.status,
        reason=data.status_reason,
    )
    
    # Log audit
    audit = AuditLogModel()
    await audit.log_event(
        salon_id=salon_id,
        event_type=AuditEventType.CONFIG_CHANGED,
        severity=AuditSeverity.INFO,
        actor=user.get("uid", "unknown"),
        action=f"Agent status changed to {data.status.value}",
        resource_type="agent",
        resource_id=agent_name,
        details={"new_status": data.status.value, "reason": data.status_reason},
    )
    
    logger.info(
        "agent_status_updated",
        salon_id=salon_id,
        agent=agent_name,
        status=data.status,
    )
    
    return updated


@router.put("/agents/{agent_name}/config", response_model=AgentStateResponse)
async def update_agent_config(
    agent_name: str,
    data: AgentConfigUpdate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Update agent configuration."""
    model = AgentStateModel()
    
    state = await model.get_agent_state(salon_id, agent_name)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_name} not found",
        )
    
    # Build config update
    config_update = {}
    if data.max_hourly_actions:
        config_update["rate_limits.hourly_actions.limit"] = data.max_hourly_actions
    if data.max_daily_actions:
        config_update["rate_limits.daily_actions.limit"] = data.max_daily_actions
    if data.auto_recovery is not None:
        config_update["circuit_breaker.auto_recovery"] = data.auto_recovery
    if data.cooldown_minutes:
        config_update["config.cooldown_minutes"] = data.cooldown_minutes
    if data.custom_config:
        for key, value in data.custom_config.items():
            config_update[f"config.{key}"] = value
    
    config_update["updated_at"] = datetime.utcnow().isoformat()
    
    state_id = f"state_{salon_id}_{agent_name}"
    updated = await model.update(state_id, config_update)
    
    logger.info(
        "agent_config_updated",
        salon_id=salon_id,
        agent=agent_name,
        changes=list(config_update.keys()),
    )
    
    return updated


@router.post("/agents/{agent_name}/reset-circuit-breaker", response_model=CircuitBreakerResponse)
async def reset_circuit_breaker(
    agent_name: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Manually reset agent circuit breaker."""
    model = AgentStateModel()
    
    success = await model.reset_circuit_breaker(salon_id, agent_name)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_name} not found",
        )
    
    # Log audit
    audit = AuditLogModel()
    await audit.log_event(
        salon_id=salon_id,
        event_type=AuditEventType.MANUAL_OVERRIDE,
        severity=AuditSeverity.WARNING,
        actor=user.get("uid", "unknown"),
        action="Circuit breaker manually reset",
        resource_type="agent",
        resource_id=agent_name,
        details={"action": "reset_circuit_breaker"},
    )
    
    return CircuitBreakerResponse(
        success=True,
        circuit_breaker_state=CircuitBreakerState.CLOSED,
        error_count=0,
        can_operate=True,
    )


# ==================== APPROVAL ENDPOINTS ====================

@router.get("/approvals", response_model=ApprovalListResponse)
async def list_approvals(
    status_filter: Optional[ApprovalStatus] = None,
    priority: Optional[ApprovalPriority] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """List approval requests."""
    model = ApprovalModel()
    
    filters = []
    if status_filter:
        filters.append(("status", "==", status_filter.value))
    if priority:
        filters.append(("priority", "==", priority.value))
    
    offset = (page - 1) * page_size
    
    approvals = await model.list(
        salon_id=salon_id,
        filters=filters,
        order_by="created_at",
        order_direction="ASCENDING",
        limit=page_size,
        offset=offset,
    )
    
    total_approvals = await model.list(
        salon_id=salon_id,
        filters=filters,
        limit=1000,
    )
    
    return ApprovalListResponse(
        items=approvals,
        total=len(total_approvals),
        page=page,
        page_size=page_size,
        has_more=len(approvals) == page_size,
    )


@router.get("/approvals/pending", response_model=List[ApprovalRequestResponse])
async def get_pending_approvals(
    limit: int = Query(20, ge=1, le=50),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get all pending approval requests."""
    model = ApprovalModel()
    return await model.get_pending_approvals(salon_id, limit)


@router.get("/approvals/{approval_id}", response_model=ApprovalRequestResponse)
async def get_approval(
    approval_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get a specific approval request."""
    model = ApprovalModel()
    approval = await model.get(approval_id)
    
    if not approval or approval.get("salon_id") != salon_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found",
        )
    
    return approval


@router.post("/approvals/{approval_id}/action", response_model=ApprovalRequestResponse)
async def process_approval_action(
    approval_id: str,
    data: ApprovalAction,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Approve or reject an approval request."""
    model = ApprovalModel()
    approval = await model.get(approval_id)
    
    if not approval or approval.get("salon_id") != salon_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found",
        )
    
    if approval.get("status") != ApprovalStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Approval already {approval.get('status')}",
        )
    
    user_id = user.get("uid", "unknown")
    
    if data.action == "approve":
        updated = await model.approve(approval_id, user_id, data.notes)
        event_type = AuditEventType.APPROVAL_GRANTED
    else:
        updated = await model.reject(approval_id, user_id, data.notes or "Rejected")
        event_type = AuditEventType.APPROVAL_REJECTED
    
    # Log audit
    audit = AuditLogModel()
    await audit.log_event(
        salon_id=salon_id,
        event_type=event_type,
        severity=AuditSeverity.INFO,
        actor=user_id,
        action=f"Approval {data.action}d",
        resource_type="approval",
        resource_id=approval_id,
        details={
            "action": data.action,
            "notes": data.notes,
            "decision_id": approval.get("decision_id"),
        },
    )
    
    logger.info(
        "approval_action",
        salon_id=salon_id,
        approval_id=approval_id,
        action=data.action,
        user=user_id,
    )
    
    return updated


@router.get("/approvals/stats/summary", response_model=ApprovalStatsResponse)
async def get_approval_stats(
    days: int = Query(7, ge=1, le=30),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get approval statistics."""
    model = ApprovalModel()
    return await model.get_approval_stats(salon_id, days)


# ==================== GAP ENDPOINTS ====================

@router.get("/gaps", response_model=GapListResponse)
async def list_gaps(
    status_filter: Optional[GapStatus] = None,
    target_date: Optional[date] = None,
    staff_id: Optional[str] = None,
    min_duration: int = Query(30, ge=15),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """List schedule gaps."""
    model = GapModel()
    
    filters = []
    if status_filter:
        filters.append(("status", "==", status_filter.value))
    if target_date:
        filters.append(("date", "==", target_date.isoformat()))
    if staff_id:
        filters.append(("staff_id", "==", staff_id))
    
    filters.append(("duration_minutes", ">=", min_duration))
    
    offset = (page - 1) * page_size
    
    gaps = await model.list(
        salon_id=salon_id,
        filters=filters,
        order_by="duration_minutes",
        order_direction="DESCENDING",
        limit=page_size,
        offset=offset,
    )
    
    total_gaps = await model.list(
        salon_id=salon_id,
        filters=filters,
        limit=1000,
    )
    
    return GapListResponse(
        items=gaps,
        total=len(total_gaps),
        page=page,
        page_size=page_size,
        has_more=len(gaps) == page_size,
    )


@router.get("/gaps/open", response_model=List[GapResponse])
async def get_open_gaps(
    target_date: Optional[date] = None,
    min_duration: int = Query(30, ge=15),
    limit: int = Query(50, ge=1, le=100),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get open gaps for gap-fill agent."""
    model = GapModel()
    return await model.get_open_gaps(salon_id, target_date, min_duration, limit)


@router.get("/gaps/high-priority", response_model=List[GapResponse])
async def get_high_priority_gaps(
    limit: int = Query(20, ge=1, le=50),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get high priority gaps for immediate action."""
    model = GapModel()
    return await model.get_high_priority_gaps(salon_id, limit)


@router.get("/gaps/{gap_id}", response_model=GapResponse)
async def get_gap(
    gap_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get a specific gap."""
    model = GapModel()
    gap = await model.get(gap_id)
    
    if not gap or gap.get("salon_id") != salon_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gap not found",
        )
    
    return gap


@router.get("/gaps/stats/daily", response_model=GapStatsResponse)
async def get_gap_stats(
    target_date: Optional[date] = None,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get gap statistics for a day."""
    model = GapModel()
    return await model.get_gap_stats(salon_id, target_date)


# ==================== OUTREACH ENDPOINTS ====================

@router.post("/outreach", response_model=OutreachResponse, status_code=status.HTTP_201_CREATED)
async def create_outreach(
    data: OutreachCreate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Create a new outreach attempt."""
    model = OutreachModel()
    
    # Check for recent outreach to same phone
    recent = await model.get_recent_by_phone(data.customer_phone, salon_id, hours=1)
    if recent:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Recent outreach already sent to this customer",
        )
    
    outreach = await model.create_outreach(
        salon_id=salon_id,
        customer_id=data.customer_id,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        outreach_type=data.outreach_type,
        channel=data.channel,
        message=data.message,
        trigger_id=data.trigger_id,
        trigger_type=data.trigger_type,
        offer_details=data.offer_details,
        expires_in_minutes=data.expires_in_minutes,
    )
    
    logger.info(
        "outreach_created",
        salon_id=salon_id,
        outreach_id=outreach["id"],
        customer=data.customer_id,
        type=data.outreach_type.value,
    )
    
    return outreach


@router.get("/outreach", response_model=OutreachListResponse)
async def list_outreach(
    status_filter: Optional[OutreachStatus] = None,
    outreach_type: Optional[OutreachType] = None,
    customer_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """List outreach attempts."""
    model = OutreachModel()
    
    filters = []
    if status_filter:
        filters.append(("status", "==", status_filter.value))
    if outreach_type:
        filters.append(("outreach_type", "==", outreach_type.value))
    if customer_id:
        filters.append(("customer_id", "==", customer_id))
    
    offset = (page - 1) * page_size
    
    outreach_list = await model.list(
        salon_id=salon_id,
        filters=filters,
        order_by="created_at",
        order_direction="DESCENDING",
        limit=page_size,
        offset=offset,
    )
    
    total_outreach = await model.list(
        salon_id=salon_id,
        filters=filters,
        limit=1000,
    )
    
    return OutreachListResponse(
        items=outreach_list,
        total=len(total_outreach),
        page=page,
        page_size=page_size,
        has_more=len(outreach_list) == page_size,
    )


@router.get("/outreach/{outreach_id}", response_model=OutreachResponse)
async def get_outreach(
    outreach_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get a specific outreach attempt."""
    model = OutreachModel()
    outreach = await model.get(outreach_id)
    
    if not outreach or outreach.get("salon_id") != salon_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outreach not found",
        )
    
    return outreach


@router.patch("/outreach/{outreach_id}", response_model=OutreachResponse)
async def update_outreach_status(
    outreach_id: str,
    data: OutreachUpdate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Update outreach status (for webhook callbacks)."""
    model = OutreachModel()
    outreach = await model.get(outreach_id)
    
    if not outreach or outreach.get("salon_id") != salon_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outreach not found",
        )
    
    if data.status == OutreachStatus.SENT and data.message_id:
        updated = await model.mark_sent(outreach_id, data.message_id)
    elif data.status == OutreachStatus.DELIVERED:
        updated = await model.mark_delivered(outreach_id)
    elif data.status == OutreachStatus.READ:
        updated = await model.mark_read(outreach_id)
    elif data.status == OutreachStatus.FAILED:
        updated = await model.mark_failed(outreach_id, data.error or "Unknown error")
    else:
        updated = await model.update(outreach_id, {
            "status": data.status.value,
            "updated_at": datetime.utcnow().isoformat(),
        })
    
    return updated


@router.get("/outreach/stats/summary", response_model=OutreachStatsResponse)
async def get_outreach_stats(
    days: int = Query(7, ge=1, le=30),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get outreach statistics."""
    model = OutreachModel()
    return await model.get_outreach_stats(salon_id, days)


# ==================== ANALYTICS ENDPOINTS ====================

@router.get("/analytics/dashboard")
async def get_autonomous_dashboard(
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get comprehensive autonomous agent dashboard data.
    
    Returns aggregated metrics for all autonomous operations.
    """
    decision_model = AutonomousDecisionModel()
    gap_model = GapModel()
    outreach_model = OutreachModel()
    approval_model = ApprovalModel()
    agent_model = AgentStateModel()
    
    # Get today's stats
    today = date.today()
    
    decision_stats = await decision_model.get_daily_stats(salon_id, today)
    gap_stats = await gap_model.get_gap_stats(salon_id, today)
    outreach_stats = await outreach_model.get_outreach_stats(salon_id, days=7)
    approval_stats = await approval_model.get_approval_stats(salon_id, days=7)
    success_rate = await decision_model.get_success_rate(salon_id, days=7)
    
    # Get agent states
    agents = await agent_model.get_all_agents_state(salon_id)
    
    # Calculate totals
    total_revenue_potential = decision_stats.get("revenue", {}).get("potential", 0)
    total_revenue_actual = decision_stats.get("revenue", {}).get("actual", 0)
    
    return {
        "date": today.isoformat(),
        "summary": {
            "decisions_today": decision_stats.get("total", 0),
            "success_rate_7d": success_rate.get("rate", 0),
            "revenue_today": total_revenue_actual,
            "revenue_potential": total_revenue_potential,
            "gaps_filled_today": gap_stats.get("by_status", {}).get("filled", 0),
            "gap_fill_rate": gap_stats.get("fill_rate", 0),
            "outreach_conversion": outreach_stats.get("conversion_rate", 0),
            "pending_approvals": approval_stats.get("by_status", {}).get("pending", 0),
        },
        "agents": {
            "total": len(agents),
            "active": sum(1 for a in agents if a.get("status") == "active"),
            "paused": sum(1 for a in agents if a.get("status") == "paused"),
            "error": sum(1 for a in agents if a.get("status") in ["error", "circuit_breaker"]),
        },
        "decisions": decision_stats,
        "gaps": gap_stats,
        "outreach": outreach_stats,
        "approvals": approval_stats,
    }


@router.get("/analytics/revenue-impact")
async def get_revenue_impact(
    days: int = Query(30, ge=1, le=90),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user),
):
    """Get revenue impact from autonomous agents.
    
    Shows revenue generated by autonomous actions over time.
    """
    model = AutonomousDecisionModel()
    
    from datetime import timedelta
    start_date = date.today() - timedelta(days=days)
    
    decisions = await model.list(
        salon_id=salon_id,
        filters=[("created_at", ">=", start_date.isoformat())],
        limit=1000,
    )
    
    # Aggregate by date
    daily_revenue = {}
    for decision in decisions:
        created = decision.get("created_at", "")[:10]  # Get date part
        if created not in daily_revenue:
            daily_revenue[created] = {
                "potential": 0,
                "actual": 0,
                "decisions": 0,
                "successful": 0,
            }
        
        revenue = decision.get("revenue_impact", {})
        daily_revenue[created]["potential"] += revenue.get("potential", 0)
        daily_revenue[created]["decisions"] += 1
        
        if decision.get("outcome", {}).get("status") == "success":
            daily_revenue[created]["actual"] += revenue.get("actual", 0)
            daily_revenue[created]["successful"] += 1
    
    # Convert to list sorted by date
    revenue_data = [
        {"date": k, **v}
        for k, v in sorted(daily_revenue.items())
    ]
    
    return {
        "period_days": days,
        "daily": revenue_data,
        "totals": {
            "potential": sum(d["potential"] for d in revenue_data),
            "actual": sum(d["actual"] for d in revenue_data),
            "decisions": sum(d["decisions"] for d in revenue_data),
            "successful": sum(d["successful"] for d in revenue_data),
        },
    }
