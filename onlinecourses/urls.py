from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from courses.views import CoursesViews, LessonCoursesViewSet, TestView, CertificateViewSet, ReviewViewSet, Buy
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView,
)
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r"api/courses", CoursesViews, basename="course")

router.register(r'reviews', ReviewViewSet, basename='review') # Исправленный URL для отзывов
router.register(r'certificates', CertificateViewSet)
# router.register(r"api/courses/(?P<course_id>\d+)/lessons/(?P<lesson_id>\d+)/tests", TestView, basename='test')



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api/courses/<int:course_id>/lessons/', LessonCoursesViewSet.as_view({'get': 'list', 'post': 'create'}), name='lesson-list'),
    path('api/courses/<int:course_id>/lessons/<int:pk>/', LessonCoursesViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='lesson-detail'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/courses/<int:course_id>/lessons/<int:lesson_id>/tests/', TestView.as_view({'get': 'list', 'post': 'create'}), name='test-list'),
    path('api/courses/<int:course_id>/lessons/<int:lesson_id>/tests/<int:pk>/', TestView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='test-detail'),
    # path('api/courses/certificates/', CertificatesViews.as_view({'get':"list"}), name='certificate-list'),  # Исправлено
    # path('api/courses/<int:course_id>/lessons/<int:pk>/tests/',TestView.as_view({'get': 'list', 'post': 'create'}), name='test-list'),
    # path('api/courses/<int:course_id>/lessons/<int:pk>/tests/<int:pk>',TestView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='test-detail'),
]
