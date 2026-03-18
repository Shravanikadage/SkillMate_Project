from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Course



# Home
def home(request):
    return render(request, 'home.html')


# Register
def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        # ✅ Create Django User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )

    
        UserProfile.objects.create(
            full_name=full_name,
            email=email
        )

        messages.success(request, 'Registration successful!')
        return redirect('login')

    return render(request, 'register.html')


# Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


# Dashboard
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

# Logout
def user_logout(request):
    logout(request)
    return redirect('home')

# Course
def course_list(request):
    courses = Course.objects.all()
    return render(request, "course.html", {"courses": courses})

def course_detail(request, id):
    course = get_object_or_404(Course, id=id)
    return render(request, 'course_detail.html', {'course': course})