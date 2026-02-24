"""Agent state schemas for autonomous agent API."""
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    CIRCUIT_BREAKER = "circuit_breaker"


class CircuitBreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerInfo(BaseModel):
    """Circuit breaker state information."""
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    error_count: int = Field(default=0, ge=0)
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None
    auto_recovery: bool = True


class RateLimitInfo(BaseModel):
    """Rate limit information."""
    limit: int
    current: int
    remaining: int
    reset_at: Optional[datetime] = None


class AgentCounters(BaseModel):
    """Agent action counters."""
    date: str
    actions_taken: int = 0
    actions_successful: int = 0
    actions_failed: int = 0
    revenue_generated: float = 0
    by_type: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class AgentHealth(BaseModel):
    """Agent health metrics."""
    last_heartbeat: Optional[datetime] = None
    consecutive_failures: int = 0
    average_response_time_ms: float = 0
    success_rate_24h: float = 1.0


class AgentStateResponse(BaseModel):
    """Schema for agent state response."""
    id: str
    salon_id: str
    agent_name: str
    status: AgentStatus
    last_execution: Optional[datetime] = None
    next_scheduled: Optional[datetime] = None
    circuit_breaker: CircuitBreakerInfo
    config: Dict[str, Any]
    counters: AgentCounters
    rate_limits: Dict[str, RateLimitInfo]
    health: AgentHealth
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentStateUpdate(BaseModel):
    """Schema for updating agent state."""
    status: Optional[AgentStatus] = None
    status_reason: Optional[str] = None


class AgentConfigUpdate(BaseModel):
    """Schema for updating agent configuration."""
    max_hourly_actions: Optional[int] = Field(None, ge=1, le=100)
    max_daily_actions: Optional[int] = Field(None, ge=1, le=500)
    auto_recovery: Optional[bool] = None
    cooldown_minutes: Optional[int] = Field(None, ge=1, le=60)
    custom_config: Optional[Dict[str, Any]] = None


class CircuitBreakerResponse(BaseModel):
    """Schema for circuit breaker operation response."""
    success: bool
    circuit_breaker_state: CircuitBreakerState
    error_count: int
    cooldown_until: Optional[datetime] = None
    can_operate: bool
    remaining_seconds: Optional[int] = None
