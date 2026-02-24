"""Internal Task Handlers.

Endpoints for Cloud Tasks to execute:
- Autonomous agent tasks
- Notification sending
- Analytics aggregation
- Cleanup jobs
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional
import structlog

from fastapi import APIRouter, Request, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.autonomous import (
    AgentStateModel,
    AgentStatus,
    AutonomousDecisionModel,
    GapModel,
    OutreachModel,
    ApprovalModel,
)
from app.services.autonomous.gap_fill_service import GapFillService
from app.services.autonomous.outreach_service import OutreachService
from app.services.autonomous.approval_service import ApprovalService

logger = structlog.get_logger()
router = APIRouter(prefix="/internal", tags=["Internal"])


class AgentTaskPayload(BaseModel):
    """Payload for autonomous agent task."""
    salon_id: str
    agent_name: str
    action: str
    data: Dict[str, Any] = Field(default_factory=dict)


class NotificationTaskPayload(BaseModel):
    """Payload for notification task."""
    salon_id: str
    outreach_id: str
    channel: str


class AnalyticsTaskPayload(BaseModel):
    """Payload for analytics task."""
    salon_id: str
    task_type: str
    data: Dict[str, Any] = Field(default_factory=dict)


class CleanupTaskPayload(BaseModel):
    """Payload for cleanup task."""
    task_type: str
    data: Dict[str, Any] = Field(default_factory=dict)


@router.post("/tasks/execute")
async def execute_agent_task(
    payload: AgentTaskPayload,
    background_tasks: BackgroundTasks,
):
    """Execute autonomous agent task.
    
    Called by Cloud Tasks to run agent actions.
    """
    logger.info(
        "agent_task_received",
        salon_id=payload.salon_id,
        agent=payload.agent_name,
        action=payload.action,
    )
    
    agent_model = AgentStateModel()
    
    # Verify agent can operate
    state = await agent_model.get_agent_state(payload.salon_id, payload.agent_name)
    
    if state and state.get("status") == AgentStatus.PAUSED.value:
        logger.info(
            "agent_task_skipped_paused",
            salon_id=payload.salon_id,
            agent=payload.agent_name,
        )
        return {"status": "skipped", "reason": "agent_paused"}
    
    # Check circuit breaker
    if state:
        cb_check = await agent_model.check_circuit_breaker(payload.salon_id, payload.agent_name)
        if not cb_check.get("can_operate"):
            logger.warning(
                "agent_task_skipped_circuit_breaker",
                salon_id=payload.salon_id,
                agent=payload.agent_name,
            )
            return {"status": "skipped", "reason": "circuit_breaker_active"}
    
    
    # Route to appropriate handler
    result = {"status": "unknown_action"}
    
    try:
        if payload.agent_name == "gap_fill_agent":
            result = await _handle_gap_fill_task(payload)
        elif payload.agent_name == "no_show_prevention_agent":
            result = await _handle_no_show_task(payload)
        elif payload.agent_name == "waitlist_agent":
            result = await _handle_waitlist_task(payload)
        elif payload.agent_name == "retention_agent":
            result = await _handle_retention_task(payload)
        elif payload.agent_name == "cleanup_agent":
            result = await _handle_cleanup_task(payload)
        else:
            # Generic periodic check
            result = await _handle_periodic_check(payload)
        
        # Record successful execution
        await agent_model.record_action(
            salon_id=payload.salon_id,
            agent_name=payload.agent_name,
            action_type=payload.action,
            success=result.get("status") == "success",
        )
        
    except Exception as e:
        logger.error(
            "agent_task_failed",
            salon_id=payload.salon_id,
            agent=payload.agent_name,
            action=payload.action,
            error=str(e),
        )
        
        # Record failure
        await agent_model.record_failure(
            salon_id=payload.salon_id,
            agent_name=payload.agent_name,
            error=str(e),
        )
        
        result = {"status": "error", "error": str(e)}
    
    return result


async def _handle_gap_fill_task(payload: AgentTaskPayload) -> Dict[str, Any]:
    """Handle gap fill agent task."""
    service = GapFillService()
    
    if payload.action == "fill_gap":
        gap_id = payload.data.get("gap_id")
        if gap_id:
            return await service.execute_gap_fill(
                salon_id=payload.salon_id,
                gap_id=gap_id,
            )
    elif payload.action == "periodic_check":
        # Detect and process gaps
        gaps = await service.detect_gaps(payload.salon_id)
        
        results = []
        for gap in gaps[:5]:  # Process top 5 gaps
            result = await service.execute_gap_fill(
                salon_id=payload.salon_id,
                gap_id=gap["id"],
            )
            results.append(result)
        
        
        return {
            "status": "success",
            "gaps_found": len(gaps),
            "processed": len(results),
        }
    
    return {"status": "unknown_action"}


async def _handle_no_show_task(payload: AgentTaskPayload) -> Dict[str, Any]:
    """Handle no-show prevention agent task."""
    # TODO: Implement no-show prevention logic
    return {"status": "success", "action": "no_show_prevention"}


async def _handle_waitlist_task(payload: AgentTaskPayload) -> Dict[str, Any]:
    """Handle waitlist promotion agent task."""
    # TODO: Implement waitlist promotion logic
    return {"status": "success", "action": "waitlist_promotion"}


async def _handle_retention_task(payload: AgentTaskPayload) -> Dict[str, Any]:
    """Handle retention agent task."""
    # TODO: Implement retention check logic
    return {"status": "success", "action": "retention_check"}


async def _handle_cleanup_task(payload: AgentTaskPayload) -> Dict[str, Any]:
    """Handle cleanup agent task."""
    salon_id = payload.data.get("salon_id")
    
    if payload.action == "cleanup_expired":
        approval_service = ApprovalService()
        outreach_service = OutreachService()
        
        expired_approvals = 0
        expired_outreach = 0
        
        if salon_id:
            expired_approvals = await approval_service.cleanup_expired(salon_id)
            expired_outreach = await outreach_service.cleanup_expired(salon_id)
        
        
        return {
            "status": "success",
            "expired_approvals": expired_approvals,
            "expired_outreach": expired_outreach,
        }
    
    return {"status": "unknown_action"}


async def _handle_periodic_check(payload: AgentTaskPayload) -> Dict[str, Any]:
    """Handle generic periodic check."""
    return {"status": "success", "action": "periodic_check"}


@router.post("/tasks/send-notification")
async def send_notification_task(
    payload: NotificationTaskPayload,
    background_tasks: BackgroundTasks,
):
    """Send notification via Twilio.
    
    Called by Cloud Tasks to send WhatsApp/SMS.
    """
    logger.info(
        "notification_task_received",
        salon_id=payload.salon_id,
        outreach_id=payload.outreach_id,
        channel=payload.channel,
    )
    
    # TODO: Integrate with Twilio client
    # For now, mark as sent
    outreach_model = OutreachModel()
    outreach = await outreach_model.get(payload.outreach_id)
    
    if not outreach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outreach not found",
        )
    
    # Simulate sending
    await outreach_model.mark_sent(
        payload.outreach_id,
        f"simulated_{payload.channel}_{datetime.utcnow().timestamp()}"
    )
    
    return {"status": "sent", "channel": payload.channel}


@router.post("/tasks/analytics")
async def analytics_task(
    payload: AnalyticsTaskPayload,
    background_tasks: BackgroundTasks,
):
    """Run analytics aggregation.
    
    Called by Cloud Tasks for scheduled analytics.
    """
    logger.info(
        "analytics_task_received",
        salon_id=payload.salon_id,
        task_type=payload.task_type,
    )
    
    # TODO: Implement analytics aggregation
    return {"status": "success", "task_type": payload.task_type}


@router.post("/tasks/cleanup")
async def cleanup_task(
    payload: CleanupTaskPayload,
    background_tasks: BackgroundTasks,
):
    """Run cleanup task.
    
    Called by Cloud Tasks for scheduled cleanup.
    """
    logger.info(
        "cleanup_task_received",
        task_type=payload.task_type,
    )
    
    salon_id = payload.data.get("salon_id")
    
    if payload.task_type == "expired_approvals":
        service = ApprovalService()
        count = await service.cleanup_expired(salon_id) if salon_id else 0
        return {"status": "success", "expired": count}
    
    elif payload.task_type == "expired_outreach":
        service = OutreachService()
        count = await service.cleanup_expired(salon_id) if salon_id else 0
        return {"status": "success", "expired": count}
    
    
    return {"status": "success", "task_type": payload.task_type}
