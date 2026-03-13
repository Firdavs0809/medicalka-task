from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import User


def cleanup_unverified_users() -> int:
    threshold = timezone.now() - timedelta(hours=24)
    qs = User.objects.filter(is_verified=False, created_at__lt=threshold)
    deleted, _ = qs.delete()
    return deleted


@shared_task(name="apps.users.tasks.cleanup_unverified_users_task")
def cleanup_unverified_users_task() -> int:
    return cleanup_unverified_users()
