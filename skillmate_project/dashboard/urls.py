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
]