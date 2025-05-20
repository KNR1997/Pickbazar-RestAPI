import django_filters

from promotions.models import Coupon


class BaseCouponFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(field_name='code', lookup_expr='icontains', label="Code")

    class Meta:
        model = Coupon
        fields = ('id', 'code')
