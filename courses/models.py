import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import User


from django.contrib.auth.models import AbstractUser
from django.db import models

# class CustomUser(AbstractUser):
#     email = models.EmailField(unique=True)  # Сделаем email уникальным и обязательным

class CoursesModels(models.Model):
    name = models.CharField(max_length=55)
    requirements = models.CharField(max_length=80)
    description = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.name}"



class LessonCourses(models.Model):
    course = models.ForeignKey(CoursesModels, related_name='lessons', on_delete=models.CASCADE)
    lesson_id = models.IntegerField(editable=False)  # Сделаем поле не редактируемым
    title = models.CharField(max_length=100)
    content = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'lesson_id'], name='unique_course_lesson')
        ]

    def save(self, *args, **kwargs):
        if not self.lesson_id:
            last_lesson = LessonCourses.objects.filter(course=self.course).order_by('lesson_id').last()
            self.lesson_id = last_lesson.lesson_id + 1 if last_lesson else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"





class TestModel(models.Model):
    lesson = models.ForeignKey(LessonCourses,related_name='tests',on_delete=models.CASCADE)
    test_id = models.IntegerField(editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    question_count = models.PositiveIntegerField(default=0)  # Новое поле для количества вопросов

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['lesson', 'test_id'], name='unique_lesson_test')
        ]

    def save(self, *args, **kwargs):
        if not self.test_id:
            # Получаем максимальное значение test_id для данного урока
            last_test = TestModel.objects.filter(lesson=self.lesson).order_by('test_id').last()
            self.test_id = last_test.test_id + 1 if last_test else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name




User = get_user_model()

class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('CoursesModels', on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    certificate_code = models.CharField(max_length=50, unique=True)
    pdf = models.FileField(upload_to='certificates/', null=True, blank=True)

    def __str__(self):
        return f"Certificate for {self.user.username} - {self.course.name}"





class Review(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    courses = models.ForeignKey(CoursesModels, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)




class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(CoursesModels,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


