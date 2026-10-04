from django.db import models
from django.urls import reverse
from tinymce.models import HTMLField
from core.utils import extract_youtube_id, fetch_bandcamp_embed


class Page(models.Model):
    """Editable flat page: bio, services, lessons, sheet-music, orchestra."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text='URL key, e.g. "bio" → /bio/')
    content = HTMLField()
    hero_image = models.ImageField(upload_to='pages/', blank=True, null=True)
    hero_image_caption = models.CharField(max_length=200, blank=True)
    audio_file = models.FileField(
        upload_to='audio/',
        blank=True,
        null=True,
        help_text='Optional MP3/audio file displayed as a player on this page',
    )
    is_published = models.BooleanField(default=True)
    nav_order = models.PositiveSmallIntegerField(default=10, help_text='Lower = earlier in nav')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nav_order', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('page_detail', kwargs={'slug': self.slug})


class Video(models.Model):
    """YouTube embed for the Video page."""

    title = models.CharField(max_length=200)
    youtube_url = models.CharField(
        max_length=200,
        default='',
        blank=True,
        help_text='Paste the full YouTube URL, e.g. https://www.youtube.com/watch?v=…',
    )
    video_file = models.FileField(
        upload_to='videos/',
        blank=True,
        null=True,
        help_text='Upload an MP4/WebM video file (alternative to YouTube URL)',
    )
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=10)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    @property
    def video_id(self):
        return extract_youtube_id(self.youtube_url)

    @property
    def embed_url(self):
        vid = self.video_id
        return f'https://www.youtube-nocookie.com/embed/{vid}?origin=https://joshuashneider.com' if vid else ''


class BandcampEmbed(models.Model):
    """Featured media item on the Listen page / homepage."""

    title = models.CharField(max_length=200)
    bandcamp_url = models.CharField(
        max_length=500,
        blank=True,
        help_text='Paste the Bandcamp album or track URL — embed code is fetched automatically',
    )
    embed_code = models.TextField(
        blank=True,
        help_text='Auto-populated from Bandcamp URL. Override here if needed.',
    )
    youtube_url = models.CharField(
        max_length=200,
        blank=True,
        help_text='YouTube URL — alternative to Bandcamp',
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=10)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.bandcamp_url:
            fetched = fetch_bandcamp_embed(self.bandcamp_url)
            if fetched:
                self.embed_code = fetched
        super().save(*args, **kwargs)

    @property
    def youtube_embed_url(self):
        vid = extract_youtube_id(self.youtube_url)
        return f'https://www.youtube.com/embed/{vid}' if vid else ''
