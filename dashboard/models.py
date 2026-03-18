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
    

# -----------------------------
# Enrollment Model
# -----------------------------
class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    

# -----------------------------
# Lesson Model (Video Lessons)
# -----------------------------
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_url = models.URLField()

    def get_embed_url(self):
        if "youtube.com/watch?v=" in self.video_url:
            video_id = self.video_url.split("watch?v=")[1]
            return f"https://www.youtube.com/embed/{video_id}"
        elif "youtu.be/" in self.video_url:
            video_id = self.video_url.split("youtu.be/")[1]
            return f"https://www.youtube.com/embed/{video_id}"
        return self.video_url
    

# -----------------------------
# Progress Model
# -----------------------------
class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"
    
    
# -----------------------------
# Certificate Model
# -----------------------------
class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"