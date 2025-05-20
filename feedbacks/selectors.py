from django.db.models import QuerySet

from promotions.models import Coupon, FlashSale


def coupon_list(*, filters=None) -> QuerySet[Coupon]:
    filters = filters or {}

    qs = Coupon.objects.all()

    return qs


def flash_sale_list(*, filters=None) -> QuerySet[FlashSale]:
    filters = filters or {}

    qs = FlashSale.objects.all()

    return qs
