from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum

from .models import School
from users.models import CustomUser
from learning.models import (
    Course, TrainingEvent, CourseEnrollment, Achievement
)
from gamification.models import UserProgression
from resources.models import Post


@login_required
def dashboard(request):
    context = {'page_title': 'Dashboard', 'brand_context': 'Dashboard'}

    if request.user.role == 'SUPERUSER':
        context['total_students'] = CustomUser.objects.filter(role='STUDENT').count()
        context['total_admins'] = CustomUser.objects.filter(role='SCHOOL_ADMIN').count()
        context['total_schools'] = School.objects.count()
        context['total_enrollments'] = CourseEnrollment.objects.count()

        school_stats = []
        for school in School.objects.all():
            school_stats.append({
                'name': school.name,
                'student_count': CustomUser.objects.filter(school=school, role='STUDENT').count(),
                'enrollment_count': CourseEnrollment.objects.filter(course__school=school).count(),
            })
        context['school_stats'] = school_stats
        context['brand_context'] = 'Super Management'
        return render(request, 'dashboards/superuser.html', context)

    elif request.user.role == 'SCHOOL_ADMIN':
        students = CustomUser.objects.filter(school=request.user.school, role='STUDENT')
        for student in students:
            enrollments = CourseEnrollment.objects.filter(user=student)
            completed = enrollments.filter(status='COMPLETED').count()
            total = enrollments.count()
            student.completion_rate = int((completed / total * 100)) if total > 0 else 0
            student.total_enrollments = total

        context['students'] = students
        context['school_name'] = request.user.school.name if request.user.school else ''
        context['active_courses'] = Course.objects.filter(school=request.user.school, is_active=True).count()
        context['total_enrollments'] = CourseEnrollment.objects.filter(course__school=request.user.school).count()
        context['brand_context'] = 'Management'
        return render(request, 'dashboards/school_admin.html', context)

    else:
        # Student dashboard
        enrollments = CourseEnrollment.objects.filter(user=request.user)
        context['assigned_count'] = enrollments.count()
        context['completed_count'] = enrollments.filter(status='COMPLETED').count()
        context['in_progress_count'] = enrollments.filter(status='IN_PROGRESS').count()

        progression = getattr(request.user, 'progression', None)
        if not progression:
            progression, _ = UserProgression.objects.get_or_create(user=request.user)

        achievement_points = Achievement.objects.filter(user=request.user).aggregate(Sum('points'))['points__sum'] or 0
        context['total_points'] = progression.points + achievement_points

        context['courses'] = Course.objects.for_user(request.user)[:3]
        context['trainings'] = TrainingEvent.objects.for_user(request.user).order_by('date')[:3]
        context['achievements'] = Achievement.objects.filter(user=request.user).order_by('-earned_at')[:5]
        context['enrollments'] = enrollments[:5]
        context['recent_resources'] = Post.objects.filter(is_published=True).order_by('-published_at')[:4]

        return render(request, 'dashboards/student.html', context)


@login_required
def student_upsert(request, pk=None):
    """Create or edit a student (admin only)."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    student = None
    if pk:
        student = get_object_or_404(CustomUser, pk=pk)
        if not request.user.is_superuser and student.school != request.user.school:
            raise PermissionDenied

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not student:
            student = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password or 'german_temp123',
                school=request.user.school,
                role=CustomUser.Role.STUDENT
            )
        else:
            student.username = username
            student.email = email
            if password:
                student.set_password(password)
            student.save()

        return redirect('dashboard')

    return render(request, 'management/student_form.html', {
        'student': student,
        'page_title': 'Edit Student' if pk else 'Add New Student',
        'brand_context': 'Management',
    })


@login_required
def student_delete(request, pk):
    """Deactivate a student."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    student = get_object_or_404(CustomUser, pk=pk)
    if not request.user.is_superuser and student.school != request.user.school:
        raise PermissionDenied

    student.is_active = False
    student.save()
    return redirect('dashboard')
