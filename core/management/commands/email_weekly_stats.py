from datetime import timedelta
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone
from core.models import PageVisit

RECIPIENT = 'josh@joshuashneider.com'


class Command(BaseCommand):
    help = 'Send weekly visitor stats digest to Josh'

    def handle(self, *args, **options):
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        prev_week_ago = now - timedelta(days=14)

        humans = PageVisit.objects.filter(is_bot=False)
        this_week = humans.filter(visited_at__gte=week_ago).count()
        last_week = humans.filter(visited_at__gte=prev_week_ago, visited_at__lt=week_ago).count()
        bots = PageVisit.objects.filter(is_bot=True, visited_at__gte=week_ago).count()

        top_pages = (
            humans.filter(visited_at__gte=week_ago)
            .values('path').annotate(n=Count('id')).order_by('-n')[:8]
        )
        top_refs = (
            humans.filter(visited_at__gte=week_ago)
            .exclude(referrer='')
            .values('referrer').annotate(n=Count('id')).order_by('-n')[:5]
        )

        delta = this_week - last_week
        trend = f'+{delta}' if delta >= 0 else str(delta)

        lines = [
            f'Weekly visitor report for joshuashneider.com',
            f'{now.strftime("%B %d, %Y")}',
            '',
            f'Human visits this week:  {this_week}  ({trend} vs prior week)',
            f'Human visits last week:  {last_week}',
            f'Bot requests filtered:   {bots}',
            '',
            '── Top pages ──────────────────────────',
        ]
        for row in top_pages:
            lines.append(f"  {row['n']:>4}  {row['path']}")
        if not top_pages:
            lines.append('  (none yet)')

        lines += ['', '── Top referrers ──────────────────────']
        for row in top_refs:
            lines.append(f"  {row['n']:>4}  {row['referrer'][:70]}")
        if not top_refs:
            lines.append('  (none yet)')

        lines += ['', '──────────────────────────────────────', 'joshuashneider.com admin']

        body = '\n'.join(lines)
        send_mail(
            subject=f'Site stats — {this_week} visits this week',
            message=body,
            from_email='josh@joshuashneider.com',
            recipient_list=[RECIPIENT],
            fail_silently=False,
        )
        self.stdout.write(self.style.SUCCESS(f'Sent weekly stats to {RECIPIENT}'))
