from django.contrib import admin
from .models import CoursesModels, LessonCourses, TestModel, Certificate


@admin.register(CoursesModels)
class CoursesAdmin(admin.ModelAdmin):
    list_display = ('name', 'requirements', 'description', 'price')

@admin.register(LessonCourses)
class LessonCoursesAdmin(admin.ModelAdmin):
    list_display = ('course', 'lesson_id', 'title', 'content')
    list_filter = ('course', 'lesson_id')
    search_fields = ('title', 'content')


@admin.register(TestModel)
class TestModelAdmin(admin.ModelAdmin):
    list_display = ('name','description')

@admin.register(Certificate)
class CertificatesAdmin(admin.ModelAdmin):
    list_display = ('id','user','course')
