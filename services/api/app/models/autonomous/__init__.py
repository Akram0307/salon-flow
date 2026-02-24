"""Autonomous Agent Models Package.

Provides Firestore models for autonomous agent operations:
- Decision tracking and analytics
- Agent state management with circuit breakers
- Approval workflows for supervised actions
- Comprehensive audit logging
- Customer scoring and segmentation
- Schedule gap detection
- Outreach tracking and conversion
"""
from app.models.autonomous.decision import (
    AutonomousDecisionModel,
    DecisionType,
    AutonomyLevel,
    DecisionStatus,
)
from app.models.autonomous.agent_state import (
    AgentStateModel,
    AgentStatus,
    CircuitBreakerState,
)
from app.models.autonomous.approval import (
    ApprovalModel,
    ApprovalStatus,
    ApprovalPriority,
)
from app.models.autonomous.audit import (
    AuditLogModel,
    AuditEventType,
    AuditSeverity,
)
from app.models.autonomous.customer_score import (
    CustomerScoreModel,
    CustomerSegment,
    RiskLevel,
)
from app.models.autonomous.gap import (
    GapModel,
    GapStatus,
    GapPriority,
)
from app.models.autonomous.outreach import (
    OutreachModel,
    OutreachChannel,
    OutreachStatus,
    OutreachType,
)

__all__ = [
    # Decision models
    "AutonomousDecisionModel",
    "DecisionType",
    "AutonomyLevel",
    "DecisionStatus",
    # Agent state models
    "AgentStateModel",
    "AgentStatus",
    "CircuitBreakerState",
    # Approval models
    "ApprovalModel",
    "ApprovalStatus",
    "ApprovalPriority",
    # Audit models
    "AuditLogModel",
    "AuditEventType",
    "AuditSeverity",
    # Customer score models
    "CustomerScoreModel",
    "CustomerSegment",
    "RiskLevel",
    # Gap models
    "GapModel",
    "GapStatus",
    "GapPriority",
    # Outreach models
    "OutreachModel",
    "OutreachChannel",
    "OutreachStatus",
    "OutreachType",
]
