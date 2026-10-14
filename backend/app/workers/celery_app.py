from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "crypto_trader",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
)

celery_app.conf.beat_schedule = {
    "hourly-candles": {
        "task": "app.workers.tasks.sync_all_candles",
        "schedule": crontab(minute=1),
    }
}
