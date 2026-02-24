"""Agent State Firestore Model.

Manages runtime state for autonomous agents per salon.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

from google.cloud.firestore_v1.base_query import FieldFilter
import structlog

from app.models.base import FirestoreBase

logger = structlog.get_logger()


class AgentStatus(str, Enum):
    """Status of an autonomous agent."""
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    CIRCUIT_BREAKER = "circuit_breaker"


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery


class AgentStateModel(FirestoreBase):
    """Model for agent state operations.
    
    Tracks runtime state, circuit breaker, counters, and rate limits
    for each autonomous agent per salon.
    """
    
    collection_name = "agent_state"
    
    async def get_agent_state(
        self,
        salon_id: str,
        agent_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Get state for a specific agent.
        
        Args:
            salon_id: Salon ID
            agent_name: Name of the agent
            
        Returns:
            Agent state if found
        """
        state_id = f"state_{salon_id}_{agent_name}"
        return await self.get(state_id)
    
    async def get_all_agents_state(
        self,
        salon_id: str,
    ) -> List[Dict[str, Any]]:
        """Get state for all agents in a salon.
        
        Args:
            salon_id: Salon ID
            
        Returns:
            List of agent states
        """
        return await self.list(
            salon_id=salon_id,
            limit=50,
        )
    
    async def initialize_agent_state(
        self,
        salon_id: str,
        agent_name: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Initialize state for a new agent.
        
        Args:
            salon_id: Salon ID
            agent_name: Name of the agent
            config: Initial configuration
            
        Returns:
            Created agent state
        """
        state_id = f"state_{salon_id}_{agent_name}"
        now = datetime.utcnow()
        today = date.today().isoformat()
        
        state_data = {
            "id": state_id,
            "salon_id": salon_id,
            "agent_name": agent_name,
            "status": AgentStatus.ACTIVE.value,
            "last_execution": None,
            "next_scheduled": None,
            "circuit_breaker": {
                "state": CircuitBreakerState.CLOSED.value,
                "error_count": 0,
                "last_error": None,
                "last_error_time": None,
                "cooldown_until": None,
                "auto_recovery": True,
            },
            "config": config,
            "counters": {
                "date": today,
                "actions_taken": 0,
                "actions_successful": 0,
                "actions_failed": 0,
                "revenue_generated": 0,
                "by_type": {},
            },
            "rate_limits": {
                "hourly_actions": {
                    "limit": config.get("max_hourly_actions", 10),
                    "current": 0,
                    "reset_at": None,
                },
                "daily_actions": {
                    "limit": config.get("max_daily_actions", 50),
                    "current": 0,
                    "reset_at": None,
                },
            },
            "health": {
                "last_heartbeat": now.isoformat(),
                "consecutive_failures": 0,
                "average_response_time_ms": 0,
                "success_rate_24h": 1.0,
            },
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        
        return await self.create(state_data, document_id=state_id)
    
    async def update_status(
        self,
        salon_id: str,
        agent_name: str,
        status: AgentStatus,
        reason: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update agent status.
        
        Args:
            salon_id: Salon ID
            agent_name: Name of the agent
            status: New status
            reason: Optional reason for status change
            
        Returns:
            Updated state
        """
        state_id = f"state_{salon_id}_{agent_name}"
        update_data = {
            "status": status.value,
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        if reason:
            update_data["status_reason"] = reason
        
        return await self.update(state_id, update_data)
    
    async def record_action(
        self,
        salon_id: str,
        agent_name: str,
        action_type: str,
        success: bool,
        revenue: float = 0,
        response_time_ms: int = 0,
    ) -> bool:
        """Record an agent action.
        
        Updates counters, rate limits, and health metrics.
        
        Args:
            salon_id: Salon ID
            agent_name: Name of the agent
            action_type: Type of action taken
            success: Whether action succeeded
            revenue: Revenue generated (if successful)
            response_time_ms: Response time in milliseconds
            
        Returns:
            True if recorded successfully
        """
        state_id = f"state_{salon_id}_{agent_name}"
        state = await self.get(state_id)
        
        if not state:
            logger.error("agent_state_not_found", salon_id=salon_id, agent=agent_name)
            return False
        
        now = datetime.utcnow()
        today = date.today().isoformat()
        
        # Reset counters if new day
        counters = state.get("counters", {})
        if counters.get("date") != today:
            counters = {
                "date": today,
                "actions_taken": 0,
                "actions_successful": 0,
                "actions_failed": 0,
                "revenue_generated": 0,
                "by_type": {},
            }
        
        # Update counters
        counters["actions_taken"] += 1
        if success:
            counters["actions_successful"] += 1
            counters["revenue_generated"] += revenue
        else:
            counters["actions_failed"] += 1
        
        # Update by_type
        type_counts = counters.get("by_type", {})
        if action_type not in type_counts:
            type_counts[action_type] = {"count": 0, "revenue": 0}
        type_counts[action_type]["count"] += 1
        if success:
            type_counts[action_type]["revenue"] += revenue
        counters["by_type"] = type_counts
        
        # Update rate limits
        rate_limits = state.get("rate_limits", {})
        hourly = rate_limits.get("hourly_actions", {})
        hourly["current"] = hourly.get("current", 0) + 1
        
        daily = rate_limits.get("daily_actions", {})
        daily["current"] = daily.get("current", 0) + 1
        
        # Update health
        health = state.get("health", {})
        if success:
            health["consecutive_failures"] = 0
        else:
            health["consecutive_failures"] = health.get("consecutive_failures", 0) + 1
        
        # Update average response time (rolling average)
        current_avg = health.get("average_response_time_ms", 0)
        total_actions = counters["actions_taken"]
        health["average_response_time_ms"] = (
            (current_avg * (total_actions - 1) + response_time_ms) / total_actions
        )
        health["last_heartbeat"] = now.isoformat()
        
        # Calculate success rate
        if counters["actions_taken"] > 0:
            health["success_rate_24h"] = (
                counters["actions_successful"] / counters["actions_taken"]
            )
        
        # Update state
        update_data = {
            "counters": counters,
            "rate_limits": rate_limits,
            "health": health,
            "last_execution": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        
        await self.update(state_id, update_data)
        return True
    
    async def check_rate_limit(
        self,
        salon_id: str,
        agent_name: str,
        limit_type: str = "hourly",
    ) -> Dict[str, Any]:
        """Check if agent is within rate limits.
        
        Args:
            salon_id: Salon ID
            agent_name: Name of the agent
            limit_type: "hourly" or "daily"
            
        Returns:
            Dict with allowed, current, limit, reset_at
        """
        state_id = f"state_{salon_id}_{agent_name}"
        state = await self.get(state_id)
        
        if not state:
            return {"allowed": False, "reason": "state_not_found"}
        
        rate_limits = state.get("rate_limits", {})
        key = f"{limit_type}_actions"
        limit_data = rate_limits.get(key, {})
        
        current = limit_data.get("current", 0)
        limit = limit_data.get("limit", 50)
        reset_at = limit_data.get("reset_at")
        
        # Check if we need to reset
        now = datetime.utcnow()
        if reset_at:
            reset_time = datetime.fromisoformat(reset_at)
            if now >= reset_time:
                # Reset the counter
                current = 0
                if limit_type == "hourly":
                    new_reset = now + timedelta(hours=1)
                else:
                    new_reset = now + timedelta(days=1)
                reset_at = new_reset.isoformat()
                
                # Update in background
                await self.update(state_id, {
                    f"rate_limits.{key}.current": 0,
                    f"rate_limits.{key}.reset_at": reset_at,
                })
        
        return {
            "allowed": current < limit,
            "current": current,
            "limit": limit,
            "remaining": max(0, limit - current),
            "reset_at": reset_at,
        }
    
    async def trigger_circuit_breaker(
        self,
        salon_id: str,
        agent_name: str,
        error: str,
        cooldown_minutes: int = 5,
    ) -> Dict[str, Any]:
        """Trigger circuit breaker for an agent.
        
        Args:
            salon_id: Salon ID
            agent_name: Name of the agent
            error: Error message
            cooldown_minutes: Minutes to wait before retry
            
        Returns:
            Updated circuit breaker state
        """
        state_id = f"state_{salon_id}_{agent_name}"
        state = await self.get(state_id)
        
        if not state:
            return {"success": False, "reason": "state_not_found"}
        
        now = datetime.utcnow()
        cooldown_until = now + timedelta(minutes=cooldown_minutes)
        
        cb_state = state.get("circuit_breaker", {})
        error_count = cb_state.get("error_count", 0) + 1
        
        update_data = {
            "status": AgentStatus.CIRCUIT_BREAKER.value,
            "circuit_breaker": {
                "state": CircuitBreakerState.OPEN.value,
                "error_count": error_count,
                "last_error": error,
                "last_error_time": now.isoformat(),
                "cooldown_until": cooldown_until.isoformat(),
                "auto_recovery": cb_state.get("auto_recovery", True),
            },
            "updated_at": now.isoformat(),
        }
        
        await self.update(state_id, update_data)
        
        logger.warning(
            "circuit_breaker_triggered",
            salon_id=salon_id,
            agent=agent_name,
            error_count=error_count,
            cooldown_until=cooldown_until.isoformat(),
        )
        
        return {
            "success": True,
            "circuit_breaker_state": CircuitBreakerState.OPEN.value,
            "error_count": error_count,
            "cooldown_until": cooldown_until.isoformat(),
        }
    
    async def check_circuit_breaker(
        self,
        salon_id: str,
        agent_name: str,
    ) -> Dict[str, Any]:
        """Check circuit breaker status and attempt recovery.
        
        Args:
            salon_id: Salon ID
            agent_name: Name of the agent
            
        Returns:
            Circuit breaker status and whether agent can operate
        """
        state_id = f"state_{salon_id}_{agent_name}"
        state = await self.get(state_id)
        
        if not state:
            return {"can_operate": False, "reason": "state_not_found"}
        
        cb = state.get("circuit_breaker", {})
        cb_state = cb.get("state", CircuitBreakerState.CLOSED.value)
        
        if cb_state == CircuitBreakerState.CLOSED.value:
            return {"can_operate": True, "state": cb_state}
        
        now = datetime.utcnow()
        cooldown_until = cb.get("cooldown_until")
        
        if cooldown_until:
            cooldown_time = datetime.fromisoformat(cooldown_until)
            if now < cooldown_time:
                return {
                    "can_operate": False,
                    "state": cb_state,
                    "remaining_seconds": int((cooldown_time - now).total_seconds()),
                }
        
        # Cooldown expired - move to half-open
        if cb.get("auto_recovery", True):
            await self.update(state_id, {
                "circuit_breaker.state": CircuitBreakerState.HALF_OPEN.value,
                "updated_at": now.isoformat(),
            })
            
            return {
                "can_operate": True,
                "state": CircuitBreakerState.HALF_OPEN.value,
                "testing": True,
            }
        
        
        return {
            "can_operate": False,
            "state": cb_state,
            "auto_recovery": False,
        }
    
    async def reset_circuit_breaker(
        self,
        salon_id: str,
        agent_name: str,
    ) -> bool:
        """Manually reset circuit breaker.
        
        Args:
            salon_id: Salon ID
            agent_name: Name of the agent
            
        Returns:
            True if reset successfully
        """
        state_id = f"state_{salon_id}_{agent_name}"
        
        update_data = {
            "status": AgentStatus.ACTIVE.value,
            "circuit_breaker": {
                "state": CircuitBreakerState.CLOSED.value,
                "error_count": 0,
                "last_error": None,
                "last_error_time": None,
                "cooldown_until": None,
                "auto_recovery": True,
            },
            "health.consecutive_failures": 0,
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        result = await self.update(state_id, update_data)
        return result is not None
