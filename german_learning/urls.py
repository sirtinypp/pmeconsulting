from django.contrib import admin
from django.urls import path, include
from core import views as dashboard_views
from core.public_views import public_index, book_service, book_service_success
from users import views as user_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', public_index, name='public_index'),
    path('services/book/', book_service, name='book_service'),
    path('services/success/', book_service_success, name='book_service_success'),
    path('dashboard/', dashboard_views.dashboard, name='dashboard'),
    path('events/', dashboard_views.events_list, name='events_list'),
    path('learning/', include('learning.urls')),
    path('resources/', include('resources.urls')),
    path('management/student/add/', dashboard_views.student_upsert, name='student_add'),
    path('management/student/<int:pk>/edit/', dashboard_views.student_upsert, name='student_edit'),
    path('management/student/<int:pk>/delete/', dashboard_views.student_delete, name='student_delete'),
    path('management/course/add/', dashboard_views.course_upsert, name='course_add'),
    path('management/course/<int:pk>/edit/', dashboard_views.course_upsert, name='course_edit'),
    path('management/course/<int:course_id>/lesson/add/', dashboard_views.lesson_upsert, name='lesson_add'),
    path('management/lesson/<int:pk>/edit/', dashboard_views.lesson_upsert, name='lesson_edit'),
    path('management/event/add/', dashboard_views.event_upsert, name='event_add'),
    path('management/event/<int:pk>/edit/', dashboard_views.event_upsert, name='event_edit'),
    path('accounts/login/', include([
        path('', user_views.StudentLoginView.as_view(), name='login'),
        path('admin/', user_views.AdminLoginView.as_view(), name='admin_login'),
    ])),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
