from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


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
