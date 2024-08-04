import uuid
from io import BytesIO
import logging
from django.core.files.base import ContentFile
from django_filters import filters
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from .models import CoursesModels, LessonCourses, TestModel, Certificate, Review, Certificate, Purchase
from .serializers import CoursesSerializers, LessonSerializers, TestSerializers, CertificateSerializer, \
    ReviewSerializer, PurchaseSerializer
from rest_framework.permissions import IsAuthenticated
from courses.filters import CoursesFilter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .utils import send_confirmation_email

logger = logging.getLogger(__name__)
def generate_certificate_pdf(certificate):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "Certificate of Completion")
    p.drawString(100, 700, f"Presented to {certificate.user.username}")
    p.drawString(100, 650, f"For successfully completing the course {certificate.course.name}")
    p.drawString(100, 600, f"Issue Date: {certificate.issue_date.strftime('%Y-%m-%d')}")
    p.drawString(100, 550, f"Certificate Code: {certificate.certificate_code}")
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    return ContentFile(pdf)

class CoursesViews(viewsets.ModelViewSet):
    queryset = CoursesModels.objects.all()
    serializer_class = CoursesSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['description']
    permission_classes = [IsAuthenticated, ]
    filterset_class = CoursesFilter

    @action(detail=True, methods=['post'])
    def buy(self, request, pk=None):
        course = self.get_object()
        user = request.user

        # Создаем запись о покупке
        Purchase.objects.create(user=user, course=course)

        # Отправляем email
        send_confirmation_email(user.email, course.name)

        return Response({'message': 'Покупка успешно завершена и подтверждение отправлено на ваш email.'},
                        status=status.HTTP_200_OK)


class LessonCoursesViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializers

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        if not course_id:
            raise NotFound("Не указан идентификатор курса")
        queryset = LessonCourses.objects.filter(course_id=course_id)
        lesson_id = self.kwargs.get('pk')
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
        return queryset

    def create(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')
        lesson_id = request.data.get('lesson_id')

        if LessonCourses.objects.filter(course_id=course_id, lesson_id=lesson_id).exists():
            raise ValidationError("Урок с таким course_id и lesson_id уже существует")

        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')
        lesson_id = self.kwargs.get('pk')

        try:
            instance = LessonCourses.objects.get(course_id=course_id, lesson_id=lesson_id)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except LessonCourses.DoesNotExist:
            raise NotFound("Урок не найден")
        except LessonCourses.MultipleObjectsReturned:
            raise NotFound("Найдено несколько объектов для заданных идентификаторов")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        course_id = self.kwargs.get('course_id')
        lesson_id = self.kwargs.get('pk')

        try:
            instance = LessonCourses.objects.get(course_id=course_id, lesson_id=lesson_id)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except LessonCourses.DoesNotExist:
            raise NotFound("Урок не найден")
        except LessonCourses.MultipleObjectsReturned:
            raise NotFound("Найдено несколько объектов для заданных идентификаторов")

    def destroy(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')
        lesson_id = self.kwargs.get('pk')

        try:
            instance = LessonCourses.objects.get(course_id=course_id, lesson_id=lesson_id)
            instance.delete()
            return Response(status=204)
        except LessonCourses.DoesNotExist:
            raise NotFound("Урок не найден")
        except LessonCourses.MultipleObjectsReturned:
            raise NotFound("Найдено несколько объектов для заданных идентификаторов")


class TestView(viewsets.ModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestSerializers

    def get_queryset(self):
        lesson_id = self.kwargs.get('lesson_id')
        if not lesson_id:
            raise NotFound("Не указан идентификатор урока")

        queryset = TestModel.objects.filter(lesson_id=lesson_id)
        test_id = self.kwargs.get('pk')
        if test_id:
            queryset = queryset.filter(id=test_id)
        return queryset

    def create(self, request, *args, **kwargs):
        lesson_id = self.kwargs.get('lesson_id')
        request.data['lesson'] = lesson_id

        if not LessonCourses.objects.filter(id=lesson_id).exists():
            raise NotFound("Урок с указанным идентификатором не найден")

        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        lesson_id = self.kwargs.get('lesson_id')
        test_id = self.kwargs.get('pk')

        logger.debug(f"Retrieve Test: lesson_id={lesson_id}, test_id={test_id}")

        try:
            instance = TestModel.objects.get(lesson_id=lesson_id, id=test_id)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except TestModel.DoesNotExist:
            logger.error(f"Test not found for lesson_id={lesson_id} and test_id={test_id}")
            raise NotFound(f"Тест не найден для lesson_id: {lesson_id} и test_id: {test_id}")
        except TestModel.MultipleObjectsReturned:
            logger.error(f"Multiple tests found for lesson_id={lesson_id} and test_id={test_id}")
            raise NotFound("Найдено несколько объектов для заданных идентификаторов")

    def update(self, request, *args, **kwargs):
        lesson_id = self.kwargs.get('lesson_id')
        test_id = self.kwargs.get('pk')

        logger.debug(f"Update Test: lesson_id={lesson_id}, test_id={test_id}")

        try:
            instance = TestModel.objects.get(lesson_id=lesson_id, id=test_id)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except TestModel.DoesNotExist:
            logger.error(f"Test not found for lesson_id={lesson_id} and test_id={test_id}")
            raise NotFound(f"Тест не найден для lesson_id: {lesson_id} и test_id: {test_id}")
        except TestModel.MultipleObjectsReturned:
            logger.error(f"Multiple tests found for lesson_id={lesson_id} and test_id={test_id}")
            raise NotFound("Найдено несколько объектов для заданных идентификаторов")

    def destroy(self, request, *args, **kwargs):
        lesson_id = self.kwargs.get('lesson_id')
        test_id = self.kwargs.get('pk')

        logger.debug(f"Destroy Test: lesson_id={lesson_id}, test_id={test_id}")

        try:
            instance = TestModel.objects.get(lesson_id=lesson_id, id=test_id)
            instance.delete()
            return Response(status=204)
        except TestModel.DoesNotExist:
            logger.error(f"Test not found for lesson_id={lesson_id} and test_id={test_id}")
            raise NotFound(f"Тест не найден для lesson_id: {lesson_id} и test_id: {test_id}")
        except TestModel.MultipleObjectsReturned:
            logger.error(f"Multiple tests found for lesson_id={lesson_id} and test_id={test_id}")
            raise NotFound("Найдено несколько объектов для заданных идентификаторов")


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course')

        if not course_id:
            raise ValidationError("Не указан идентификатор курса")

        if Certificate.objects.filter(user=user, course_id=course_id).exists():
            raise ValidationError("Сертификат для этого курса уже существует")

        certificate_code = str(uuid.uuid4())
        certificate = Certificate.objects.create(
            user=user,
            course_id=course_id,
            certificate_code=certificate_code
        )

        serializer = self.get_serializer(certificate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        try:
            certificate = Certificate.objects.get(pk=kwargs.get('pk'))
            serializer = self.get_serializer(certificate)
            return Response(serializer.data)
        except Certificate.DoesNotExist:
            raise NotFound("Сертификат не найден")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            instance = Certificate.objects.get(pk=kwargs.get('pk'))
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Certificate.DoesNotExist:
            raise NotFound("Сертификат не найден")

    def destroy(self, request, *args, **kwargs):
        try:
            instance = Certificate.objects.get(pk=kwargs.get('pk'))
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Certificate.DoesNotExist:
            raise NotFound("Сертификат не найден")


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course')

        if not course_id:
            raise ValidationError("Не указан идентификатор курса")

        if Certificate.objects.filter(user=user, course_id=course_id).exists():
            raise ValidationError("Сертификат для этого курса уже существует")

        certificate_code = str(uuid.uuid4())
        certificate = Certificate.objects.create(
            user=user,
            course_id=course_id,
            certificate_code=certificate_code
        )

        pdf_content = generate_certificate_pdf(certificate)
        certificate.pdf.save(f"certificate_{certificate.id}.pdf", pdf_content)

        serializer = self.get_serializer(certificate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        try:
            certificate = Certificate.objects.get(pk=kwargs.get('pk'))
            serializer = self.get_serializer(certificate)
            return Response(serializer.data)
        except Certificate.DoesNotExist:
            raise NotFound("Сертификат не найден")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            instance = Certificate.objects.get(pk=kwargs.get('pk'))
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Certificate.DoesNotExist:
            raise NotFound("Сертификат не найден")

    def destroy(self, request, *args, **kwargs):
        try:
            instance = Certificate.objects.get(pk=kwargs.get('pk'))
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Certificate.DoesNotExist:
            raise NotFound("Сертификат не найден")



class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        courses_id = self.request.query_params.get('courses_id')
        if courses_id is not None:
            return Review.objects.filter(courses_id=courses_id)
        return Review.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class Buy(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
