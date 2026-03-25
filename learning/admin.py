from django.contrib import admin
from .models import Course, Lesson, LessonResource, TrainingEvent, CourseEnrollment, Achievement


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'school', 'is_active', 'start_date']
    list_filter = ['level', 'school', 'is_active']
    search_fields = ['title']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'lesson_type', 'order', 'is_required']
    list_filter = ['lesson_type', 'course']
    ordering = ['course', 'order']


@admin.register(TrainingEvent)
class TrainingEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'school']
    list_filter = ['school']


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'progress_percent', 'enrolled_at']
    list_filter = ['status', 'course']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'points', 'earned_at']
