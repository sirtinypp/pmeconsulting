from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from .forms import StudentSignUpForm
from .models import CustomUser


class StudentLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['login_type'] = 'student'
        ctx['page_title'] = 'Student Login'
        return ctx


class AdminLoginView(LoginView):
    template_name = 'registration/admin_login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['login_type'] = 'admin'
        ctx['page_title'] = 'Admin Portal'
        return ctx


class StudentSignUpView(CreateView):
    model = CustomUser
    form_class = StudentSignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        from core.models import ServiceInquiry
        user = form.save()
        interest = form.cleaned_data.get('primary_interest')
        
        # Auto-create lead inquiry for the admin dashboard context
        if interest:
            ServiceInquiry.objects.create(
                user=user,
                name=f"{user.first_name} {user.last_name}",
                email=user.email,
                service_requested=interest,
                status=ServiceInquiry.Status.PENDING
            )
            
        login(self.request, user)
        return redirect(self.success_url)


class UpgradeToStudentView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/upgrade.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from learning.models import Course, CourseEnrollment
        active_courses = Course.objects.filter(is_active=True)
        
        # Map each level to its active course
        level_courses = {}
        for level in ['A1', 'A2', 'B1', 'B2', 'C1']:
            course = active_courses.filter(level=level).first()
            if course:
                level_courses[level] = course.id

        # Check user's active enrollments
        enrolled_ids = list(CourseEnrollment.objects.filter(
            user=self.request.user,
            status__in=['ENROLLED', 'IN_PROGRESS', 'COMPLETED']
        ).values_list('course_id', flat=True))

        context['level_courses_json'] = level_courses
        context['enrolled_course_ids'] = enrolled_ids
        return context

    def post(self, request, *args, **kwargs):
        # Simulated Payment/Upgrade Success
        user = request.user
        user.role = CustomUser.Role.STUDENT
        user.save()
        return redirect('dashboard')
