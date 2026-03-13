import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "cleanup-unverified-users-hourly": {
        "task": "apps.users.tasks.cleanup_unverified_users_task",
        "schedule": crontab(minute=0, hour="*"),
    }
}
