"""Autonomous Agent Schemas Package.

Pydantic models for API request/response validation.
"""
from app.schemas.autonomous.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionUpdate,
    DecisionListResponse,
    DecisionStatsResponse,
)
from app.schemas.autonomous.agent_state import (
    AgentStateResponse,
    AgentStateUpdate,
    AgentConfigUpdate,
    CircuitBreakerResponse,
)
from app.schemas.autonomous.approval import (
    ApprovalRequestCreate,
    ApprovalRequestResponse,
    ApprovalAction,
    ApprovalListResponse,
    ApprovalStatsResponse,
)
from app.schemas.autonomous.gap import (
    GapCreate,
    GapResponse,
    GapListResponse,
    GapStatsResponse,
)
from app.schemas.autonomous.outreach import (
    OutreachCreate,
    OutreachResponse,
    OutreachUpdate,
    OutreachListResponse,
    OutreachStatsResponse,
)

__all__ = [
    # Decision schemas
    "DecisionCreate",
    "DecisionResponse",
    "DecisionUpdate",
    "DecisionListResponse",
    "DecisionStatsResponse",
    # Agent state schemas
    "AgentStateResponse",
    "AgentStateUpdate",
    "AgentConfigUpdate",
    "CircuitBreakerResponse",
    # Approval schemas
    "ApprovalRequestCreate",
    "ApprovalRequestResponse",
    "ApprovalAction",
    "ApprovalListResponse",
    "ApprovalStatsResponse",
    # Gap schemas
    "GapCreate",
    "GapResponse",
    "GapListResponse",
    "GapStatsResponse",
    # Outreach schemas
    "OutreachCreate",
    "OutreachResponse",
    "OutreachUpdate",
    "OutreachListResponse",
    "OutreachStatsResponse",
]
