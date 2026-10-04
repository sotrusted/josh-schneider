from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db.models import F
from django.utils import timezone
from core.models import PageVisit, SiteSettings


class Command(BaseCommand):
    help = 'Delete PageVisit records older than DAYS days (default: 90), preserving all-time counters'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=90)

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=options['days'])
        old = PageVisit.objects.filter(visited_at__lt=cutoff)
        humans = old.filter(is_bot=False).count()
        bots = old.filter(is_bot=True).count()

        # Accumulate into the lifetime counters before deleting
        SiteSettings.objects.filter(pk=1).update(
            lifetime_human_visits=F('lifetime_human_visits') + humans,
            lifetime_bot_visits=F('lifetime_bot_visits') + bots,
        )

        deleted, _ = old.delete()
        self.stdout.write(self.style.SUCCESS(
            f'Deleted {deleted} visits older than {options["days"]} days '
            f'(+{humans} human, +{bots} bot added to lifetime counters)'
        ))
