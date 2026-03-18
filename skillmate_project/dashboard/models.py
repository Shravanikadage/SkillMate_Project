from django.db import models
from django.contrib.auth.models import User


# -----------------------------
# User Profile Model
# -----------------------------
class UserProfile(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
   
    def __str__(self):
        return self.full_name


# -----------------------------
# Course Model (Admin Only)
# -----------------------------
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title