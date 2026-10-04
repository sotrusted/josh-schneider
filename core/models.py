import hashlib
from django.db import models


class PageVisit(models.Model):
    path = models.CharField(max_length=500)
    ip_hash = models.CharField(max_length=64)
    user_agent = models.CharField(max_length=500, blank=True)
    referrer = models.CharField(max_length=500, blank=True)
    is_bot = models.BooleanField(default=False, db_index=True)
    visited_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['visited_at', 'is_bot']),
            models.Index(fields=['path', 'visited_at']),
        ]

    @classmethod
    def human_visits(cls):
        return cls.objects.filter(is_bot=False)


class SiteStats(PageVisit):
    """Proxy model — admin-only stats dashboard, no extra DB table."""
    class Meta:
        proxy = True
        verbose_name = 'Visitor Stats'
        verbose_name_plural = '📊 Visitor Stats'


class SiteSettings(models.Model):
    """Singleton — only one row (pk=1). Stores global site config."""

    site_name = models.CharField(max_length=100, default='Joshua Shneider')
    tagline = models.CharField(max_length=200, blank=True, default='Composer · Saxophonist · Arranger')
    contact_email = models.EmailField(default='contact@joshuashneider.com')
    bandcamp_url = models.URLField(
        blank=True,
        default='https://joshuashneider.bandcamp.com',
        help_text='External Bandcamp profile link used in nav',
    )
    hero_text = models.TextField(
        blank=True,
        default=(
            'Welcome to the website of Composer Joshua Shneider. '
            'Please take a look and a listen and let us know what you think — '
            "we'd love to hear from you!"
        ),
    )
    lifetime_human_visits = models.PositiveBigIntegerField(default=0)
    lifetime_bot_visits = models.PositiveBigIntegerField(default=0)

    hero_image = models.ImageField(upload_to='site/', blank=True, null=True)
    header_banner = models.ImageField(
        upload_to='site/',
        blank=True,
        null=True,
        help_text='Wide banner image displayed in the site header',
    )

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
