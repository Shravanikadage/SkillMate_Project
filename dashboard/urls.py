from django.urls import path
from .import views

urlpatterns = [
    path('',views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('course/', views.course_list, name='course'),
    path('course/<int:id>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll'),
    path('complete-lesson/<int:lesson_id>/', views.complete_lesson, name='complete_lesson'),
    path('certificate/<int:course_id>/', views.certificate, name='certificate'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('checkout/<int:course_id>/', views.checkout, name='checkout'),
    path('success/<int:course_id>/', views.payment_success, name='payment_success'),
]