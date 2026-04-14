from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
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

    # Split lessons into standard curriculum and the final exam
    regular_lessons = lessons.filter(is_final_exam=False)
    final_exam = lessons.filter(is_final_exam=True).first()

    # Calculate curriculum progress (excluding the exam itself)
    required_lessons = regular_lessons.filter(is_required=True)
    required_count = required_lessons.count()
    
    completed_required_count = LessonCompletion.objects.filter(
        user=request.user, 
        lesson__in=required_lessons
    ).count()

    progress_percent = int((completed_required_count / required_count * 100)) if required_count > 0 else 100
    can_take_exam = (progress_percent >= 100)

    # Sync enrollment progress for the dashboard stats
    if enrollment:
        enrollment.progress_percent = progress_percent
        enrollment.save()

    return render(request, 'learning/course_detail.html', {
        'course': course,
        'lessons': regular_lessons,
        'final_exam': final_exam,
        'can_take_exam': can_take_exam,
        'enrollment': enrollment,
        'progress_percent': progress_percent,
        'completed_lesson_ids': list(completed_lesson_ids),
        'page_title': course.title,
        'brand_context': 'Learning',
    })


@login_required
def enroll_course(request, pk):
    """Student requests to enroll in a course (sets status to PENDING)."""
    # GUEST users must upgrade before enrolling
    if request.user.role == 'GUEST':
        return redirect('upgrade')

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
    try:
        lesson = Lesson.objects.get(pk=pk)
        # Force a check for the new column
        _ = lesson.is_final_exam
    except Exception:
        # Fallback for missing columns
        lesson = get_object_or_404(Lesson.objects.defer('is_final_exam', 'duration_minutes'), pk=pk)
    
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
    
    # Fetch user's submissions for activities in this lesson
    from .models import ActivitySubmission
    user_submissions = {
        s.activity_id: s for s in ActivitySubmission.objects.filter(user=request.user, activity__lesson=lesson)
    }

    # Quiz specific data
    questions = None
    previous_attempt = None
    if lesson.lesson_type == 'QIZ':
        from .models import QuizAttempt
        questions = lesson.questions.all().prefetch_related('choices')
        previous_attempt = QuizAttempt.objects.filter(user=request.user, lesson=lesson).first()

    return render(request, 'learning/lesson_detail.html', {
        'course': lesson.course,
        'lesson': lesson,
        'questions': questions,
        'previous_attempt': previous_attempt,
        'completed': completed,
        'user_submissions': user_submissions,
        'page_title': lesson.title,
        'brand_context': 'Learning',
    })


@login_required
def submit_activity(request, pk):
    """Handle student activity submissions (text and/or file uploads like Audio)."""
    from .models import LessonActivity, ActivitySubmission
    activity = get_object_or_404(LessonActivity, pk=pk)
    
    # Check if student is enrolled in the parent course
    enrollment = CourseEnrollment.objects.filter(
        user=request.user, course=activity.lesson.course, status='ENROLLED'
    ).exists()
    
    if not enrollment and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        from django.contrib import messages
        try:
            submission_text = request.POST.get('submission_text', '')
            submission_url = request.POST.get('submission_url', '')
            submission_file = request.FILES.get('submission_file')

            # Create or update submission logic
            defaults = {
                'submission_text': submission_text,
                'submission_url': submission_url,
                'status': 'PENDING'
            }
            if submission_file:
                # Validation: Prevent massive file uploads that might crash the ephemeral worker
                if submission_file.size > 10 * 1024 * 1024: # 10MB limit
                    messages.error(request, "File too large (Max 10MB). Please use a Google Drive link for larger files.")
                    return redirect('lesson_detail', pk=activity.lesson.pk)
                
                defaults['submission_file'] = submission_file

            ActivitySubmission.objects.update_or_create(
                user=request.user,
                activity=activity,
                defaults=defaults
            )
            messages.success(request, f"Task '{activity.title}' submitted successfully!")
            
        except Exception as e:
            messages.error(request, f"Error submitting work: {str(e)}")

    return redirect('lesson_detail', pk=activity.lesson.pk)


@login_required
@require_POST
def submit_quiz(request, pk):
    """Processes quiz submissions, calculates score, and marks course as completed if final exam."""
    from .models import Lesson, QuizQuestion, QuizChoice, QuizAttempt, LessonCompletion, CourseEnrollment
    import datetime

    lesson = get_object_or_404(Lesson, pk=pk)
    questions = lesson.questions.all().prefetch_related('choices')
    total_questions = questions.count()
    correct_count = 0

    if total_questions == 0:
        return redirect('lesson_detail', pk=pk)

    for q in questions:
        selected_choice_id = request.POST.get(f'question_{q.id}')
        if selected_choice_id:
            try:
                choice = QuizChoice.objects.get(id=selected_choice_id, question=q)
                if choice.is_correct:
                    correct_count += 1
            except QuizChoice.DoesNotExist:
                continue

    score_percent = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
    passed = score_percent >= 80

    # Record the attempt
    QuizAttempt.objects.update_or_create(
        user=request.user,
        lesson=lesson,
        defaults={
            'score': correct_count,
            'total_questions': total_questions,
            'passed': passed,
            'attempted_at': datetime.datetime.now()
        }
    )

    if passed:
        # Mark lesson as completed
        LessonCompletion.objects.get_or_create(user=request.user, lesson=lesson)

        # Re-calculate overall enrollment progress immediately
        enrollment = CourseEnrollment.objects.filter(user=request.user, course=lesson.course).first()
        if enrollment:
            required_lessons = Lesson.objects.filter(course=lesson.course, is_required=True, is_final_exam=False)
            required_count = required_lessons.count()
            completed_required_count = LessonCompletion.objects.filter(
                user=request.user, 
                lesson__in=required_lessons
            ).count()
            
            new_progress = int((completed_required_count / required_count * 100)) if required_count > 0 else 100
            enrollment.progress_percent = new_progress

            # If this is the Final Exam and they passed, mark the entire course as completed
            if lesson.is_final_exam:
                enrollment.status = CourseEnrollment.Status.COMPLETED
                enrollment.completed_at = datetime.datetime.now()
                enrollment.save()
                return redirect('dashboard') # Celebrate!
            
            enrollment.save()

    return redirect('lesson_detail', pk=pk)
