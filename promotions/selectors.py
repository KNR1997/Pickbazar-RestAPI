from typing import Optional

from django.db.models import QuerySet

from common.utils import get_object
from feedbacks.models import Review
from promotions.filters import BaseCouponFilter
from promotions.models import Coupon, FlashSale


def coupon_list(*, filters=None) -> QuerySet[Coupon]:
    filters = filters or {}

    qs = Coupon.objects.all()

    return BaseCouponFilter(filters, qs).qs


def coupon_get(code_id) -> Optional[Coupon]:
    coupon = get_object(Coupon, id=code_id)

    return coupon


def coupon_get_by_code(code) -> Optional[Coupon]:
    coupon = get_object(Coupon, code=code)

    return coupon


def flash_sale_list(*, filters=None) -> QuerySet[FlashSale]:
    filters = filters or {}

    qs = FlashSale.objects.all()

    return qs


def flash_sale_get(code_id) -> Optional[FlashSale]:
    flash_sale = get_object(FlashSale, id=code_id)

    return flash_sale


def flash_sale_get_by_slug(slug) -> Optional[FlashSale]:
    flash_sale = get_object(FlashSale, slug=slug)

    return flash_sale


def review_list(*, filters=None) -> QuerySet[FlashSale]:
    filters = filters or {}

    qs = Review.objects.all()

    return qs
