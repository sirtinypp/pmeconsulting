from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    path('approve-enrollment/<int:pk>/', views.approve_enrollment, name='approve_enrollment'),
    path('reject-enrollment/<int:pk>/', views.reject_enrollment, name='reject_enrollment'),
    path('lesson/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:pk>/complete/', views.complete_lesson, name='complete_lesson'),
    path('activity/<int:pk>/submit/', views.submit_activity, name='submit_activity'),
    path('checkout/<int:course_id>/<str:tier_type>/', views.initiate_checkout, name='initiate_checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment/webhook/', views.paymongo_webhook, name='paymongo_webhook'),
]

