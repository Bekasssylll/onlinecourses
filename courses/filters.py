import django_filters
from django_filters import filters
from courses.models import CoursesModels

class CoursesFilter(django_filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')

    class Meta:
        model = CoursesModels
        fields = ['name', 'min_price', 'max_price']
