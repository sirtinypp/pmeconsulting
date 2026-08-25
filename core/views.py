from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.db.models import Sum

from .models import School
from users.models import CustomUser
from learning.models import (
    Course, TrainingEvent, CourseEnrollment, Achievement, Lesson
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
        school = request.user.school
        if not school and (request.user.is_superuser or request.user.role in ['SUPERUSER', 'SCHOOL_ADMIN']):
            school = School.objects.first()

        from learning.models import LessonCompletion, Lesson
        students = CustomUser.objects.filter(school=school, role='STUDENT')
        for student in students:
            enrollments = CourseEnrollment.objects.filter(user=student, status__in=['ENROLLED', 'IN_PROGRESS', 'COMPLETED'])
            course_ids = enrollments.values_list('course_id', flat=True)
            
            # Count total mandatory lessons in these courses
            total_lessons = Lesson.objects.filter(course_id__in=course_ids, is_required=True).count()
            
            # Count completed lessons by this student
            completed_lessons = LessonCompletion.objects.filter(user=student, lesson__course_id__in=course_ids).count()
            
            student.completion_rate = int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0
            student.total_enrollments = enrollments.count()

        context['students'] = students.order_by('-date_joined')
        # Prefetch inquiries for guests (institutional leads + unassigned leads)
        from django.db.models import Q
        context['guests'] = CustomUser.objects.filter(
            Q(role='GUEST'),
            Q(school=school) | Q(school__isnull=True)
        ).prefetch_related('service_inquiries').order_by('-date_joined')
        context['school_name'] = school.name if school else 'General Management'
        
        # Course Management Data
        from django.db.models import Count, Q
        context['all_courses'] = Course.objects.filter(school=school).annotate(
            enrollment_count=Count('enrollments', filter=Q(enrollments__status__in=['ENROLLED', 'IN_PROGRESS', 'COMPLETED']))
        ).order_by('title')
        context['active_courses_count'] = context['all_courses'].filter(is_active=True).count()
        
        # Training Management Data
        context['training_events'] = TrainingEvent.objects.filter(school=school).order_by('date')
        
        context['total_enrollments'] = CourseEnrollment.objects.filter(course__school=school).count()
        context['pending_enrollments'] = CourseEnrollment.objects.filter(
            course__school=school, 
            status=CourseEnrollment.Status.PENDING
        ).order_by('-enrolled_at')
        
        from learning.models import ActivitySubmission, PaymentOrder
        context['pending_submissions'] = ActivitySubmission.objects.filter(
            activity__lesson__course__school=school,
            status='PENDING'
        ).order_by('-submitted_at')
        
        # Payment Management Data
        payment_orders = PaymentOrder.objects.filter(
            enrollment__course__school=school
        ).select_related('user', 'enrollment__course', 'tier').order_by('-created_at')
        
        context['payment_orders'] = payment_orders
        context['paid_orders_count'] = payment_orders.filter(status=PaymentOrder.PaymentStatus.PAID).count()
        context['total_revenue'] = payment_orders.filter(
            status=PaymentOrder.PaymentStatus.PAID
        ).aggregate(total=Sum('amount'))['total'] or 0.00
        
        context['brand_context'] = 'Management'
        return render(request, 'dashboards/school_admin.html', context)

    elif request.user.role == 'GUEST':
        context['brand_context'] = 'Discovery'
        context['page_title'] = 'Guest Access'
        context['featured_courses'] = Course.objects.filter(is_active=True)[:3]
        context['recent_resources'] = Post.objects.filter(is_published=True).order_by('-published_at')[:4]
        return render(request, 'dashboards/guest.html', context)

    else:
        # Student dashboard
        from learning.models import LessonCompletion, Lesson
        all_enrollments = CourseEnrollment.objects.filter(user=request.user)
        active_course_ids = all_enrollments.filter(status__in=['ENROLLED', 'IN_PROGRESS', 'COMPLETED']).values_list('course_id', flat=True)
        
        # Calculate curriculum-wide completion rate
        total_lessons = Lesson.objects.filter(course_id__in=active_course_ids, is_required=True).count()
        completed_lessons = LessonCompletion.objects.filter(user=request.user, lesson__course_id__in=active_course_ids).count()
        context['completion_rate'] = int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0

        # Stat counters
        context['assigned_count'] = len(active_course_ids)
        context['pending_count'] = all_enrollments.filter(status='PENDING').count()
        context['completed_count'] = all_enrollments.filter(status='COMPLETED').count()
        context['in_progress_count'] = all_enrollments.filter(status='IN_PROGRESS').count()

        progression = getattr(request.user, 'progression', None)
        if not progression:
            progression, _ = UserProgression.objects.get_or_create(user=request.user)

        achievement_points = Achievement.objects.filter(user=request.user).aggregate(Sum('points'))['points__sum'] or 0
        context['total_points'] = progression.points + achievement_points

        # Data Lists
        context['active_enrollments'] = all_enrollments.filter(
            status__in=['ENROLLED', 'IN_PROGRESS', 'COMPLETED']
        ).select_related('course').order_by('-enrolled_at')[:5]
        
        context['pending_enrollments'] = all_enrollments.filter(
            status='PENDING'
        ).select_related('course').order_by('-enrolled_at')
        
        context['trainings'] = TrainingEvent.objects.for_user(request.user).order_by('date')[:3]
        context['achievements'] = Achievement.objects.filter(user=request.user).order_by('-earned_at')[:5]
        context['recent_resources'] = Post.objects.filter(is_published=True).order_by('-published_at')[:4]

        return render(request, 'dashboards/student.html', context)


@login_required
def student_upsert(request, pk=None):
    """Create or edit a student (admin only)."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    inquiry = None
    student = None
    if pk:
        student = get_object_or_404(CustomUser, pk=pk)
        # Allow school admin to edit guests with NO school, or students from their school
        if not request.user.is_superuser:
            if student.school and student.school != request.user.school:
                raise PermissionDenied
        
        # Fetch latest inquiry for lead management (fallback to email match for non-linked leads)
        from core.models import ServiceInquiry
        inquiry = student.service_inquiries.first()
        if not inquiry:
            inquiry = ServiceInquiry.objects.filter(email=student.email).first()
            if inquiry and not inquiry.user:
                inquiry.user = student
                inquiry.save()

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'STUDENT')

        school = request.user.school
        if not school and (request.user.is_superuser or request.user.role in ['SUPERUSER', 'SCHOOL_ADMIN']):
            school = School.objects.first()

        if not student:
            student = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password or 'german_temp123',
                school=school,
                role=role
            )
        else:
            student.username = username
            student.email = email
            student.role = role
            # If the student (guest) had no school, associate it with the current admin's school
            if not student.school:
                student.school = request.user.school
            if password:
                student.set_password(password)
            student.save()

            # Handle Inquiry Update (High-Fidelity Lead CRM)
            if inquiry:
                inquiry.is_paid = request.POST.get('is_paid') == 'on'
                inquiry.status = request.POST.get('inquiry_status')
                inquiry.save()

        return redirect('dashboard')

    from core.models import ServiceInquiry
    return render(request, 'management/student_form.html', {
        'student': student,
        'inquiry': inquiry,
        'inquiry_choices': ServiceInquiry.Status.choices,
        'page_title': 'Edit Student' if pk else 'Add New Student',
        'brand_context': 'Management',
    })


@login_required
def events_list(request):
    """List all upcoming training events for the user's school."""
    from learning.models import TrainingEvent
    from django.utils import timezone
    events = TrainingEvent.objects.filter(school=request.user.school).order_by('date')
    context = {
        'events': events,
        'brand_context': 'Events',
        'is_live': any(e.date.date() == timezone.now().date() for e in events)
    }
    return render(request, 'learning/events.html', context)


@login_required
def event_upsert(request, pk=None):
    """Create or edit a training event (admin only)."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    event = None
    if pk:
        event = get_object_or_404(TrainingEvent, pk=pk)
        if not request.user.is_superuser and event.school != request.user.school:
            raise PermissionDenied

    if request.method == 'POST':
        title = request.POST.get('title')
        date = request.POST.get('date')
        location = request.POST.get('location') or 'Online - Zoom'
        description = request.POST.get('description')

        if not event:
            event = TrainingEvent.objects.create(
                title=title,
                date=date,
                location=location,
                description=description,
                school=request.user.school
            )
        else:
            event.title = title
            event.date = date
            event.location = location
            event.description = description
            event.save()

        return redirect('dashboard')

    return render(request, 'management/event_form.html', {
        'event': event,
        'page_title': 'Edit Event' if pk else 'Schedule New Event',
        'brand_context': 'Management',
    })


@login_required
def event_delete(request, pk):
    """Delete a training event."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    event = get_object_or_404(TrainingEvent, pk=pk)
    if not request.user.is_superuser and event.school != request.user.school:
        raise PermissionDenied

    event.delete()
    return redirect('dashboard')




@login_required
def course_delete(request, pk):
    """Deactivate a course."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    course = get_object_or_404(Course, pk=pk)
    if not request.user.is_superuser and course.school != request.user.school:
        raise PermissionDenied

    course.is_active = False
    course.save()
    return redirect('dashboard')


@login_required
def school_settings(request):
    """Edit the school settings (brand settings)."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    school = request.user.school
    if not school:
        return redirect('dashboard')

    if request.method == 'POST':
        school.name = request.POST.get('name')
        school.primary_color = request.POST.get('primary_color')
        # school.logo = request.FILES.get('logo') # Could handle files later
        school.save()
        return redirect('dashboard')

    return render(request, 'management/school_form.html', {
        'school': school,
        'page_title': 'Website & School Settings',
        'brand_context': 'Management',
    })


@login_required
def mark_inquiry_paid(request, pk):
    """Mark a service inquiry as paid."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied
    from core.models import ServiceInquiry
    inquiry = get_object_or_404(ServiceInquiry, pk=pk)
    inquiry.is_paid = True
    inquiry.save()
    return redirect('dashboard')


@login_required
def mark_inquiry_status(request, pk, status):
    """Update inquiry status (CONTACTED, RESOLVED, etc.)."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied
    from core.models import ServiceInquiry
    inquiry = get_object_or_404(ServiceInquiry, pk=pk)
    if status in ServiceInquiry.Status.values:
        inquiry.status = status
        inquiry.save()
    return redirect('dashboard')


@login_required
def student_delete(request, pk):
    """Permanently delete a student."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    student = get_object_or_404(CustomUser, pk=pk)
    if not request.user.is_superuser and student.school != request.user.school:
        raise PermissionDenied

    from django.contrib import messages
    try:
        username = student.username
        student.delete()
        messages.success(request, f"Student '{username}' deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting student: {str(e)}")
        
    return redirect('dashboard')


@login_required
def course_upsert(request, pk=None):
    """Create or edit a course (admin only)."""
    from django.contrib import messages
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    course = None
    if pk:
        course = get_object_or_404(Course, pk=pk)
        if not request.user.is_superuser and course.school != request.user.school:
            raise PermissionDenied

    if request.method == 'POST':
        title = request.POST.get('title')
        level = request.POST.get('level', 'A1')
        category = request.POST.get('category', 'GEN')
        duration = request.POST.get('duration')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'
        show_in_catalog = request.POST.get('show_in_catalog') == 'on'
        
        # Handle thumbnail file upload
        thumbnail = request.FILES.get('thumbnail')

        school = request.user.school
        if not school and (request.user.is_superuser or request.user.role in ['SUPERUSER', 'SCHOOL_ADMIN']):
            school = School.objects.first()

        if not school:
             return render(request, 'management/course_form.html', {
                'error': "No school association found. Please create a school first.",
                'course': course,
                'category_choices': Course.CATEGORY_CHOICES,
                'level_choices': Course.LEVEL_CHOICES,
            })

        if not course:
            course = Course.objects.create(
                title=title, school=school, level=level, 
                category=category, duration=duration, 
                description=description, is_active=is_active,
                show_in_catalog=show_in_catalog
            )
        else:
            course.title = title
            course.level = level
            course.category = category
            course.duration = duration
            course.description = description
            course.is_active = is_active
            course.show_in_catalog = show_in_catalog
            
        if thumbnail:
            try:
                # Basic size validation
                if thumbnail.size > 2 * 1024 * 1024:
                    messages.warning(request, "Thumbnail too large (Max 2MB). Resetting to default.")
                else:
                    course.thumbnail = thumbnail
                    course.save()
                    messages.success(request, "Course metadata and thumbnail updated.")
            except Exception as e:
                messages.error(request, f"Error saving thumbnail: {str(e)}")
        
        course.save()
        messages.success(request, f"Course '{course.title}' saved successfully.")
        return redirect('dashboard')

    return render(request, 'management/course_form.html', {
        'course': course,
        'category_choices': Course.CATEGORY_CHOICES,
        'level_choices': Course.LEVEL_CHOICES,
        'page_title': 'Edit Course' if pk else 'Create New Course',
        'brand_context': 'Management',
    })


@login_required
def lesson_upsert(request, pk=None, course_id=None):
    """Create or edit a lesson (admin only)."""
    import os
    from django.contrib import messages
    from learning.models import Lesson, LessonResource
    
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    lesson = None
    if pk:
        lesson = get_object_or_404(Lesson, pk=pk)
        course = lesson.course
    elif course_id:
        course = get_object_or_404(Course, pk=course_id)
    else:
        return redirect('school_settings') # Fallback if no context provided

    if not request.user.is_superuser and course.school != request.user.school:
        raise PermissionDenied

    if request.method == 'POST':
        # Check if we are deleting a resource
        delete_resource_id = request.POST.get('delete_resource')
        if delete_resource_id and lesson:
            try:
                res = get_object_or_404(LessonResource, pk=delete_resource_id, lesson=lesson)
                res_title = res.title
                res.delete()
                messages.success(request, f"Successfully removed resource: {res_title}")
            except Exception as e:
                messages.error(request, f"Failed to delete resource: {str(e)}")
            return redirect('lesson_edit', pk=lesson.pk)

        title = request.POST.get('title')
        lesson_type = request.POST.get('lesson_type')
        description = request.POST.get('description')
        video_url = request.POST.get('video_url', '')
        order = request.POST.get('order', 0)

        # Backend validations
        errors = []
        if not title:
            errors.append("Title is required.")
        elif len(title) > 255:
            errors.append(f"Title is too long ({len(title)} characters). Max limit is 255 characters.")
        
        if len(video_url) > 500:
            errors.append(f"Video URL is too long ({len(video_url)} characters). Max limit is 500 characters.")
        
        try:
            order_int = int(order)
            if order_int < 0:
                errors.append("Sequence number cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Sequence number must be a valid integer.")

        if errors:
            for error in errors:
                messages.error(request, error)
            temp_lesson = lesson or Lesson(course=course)
            temp_lesson.title = title
            temp_lesson.lesson_type = lesson_type
            temp_lesson.description = description
            temp_lesson.video_url = video_url
            try:
                temp_lesson.order = int(order)
            except Exception:
                temp_lesson.order = 0
            
            return render(request, 'management/lesson_form.html', {
                'lesson': temp_lesson,
                'course': course,
                'lesson_types': Lesson.LessonType.choices,
                'page_title': 'Edit Lesson' if pk else 'Add Lesson',
                'brand_context': 'Management',
            })

        try:
            if not lesson:
                lesson = Lesson.objects.create(
                    course=course, title=title, lesson_type=lesson_type,
                    description=description, order=order, video_url=video_url
                )
            else:
                lesson.title = title
                lesson.lesson_type = lesson_type
                lesson.description = description
                lesson.video_url = video_url
                lesson.order = order
                lesson.save()
        except Exception as e:
            messages.error(request, f"Database error when saving lesson: {str(e)}")
            temp_lesson = lesson or Lesson(course=course)
            temp_lesson.title = title
            temp_lesson.lesson_type = lesson_type
            temp_lesson.description = description
            temp_lesson.video_url = video_url
            try:
                temp_lesson.order = int(order)
            except Exception:
                temp_lesson.order = 0
            
            return render(request, 'management/lesson_form.html', {
                'lesson': temp_lesson,
                'course': course,
                'lesson_types': Lesson.LessonType.choices,
                'page_title': 'Edit Lesson' if pk else 'Add Lesson',
                'brand_context': 'Management',
            })

        # Handle Material Upload
        lesson_material = request.FILES.get('lesson_material')
        lesson_material_url = request.POST.get('lesson_material_url', '').strip()
        lesson_material_title = request.POST.get('lesson_material_title', '').strip()

        if lesson_material:
            try:
                ext = os.path.splitext(lesson_material.name)[1].lower()
                
                # Surgical Type Detection & Mismatch Warning
                resource_type = 'DOC'
                is_mismatch = False
                
                if ext in ['.mp4', '.mov', '.avi', '.wmv']:
                    resource_type = 'VID' 
                    if lesson_type != 'VID':
                        is_mismatch = True
                        messages.warning(request, f"Note: You uploaded a video file ({ext}) to a non-video lesson type. It has been processed, but please verify.")
                elif ext not in ['.pdf', '.doc', '.docx', '.zip', '.txt']:
                    if lesson_type == 'DOC':
                        is_mismatch = True
                        messages.warning(request, f"Warning: Unrecognized file extension ({ext}). Material saved, but may not render correctly for students.")

                # Atomic creation with fault tolerance
                LessonResource.objects.create(
                    lesson=lesson,
                    title=lesson_material_title or lesson_material.name,
                    resource_type=resource_type,
                    file=lesson_material
                )
                
                if not is_mismatch:
                    messages.success(request, f"Successfully uploaded: {lesson_material.name}")

            except Exception as e:
                messages.error(request, f"Failed to process material upload: {str(e)}. Lesson saved without material.")

        elif lesson_material_url:
            try:
                # Default title logic
                title_val = lesson_material_title or "Study Material Link"
                
                # Determine type
                resource_type = 'URL'
                if any(x in lesson_material_url.lower() for x in ['.mp4', '.mov', '.avi', 'youtube.com', 'youtu.be', 'vimeo.com']):
                    resource_type = 'VID'
                elif any(x in lesson_material_url.lower() for x in ['.pdf', '.doc', '.docx', '.zip']):
                    resource_type = 'DOC'
                
                LessonResource.objects.create(
                    lesson=lesson,
                    title=title_val,
                    resource_type=resource_type,
                    url=lesson_material_url
                )
                messages.success(request, f"Successfully linked resource: {title_val}")
            except Exception as e:
                messages.error(request, f"Failed to link material URL: {str(e)}")

        return redirect('course_detail', pk=course.pk)

    return render(request, 'management/lesson_form.html', {
        'lesson': lesson,
        'course': course,
        'lesson_types': Lesson.LessonType.choices,
        'page_title': 'Edit Lesson' if pk else 'Add Lesson',
        'brand_context': 'Management',
    })


@login_required
def lesson_delete(request, pk):
    """Delete a lesson (admin only)."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied
    
    lesson = get_object_or_404(Lesson, pk=pk)
    course_pk = lesson.course.pk
    
    if not request.user.is_superuser and lesson.course.school != request.user.school:
        raise PermissionDenied
    
    if request.method == 'POST':
        lesson.delete()
        return redirect('course_detail', pk=course_pk)
    
    return redirect('course_detail', pk=course_pk)


@login_required
def activity_upsert(request, pk=None, lesson_id=None):
    """Create or edit a lesson activity (admin only)."""
    from learning.models import LessonActivity
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    activity = None
    if pk:
        activity = get_object_or_404(LessonActivity, pk=pk)
        lesson = activity.lesson
    elif lesson_id:
        lesson = get_object_or_404(Lesson, pk=lesson_id)
    else:
        return redirect('school_settings')

    if not request.user.is_superuser and lesson.course.school != request.user.school:
        raise PermissionDenied

    if request.method == 'POST':
        title = request.POST.get('title')
        activity_type = request.POST.get('activity_type')
        description = request.POST.get('description')
        order = request.POST.get('order', 0)

        if not activity:
            LessonActivity.objects.create(
                lesson=lesson, title=title, activity_type=activity_type,
                description=description, order=order
            )
        else:
            activity.title = title
            activity.activity_type = activity_type
            activity.description = description
            activity.order = order
            activity.save()

        return redirect('lesson_edit', pk=lesson.pk)

    return render(request, 'management/activity_form.html', {
        'activity': activity,
        'lesson': lesson,
        'activity_types': LessonActivity.ActivityType.choices,
        'page_title': 'Edit Activity' if pk else 'Add Activity',
        'brand_context': 'Management',
    })


@login_required
def activity_delete(request, pk):
    """Delete an activity (admin only)."""
    from learning.models import LessonActivity
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied
    
    activity = get_object_or_404(LessonActivity, pk=pk)
    lesson_pk = activity.lesson.pk
    
    if not request.user.is_superuser and activity.lesson.course.school != request.user.school:
        raise PermissionDenied
    
    if request.method == 'POST':
        activity.delete()
        return redirect('lesson_edit', pk=lesson_pk)
    
    return redirect('lesson_edit', pk=lesson_pk)


@login_required
def event_upsert(request, pk=None):
    """Create or edit a training event (admin only)."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    event = None
    if pk:
        event = get_object_or_404(TrainingEvent, pk=pk)
        if not request.user.is_superuser and event.school != request.user.school:
            raise PermissionDenied

    if request.method == 'POST':
        title = request.POST.get('title')
        date = request.POST.get('date')
        location = request.POST.get('location')
        description = request.POST.get('description')

        school = request.user.school
        if not school and (request.user.is_superuser or request.user.role in ['SUPERUSER', 'SCHOOL_ADMIN']):
            school = School.objects.first()

        if not event:
            TrainingEvent.objects.create(
                title=title, school=school,
                date=date, location=location, description=description
            )
        else:
            event.title = title
            event.date = date
            event.location = location
            event.description = description
            event.save()

        return redirect('events_list')

    return render(request, 'management/event_form.html', {
        'event': event,
        'page_title': 'Edit Event' if pk else 'Schedule Training Event',
        'brand_context': 'Management',
    })


@login_required
def activity_review_list(request):
    """List all student activity submissions for the school's admin to review."""
    from learning.models import ActivitySubmission
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    # Filter submissions for courses belonging to this admin's school
    school = request.user.school
    if not school:
        from core.models import School
        school = School.objects.first()

    submissions = ActivitySubmission.objects.filter(
        activity__lesson__course__school=school
    ).order_by('-submitted_at')

    if request.user.is_superuser:
        submissions = ActivitySubmission.objects.all().order_by('-submitted_at')

    return render(request, 'management/activity_review_list.html', {
        'submissions': submissions,
        'page_title': 'Activity Review Hub',
        'brand_context': 'Management',
    })


@login_required
def activity_review_detail(request, pk):
    """Review and grade a specific student submission."""
    from learning.models import ActivitySubmission
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    submission = get_object_or_404(ActivitySubmission, pk=pk)
    
    if not request.user.is_superuser and submission.activity.lesson.course.school != request.user.school:
        raise PermissionDenied

    if request.method == 'POST':
        status = request.POST.get('status')
        feedback = request.POST.get('feedback')
        grade = request.POST.get('grade')

        submission.status = status
        submission.feedback = feedback
        if grade:
            submission.grade = int(grade)
        submission.save()
        
        return redirect('activity_review_list')

    return render(request, 'management/activity_review_detail.html', {
        'submission': submission,
        'page_title': f'Review: {submission.user.username}',
        'brand_context': 'Management',
    })


@login_required
def course_roster(request, pk):
    """View a list of students enrolled in a specific course."""
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    course = get_object_or_404(Course, pk=pk)
    
    if not request.user.is_superuser and course.school != request.user.school:
        raise PermissionDenied

    enrollments = CourseEnrollment.objects.filter(
        course=course
    ).select_related('user').order_by('user__username')

    enrolled_count = enrollments.filter(status__in=['ENROLLED', 'IN_PROGRESS', 'COMPLETED']).count()
    pending_count = enrollments.filter(status='PENDING').count()

    return render(request, 'management/course_roster.html', {
        'course': course,
        'enrollments': enrollments,
        'enrolled_count': enrolled_count,
        'pending_count': pending_count,
        'page_title': f'Roster: {course.title}',
        'brand_context': 'Management',
    })


@login_required
def quiz_studio(request, pk):
    """A dedicated workspace for admins to manually build and edit quizzes."""
    from learning.models import Lesson, QuizQuestion, QuizChoice
    
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    lesson = get_object_or_404(Lesson, pk=pk)
    if lesson.lesson_type != 'QIZ':
        return redirect('lesson_edit', pk=lesson.pk)
    
    if not request.user.is_superuser and lesson.course.school != request.user.school:
        raise PermissionDenied

    if request.method == 'POST':
        # Safely handle the integer conversion
        try:
            d_min = request.POST.get('duration_minutes', '30')
            lesson.duration_minutes = int(d_min) if d_min.isdigit() else 30
        except (ValueError, TypeError):
            lesson.duration_minutes = 30
            
        lesson.is_final_exam = request.POST.get('is_final_exam') == 'on'
        lesson.save()
        from django.contrib import messages
        messages.success(request, "Quiz settings updated successfully.")
        return redirect('quiz_studio', pk=lesson.pk)

    questions = lesson.questions.all().prefetch_related('choices')
    
    return render(request, 'management/quiz_studio.html', {
        'lesson': lesson,
        'questions': questions,
        'page_title': f'Quiz Studio: {lesson.title}',
        'brand_context': 'Management',
    })


@login_required
@require_POST
def quiz_question_add(request, pk):
    from learning.models import Lesson, QuizQuestion
    from django.contrib import messages
    lesson = get_object_or_404(Lesson, pk=pk)
    text = request.POST.get('text', 'New Question')
    
    image = request.FILES.get('image')
    audio = request.FILES.get('audio')
    video_url = request.POST.get('video_url', '').strip()

    # Size validations
    if image and image.size > 2 * 1024 * 1024:
        messages.error(request, "Image size exceeds 2MB limit. Question was not created.")
        return redirect('quiz_studio', pk=lesson.pk)

    if audio and audio.size > 5 * 1024 * 1024:
        messages.error(request, "Audio size exceeds 5MB limit. Question was not created.")
        return redirect('quiz_studio', pk=lesson.pk)

    QuizQuestion.objects.create(
        lesson=lesson, 
        text=text, 
        order=lesson.questions.count() + 1,
        image=image,
        audio=audio,
        video_url=video_url if video_url else None
    )
    messages.success(request, "Question added successfully.")
    return redirect('quiz_studio', pk=lesson.pk)


@login_required
@require_POST
def quiz_question_delete(request, pk):
    from learning.models import QuizQuestion
    question = get_object_or_404(QuizQuestion, pk=pk)
    lesson_id = question.lesson_id
    question.delete()
    return redirect('quiz_studio', pk=lesson_id)


@login_required
@require_POST
def quiz_choice_add(request, pk):
    from learning.models import QuizQuestion, QuizChoice
    question = get_object_or_404(QuizQuestion, pk=pk)
    text = request.POST.get('text', 'New Answer')
    is_correct = 'is_correct' in request.POST
    
    if is_correct:
        question.choices.update(is_correct=False)
    QuizChoice.objects.create(question=question, text=text, is_correct=is_correct)
    return redirect('quiz_studio', pk=question.lesson.pk)


@login_required
@require_POST
def quiz_choice_delete(request, pk):
    from learning.models import QuizChoice
    choice = get_object_or_404(QuizChoice, pk=pk)
    lesson_id = choice.question.lesson_id
    choice.delete()
    return redirect('quiz_studio', pk=lesson_id)


@login_required
def bulk_enroll(request, pk):
    """Enroll multiple students into a course simultaneously."""
    from django.contrib import messages
    from django.db.models import Q
    from users.models import CustomUser
    from learning.models import Course, CourseEnrollment
    
    course = get_object_or_404(Course, pk=pk)
    
    if request.user.role not in ['SCHOOL_ADMIN', 'SUPERUSER']:
        raise PermissionDenied

    if request.method == 'POST':
        student_data = request.POST.get('student_list', '')
        # Handle commas, newlines, and spaces
        import re
        entries = re.split(r'[,\n\r\s]+', student_data)
        entries = [e.strip() for e in entries if e.strip()]
        
        success_count = 0
        skipped_count = 0
        
        for entry in entries:
            # Find user by email or username within the same school or if guest
            student = CustomUser.objects.filter(
                Q(email__iexact=entry) | Q(username__iexact=entry),
                role__in=['STUDENT', 'GUEST']
            ).first()
            
            # Auto-assign school if it matches or is null
            if student:
                if not student.school:
                    student.school = course.school
                    student.role = 'STUDENT' # Upgrade to student if was guest
                    student.save()
                
                if student.school == course.school:
                    enrollment, created = CourseEnrollment.objects.get_or_create(
                        user=student,
                        course=course,
                        defaults={'status': 'ENROLLED'}
                    )
                    if created:
                        success_count += 1
                    else:
                        skipped_count += 1
                else:
                    skipped_count += 1
            else:
                skipped_count += 1
        
        messages.success(request, f"Bulk Enrollment Complete: {success_count} students enrolled, {skipped_count} entries skipped.")
        return redirect('course_roster', pk=course.pk)

    return render(request, 'management/bulk_enroll.html', {
        'course': course,
        'page_title': 'Bulk Enrollment',
        'brand_context': 'Management'
    })


@login_required
def student_detail_api(request, pk):
    from django.http import JsonResponse
    if not (request.user.is_superuser or request.user.role in ['SUPERUSER', 'SCHOOL_ADMIN']):
        raise PermissionDenied("Only admins can access student detail metrics.")

    student = get_object_or_404(CustomUser, pk=pk)
    
    from learning.models import CourseEnrollment, LessonCompletion, Lesson, ActivitySubmission
    from quiz.models import QuizAttempt

    enrollments = CourseEnrollment.objects.filter(user=student).select_related('course').order_by('-enrolled_at')
    
    enrollment_data = []
    for en in enrollments:
        total_lessons = Lesson.objects.filter(course=en.course).count()
        completed_completions = LessonCompletion.objects.filter(user=student, lesson__course=en.course).select_related('lesson').order_by('completed_at')
        completed_count = completed_completions.count()
        progress_pct = int((completed_count / total_lessons * 100)) if total_lessons > 0 else 0

        lesson_history = []
        for comp in completed_completions:
            lesson_history.append({
                'title': comp.lesson.title,
                'completed_at': comp.completed_at.strftime('%d %b %Y, %H:%M') if comp.completed_at else 'Completed'
            })

        enrollment_data.append({
            'course_id': en.course.id,
            'course_title': en.course.title,
            'course_level': en.course.get_level_display(),
            'status': en.status,
            'status_display': en.get_status_display(),
            'admin_note': en.admin_note or '',
            'enrolled_at': en.enrolled_at.strftime('%d %b %Y, %H:%M') if en.enrolled_at else '',
            'total_lessons': total_lessons,
            'completed_lessons_count': completed_count,
            'progress_pct': progress_pct,
            'completed_lessons': lesson_history,
        })

    # Quiz Attempts
    attempts = QuizAttempt.objects.filter(user=student).select_related('quiz').order_by('-completed_at')[:10]
    quiz_data = []
    for att in attempts:
        quiz_data.append({
            'quiz_title': att.quiz.title if att.quiz else 'Quiz',
            'score': att.score,
            'total_possible': att.total_possible,
            'percentage': round((att.score / att.total_possible * 100), 1) if att.total_possible else 0,
            'completed_at': att.completed_at.strftime('%d %b %Y, %H:%M') if att.completed_at else ''
        })

    # Activity Submissions
    submissions = ActivitySubmission.objects.filter(user=student).select_related('activity').order_by('-submitted_at')[:10]
    submission_data = []
    for sub in submissions:
        submission_data.append({
            'activity_title': sub.activity.title,
            'status': sub.status,
            'status_display': sub.get_status_display(),
            'grade': sub.grade or '',
            'submitted_at': sub.submitted_at.strftime('%d %b %Y, %H:%M') if sub.submitted_at else ''
        })

    return JsonResponse({
        'success': True,
        'student': {
            'id': student.id,
            'username': student.username,
            'email': student.email,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'date_joined': student.date_joined.strftime('%d %b %Y'),
            'role': student.role,
            'is_active': student.is_active,
        },
        'enrollments': enrollment_data,
        'quizzes': quiz_data,
        'submissions': submission_data,
    })

