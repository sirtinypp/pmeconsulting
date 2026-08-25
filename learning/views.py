from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .models import Course, CourseEnrollment, Lesson, LessonCompletion


@login_required
def course_list(request):
    """List courses available to the user's school."""
    enrolled_ids = list(CourseEnrollment.objects.filter(
        user=request.user
    ).values_list('course_id', flat=True))

    courses = Course.objects.for_user(request.user).filter(is_active=True)
    if request.user.role == 'STUDENT':
        courses = courses.filter(Q(show_in_catalog=True) | Q(id__in=enrolled_ids))

    return render(request, 'learning/course_list.html', {
        'courses': courses,
        'enrolled_ids': enrolled_ids,
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

    # Fetch user's quiz attempts for this course
    from .models import QuizAttempt
    user_attempts = {
        qa.lesson_id: qa for qa in QuizAttempt.objects.filter(user=request.user, lesson__course=course)
    }
    for l in regular_lessons:
        l.user_attempt = user_attempts.get(l.id)
    if final_exam:
        final_exam.user_attempt = user_attempts.get(final_exam.id)

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
        enrollment = CourseEnrollment.objects.filter(
            user=request.user, 
            course=lesson.course,
            status__in=['ENROLLED', 'IN_PROGRESS', 'COMPLETED']
        ).first()

        is_admin = request.user.role in ['SCHOOL_ADMIN', 'SUPERUSER'] or request.user.is_superuser
        if not enrollment and not is_admin:
            raise PermissionDenied

        LessonCompletion.objects.get_or_create(user=request.user, lesson=lesson)

        # Update enrollment progress
        course = lesson.course
        total = course.lessons.filter(is_required=True).count()
        done = LessonCompletion.objects.filter(
            user=request.user, lesson__course=course, lesson__is_required=True
        ).count()

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
    """View a lesson, its material, activities, and quiz."""
    lesson = get_object_or_404(Lesson, pk=pk)

    # Check if student is enrolled in the parent course
    enrollment = CourseEnrollment.objects.filter(
        user=request.user,
        course=lesson.course,
        status__in=['ENROLLED', 'IN_PROGRESS', 'COMPLETED']
    ).first()

    # Staff or Superusers can view any lesson
    is_staff_or_admin = request.user.role in ['SCHOOL_ADMIN', 'SUPERUSER'] or request.user.is_superuser
    
    if not enrollment and not is_staff_or_admin:
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
        user=request.user,
        course=activity.lesson.course,
        status__in=['ENROLLED', 'IN_PROGRESS', 'COMPLETED']
    ).exists()
    
    # Allow school admin or superuser
    is_staff_or_admin = request.user.role in ['SCHOOL_ADMIN', 'SUPERUSER'] or request.user.is_superuser
    
    if not enrollment and not is_staff_or_admin:
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
    from django.contrib import messages
    import datetime

    lesson = get_object_or_404(Lesson, pk=pk)
    questions = lesson.questions.all().prefetch_related('choices')
    total_questions = questions.count()
    correct_count = 0

    if total_questions == 0:
        messages.error(request, "This quiz currently has 0 questions.")
        return redirect('course_detail', pk=lesson.course.pk)

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
        messages.success(
            request, 
            f"🎉 PASSED! You scored {correct_count} out of {total_questions} ({score_percent}%)."
        )
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
                messages.success(
                    request,
                    f"🏆 Congratulations! You passed the Final Exam with {correct_count}/{total_questions} ({score_percent}%) and completed the course!"
                )
                return redirect('course_detail', pk=lesson.course.pk)
            
            enrollment.save()
    else:
        messages.error(
            request, 
            f"❌ NOT PASSED. You scored {correct_count} out of {total_questions} ({score_percent}%). A minimum score of 80% is required to pass."
        )

    if lesson.is_final_exam:
        return redirect('course_detail', pk=lesson.course.pk)
    else:
        return redirect('lesson_detail', pk=lesson.pk)


import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .models import CourseTier, PaymentOrder
from .payment_service import create_paymongo_checkout_session, verify_paymongo_webhook


@login_required
def initiate_checkout(request, course_id, tier_type='BASIC'):
    """Initiates PayMongo checkout session for a course level and tier."""
    course = get_object_or_404(Course, pk=course_id)
    tier = CourseTier.objects.filter(course=course, tier_type=tier_type.upper()).first()
    
    # Default prices if CourseTier object doesn't exist yet
    default_prices = {
        'A1': {'BASIC': 12000, 'STANDARD': 15000, 'PREMIUM': 20000},
        'A2': {'BASIC': 15000, 'STANDARD': 18000, 'PREMIUM': 22000},
        'B1': {'BASIC': 18000, 'STANDARD': 21000, 'PREMIUM': 25000},
        'B2': {'BASIC': 20000, 'STANDARD': 24000, 'PREMIUM': 28000},
        'C1': {'BASIC': 25000, 'STANDARD': 30000, 'PREMIUM': 35000},
    }

    price_amount = tier.price if tier else default_prices.get(course.level, {}).get(tier_type.upper(), 15000)

    # 1. Create or get enrollment in PENDING status
    enrollment, _ = CourseEnrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'status': CourseEnrollment.Status.PENDING}
    )

    if enrollment.status == CourseEnrollment.Status.ENROLLED:
        messages.info(request, f"You are already enrolled in {course.title}!")
        return redirect('course_detail', pk=course.pk)

    # 2. Build Callback URLs
    domain = request.build_absolute_uri('/')[:-1]
    success_url = f"{domain}/learning/payment/success/?course_id={course.id}"
    cancel_url = f"{domain}/learning/payment/cancel/?course_id={course.id}"

    # 3. Request PayMongo Checkout Session
    session_result = create_paymongo_checkout_session(
        user=request.user,
        course_title=f"{course.title} ({course.level})",
        tier_name=tier_type.capitalize(),
        price_php=price_amount,
        success_url=success_url,
        cancel_url=cancel_url
    )

    if session_result.get('success'):
        # Save Payment Order record
        PaymentOrder.objects.create(
            user=request.user,
            enrollment=enrollment,
            tier=tier,
            amount=price_amount,
            checkout_session_id=session_result['checkout_session_id'],
            checkout_url=session_result['checkout_url'],
            status=PaymentOrder.PaymentStatus.PENDING
        )
        return redirect(session_result['checkout_url'])
    else:
        messages.error(request, f"Could not initiate checkout: {session_result.get('error')}")
        return redirect('public_courses')


@login_required
def payment_success(request):
    """View shown after successful payment completion."""
    course_id = request.GET.get('course_id')
    course = Course.objects.filter(pk=course_id).first() if course_id else None
    
    # Fallback sync: Check latest pending order for this user & mark as PAID if completed in PayMongo
    latest_order = PaymentOrder.objects.filter(
        user=request.user, 
        status=PaymentOrder.PaymentStatus.PENDING
    ).order_by('-created_at').first()

    if latest_order and latest_order.checkout_session_id:
        import requests
        from .payment_service import get_paymongo_headers
        try:
            url = f"https://api.paymongo.com/v1/checkout_sessions/{latest_order.checkout_session_id}"
            res = requests.get(url, headers=get_paymongo_headers(), timeout=10)
            if res.status_code == 200:
                attributes = res.json().get('data', {}).get('attributes', {})
                payments = attributes.get('payments', [])
                payment_intent = attributes.get('payment_intent', {})
                
                # Check if payment is paid or has successful payments array
                is_paid = len(payments) > 0 or (isinstance(payment_intent, dict) and payment_intent.get('attributes', {}).get('status') == 'succeeded')
                
                if is_paid:
                    latest_order.status = PaymentOrder.PaymentStatus.PAID
                    latest_order.save()
                    
                    enrollment = latest_order.enrollment
                    enrollment.status = CourseEnrollment.Status.ENROLLED
                    enrollment.save()

                    # Upgrade User Role to STUDENT if guest
                    if request.user.role == 'GUEST':
                        request.user.role = 'STUDENT'
                        request.user.save()
        except Exception:
            pass

    return render(request, 'learning/payment_success.html', {
        'course': course,
        'page_title': 'Enrollment Successful',
        'brand_context': 'Learning',
    })



@login_required
def payment_cancel(request):
    """View shown if user cancels payment checkout."""
    course_id = request.GET.get('course_id')
    course = Course.objects.filter(pk=course_id).first() if course_id else None

    return render(request, 'learning/payment_cancel.html', {
        'course': course,
        'page_title': 'Payment Cancelled',
        'brand_context': 'Learning',
    })


@csrf_exempt
def paymongo_webhook(request):
    """
    PayMongo Webhook Receiver.
    Listens for `checkout_session.payment.paid` events and automatically converts
    CourseEnrollment status from PENDING -> ENROLLED.
    """
    if request.method != 'POST':
        return HttpResponse(status=405)

    signature_header = request.headers.get('Paymongo-Signature', '')
    raw_body = request.body

    # Validate webhook signature in production if secret is set
    from django.conf import settings
    if getattr(settings, 'PAYMONGO_WEBHOOK_SECRET', '') and getattr(settings, 'PAYMONGO_WEBHOOK_SECRET') != 'whsec_placeholder':
        if not verify_paymongo_webhook(raw_body, signature_header):
            return HttpResponse("Invalid Signature", status=400)

    try:
        event = json.loads(raw_body.decode('utf-8'))
        event_type = event.get('data', {}).get('attributes', {}).get('type')

        if event_type == 'checkout_session.payment.paid':
            session_data = event.get('data', {}).get('attributes', {}).get('data', {})
            checkout_session_id = session_data.get('id')

            if checkout_session_id:
                order = PaymentOrder.objects.filter(checkout_session_id=checkout_session_id).first()
                if order:
                    order.status = PaymentOrder.PaymentStatus.PAID
                    order.save()

                    # Unlock Enrollment immediately
                    enrollment = order.enrollment
                    enrollment.status = CourseEnrollment.Status.ENROLLED
                    enrollment.save()

        return JsonResponse({'status': 'success'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
