from rest_framework import serializers

from courses.models import CoursesModels, LessonCourses, TestModel, Certificate, Review, Certificate, Purchase


class LessonSerializers(serializers.ModelSerializer):
    class Meta:
        model = LessonCourses
        fields = "__all__"

class CoursesSerializers(serializers.ModelSerializer):
    lessons = LessonSerializers(many=True, read_only=True)
    class Meta:
        model = CoursesModels
        fields = "__all__"



class TestSerializers(serializers.ModelSerializer):
    class Meta:
        model = TestModel
        fields = "__all__"


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'
        read_only_fields = ('id', 'issue_date', 'certificate_code')



class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'user', 'courses', 'content', 'rating', 'created_at')
        read_only_fields = ('id', 'created_at')  # Добавляем created_at в read_only_fields



class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'


