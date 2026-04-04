from django.contrib import admin
from .models import School, ServiceInquiry


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'primary_color', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(ServiceInquiry)
class ServiceInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'service_requested', 'status', 'created_at']
    list_filter = ['status', 'service_requested', 'created_at']
    search_fields = ['name', 'email']
