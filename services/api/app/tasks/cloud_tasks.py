"""Google Cloud Tasks Client.

Manages async task execution via Cloud Tasks queues.
"""
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import structlog

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

from app.core.config import settings

logger = structlog.get_logger()


class CloudTasksClient:
    """Client for Google Cloud Tasks.
    
    Provides:
    - Task creation with scheduling
    - Retry configuration
    - Dead-letter handling
    """
    
    # Queue names
    QUEUE_AUTONOMOUS = "autonomous-agents"
    QUEUE_NOTIFICATIONS = "notifications"
    QUEUE_ANALYTICS = "analytics"
    QUEUE_CLEANUP = "cleanup"
    
    def __init__(self):
        self.client = tasks_v2.CloudTasksClient()
        self.project = settings.GCP_PROJECT_ID
        self.location = settings.GCP_REGION
        self.base_url = settings.API_BASE_URL
    
    def _get_queue_path(self, queue_name: str) -> str:
        """Get full queue path."""
        return self.client.queue_path(self.project, self.location, queue_name)
    
    async def create_task(
        self,
        queue_name: str,
        task_name: str,
        handler_path: str,
        payload: Dict[str, Any],
        schedule_time: Optional[datetime] = None,
        delay_seconds: Optional[int] = None,
    ) -> str:
        """Create a Cloud Task.
        
        Args:
            queue_name: Target queue
            task_name: Unique task identifier
            handler_path: API endpoint path
            payload: Task payload
            schedule_time: When to execute (optional)
            delay_seconds: Delay from now (optional)
            
        Returns:
            Task name
        """
        queue_path = self._get_queue_path(queue_name)
        
        # Calculate schedule time
        if delay_seconds:
            schedule_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
        
        # Build task
        task = {
            "name": f"{queue_path}/tasks/{task_name}",
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"{self.base_url}{handler_path}",
                "headers": {
                    "Content-Type": "application/json",
                    "X-CloudTasks-Queue": queue_name,
                },
                "body": json.dumps(payload).encode(),
            },
        }
        
        # Add schedule time if specified
        if schedule_time:
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(schedule_time)
            task["schedule_time"] = timestamp
        
        # Create task
        response = self.client.create_task(
            request={"parent": queue_path, "task": task}
        )
        
        logger.debug(
            "cloud_task_created",
            task_name=task_name,
            queue=queue_name,
            handler=handler_path,
        )
        
        return response.name
    
    async def create_autonomous_task(
        self,
        salon_id: str,
        agent_name: str,
        action: str,
        data: Dict[str, Any],
        delay_seconds: Optional[int] = None,
    ) -> str:
        """Create task for autonomous agent.
        
        Args:
            salon_id: Salon ID
            agent_name: Agent to execute
            action: Action to perform
            data: Action data
            delay_seconds: Optional delay
            
        Returns:
            Task name
        """
        task_name = f"{agent_name}-{salon_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return await self.create_task(
            queue_name=self.QUEUE_AUTONOMOUS,
            task_name=task_name,
            handler_path="/internal/tasks/execute",
            payload={
                "salon_id": salon_id,
                "agent_name": agent_name,
                "action": action,
                "data": data,
            },
            delay_seconds=delay_seconds,
        )
    
    async def create_notification_task(
        self,
        salon_id: str,
        outreach_id: str,
        channel: str,
        delay_seconds: Optional[int] = None,
    ) -> str:
        """Create task for sending notification.
        
        Args:
            salon_id: Salon ID
            outreach_id: Outreach document ID
            channel: Communication channel
            delay_seconds: Optional delay
            
        Returns:
            Task name
        """
        task_name = f"notify-{outreach_id}"
        
        return await self.create_task(
            queue_name=self.QUEUE_NOTIFICATIONS,
            task_name=task_name,
            handler_path="/internal/tasks/send-notification",
            payload={
                "salon_id": salon_id,
                "outreach_id": outreach_id,
                "channel": channel,
            },
            delay_seconds=delay_seconds,
        )
    
    async def create_analytics_task(
        self,
        salon_id: str,
        task_type: str,
        data: Dict[str, Any],
        schedule_time: Optional[datetime] = None,
    ) -> str:
        """Create task for analytics aggregation.
        
        Args:
            salon_id: Salon ID
            task_type: Type of analytics task
            data: Task data
            schedule_time: When to execute
            
        Returns:
            Task name
        """
        task_name = f"analytics-{task_type}-{salon_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return await self.create_task(
            queue_name=self.QUEUE_ANALYTICS,
            task_name=task_name,
            handler_path="/internal/tasks/analytics",
            payload={
                "salon_id": salon_id,
                "task_type": task_type,
                "data": data,
            },
            schedule_time=schedule_time,
        )
    
    async def create_cleanup_task(
        self,
        task_type: str,
        data: Dict[str, Any],
        schedule_time: Optional[datetime] = None,
    ) -> str:
        """Create cleanup task.
        
        Args:
            task_type: Type of cleanup
            data: Task data
            schedule_time: When to execute
            
        Returns:
            Task name
        """
        task_name = f"cleanup-{task_type}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return await self.create_task(
            queue_name=self.QUEUE_CLEANUP,
            task_name=task_name,
            handler_path="/internal/tasks/cleanup",
            payload={
                "task_type": task_type,
                "data": data,
            },
            schedule_time=schedule_time,
        )
