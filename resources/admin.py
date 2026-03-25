from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display  = ['title', 'category', 'author', 'is_published', 'published_at']
    list_filter   = ['category', 'is_published']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published']
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'cover_emoji', 'author', 'is_published', 'published_at')
        }),
        ('Content', {
            'fields': ('excerpt', 'content')
        }),
    )
