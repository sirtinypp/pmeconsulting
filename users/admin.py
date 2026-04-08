from django.contrib import admin
from django.db import models
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, GuestUser, StudentUser, AdminUser


class SharedUserAdmin(UserAdmin):
    """Common admin logic for all roles."""
    list_display = ['username', 'email', 'role', 'school', 'is_active', 'date_joined']
    list_filter = ['school', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('German Learning Platform', {'fields': ('role', 'school')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('German Learning Platform', {'fields': ('role', 'school')}),
    )


@admin.register(GuestUser)
class GuestUserAdmin(SharedUserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=CustomUser.Role.GUEST)


@admin.register(StudentUser)
class StudentUserAdmin(SharedUserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=CustomUser.Role.STUDENT)


@admin.register(AdminUser)
class AdminUserAdmin(SharedUserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            models.Q(role=CustomUser.Role.SCHOOL_ADMIN) | 
            models.Q(role=CustomUser.Role.SUPERUSER) |
            models.Q(is_staff=True)
        )


# Keep CustomUser available for total overview but move it to the bottom or just keep it simple
@admin.register(CustomUser)
class CustomUserAdmin(SharedUserAdmin):
    list_filter = ['role', 'school', 'is_active']
