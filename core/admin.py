from datetime import timedelta
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from .models import PageVisit, SiteSettings, SiteStats

# Admin branding
admin.site.site_header = "Joshua Shneider — Website Admin"
admin.site.site_title = "Josh Site"
admin.site.index_title = "What would you like to update?"

# Hide auth models — Josh doesn't need user/group management
admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Identity', {'fields': ('site_name', 'tagline', 'contact_email', 'bandcamp_url')}),
        ('Homepage', {'fields': ('hero_text', 'hero_image', 'header_banner')}),
    )

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.get()
        return HttpResponseRedirect(reverse('admin:core_sitesettings_change', args=[obj.pk]))

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteStats)
class SiteStatsAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        now = timezone.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        humans = PageVisit.objects.filter(is_bot=False)
        total_30d = humans.filter(visited_at__gte=month_ago).count()

        site = SiteSettings.get()
        live_human_total = humans.count()
        ctx = {
            **self.admin_site.each_context(request),
            'title': 'Visitor Stats',
            'today': humans.filter(visited_at__gte=day_ago).count(),
            'this_week': humans.filter(visited_at__gte=week_ago).count(),
            'this_month': total_30d,
            'total_all': site.lifetime_human_visits + live_human_total,
            'bot_count_30d': PageVisit.objects.filter(is_bot=True, visited_at__gte=month_ago).count(),
            'top_pages': (
                humans.filter(visited_at__gte=month_ago)
                .values('path').annotate(n=Count('id')).order_by('-n')[:10]
            ),
            'top_referrers': (
                humans.filter(visited_at__gte=month_ago)
                .exclude(referrer='')
                .values('referrer').annotate(n=Count('id')).order_by('-n')[:8]
            ),
            'recent': (
                humans.filter(visited_at__gte=week_ago)
                .order_by('-visited_at')
                .values('path', 'referrer', 'visited_at')[:20]
            ),
        }
        return TemplateResponse(request, 'admin/visitor_stats.html', ctx)

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
