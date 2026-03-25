from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Course, CourseEnrollment, Lesson, LessonCompletion


@login_required
def course_list(request):
    """List courses available to the user's school."""
    courses = Course.objects.for_user(request.user).filter(is_active=True)
    enrolled_ids = CourseEnrollment.objects.filter(
        user=request.user
    ).values_list('course_id', flat=True)

    return render(request, 'learning/course_list.html', {
        'courses': courses,
        'enrolled_ids': list(enrolled_ids),
        'page_title': 'Course Catalog',
        'brand_context': 'Learning',
    })


@login_required
def course_detail(request, pk):
    """View a single course and its lessons."""
    course = get_object_or_404(Course, pk=pk)
    lessons = course.lessons.order_by('order')

    enrollment = CourseEnrollment.objects.filter(
        user=request.user, course=course
    ).first()

    completed_lesson_ids = LessonCompletion.objects.filter(
        user=request.user, lesson__course=course
    ).values_list('lesson_id', flat=True)

    return render(request, 'learning/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'enrollment': enrollment,
        'completed_lesson_ids': list(completed_lesson_ids),
        'page_title': course.title,
        'brand_context': 'Learning',
    })


@login_required
def enroll_course(request, pk):
    """Student requests to enroll in a course (sets status to PENDING)."""
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        CourseEnrollment.objects.get_or_create(
            user=request.user, course=course,
            defaults={'status': CourseEnrollment.Status.PENDING}
        )
    return redirect('course_detail', pk=pk)


@login_required
def approve_enrollment(request, pk):
    """School Admin approves an enrollment request."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied
    
    enrollment = get_object_or_404(CourseEnrollment, pk=pk)
    # Security check: Admin can only approve for their own school
    if not request.user.is_superuser and enrollment.course.school != request.user.school:
        raise PermissionDenied

    if request.method == 'POST':
        enrollment.status = CourseEnrollment.Status.ENROLLED
        enrollment.save()
    return redirect('dashboard')


@login_required
def reject_enrollment(request, pk):
    """School Admin rejects an enrollment request."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied
    
    enrollment = get_object_or_404(CourseEnrollment, pk=pk)
    if not request.user.is_superuser and enrollment.course.school != request.user.school:
        raise PermissionDenied

    if request.method == 'POST':
        enrollment.status = CourseEnrollment.Status.REJECTED
        enrollment.save()
    return redirect('dashboard')


@login_required
def complete_lesson(request, pk):
    """Mark a lesson as completed."""
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        LessonCompletion.objects.get_or_create(user=request.user, lesson=lesson)

        # Update enrollment progress
        course = lesson.course
        total = course.lessons.filter(is_required=True).count()
        done = LessonCompletion.objects.filter(
            user=request.user, lesson__course=course, lesson__is_required=True
        ).count()

        enrollment = CourseEnrollment.objects.filter(
            user=request.user, course=course
        ).first()

        if enrollment:
            enrollment.progress_percent = int((done / total * 100)) if total > 0 else 0
            if enrollment.progress_percent >= 100:
                enrollment.status = CourseEnrollment.Status.COMPLETED
            elif enrollment.progress_percent > 0:
                enrollment.status = CourseEnrollment.Status.IN_PROGRESS
            enrollment.save()

    return redirect('course_detail', pk=lesson.course.pk)


@login_required
def lesson_detail(request, pk):
    """View a single lesson's full content."""
    lesson = get_object_or_404(Lesson, pk=pk)
    
    # Check if user is enrolled in the course or is admin
    enrollment = CourseEnrollment.objects.filter(
        user=request.user, course=lesson.course
    ).first()
    
    # Allow enrolled students OR admins/superusers
    if not enrollment and request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    # Check if approved if student
    if enrollment and enrollment.status == CourseEnrollment.Status.PENDING and request.user.role == 'STUDENT':
        return redirect('course_detail', pk=lesson.course.pk)

    completed = LessonCompletion.objects.filter(user=request.user, lesson=lesson).exists()

    return render(request, 'learning/lesson_detail.html', {
        'lesson': lesson,
        'course': lesson.course,
        'completed': completed,
        'page_title': lesson.title,
        'brand_context': 'Learning',
    })
