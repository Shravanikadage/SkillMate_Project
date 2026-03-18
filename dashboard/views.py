from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Course, Enrollment, Lesson, LessonProgress, Certificate

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor
from django.conf import settings
import os
from datetime import date 
from reportlab.lib.utils import ImageReader



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

        # Create Django User
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

    total_courses = Course.objects.count()

    enrolled_courses = Enrollment.objects.filter(user=request.user)

    recent_enrollments = enrolled_courses.order_by('-enrolled_at')[:5]

    progress_data = []

    completed_courses = 0   # NEW

    for enroll in enrolled_courses:
        course = enroll.course

        total_lessons = Lesson.objects.filter(course=course).count()

        completed = LessonProgress.objects.filter(
            user=request.user,
            lesson__course=course,
            completed=True
        ).count()

        percent = 0
        if total_lessons > 0:
            percent = int((completed / total_lessons) * 100)

        # check completed course
        if percent == 100:
            completed_courses += 1

        progress_data.append({
            "course": course,
            "completed": completed,
            "total": total_lessons,
            "percent": percent
        })

    context = {
        'enrolled_count': enrolled_courses.count(),
        'total_courses': total_courses,
        'recent_enrollments': recent_enrollments,
        'progress_data': progress_data,
        'completed_courses': completed_courses   # NEW
    }

    return render(request, 'dashboard.html', context)

@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user)

    return render(request, "my_courses.html", {
        "enrollments": enrollments
    })

# Logout
def user_logout(request):
    logout(request)
    return redirect('home')

# Course
def course_list(request):
    courses = Course.objects.all()
    return render(request, "course.html", {"courses": courses})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment, Lesson, LessonProgress, Certificate

def course_detail(request, id):
    course = get_object_or_404(Course, id=id)

    # Count total students enrolled in this course
    student_count = Enrollment.objects.filter(course=course).count()

    is_enrolled = False
    completed_lessons = []
    progress = 0
    certificate_exists = False
    lessons = []

    # Check if user is logged in
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()

        # Fetch lessons only if enrolled
        if is_enrolled:
            lessons = Lesson.objects.filter(course=course)

            completed_lessons = LessonProgress.objects.filter(
                user=request.user,
                lesson__course=course,
                completed=True
            ).values_list("lesson_id", flat=True)

            total_lessons = lessons.count()
            completed_count = len(completed_lessons)

            if total_lessons > 0:
                progress = int((completed_count / total_lessons) * 100)

            # Check if certificate exists
            certificate_exists = Certificate.objects.filter(user=request.user, course=course).exists()

    context = {
        'course': course,
        'student_count': student_count,
        'is_enrolled': is_enrolled,
        'lessons': lessons,
        'completed_lessons': completed_lessons,
        'progress': progress,
        'certificate_exists': certificate_exists
    }

    return render(request, 'course_detail.html', context)


# Enroll
@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        # Create enrollment
        Enrollment.objects.create(
            user=request.user,
            course=course
        )
        return redirect('my_courses')

    return render(request, 'enroll.html', {'course': course})


@login_required
def course_detail(request, id):

    course = get_object_or_404(Course, id=id)

    lessons = Lesson.objects.filter(course=course)

    student_count = Enrollment.objects.filter(course=course).count()

    is_enrolled = Enrollment.objects.filter(
        user=request.user,
        course=course
    ).exists()

    completed_lessons = LessonProgress.objects.filter(
        user=request.user,
        lesson__course=course,
        completed=True
    ).values_list("lesson_id", flat=True)

    total_lessons = lessons.count()
    completed_count = len(completed_lessons)

    progress = 0
    if total_lessons > 0:
        progress = int((completed_count / total_lessons) * 100)

    # certificate check
    certificate_exists = Certificate.objects.filter(
        user=request.user,
        course=course
    ).exists()

    return render(request, 'course_detail.html', {
        'course': course,
        'lessons': lessons,
        'student_count': student_count,
        'is_enrolled': is_enrolled,
        'completed_lessons': completed_lessons,
        'progress': progress,
        'certificate_exists': certificate_exists
    })

@login_required
def complete_lesson(request, lesson_id):

    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    # Check if user is enrolled in the course
    enrolled = Enrollment.objects.filter(
        user=request.user,
        course=course
    ).exists()

    if not enrolled:
        messages.error(request, "You must enroll in the course first.")
        return redirect('course_detail', id=course.id)

    # Mark lesson as completed
    progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )

    if not progress.completed:
        progress.completed = True
        progress.save()

    # Check course completion
    total_lessons = Lesson.objects.filter(course=course).count()

    completed_lessons = LessonProgress.objects.filter(
        user=request.user,
        lesson__course=course,
        completed=True
    ).count()

    # If all lessons completed → create certificate
    if total_lessons == completed_lessons and total_lessons > 0:
        Certificate.objects.get_or_create(
            user=request.user,
            course=course
        )

    return redirect('course_detail', id=course.id)


@login_required
def certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="SkillMate_Certificate.pdf"'

    # Landscape certificate
    p = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Equal top and bottom margin
    margin = 80 

    # Border
    p.setStrokeColor(HexColor("#1a548e"))
    p.setLineWidth(4)
    p.rect(margin/2, margin/2, width-margin, height-margin)

    # Graduation cap image path
    grad_cap_path = os.path.join(settings.BASE_DIR, "static", "images", "logo.png")
    grad_cap = ImageReader(str(grad_cap_path))

    # SkillMate Text and Logo aligned
    p.setFont("Helvetica-Bold", 30)
    p.setFillColor(HexColor("#ff7a00"))

    text = "SkillMate"
    text_width = p.stringWidth(text, "Helvetica-Bold", 30)  # text width

    # Logo dimensions
    logo_width = 40
    logo_height = 40
    logo_x = (width - (logo_width + 10 + text_width)) / 2  # center combined
    logo_y = height - margin - 55  # align vertically with text

    # Draw logo
    p.drawImage(grad_cap, logo_x, logo_y, width=logo_width, height=logo_height, mask='auto')

    # Draw text next to logo
    p.drawString(logo_x + logo_width + 10, height - margin - 50, text)

    # Certificate title
    p.setFont("Helvetica-Bold", 25)
    p.setFillColor(HexColor("#000000"))
    p.drawCentredString(width/2, height - margin - 120, "Certificate of Completion")

    # Presented text
    p.setFont("Helvetica", 16)
    p.drawCentredString(width/2, height - margin - 170, "This certificate is proudly presented to")

    # Student Name
    p.setFont("Helvetica-Bold", 28)
    p.setFillColor(HexColor("#1a548e"))
    p.drawCentredString(width/2, height - margin - 220, user.first_name)

    # Completion text
    p.setFont("Helvetica", 18)
    p.setFillColor(HexColor("#000000"))
    p.drawCentredString(width/2, height - margin - 270, "for successfully completing the course")

    # Course Name
    p.setFont("Helvetica-Bold", 22)
    p.setFillColor(HexColor("#1a548e"))
    p.drawCentredString(width/2, height - margin - 310, course.title)

    # Date
    today = date.today().strftime("%d %B %Y")
    p.setFont("Helvetica", 16)
    p.setFillColor(HexColor("#000000"))
    p.drawCentredString(width/2, height - margin - 360, f"Issued on {today}")

    # Signature Image Path
    signature_path = os.path.join(settings.BASE_DIR, "static", "images", "signature.png")
    signature = ImageReader(signature_path)

    # Draw Signature slightly more to the right
    signature_x = width - 250  
    signature_y = margin + 40  

    p.drawImage(
        signature,
        signature_x,
        signature_y,
        width=150,
        height=60,
        mask='auto'
    )

    # Signature Text
    p.setFont("Helvetica", 14)
    p.drawCentredString(signature_x + 75, margin + 20, "Instructor Signature")

    p.showPage()
    p.save()

    return response

import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import Course

def checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    payment = client.order.create({
        "amount": int(course.price * 100),  # amount in paise
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "course": course,
        "order_id": payment['id'],
        "razorpay_key": settings.RAZORPAY_KEY_ID
    }

    return render(request, "checkout.html", context)


from django.http import HttpResponse

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment

@login_required
def payment_success(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    return redirect('enroll', course_id=course.id)

    