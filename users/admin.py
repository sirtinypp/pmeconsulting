from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'school', 'is_active']
    list_filter = ['role', 'school', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('German Learning Platform', {'fields': ('role', 'school')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('German Learning Platform', {'fields': ('role', 'school')}),
    )
