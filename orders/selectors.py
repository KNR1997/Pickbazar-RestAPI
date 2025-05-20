from typing import Optional

from django.db.models import QuerySet

from common.utils import get_object
from orders.models import Order


def order_list(*, filters=None) -> QuerySet[Order]:
    filters = filters or {}

    qs = Order.objects.all()

    return qs


def order_get(type_id) -> Optional[Order]:
    type_ = get_object(Order, id=type_id)

    return type_
