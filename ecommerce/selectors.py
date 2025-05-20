from typing import Optional

from django.db.models import QuerySet

from common.utils import get_object
from ecommerce.models import Tax, Shipping


def tax_list(*, filters=None) -> QuerySet[Tax]:
    filters = filters or {}

    qs = Tax.objects.all()

    return qs


def tax_get(faq_id) -> Optional[Tax]:
    tax = get_object(Tax, id=faq_id)

    return tax


def shipping_list(*, filters=None) -> QuerySet[Shipping]:
    filters = filters or {}

    qs = Shipping.objects.all()

    return qs


def shipping_get(shipping_id) -> Optional[Shipping]:
    shipping = get_object(Shipping, id=shipping_id)

    return shipping
