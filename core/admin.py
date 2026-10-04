from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import SiteSettings

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
