from django.contrib import admin
from .models import UserProfile, Course, Enrollment, Lesson, LessonProgress, Certificate


admin.site.register(UserProfile)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Lesson)
admin.site.register(LessonProgress)
admin.site.register(Certificate)