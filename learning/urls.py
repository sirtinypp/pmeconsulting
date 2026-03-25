from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    path('approve-enrollment/<int:pk>/', views.approve_enrollment, name='approve_enrollment'),
    path('reject-enrollment/<int:pk>/', views.reject_enrollment, name='reject_enrollment'),
    path('lesson/<int:pk>/complete/', views.complete_lesson, name='complete_lesson'),
]
