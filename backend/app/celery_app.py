from celery import Celery
from app.config import settings

celery_app = Celery(
    "worker", 
    broker=settings.redis_url,  # Redis broker URL
    backend=settings.redis_url  # store task results
)

# route all tasks under "app.tasks" to default queue
celery_app.conf.task_routes = {
    "app.tasks.*": {"queue": "default"},
}

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

from .jobs import celery_tasks
