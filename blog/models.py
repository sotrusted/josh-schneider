import re
from django.db import models
from django.urls import reverse
from django.utils import timezone
from tinymce.models import HTMLField
from core.utils import extract_youtube_id, fetch_bandcamp_embed


class Post(models.Model):
    class Category(models.TextChoices):
        NEWS = 'news', 'News'
        EVENTS = 'events', 'Events'
        PRESS = 'press', 'Press'

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=300)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.NEWS)
    content = HTMLField()
    excerpt = models.TextField(
        blank=True,
        help_text='Short summary shown in list view. Leave blank to auto-generate.',
    )
    youtube_url = models.CharField(
        max_length=200,
        blank=True,
        help_text='Optional: paste a YouTube URL to embed a video in the post',
    )
    bandcamp_url = models.CharField(
        max_length=500,
        blank=True,
        help_text='Optional: paste a Bandcamp album or track URL to embed audio',
    )
    bandcamp_embed_html = models.TextField(blank=True, editable=False)
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    image_caption = models.CharField(max_length=300, blank=True)
    audio_file = models.FileField(
        upload_to='audio/',
        blank=True,
        null=True,
        help_text='Optional MP3/audio file displayed as a player in this post',
    )
    tags = models.CharField(
        max_length=300,
        blank=True,
        help_text='Comma-separated: jazz, orchestra, recording',
    )
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def youtube_embed_url(self):
        vid = extract_youtube_id(self.youtube_url)
        return f'https://www.youtube-nocookie.com/embed/{vid}?origin=https://joshuashneider.com' if vid else ''

    def save(self, *args, **kwargs):
        if self.bandcamp_url:
            fetched = fetch_bandcamp_embed(self.bandcamp_url)
            if fetched:
                self.bandcamp_embed_html = fetched
        super().save(*args, **kwargs)

    def get_list_url(self):
        return reverse(self.category)

    def get_excerpt(self):
        if self.excerpt:
            return self.excerpt
        text = re.sub(r'<[^>]+>', '', self.content)
        return text[:220].rsplit(' ', 1)[0] + '…' if len(text) > 220 else text
