from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'published_at')
    list_editable = ('is_published',)
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'category', 'is_published', 'published_at')}),
        ('Content', {'fields': ('content', 'excerpt')}),
        ('Media', {'fields': ('youtube_url', 'bandcamp_url', 'image', 'image_caption')}),
        ('Tags', {'fields': ('tags',)}),
    )
