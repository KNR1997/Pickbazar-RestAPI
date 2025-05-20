import django_filters

from products.models import Category, Product


class BaseCategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label="Name")

    class Meta:
        model = Category
        fields = ('id', 'name')


class BaseProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label="Name")

    class Meta:
        model = Product
        fields = ("id", "name")
