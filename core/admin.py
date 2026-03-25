from django.contrib import admin
from .models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'primary_color', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
