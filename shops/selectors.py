from django.db.models import QuerySet

from shops.models import Shop


def shop_list(*, filters=None) -> QuerySet[Shop]:
    filters = filters or {}

    qs = Shop.objects.all()

    return qs