"""Agent Scheduler for Autonomous Operations.

Manages scheduling and execution of autonomous agent tasks.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import structlog

from app.tasks.cloud_tasks import CloudTasksClient
from app.models.autonomous import AgentStateModel, AgentStatus

logger = structlog.get_logger()


class AgentScheduler:
    """Schedules and manages autonomous agent tasks.
    
    Handles:
    - Periodic agent execution
    - Task prioritization
    - Failure recovery
    - Rate limit compliance
    """
    
    # Default intervals for agents (in minutes)
    AGENT_INTERVALS = {
        "gap_fill_agent": 5,
        "no_show_prevention_agent": 10,
        "waitlist_agent": 5,
        "retention_agent": 60,
        "upsell_agent": 30,
        "analytics_agent": 60,
        "cleanup_agent": 60,
    }
    
    def __init__(self):
        self.tasks_client = CloudTasksClient()
        self.agent_model = AgentStateModel()
    
    async def schedule_agent_run(
        self,
        salon_id: str,
        agent_name: str,
        action: str,
        data: Optional[Dict[str, Any]] = None,
        delay_minutes: Optional[int] = None,
    ) -> str:
        """Schedule an agent task.
        
        Args:
            salon_id: Salon ID
            agent_name: Agent to run
            action: Action to perform
            data: Action data
            delay_minutes: Optional delay
            
        Returns:
            Task name
        """
        # Check agent state
        state = await self.agent_model.get_agent_state(salon_id, agent_name)
        
        if state:
            # Skip if agent is paused
            if state.get("status") == AgentStatus.PAUSED.value:
                logger.info(
                    "agent_skipped_paused",
                    salon_id=salon_id,
                    agent=agent_name,
                )
                return ""
            
            # Check circuit breaker
            cb_check = await self.agent_model.check_circuit_breaker(salon_id, agent_name)
            if not cb_check.get("can_operate"):
                logger.warning(
                    "agent_skipped_circuit_breaker",
                    salon_id=salon_id,
                    agent=agent_name,
                    circuit_breaker=cb_check,
                )
                return ""
        
        delay_seconds = delay_minutes * 60 if delay_minutes else None
        
        return await self.tasks_client.create_autonomous_task(
            salon_id=salon_id,
            agent_name=agent_name,
            action=action,
            data=data or {},
            delay_seconds=delay_seconds,
        )
    
    async def schedule_periodic_agents(
        self,
        salon_id: str,
    ) -> List[str]:
        """Schedule all periodic agent runs for a salon.
        
        Args:
            salon_id: Salon ID
            
        Returns:
            List of scheduled task names
        """
        scheduled = []
        
        for agent_name, interval in self.AGENT_INTERVALS.items():
            # Check if agent should run now
            should_run = await self._should_run_agent(salon_id, agent_name, interval)
            
            if should_run:
                task_name = await self.schedule_agent_run(
                    salon_id=salon_id,
                    agent_name=agent_name,
                    action="periodic_check",
                )
                if task_name:
                    scheduled.append(task_name)
        
        
        return scheduled
    
    async def _should_run_agent(
        self,
        salon_id: str,
        agent_name: str,
        interval_minutes: int,
    ) -> bool:
        """Check if agent should run based on last execution.
        
        Args:
            salon_id: Salon ID
            agent_name: Agent name
            interval_minutes: Expected interval
            
        Returns:
            True if agent should run
        """
        state = await self.agent_model.get_agent_state(salon_id, agent_name)
        
        if not state:
            return True  # No state, should run
        
        last_execution = state.get("last_execution")
        if not last_execution:
            return True
        
        # Check if enough time has passed
        last_dt = datetime.fromisoformat(last_execution.replace("Z", "+00:00"))
        next_run = last_dt + timedelta(minutes=interval_minutes)
        
        return datetime.utcnow() >= next_run.replace(tzinfo=None)
    
    async def schedule_gap_fill(
        self,
        salon_id: str,
        gap_id: str,
        priority: str = "normal",
    ) -> str:
        """Schedule gap fill task.
        
        Args:
            salon_id: Salon ID
            gap_id: Gap document ID
            priority: Task priority
            
        Returns:
            Task name
        """
        delay = 0 if priority == "urgent" else None
        
        return await self.schedule_agent_run(
            salon_id=salon_id,
            agent_name="gap_fill_agent",
            action="fill_gap",
            data={"gap_id": gap_id},
            delay_minutes=delay,
        )
    
    async def schedule_no_show_prevention(
        self,
        salon_id: str,
        booking_id: str,
        hours_before: int = 2,
    ) -> str:
        """Schedule no-show prevention outreach.
        
        Args:
            salon_id: Salon ID
            booking_id: Booking document ID
            hours_before: Hours before appointment
            
        Returns:
            Task name
        """
        return await self.schedule_agent_run(
            salon_id=salon_id,
            agent_name="no_show_prevention_agent",
            action="prevent_no_show",
            data={"booking_id": booking_id, "hours_before": hours_before},
        )
    
    async def schedule_waitlist_promotion(
        self,
        salon_id: str,
        waitlist_id: str,
    ) -> str:
        """Schedule waitlist promotion.
        
        Args:
            salon_id: Salon ID
            waitlist_id: Waitlist entry ID
            
        Returns:
            Task name
        """
        return await self.schedule_agent_run(
            salon_id=salon_id,
            agent_name="waitlist_agent",
            action="promote_waitlist",
            data={"waitlist_id": waitlist_id},
        )
    
    async def schedule_retention_check(
        self,
        salon_id: str,
        customer_id: Optional[str] = None,
    ) -> str:
        """Schedule retention agent check.
        
        Args:
            salon_id: Salon ID
            customer_id: Optional specific customer
            
        Returns:
            Task name
        """
        return await self.schedule_agent_run(
            salon_id=salon_id,
            agent_name="retention_agent",
            action="check_retention",
            data={"customer_id": customer_id} if customer_id else {},
        )
    
    async def schedule_cleanup(
        self,
        task_type: str,
        salon_id: Optional[str] = None,
    ) -> str:
        """Schedule cleanup task.
        
        Args:
            task_type: Type of cleanup (expired_approvals, expired_outreach, etc.)
            salon_id: Optional salon ID
            
        Returns:
            Task name
        """
        return await self.tasks_client.create_cleanup_task(
            task_type=task_type,
            data={"salon_id": salon_id} if salon_id else {},
        )
