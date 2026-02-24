"""Background Tasks Package.

Provides Cloud Tasks integration for async processing:
- Autonomous agent scheduling
- Outreach sending
- Cleanup jobs
- Analytics aggregation
"""
from app.tasks.cloud_tasks import CloudTasksClient
from app.tasks.scheduler import AgentScheduler

__all__ = [
    "CloudTasksClient",
    "AgentScheduler",
]
