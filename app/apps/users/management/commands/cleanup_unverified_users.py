## preview first
# python manage.py cleanup_unverified_users --dry-run

## delete with default 48h threshold
# python manage.py cleanup_unverified_users

## custom threshold
# python manage.py cleanup_unverified_users --hours 24


from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User


class Command(BaseCommand):
    help = "Delete unverified users whose verification token has expired"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=48,
            help="Delete unverified users older than this many hours (default: 48)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        dry_run = options["dry_run"]
        threshold = timezone.now() - timedelta(hours=hours)

        qs = User.objects.filter(
            is_verified=False,
            email_verification_token__expires_at__lte=threshold,
        )

        count = qs.count()

        if dry_run:
            self.stdout.write(f"[DRY RUN] Would delete {count} unverified users older than {hours}h")
            return

        qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} unverified users older than {hours}h"))
