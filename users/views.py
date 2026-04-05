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
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)


class UpgradeToStudentView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/upgrade.html'

    def post(self, request, *args, **kwargs):
        # Simulated Payment/Upgrade Success
        user = request.user
        user.role = CustomUser.Role.STUDENT
        user.save()
        return redirect('dashboard')
