from typing import List

from django.db import transaction

from common.services import model_update
from common.utils import get_object
from ecommerce.models import Shipping


@transaction.atomic
def shipping_create(*, name: str,
                    amount: str = None,
                    type: str = None,
                    ) -> Shipping:
    shipping = Shipping.objects.create(name=name,
                                       amount=amount,
                                       type=type,
                                       )

    return shipping


@transaction.atomic
def shipping_update(*, shipping: Shipping, data) -> Shipping:
    non_side_effect_fields: List[str] = [
        "name",
        "amount",
        "type",
    ]

    shipping, has_updated = model_update(instance=shipping, fields=non_side_effect_fields,
                                         data=data)

    # some additional task

    return shipping


@transaction.atomic
def shipping_delete(*, shipping_id: str) -> None:
    shipping = get_object(Shipping, id=shipping_id)
    shipping.delete()
    return None
