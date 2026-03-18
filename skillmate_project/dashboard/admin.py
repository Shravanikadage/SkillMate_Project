from django.contrib import admin
from .models import UserProfile, Course


admin.site.register(UserProfile)
admin.site.register(Course)