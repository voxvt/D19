import django_filters
from .models import Ad

class AdFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Заголовок')

    class Meta:
        model = Ad
        fields = ['category', 'title']  # Поля, по которым можно фильтровать