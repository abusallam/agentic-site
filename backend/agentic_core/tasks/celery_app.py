"""
Celery application configuration for agentic task processing
"""
from celery import Celery
from ..config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery application
celery_app = Celery(
    "agentic_core",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "agentic_core.tasks.agent_tasks",
        "agentic_core.tasks.workflow_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer=settings.celery_task_serializer,
    result_serializer=settings.celery_result_serializer,
    accept_content=settings.celery_accept_content,
    timezone=settings.celery_timezone,
    enable_utc=settings.celery_enable_utc,
    
    # Task routing
    task_routes={
        "agentic_core.tasks.agent_tasks.*": {"queue": "agent_queue"},
        "agentic_core.tasks.workflow_tasks.*": {"queue": "workflow_queue"},
    },
    
    # Task execution settings
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Error handling
    task_annotations={
        "*": {
            "rate_limit": "100/m",
            "time_limit": 300,  # 5 minutes
            "soft_time_limit": 240,  # 4 minutes
        }
    }
)

# Task failure handler
@celery_app.task(bind=True)
def task_failure_handler(self, task_id, error, traceback):
    """Handle task failures"""
    logger.error(f"Task {task_id} failed: {error}")
    logger.error(f"Traceback: {traceback}")
    
    # Could implement notification system here
    # send_failure_notification(task_id, error)

# Health check task
@celery_app.task
def health_check():
    """Health check task for monitoring"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    celery_app.start()