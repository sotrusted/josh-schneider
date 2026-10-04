from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import PageVisit


class Command(BaseCommand):
    help = 'Delete PageVisit records older than DAYS days (default: 90)'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=90)

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=options['days'])
        deleted, _ = PageVisit.objects.filter(visited_at__lt=cutoff).delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} visits older than {options["days"]} days'))
