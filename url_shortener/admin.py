"""Admin configuration for url_shortener app."""

from django.contrib import admin

from .models import ShortenedURL


@admin.register(ShortenedURL)
class ShortenedURLAdmin(admin.ModelAdmin):
    """Admin configuration for ShortenedURL model."""
    
    list_display = [
        'code',
        'short_url_display',
        'original_url_display',
        'created_by',
        'created_at',
    ]
    
    list_filter = [
        'created_at',
        'created_by',
    ]
    
    search_fields = [
        'code',
        'original_url',
        'created_by__email',
        'created_by__first_name',
        'created_by__last_name',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'short_url_display',
    ]
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations du lien', {
            'fields': ('code', 'original_url', 'short_url_display')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def short_url_display(self, obj):
        """Display the short URL."""
        return obj.get_short_url()
    short_url_display.short_description = 'URL courte'
    
    def original_url_display(self, obj):
        """Display the original URL truncated."""
        if len(obj.original_url) > 60:
            return obj.original_url[:60] + '...'
        return obj.original_url
    original_url_display.short_description = 'URL originale'
