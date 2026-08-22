from django.contrib import admin
from .models import Page, Video, BandcampEmbed


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'nav_order', 'updated_at')
    list_editable = ('is_published', 'nav_order')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'nav_order', 'is_published')}),
        ('Content', {'fields': ('content',)}),
        ('Hero Image', {'fields': ('hero_image', 'hero_image_caption'), 'classes': ('collapse',)}),
    )


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'youtube_url', 'is_published', 'order')
    list_editable = ('is_published', 'order')
    fields = ('title', 'youtube_url', 'description', 'is_published', 'order')


@admin.register(BandcampEmbed)
class BandcampEmbedAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    readonly_fields = ('embed_code',)
    fieldsets = (
        (None, {'fields': ('title', 'is_active', 'order', 'description')}),
        ('Bandcamp', {'fields': ('bandcamp_url', 'embed_code')}),
        ('YouTube (alternative)', {'fields': ('youtube_url',), 'classes': ('collapse',)}),
    )
